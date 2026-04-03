"""
Inference script for the Contract Clause Analysis OpenEnv environment.

Two modes:
  --mode openai (DEFAULT) — Uses OpenAI-compatible API via official SDK.
  --mode rule              — Free, no API key needed. Uses keyword matching.

Usage:
  python inference.py                          # OpenAI mode, all tasks
  python inference.py --verbose                # OpenAI mode, with step details
  python inference.py --task clause_identification --verbose
  python inference.py --mode rule --verbose    # Free rule-based mode
  python inference.py --episode 0              # Specify episode number
"""
from __future__ import annotations
import argparse, json, os, re, sys, time, httpx
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")
TASK_IDS = ["clause_identification", "risk_flagging", "contract_comparison"]

# Task-specific safe max_steps defaults (RULE 5)
DEFAULT_MAX_STEPS = {
    "clause_identification": 15,
    "risk_flagging": 30,
    "contract_comparison": 55,
}

CLAUSE_KEYWORDS = {
    "position":          ["position","duties","role","responsibilities",
                          "reporting to","appointed","shall serve as","shall perform"],
    "compensation":      ["salary","compensation","pay","bonus","remuneration",
                          "$","per annum","payable","commission","stock option",
                          "rsu","equity"],
    "termination":       ["terminat","dismissal","separation","resign",
                          "severance","cause","without cause"],
    "confidentiality":   ["confidential","non-disclosure","nda","trade secret",
                          "proprietary","shall not disclose"],
    "non_compete":       ["non-compete","noncompete","shall not.*engage",
                          "shall not.*employed by","competitive",
                          "non-solicitation","solicit"],
    "ip_assignment":     ["intellectual property","ip assignment","work product",
                          "inventions","assigns to","copyright","patent",
                          "work made for hire"],
    "benefits":          ["benefits","insurance","401(k)","vacation",
                          "paid time off","pto","health","dental",
                          "retirement","perquisites"],
    "governing_law":     ["governing law","governed by","jurisdiction","venue",
                          "laws of the state","applicable law"],
    "dispute_resolution":["dispute","arbitration","mediation","arbitrator",
                          "aaa","jams"],
    "probation":         ["probation","probationary","trial period",
                          "initial assessment"],
    "notice_period":     ["notice period","notice of.*days","garden leave",
                          "resignation notice"],
}

RISK_KEYWORDS = {
    "unlimited_liability":    ["not be limited","not be subject to a fixed cap",
                               "sole discretion","aggregate liability","case-by-case",
                               "uncapped","no limit","lesser of","$25,000"],
    "auto_renewal_trap":      ["automatically renew","auto-renew","120 days","90 days",
                               "notice of non-renewal","prevailing rate",
                               "cancellation.*days prior"],
    "unilateral_amendment":   ["reserves the right to modify","amend.*at any time",
                               "unilateral","posting.*website","deemed accepted",
                               "continued use.*acceptance","without consent"],
    "broad_indemnification":  ["indemnify.*regardless","regardless of.*negligence",
                               "regardless of.*defects","hold harmless.*errors",
                               "indemnify.*vendor.*fault"],
    "excessive_penalty":      ["200%","shortfall penalty",
                               "early termination fee.*remaining","25% surcharge",
                               "disproportionate","liquidated damages.*$1"],
    "data_ownership_grab":    ["perpetual.*license.*data","irrevocable.*license",
                               "derivative works","commercialize.*data",
                               "machine learning.*model",
                               "without.*consent.*commercial","insights derived"],
    "non_compete_overreach":  ["36 months","24 months following","all.*personnel",
                               "regardless of.*involvement","$100,000 per",
                               "$150,000 per","any individual"],
    "jurisdiction_trap":      ["singapore","cayman islands","george town",
                               "foreign.*arbitration","notwithstanding.*domiciled",
                               "waives.*objection.*forum"],
}

SEVERITY_KEYWORDS = {
    "critical": ["sole discretion","irrevocable","perpetual","no fixed cap",
                 "cayman","singapore","200%","unilateral right",
                 "all right.*title","$25,000"],
    "high":     ["automatically renew","90 days","120 days","regardless of",
                 "hold harmless","liquidated damages","25% surcharge","36 months"],
    "medium":   ["may adjust","at its discretion","restocking fee"],
}


# ─── Structured stdout logging (RULE 2) ───────────────────────────

def log_start(task_id: str, config: dict):
    print(json.dumps({
        "event": "START",
        "task_id": task_id,
        "config": config
    }), flush=True)


def log_step(task_id: str, step: int, action: dict, obs: dict):
    print(json.dumps({
        "event": "STEP",
        "task_id": task_id,
        "step": step,
        "action": action,
        "obs": obs
    }), flush=True)


def log_end(task_id: str, score: float, steps: int):
    print(json.dumps({
        "event": "END",
        "task_id": task_id,
        "score": score,
        "steps": steps
    }), flush=True)


# ─── Observation summary for logging ──────────────────────────────

def _obs_summary(obs: dict) -> dict:
    """Extract a compact summary from the observation for structured logging."""
    return {
        "section_index": obs.get("current_section_index", -1),
        "section_heading": obs.get("current_section_heading", ""),
        "done": obs.get("done", False),
        "reward": obs.get("reward", 0.0),
        "progress": obs.get("progress", 0.0),
        "system_feedback": (obs.get("system_feedback", "") or "")[:120],
    }


# ─── Rule-based helpers ───────────────────────────────────────────

def rule_classify_clause(text: str) -> str:
    # RULE 7: empty section handling
    if not text.strip():
        return "other"
    text_lower = text.lower()
    best_type, best_score = "other", 0
    for clause_type, keywords in CLAUSE_KEYWORDS.items():
        score = sum(1 for kw in keywords if re.search(kw, text_lower))
        if score > best_score:
            best_score = score
            best_type = clause_type
    return best_type


def rule_detect_risk(text: str) -> tuple[bool, str, str]:
    if not text.strip():
        return False, "", ""
    text_lower = text.lower()
    best_risk, best_score = None, 0
    for risk_type, keywords in RISK_KEYWORDS.items():
        score = sum(1 for kw in keywords if re.search(kw, text_lower))
        if score > best_score:
            best_score = score
            best_risk = risk_type
    if best_score < 2:
        return False, "", ""
    severity = "medium"
    for sev, sev_kws in SEVERITY_KEYWORDS.items():
        for kw in sev_kws:
            if re.search(kw, text_lower):
                severity = sev
                break
        if severity != "medium":
            break
    return True, best_risk or "unknown", severity


def rule_detect_change(original: str, revised: str) -> tuple[bool, str]:
    if original.strip() == revised.strip():
        return False, "neutral"
    orig_lower, rev_lower = original.lower(), revised.lower()
    orig_numbers = set(re.findall(r'\$[\d,]+|\d+%|\d+ (?:days|months|years)', orig_lower))
    rev_numbers  = set(re.findall(r'\$[\d,]+|\d+%|\d+ (?:days|months|years)', rev_lower))
    if orig_numbers != rev_numbers:
        return True, "unfavorable"
    restrictive = ["sole discretion","shall not","may not","without prior",
                   "no obligation","immediately"]
    if sum(1 for r in restrictive if r in rev_lower) > \
       sum(1 for r in restrictive if r in orig_lower):
        return True, "unfavorable"
    orig_words = set(orig_lower.split())
    rev_words  = set(rev_lower.split())
    diff_ratio = len(orig_words.symmetric_difference(rev_words)) / \
                 max(len(orig_words | rev_words), 1)
    if diff_ratio > 0.15:
        return True, "unfavorable"
    elif diff_ratio > 0.05:
        return True, "neutral"
    return False, "neutral"


def split_comparison_section(section_text: str) -> tuple[str, str, bool]:
    """RULE 8: Try multiple delimiters to split original/revised sections."""
    for delim in ["=== REVISED ===", "--- REVISED ---", "REVISED VERSION:"]:
        parts = section_text.split(delim)
        if len(parts) == 2:
            orig_part = parts[0]
            # Also strip the ORIGINAL header if present
            for orig_delim in ["=== ORIGINAL ===", "--- ORIGINAL ---", "ORIGINAL VERSION:"]:
                orig_part = orig_part.replace(orig_delim, "")
            return orig_part.strip(), parts[1].strip(), True
    return section_text, "", False


# ─── OpenAI SDK LLM helper (RULE 1) ──────────────────────────────

def call_llm(messages: list[dict], retries: int = 3) -> str:
    api_base = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
    api_key = os.environ.get("HF_TOKEN", "")
    model = os.environ.get("MODEL_NAME", "gpt-4o-mini")
    if not api_key:
        print("ERROR: HF_TOKEN not set. Use --mode rule for free mode.")
        sys.exit(1)
    llm_client = OpenAI(
        base_url=api_base,
        api_key=api_key,
    )
    for attempt in range(1, retries + 1):
        try:
            response = llm_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,
                max_tokens=1024,
            )
            content = response.choices[0].message.content
            return content or "{}"
        except Exception as exc:
            print(f"  [Attempt {attempt}/{retries}] LLM error: {exc}")
            if attempt < retries:
                time.sleep(2 ** attempt)
    return "{}"


def parse_action(raw: str) -> dict | None:
    raw = raw.strip()
    if "```" in raw:
        for part in raw.split("```"):
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                try:
                    return json.loads(part)
                except json.JSONDecodeError:
                    continue
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(raw[start:end])
            except json.JSONDecodeError:
                pass
    return None


# ─── Task runners ─────────────────────────────────────────────────

def run_task_rule_based(task_id: str, episode: int = 0,
                        verbose: bool = False) -> dict:
    print(f"\n{'='*55}")
    print(f"  Task: {task_id} (rule-based — FREE)")
    print(f"{'='*55}")

    try:
        with httpx.Client(timeout=60, base_url=BASE_URL) as client:
            resp = client.post("/reset", json={"task_id": task_id, "contract_index": 0})
            resp.raise_for_status()
            obs = resp.json()

            # RULE 5: task-specific max_steps defaults
            max_steps = obs.get("max_steps") or DEFAULT_MAX_STEPS.get(task_id, 15)
            steps = 0

            # log_start after /reset succeeds (RULE 2)
            log_start(task_id, {"mode": "rule", "episode": episode, "max_steps": max_steps})

            prev_section_idx = -1
            same_section_count = 0  # RULE 6: anti-infinite-loop guard

            while not obs.get("done", False) and steps < max_steps:
                section_text = obs.get("current_section_text", "")
                section_idx  = obs.get("current_section_index", 0)

                # RULE 6: track consecutive identical section indices
                if section_idx == prev_section_idx:
                    same_section_count += 1
                else:
                    same_section_count = 0
                prev_section_idx = section_idx

                if same_section_count >= 2:
                    if verbose:
                        print("  Stuck on same section. Submitting...")
                    resp = client.post("/step", json={"action_type": "submit"})
                    resp.raise_for_status()
                    result = resp.json()
                    obs = result.get("observation", obs)
                    reward = result.get("reward", 0.0)
                    steps += 1
                    log_step(task_id, steps, {"action_type": "submit"}, _obs_summary(obs))
                    break

                if task_id == "clause_identification":
                    clause_type = rule_classify_clause(section_text)
                    action = {"action_type": "identify_clause",
                              "clause_index": section_idx,
                              "clause_type": clause_type,
                              "confidence": 0.8}
                    if verbose:
                        print(f"  Step {steps+1}: identify section {section_idx} -> '{clause_type}'")
                    resp = client.post("/step", json=action)
                    resp.raise_for_status()
                    result = resp.json()
                    obs = result.get("observation", obs)
                    reward = result.get("reward", 0.0)
                    steps += 1
                    log_step(task_id, steps, action, _obs_summary(obs))
                    if verbose:
                        print(f"    reward={reward:.3f} "
                              f"{obs.get('system_feedback','')[:60]}")
                    if not obs.get("done", False):
                        ns_action = {"action_type": "next_section"}
                        resp = client.post("/step", json=ns_action)
                        resp.raise_for_status()
                        result = resp.json()
                        obs = result.get("observation", obs)
                        reward = result.get("reward", 0.0)
                        steps += 1
                        log_step(task_id, steps, ns_action, _obs_summary(obs))

                elif task_id == "risk_flagging":
                    has_risk, risk_type, severity = rule_detect_risk(section_text)
                    if has_risk:
                        action = {"action_type": "flag_risk",
                                  "clause_index": section_idx,
                                  "clause_type": risk_type,
                                  "confidence": 0.8}
                        if verbose:
                            print(f"  Step {steps+1}: RISK at section {section_idx} -> '{risk_type}'")
                        resp = client.post("/step", json=action)
                        resp.raise_for_status()
                        result = resp.json()
                        obs = result.get("observation", obs)
                        reward = result.get("reward", 0.0)
                        steps += 1
                        log_step(task_id, steps, action, _obs_summary(obs))
                        if verbose:
                            print(f"    reward={reward:.3f}")
                        if not obs.get("done", False):
                            sev_action = {"action_type": "assess_severity",
                                          "clause_index": section_idx,
                                          "risk_level": severity,
                                          "confidence": 0.7}
                            resp = client.post("/step", json=sev_action)
                            resp.raise_for_status()
                            result = resp.json()
                            obs = result.get("observation", obs)
                            reward = result.get("reward", 0.0)
                            steps += 1
                            log_step(task_id, steps, sev_action, _obs_summary(obs))
                            if verbose:
                                print(f"    severity={severity} reward={reward:.3f}")
                    else:
                        if verbose:
                            print(f"  Step {steps+1}: section {section_idx} -> no risk")
                    if not obs.get("done", False):
                        ns_action = {"action_type": "next_section"}
                        resp = client.post("/step", json=ns_action)
                        resp.raise_for_status()
                        result = resp.json()
                        obs = result.get("observation", obs)
                        reward = result.get("reward", 0.0)
                        steps += 1
                        log_step(task_id, steps, ns_action, _obs_summary(obs))

                elif task_id == "contract_comparison":
                    # RULE 8: robust delimiter splitting
                    orig_part, rev_part, found_split = split_comparison_section(section_text)
                    if found_split:
                        has_change, impact = rule_detect_change(orig_part, rev_part)
                    else:
                        has_change, impact = False, "neutral"
                    if has_change:
                        action = {"action_type": "detect_change",
                                  "clause_index": section_idx,
                                  "clause_type": "modified",
                                  "confidence": 0.7}
                        if verbose:
                            print(f"  Step {steps+1}: CHANGE at section {section_idx} -> '{impact}'")
                        resp = client.post("/step", json=action)
                        resp.raise_for_status()
                        result = resp.json()
                        obs = result.get("observation", obs)
                        reward = result.get("reward", 0.0)
                        steps += 1
                        log_step(task_id, steps, action, _obs_summary(obs))
                        if verbose:
                            print(f"    reward={reward:.3f}")
                        if not obs.get("done", False):
                            impact_action = {"action_type": "assess_impact",
                                             "clause_index": section_idx,
                                             "impact": impact,
                                             "confidence": 0.7}
                            resp = client.post("/step", json=impact_action)
                            resp.raise_for_status()
                            result = resp.json()
                            obs = result.get("observation", obs)
                            reward = result.get("reward", 0.0)
                            steps += 1
                            log_step(task_id, steps, impact_action, _obs_summary(obs))
                            if verbose:
                                print(f"    impact={impact} reward={reward:.3f}")
                    else:
                        if verbose:
                            print(f"  Step {steps+1}: section {section_idx} -> no change")
                    if not obs.get("done", False):
                        ns_action = {"action_type": "next_section"}
                        resp = client.post("/step", json=ns_action)
                        resp.raise_for_status()
                        result = resp.json()
                        obs = result.get("observation", obs)
                        reward = result.get("reward", 0.0)
                        steps += 1
                        log_step(task_id, steps, ns_action, _obs_summary(obs))

            if not obs.get("done", False):
                submit_action = {"action_type": "submit"}
                resp = client.post("/step", json=submit_action)
                resp.raise_for_status()
                result = resp.json()
                obs = result.get("observation", obs)
                reward = result.get("reward", 0.0)
                steps += 1
                log_step(task_id, steps, submit_action, _obs_summary(obs))

            resp = client.get("/grader")
            resp.raise_for_status()
            grade = resp.json()

        score = grade.get("score", 0.0)
        log_end(task_id, score, steps)

        return {"task_id": task_id,
                "score": score,
                "steps": steps,
                "max_steps": max_steps}

    except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
        print(f"\nCONNECTION ERROR for {task_id}: {exc}")
        log_end(task_id, score=0.0, steps=0)
        return {"task_id": task_id, "score": 0.0,
                "steps": 0, "max_steps": 0, "error": str(exc)}


def run_task_openai(task_id: str, episode: int = 0,
                    verbose: bool = False) -> dict:
    model = os.environ.get("MODEL_NAME", "gpt-4o-mini")
    print(f"\n{'='*55}")
    print(f"  Task: {task_id} (OpenAI — {model})")
    print(f"{'='*55}")

    try:
        prompts = {
            "clause_identification": (
                "You are a legal analyst. Identify the clause type. "
                "Valid types: position, compensation, termination, confidentiality, "
                "non_compete, ip_assignment, benefits, governing_law, dispute_resolution, "
                "probation, notice_period.\n"
                'Respond ONLY with JSON: {"action_type":"identify_clause",'
                '"clause_index":<int>,"clause_type":"<type>","confidence":<float>}'
            ),
            "risk_flagging": (
                "You are a legal risk analyst. Determine if the section has a hidden risk.\n"
                "Risk types: unlimited_liability, auto_renewal_trap, unilateral_amendment, "
                "broad_indemnification, excessive_penalty, data_ownership_grab, "
                "non_compete_overreach, jurisdiction_trap.\n"
                'If risky: {"action_type":"flag_risk","clause_index":<int>,'
                '"clause_type":"<risk_type>","confidence":<float>}\n'
                'If not risky: {"action_type":"next_section"}'
            ),
            "contract_comparison": (
                "You are a contract redlining specialist. Detect changes between "
                "original and revised.\n"
                'Respond: {"action_type":"detect_change","clause_index":<int>,'
                '"clause_type":"modified","impact":"favorable|neutral|unfavorable",'
                '"confidence":<float>}'
            ),
        }
        with httpx.Client(timeout=60, base_url=BASE_URL) as client:
            resp = client.post("/reset", json={"task_id": task_id, "contract_index": 0})
            resp.raise_for_status()
            obs = resp.json()
            system_prompt = prompts.get(task_id, "You are a legal analyst.")

            # RULE 5: task-specific max_steps defaults
            max_steps = obs.get("max_steps") or DEFAULT_MAX_STEPS.get(task_id, 15)
            steps = 0

            # log_start after /reset succeeds (RULE 2)
            log_start(task_id, {"mode": "openai", "model": model, "episode": episode,
                                "max_steps": max_steps})

            prev_section_idx = -1
            same_section_count = 0  # RULE 6

            while not obs.get("done", False) and steps < max_steps:
                section_idx = obs.get("current_section_index", 0)

                # RULE 6: anti-infinite-loop guard
                if section_idx == prev_section_idx:
                    same_section_count += 1
                else:
                    same_section_count = 0
                prev_section_idx = section_idx

                if same_section_count >= 2:
                    if verbose:
                        print("  Stuck on same section. Submitting...")
                    submit_action = {"action_type": "submit"}
                    resp = client.post("/step", json=submit_action)
                    resp.raise_for_status()
                    result = resp.json()
                    obs = result.get("observation", obs)
                    steps += 1
                    log_step(task_id, steps, submit_action, _obs_summary(obs))
                    break

                user_msg = (
                    f"Section {obs['current_section_index']}: "
                    f"{obs['current_section_heading']}\n\n"
                    f"{obs['current_section_text']}"
                )
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg},
                ]
                llm_output = call_llm(messages)
                action_dict = parse_action(llm_output)

                # RULE 9: LLM fallback alerting
                if action_dict is None:
                    print(json.dumps({"event": "LLM_FALLBACK", "reason": "parse_failed",
                                      "raw": llm_output[:200]}), flush=True)
                    action_dict = {"action_type": "next_section"}
                elif "action_type" not in action_dict:
                    print(json.dumps({"event": "LLM_FALLBACK", "reason": "missing key",
                                      "raw": llm_output[:200]}), flush=True)
                    action_dict = {"action_type": "next_section"}

                if verbose:
                    atype = action_dict.get("action_type", "?")
                    print(f"  Step {steps+1}: {atype} -> idx={action_dict.get('clause_index', '-')}")
                resp = client.post("/step", json=action_dict)
                resp.raise_for_status()
                result = resp.json()
                obs = result.get("observation", obs)
                reward = result.get("reward", 0.0)
                steps += 1
                log_step(task_id, steps, action_dict, _obs_summary(obs))
                if verbose:
                    print(f"    reward={reward:.3f} "
                          f"{obs.get('system_feedback', '')[:60]}")
                main_actions = {"identify_clause", "flag_risk", "detect_change"}
                if action_dict.get("action_type") in main_actions and not obs.get("done", False):
                    ns_action = {"action_type": "next_section"}
                    resp = client.post("/step", json=ns_action)
                    resp.raise_for_status()
                    result = resp.json()
                    obs = result.get("observation", obs)
                    reward = result.get("reward", 0.0)
                    steps += 1
                    log_step(task_id, steps, ns_action, _obs_summary(obs))

            if not obs.get("done", False):
                submit_action = {"action_type": "submit"}
                resp = client.post("/step", json=submit_action)
                resp.raise_for_status()
                result = resp.json()
                obs = result.get("observation", obs)
                reward = result.get("reward", 0.0)
                steps += 1
                log_step(task_id, steps, submit_action, _obs_summary(obs))

            resp = client.get("/grader")
            resp.raise_for_status()
            grade = resp.json()

        score = grade.get("score", 0.0)
        log_end(task_id, score, steps)

        return {"task_id": task_id,
                "score": score,
                "steps": steps,
                "max_steps": max_steps}

    except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
        print(f"\nCONNECTION ERROR for {task_id}: {exc}")
        log_end(task_id, score=0.0, steps=0)
        return {"task_id": task_id, "score": 0.0,
                "steps": 0, "max_steps": 0, "error": str(exc)}


def main():
    parser = argparse.ArgumentParser(
        description="Run inference for Contract Clause Env"
    )
    parser.add_argument("--task", type=str, default=None, choices=TASK_IDS)
    parser.add_argument("--mode", type=str, default="openai",
                        choices=["rule", "openai"])
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--base-url", type=str, default=None)
    parser.add_argument("--episode", type=int, default=0)
    args = parser.parse_args()

    # RULE 4: HF_TOKEN validation at startup
    if args.mode == "openai":
        token = os.environ.get("HF_TOKEN", "")
        if not token:
            raise SystemExit("FATAL: HF_TOKEN is not set. Aborting.")

    global BASE_URL
    if args.base_url:
        BASE_URL = args.base_url

    tasks = [args.task] if args.task else TASK_IDS
    model = os.environ.get("MODEL_NAME", "gpt-4o-mini")

    if args.mode == "rule":
        run_fn = lambda tid, ep=args.episode, v=args.verbose: run_task_rule_based(tid, ep, v)
        print(f"\n  Mode: Rule-Based (FREE)")
    else:
        run_fn = lambda tid, ep=args.episode, v=args.verbose: run_task_openai(tid, ep, v)
        print(f"\n  Mode: OpenAI ({model})")

    results = []
    for tid in tasks:
        try:
            results.append(run_fn(tid))
        except Exception as exc:
            print(f"\nERROR running {tid}: {exc}")
            log_end(tid, score=0.0, steps=0)
            results.append({"task_id": tid, "score": 0.0,
                            "steps": 0, "max_steps": 0, "error": str(exc)})

    diff_map = {"clause_identification": "EASY", "risk_flagging": "MEDIUM",
                "contract_comparison": "HARD"}
    print(f"\n{'='*55}")
    print("  Contract Clause Env — Inference Results")
    print(f"{'='*55}")
    for r in results:
        diff = diff_map.get(r["task_id"], "?")
        if r.get("error"):
            print(f"  Task: {r['task_id']} ({diff})")
            print(f"    ERROR: {r['error']}")
        else:
            print(f"  Task: {r['task_id']} ({diff})")
            print(f"    Score: {r['score']:.2f} / 1.0")
            print(f"    Steps: {r['steps']} / {r['max_steps']}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
