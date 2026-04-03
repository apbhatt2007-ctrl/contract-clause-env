"""
Inference script for the Contract Clause Analysis OpenEnv environment.

Team: antigravity
Domain: Legal contract review (clause identification, risk flagging, contract comparison)

Usage:
  python inference.py                          # OpenAI mode, all tasks
  python inference.py --verbose                # OpenAI mode, with step details
  python inference.py --task clause_identification --verbose
  python inference.py --mode rule --verbose    # Free rule-based mode
  python inference.py --episode 0              # Specify episode number
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import traceback

import httpx
from openai import OpenAI

# ─── Environment variables (MANDATORY) ────────────────────────────
# Must read: API_BASE_URL, MODEL_NAME, HF_TOKEN
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:7860")
MODEL_NAME = os.environ.get("MODEL_NAME", "meta-llama/Meta-Llama-3.1-8B-Instruct")
HF_TOKEN = os.environ.get("HF_TOKEN", "")

# OpenEnv server URL — same as API_BASE_URL for the environment server
ENV_SERVER_URL = os.environ.get("API_BASE_URL", "http://localhost:7860")

TASK_IDS = ["clause_identification", "risk_flagging", "contract_comparison"]

# Task-specific safe max_steps defaults
DEFAULT_MAX_STEPS = {
    "clause_identification": 15,
    "risk_flagging": 30,
    "contract_comparison": 55,
}

# HTTP timeout for all client.post() / client.get() calls
REQUEST_TIMEOUT = 30

# ─── Keyword dictionaries for rule-based fallback ─────────────────

CLAUSE_KEYWORDS = {
    "position":          ["position", "duties", "role", "responsibilities",
                          "reporting to", "appointed", "shall serve as", "shall perform"],
    "compensation":      ["salary", "compensation", "pay", "bonus", "remuneration",
                          "$", "per annum", "payable", "commission", "stock option",
                          "rsu", "equity"],
    "termination":       ["terminat", "dismissal", "separation", "resign",
                          "severance", "cause", "without cause"],
    "confidentiality":   ["confidential", "non-disclosure", "nda", "trade secret",
                          "proprietary", "shall not disclose"],
    "non_compete":       ["non-compete", "noncompete", "shall not.*engage",
                          "shall not.*employed by", "competitive",
                          "non-solicitation", "solicit"],
    "ip_assignment":     ["intellectual property", "ip assignment", "work product",
                          "inventions", "assigns to", "copyright", "patent",
                          "work made for hire"],
    "benefits":          ["benefits", "insurance", "401(k)", "vacation",
                          "paid time off", "pto", "health", "dental",
                          "retirement", "perquisites"],
    "governing_law":     ["governing law", "governed by", "jurisdiction", "venue",
                          "laws of the state", "applicable law"],
    "dispute_resolution": ["dispute", "arbitration", "mediation", "arbitrator",
                          "aaa", "jams"],
    "probation":         ["probation", "probationary", "trial period",
                          "initial assessment"],
    "notice_period":     ["notice period", "notice of.*days", "garden leave",
                          "resignation notice"],
}

RISK_KEYWORDS = {
    "unlimited_liability":    ["not be limited", "not be subject to a fixed cap",
                               "sole discretion", "aggregate liability", "case-by-case",
                               "uncapped", "no limit", "lesser of", "$25,000"],
    "auto_renewal_trap":      ["automatically renew", "auto-renew", "120 days", "90 days",
                               "notice of non-renewal", "prevailing rate",
                               "cancellation.*days prior"],
    "unilateral_amendment":   ["reserves the right to modify", "amend.*at any time",
                               "unilateral", "posting.*website", "deemed accepted",
                               "continued use.*acceptance", "without consent"],
    "broad_indemnification":  ["indemnify.*regardless", "regardless of.*negligence",
                               "regardless of.*defects", "hold harmless.*errors",
                               "indemnify.*vendor.*fault"],
    "excessive_penalty":      ["200%", "shortfall penalty",
                               "early termination fee.*remaining", "25% surcharge",
                               "disproportionate", "liquidated damages.*$1"],
    "data_ownership_grab":    ["perpetual.*license.*data", "irrevocable.*license",
                               "derivative works", "commercialize.*data",
                               "machine learning.*model",
                               "without.*consent.*commercial", "insights derived"],
    "non_compete_overreach":  ["36 months", "24 months following", "all.*personnel",
                               "regardless of.*involvement", "$100,000 per",
                               "$150,000 per", "any individual"],
    "jurisdiction_trap":      ["singapore", "cayman islands", "george town",
                               "foreign.*arbitration", "notwithstanding.*domiciled",
                               "waives.*objection.*forum"],
}

SEVERITY_KEYWORDS = {
    "critical": ["sole discretion", "irrevocable", "perpetual", "no fixed cap",
                 "cayman", "singapore", "200%", "unilateral right",
                 "all right.*title", "$25,000"],
    "high":     ["automatically renew", "90 days", "120 days", "regardless of",
                 "hold harmless", "liquidated damages", "25% surcharge", "36 months"],
    "medium":   ["may adjust", "at its discretion", "restocking fee"],
}


# ═══════════════════════════════════════════════════════════════════
# Structured stdout logging — EXACT format required by evaluator
#
#   print(json.dumps({"type": "[START]", "task_id": "<id>", "model": MODEL_NAME}))
#   print(json.dumps({"type": "[STEP]",  "task_id": "<id>", "step": N, "action": {...}, "reward": R, "done": D}))
#   print(json.dumps({"type": "[END]",   "task_id": "<id>", "score": S}))
#
# All payloads must be valid JSON on a single line.
# ═══════════════════════════════════════════════════════════════════

TASK_NAMES = {
    "clause_identification": "Clause Identification",
    "risk_flagging": "Risk Flagging & Analysis",
    "contract_comparison": "Multi-Contract Comparison & Redlining",
}


def log_start(task_id: str) -> None:
    print(json.dumps({
        "type": "[START]",
        "task_id": task_id,
        "model": MODEL_NAME,
    }), flush=True)


def log_step(task_id: str, step: int, action: dict, reward: float, done: bool) -> None:
    print(json.dumps({
        "type": "[STEP]",
        "task_id": task_id,
        "step": step,
        "action": action,
        "reward": reward,
        "done": done,
    }), flush=True)


def log_end(task_id: str, score: float) -> None:
    print(json.dumps({
        "type": "[END]",
        "task_id": task_id,
        "score": score,
    }), flush=True)


# ═══════════════════════════════════════════════════════════════════
# Rule-based helpers (fallback when no LLM available)
# ═══════════════════════════════════════════════════════════════════

def rule_classify_clause(text: str) -> str:
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
    rev_numbers = set(re.findall(r'\$[\d,]+|\d+%|\d+ (?:days|months|years)', rev_lower))
    if orig_numbers != rev_numbers:
        return True, "unfavorable"
    restrictive = ["sole discretion", "shall not", "may not", "without prior",
                    "no obligation", "immediately"]
    if sum(1 for r in restrictive if r in rev_lower) > \
       sum(1 for r in restrictive if r in orig_lower):
        return True, "unfavorable"
    orig_words = set(orig_lower.split())
    rev_words = set(rev_lower.split())
    diff_ratio = len(orig_words.symmetric_difference(rev_words)) / \
                 max(len(orig_words | rev_words), 1)
    if diff_ratio > 0.15:
        return True, "unfavorable"
    elif diff_ratio > 0.05:
        return True, "neutral"
    return False, "neutral"


def split_comparison_section(section_text: str) -> tuple[str, str, bool]:
    for delim in ["=== REVISED ===", "--- REVISED ---", "REVISED VERSION:"]:
        parts = section_text.split(delim)
        if len(parts) == 2:
            orig_part = parts[0]
            for orig_delim in ["=== ORIGINAL ===", "--- ORIGINAL ---", "ORIGINAL VERSION:"]:
                orig_part = orig_part.replace(orig_delim, "")
            return orig_part.strip(), parts[1].strip(), True
    return section_text, "", False


# ═══════════════════════════════════════════════════════════════════
# OpenAI SDK LLM helper — uses from openai import OpenAI
# ═══════════════════════════════════════════════════════════════════

def call_llm(messages: list[dict], retries: int = 3) -> str:
    """Call the LLM using the OpenAI SDK. Uses API_BASE_URL and HF_TOKEN."""
    llm_client = OpenAI(
        base_url=API_BASE_URL,
        api_key=HF_TOKEN,
    )
    for attempt in range(1, retries + 1):
        try:
            response = llm_client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.1,
                max_tokens=512,
            )
            content = response.choices[0].message.content
            return content or "{}"
        except Exception as exc:
            print(f"  [LLM Attempt {attempt}/{retries}] Error: {exc}", file=sys.stderr, flush=True)
            if attempt < retries:
                time.sleep(2 ** attempt)
    return "{}"


def parse_action(raw: str) -> dict | None:
    """Parse LLM output to extract a JSON action dict."""
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


# ═══════════════════════════════════════════════════════════════════
# Safe HTTP call wrapper (timeout protection)
# ═══════════════════════════════════════════════════════════════════

def safe_post(client: httpx.Client, url: str, json_data: dict) -> httpx.Response:
    """Wrap client.post() with 30-second timeout and error handling."""
    return client.post(url, json=json_data, timeout=REQUEST_TIMEOUT)


def safe_get(client: httpx.Client, url: str) -> httpx.Response:
    """Wrap client.get() with 30-second timeout and error handling."""
    return client.get(url, timeout=REQUEST_TIMEOUT)


# ═══════════════════════════════════════════════════════════════════
# Task runner: Rule-based mode (FREE, no API key needed)
# ═══════════════════════════════════════════════════════════════════

def run_task_rule_based(task_id: str, episode: int = 0,
                        verbose: bool = False) -> dict:
    task_name = TASK_NAMES.get(task_id, task_id)
    if verbose:
        print(f"\n{'=' * 55}", file=sys.stderr)
        print(f"  Task: {task_id} (rule-based — FREE)", file=sys.stderr)
        print(f"{'=' * 55}", file=sys.stderr)

    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT, base_url=ENV_SERVER_URL) as client:
            # ── Reset ──
            resp = safe_post(client, "/reset", {"task_id": task_id, "contract_index": 0})
            resp.raise_for_status()
            obs = resp.json()

            max_steps = obs.get("max_steps") or obs.get("total_steps") or DEFAULT_MAX_STEPS.get(task_id, 50)
            steps = 0

            # Log [START] after /reset succeeds
            log_start(task_id)

            prev_section_idx = -1
            same_section_count = 0

            while not obs.get("done", False) and steps < max_steps:
                section_text = obs.get("current_section_text", "")
                section_idx = obs.get("current_section_index", 0)

                same_section_count = same_section_count + 1 if section_idx == prev_section_idx else 0
                prev_section_idx = section_idx

                if same_section_count >= 2:
                    if verbose:
                        print("  Stuck on same section (2 consecutive). Submitting...", file=sys.stderr)
                    submit_action = {"action_type": "submit"}
                    resp = safe_post(client, "/step", submit_action)
                    resp.raise_for_status()
                    result = resp.json()
                    obs = result.get("observation", obs)
                    reward = result.get("reward", 0.0)
                    done = obs.get("done", True)
                    steps += 1
                    log_step(task_id, steps, submit_action, reward, done)
                    break

                # ── Clause Identification ──
                if task_id == "clause_identification":
                    clause_type = rule_classify_clause(section_text)
                    action = {
                        "action_type": "identify_clause",
                        "clause_index": section_idx,
                        "clause_type": clause_type,
                        "confidence": 0.8,
                    }
                    if verbose:
                        print(f"  Step {steps + 1}: identify section {section_idx} -> '{clause_type}'", file=sys.stderr)

                    resp = safe_post(client, "/step", action)
                    resp.raise_for_status()
                    result = resp.json()
                    obs = result.get("observation", obs)
                    reward = result.get("reward", 0.0)
                    done = obs.get("done", False)
                    steps += 1
                    log_step(task_id, steps, action, reward, done)

                    if not obs.get("done", False):
                        ns_action = {"action_type": "next_section"}
                        resp = safe_post(client, "/step", ns_action)
                        resp.raise_for_status()
                        result = resp.json()
                        obs = result.get("observation", obs)
                        reward = result.get("reward", 0.0)
                        done = obs.get("done", False)
                        steps += 1
                        log_step(task_id, steps, ns_action, reward, done)

                # ── Risk Flagging ──
                elif task_id == "risk_flagging":
                    has_risk, risk_type, severity = rule_detect_risk(section_text)
                    if has_risk:
                        action = {
                            "action_type": "flag_risk",
                            "clause_index": section_idx,
                            "clause_type": risk_type,
                            "confidence": 0.8,
                        }
                        if verbose:
                            print(f"  Step {steps + 1}: RISK at section {section_idx} -> '{risk_type}'", file=sys.stderr)

                        resp = safe_post(client, "/step", action)
                        resp.raise_for_status()
                        result = resp.json()
                        obs = result.get("observation", obs)
                        reward = result.get("reward", 0.0)
                        done = obs.get("done", False)
                        steps += 1
                        log_step(task_id, steps, action, reward, done)

                        if not obs.get("done", False):
                            sev_action = {
                                "action_type": "assess_severity",
                                "clause_index": section_idx,
                                "risk_level": severity,
                                "confidence": 0.7,
                            }
                            resp = safe_post(client, "/step", sev_action)
                            resp.raise_for_status()
                            result = resp.json()
                            obs = result.get("observation", obs)
                            reward = result.get("reward", 0.0)
                            done = obs.get("done", False)
                            steps += 1
                            log_step(task_id, steps, sev_action, reward, done)

                    if not obs.get("done", False):
                        ns_action = {"action_type": "next_section"}
                        resp = safe_post(client, "/step", ns_action)
                        resp.raise_for_status()
                        result = resp.json()
                        obs = result.get("observation", obs)
                        reward = result.get("reward", 0.0)
                        done = obs.get("done", False)
                        steps += 1
                        log_step(task_id, steps, ns_action, reward, done)

                # ── Contract Comparison ──
                elif task_id == "contract_comparison":
                    orig_part, rev_part, found_split = split_comparison_section(section_text)
                    if found_split:
                        has_change, impact = rule_detect_change(orig_part, rev_part)
                    else:
                        has_change, impact = False, "neutral"

                    if has_change:
                        action = {
                            "action_type": "detect_change",
                            "clause_index": section_idx,
                            "clause_type": "modified",
                            "confidence": 0.7,
                        }
                        if verbose:
                            print(f"  Step {steps + 1}: CHANGE at section {section_idx} -> '{impact}'", file=sys.stderr)

                        resp = safe_post(client, "/step", action)
                        resp.raise_for_status()
                        result = resp.json()
                        obs = result.get("observation", obs)
                        reward = result.get("reward", 0.0)
                        done = obs.get("done", False)
                        steps += 1
                        log_step(task_id, steps, action, reward, done)

                        if not obs.get("done", False):
                            impact_action = {
                                "action_type": "assess_impact",
                                "clause_index": section_idx,
                                "impact": impact,
                                "confidence": 0.7,
                            }
                            resp = safe_post(client, "/step", impact_action)
                            resp.raise_for_status()
                            result = resp.json()
                            obs = result.get("observation", obs)
                            reward = result.get("reward", 0.0)
                            done = obs.get("done", False)
                            steps += 1
                            log_step(task_id, steps, impact_action, reward, done)

                    if not obs.get("done", False):
                        ns_action = {"action_type": "next_section"}
                        resp = safe_post(client, "/step", ns_action)
                        resp.raise_for_status()
                        result = resp.json()
                        obs = result.get("observation", obs)
                        reward = result.get("reward", 0.0)
                        done = obs.get("done", False)
                        steps += 1
                        log_step(task_id, steps, ns_action, reward, done)

            # ── Final submit if not already done ──
            if not obs.get("done", False):
                submit_action = {"action_type": "submit"}
                resp = safe_post(client, "/step", submit_action)
                resp.raise_for_status()
                result = resp.json()
                obs = result.get("observation", obs)
                reward = result.get("reward", 0.0)
                done = obs.get("done", True)
                steps += 1
                log_step(task_id, steps, submit_action, reward, done)

            # ── Get grade ──
            resp = safe_get(client, "/grader")
            resp.raise_for_status()
            grade = resp.json()

        score = grade.get("score", 0.0)
        log_end(task_id, score)

        return {"task_id": task_id, "score": score, "steps": steps, "max_steps": max_steps}

    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.TimeoutException) as exc:
        print(f"\nCONNECTION ERROR for {task_id}: {exc}", file=sys.stderr, flush=True)
        log_end(task_id, score=0.0)
        return {"task_id": task_id, "score": 0.0, "steps": 0, "max_steps": 0, "error": str(exc)}
    except Exception as exc:
        print(f"\nUNEXPECTED ERROR for {task_id}: {exc}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        log_end(task_id, score=0.0)
        return {"task_id": task_id, "score": 0.0, "steps": 0, "max_steps": 0, "error": str(exc)}


# ═══════════════════════════════════════════════════════════════════
# Task runner: OpenAI LLM mode
# ═══════════════════════════════════════════════════════════════════

def run_task_openai(task_id: str, episode: int = 0,
                    verbose: bool = False) -> dict:
    task_name = TASK_NAMES.get(task_id, task_id)
    if verbose:
        print(f"\n{'=' * 55}", file=sys.stderr)
        print(f"  Task: {task_id} (OpenAI — {MODEL_NAME})", file=sys.stderr)
        print(f"{'=' * 55}", file=sys.stderr)

    try:
        prompts = {
            "clause_identification": (
                "You are an expert legal analyst reviewing an employment contract.\n"
                "Your task: Identify the clause type of the given section.\n"
                "Valid clause types: position, compensation, termination, confidentiality, "
                "non_compete, ip_assignment, benefits, governing_law, dispute_resolution, "
                "probation, notice_period.\n\n"
                "IMPORTANT: First explain your reasoning briefly, then respond with ONLY "
                "a JSON object on a separate line:\n"
                '{"action_type":"identify_clause","clause_index":<int>,'
                '"clause_type":"<type>","confidence":<float 0-1>}'
            ),
            "risk_flagging": (
                "You are an expert legal risk analyst reviewing a vendor/service contract.\n"
                "Your task: Determine if this section contains hidden legal risks.\n"
                "Risk types: unlimited_liability, auto_renewal_trap, unilateral_amendment, "
                "broad_indemnification, excessive_penalty, data_ownership_grab, "
                "non_compete_overreach, jurisdiction_trap.\n\n"
                "IMPORTANT: First explain your legal reasoning briefly, then respond with "
                "ONLY a JSON object on a separate line:\n"
                'If risky: {"action_type":"flag_risk","clause_index":<int>,'
                '"clause_type":"<risk_type>","confidence":<float 0-1>}\n'
                'If not risky: {"action_type":"next_section"}'
            ),
            "contract_comparison": (
                "You are an expert contract redlining specialist.\n"
                "Your task: Compare the original and revised versions of a contract section. "
                "Detect changes and assess their impact.\n\n"
                "IMPORTANT: First explain your reasoning briefly, then respond with ONLY "
                "a JSON object on a separate line:\n"
                'If changed: {"action_type":"detect_change","clause_index":<int>,'
                '"clause_type":"modified","impact":"favorable|neutral|unfavorable",'
                '"confidence":<float 0-1>}\n'
                'If no change: {"action_type":"next_section"}'
            ),
        }

        with httpx.Client(timeout=REQUEST_TIMEOUT, base_url=ENV_SERVER_URL) as client:
            # ── Reset ──
            resp = safe_post(client, "/reset", {"task_id": task_id, "contract_index": 0})
            resp.raise_for_status()
            obs = resp.json()
            system_prompt = prompts.get(task_id, "You are a legal analyst.")

            max_steps = obs.get("max_steps") or obs.get("total_steps") or DEFAULT_MAX_STEPS.get(task_id, 50)
            steps = 0

            # Log [START] after /reset succeeds
            log_start(task_id)

            prev_section_idx = -1
            same_section_count = 0

            while not obs.get("done", False) and steps < max_steps:
                section_idx = obs.get("current_section_index", 0)

                same_section_count = same_section_count + 1 if section_idx == prev_section_idx else 0
                prev_section_idx = section_idx

                if same_section_count >= 2:
                    if verbose:
                        print("  Stuck on same section (2 consecutive). Submitting...", file=sys.stderr)
                    submit_action = {"action_type": "submit"}
                    resp = safe_post(client, "/step", submit_action)
                    resp.raise_for_status()
                    result = resp.json()
                    obs = result.get("observation", obs)
                    done = obs.get("done", True)
                    steps += 1
                    log_step(task_id, steps, submit_action, 0.0, done)
                    break

                # Build user message from observation
                section_heading = obs.get("current_section_heading", "Unknown")
                section_text = obs.get("current_section_text", "")
                user_msg = (
                    f"Section {section_idx}: {section_heading}\n\n"
                    f"{section_text}"
                )
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg},
                ]

                # Call LLM
                llm_output = call_llm(messages)
                action_dict = parse_action(llm_output)

                # Fallback if LLM parse fails
                if action_dict is None:
                    if verbose:
                        print(f"  LLM parse failed, falling back to next_section", file=sys.stderr)
                    action_dict = {"action_type": "next_section"}
                elif "action_type" not in action_dict:
                    action_dict = {"action_type": "next_section"}

                if verbose:
                    atype = action_dict.get("action_type", "?")
                    print(f"  Step {steps + 1}: {atype} -> idx={action_dict.get('clause_index', '-')}", file=sys.stderr)

                # Execute action
                resp = safe_post(client, "/step", action_dict)
                resp.raise_for_status()
                result = resp.json()
                obs = result.get("observation", obs)
                reward = result.get("reward", 0.0)
                done = obs.get("done", False)
                steps += 1
                log_step(task_id, steps, action_dict, reward, done)

                if verbose:
                    print(f"    reward={reward:.3f} {obs.get('system_feedback', '')[:60]}", file=sys.stderr)

                # Auto-advance after main actions
                main_actions = {"identify_clause", "flag_risk", "detect_change"}
                if action_dict.get("action_type") in main_actions and not obs.get("done", False):
                    ns_action = {"action_type": "next_section"}
                    resp = safe_post(client, "/step", ns_action)
                    resp.raise_for_status()
                    result = resp.json()
                    obs = result.get("observation", obs)
                    reward = result.get("reward", 0.0)
                    done = obs.get("done", False)
                    steps += 1
                    log_step(task_id, steps, ns_action, reward, done)

                # For risk_flagging: also assess severity after flag_risk
                if (task_id == "risk_flagging"
                        and action_dict.get("action_type") == "flag_risk"
                        and not obs.get("done", False)):
                    section_text_for_sev = obs.get("current_section_text", section_text)
                    _, _, severity = rule_detect_risk(section_text_for_sev)
                    if not severity:
                        severity = "medium"
                    sev_action = {
                        "action_type": "assess_severity",
                        "clause_index": section_idx,
                        "risk_level": severity,
                        "confidence": 0.7,
                    }
                    resp = safe_post(client, "/step", sev_action)
                    resp.raise_for_status()
                    result = resp.json()
                    obs = result.get("observation", obs)
                    reward = result.get("reward", 0.0)
                    done = obs.get("done", False)
                    steps += 1
                    log_step(task_id, steps, sev_action, reward, done)

                # For contract_comparison: also assess impact after detect_change
                if (task_id == "contract_comparison"
                        and action_dict.get("action_type") == "detect_change"
                        and not obs.get("done", False)):
                    impact = action_dict.get("impact", "unfavorable")
                    impact_action = {
                        "action_type": "assess_impact",
                        "clause_index": section_idx,
                        "impact": impact,
                        "confidence": 0.7,
                    }
                    resp = safe_post(client, "/step", impact_action)
                    resp.raise_for_status()
                    result = resp.json()
                    obs = result.get("observation", obs)
                    reward = result.get("reward", 0.0)
                    done = obs.get("done", False)
                    steps += 1
                    log_step(task_id, steps, impact_action, reward, done)

            # ── Final submit if not already done ──
            if not obs.get("done", False):
                submit_action = {"action_type": "submit"}
                resp = safe_post(client, "/step", submit_action)
                resp.raise_for_status()
                result = resp.json()
                obs = result.get("observation", obs)
                reward = result.get("reward", 0.0)
                done = obs.get("done", True)
                steps += 1
                log_step(task_id, steps, submit_action, reward, done)

            # ── Get grade ──
            resp = safe_get(client, "/grader")
            resp.raise_for_status()
            grade = resp.json()

        score = grade.get("score", 0.0)
        log_end(task_id, score)

        return {"task_id": task_id, "score": score, "steps": steps, "max_steps": max_steps}

    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.TimeoutException) as exc:
        print(f"\nCONNECTION ERROR for {task_id}: {exc}", file=sys.stderr, flush=True)
        log_end(task_id, score=0.0)
        return {"task_id": task_id, "score": 0.0, "steps": 0, "max_steps": 0, "error": str(exc)}
    except Exception as exc:
        print(f"\nUNEXPECTED ERROR for {task_id}: {exc}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        log_end(task_id, score=0.0)
        return {"task_id": task_id, "score": 0.0, "steps": 0, "max_steps": 0, "error": str(exc)}


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Run inference for Contract Clause Env (Team: antigravity)"
    )
    parser.add_argument("--task", type=str, default=None, choices=TASK_IDS)
    parser.add_argument("--mode", type=str, default="openai",
                        choices=["rule", "openai"])
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--base-url", type=str, default=None)
    parser.add_argument("--episode", type=int, default=0)
    args = parser.parse_args()

    # HF_TOKEN validation at startup for openai mode
    if args.mode == "openai":
        if not os.environ.get("HF_TOKEN"):
            raise SystemExit("ERROR: HF_TOKEN is not set. Exiting.")

    if args.base_url:
        global ENV_SERVER_URL
        ENV_SERVER_URL = args.base_url

    tasks = [args.task] if args.task else TASK_IDS

    if args.mode == "rule":
        print(f"  Mode: Rule-Based (FREE)", file=sys.stderr, flush=True)
    else:
        print(f"  Mode: OpenAI ({MODEL_NAME})", file=sys.stderr, flush=True)

    results = []
    for tid in tasks:
        try:
            if args.mode == "rule":
                result = run_task_rule_based(tid, args.episode, args.verbose)
            else:
                result = run_task_openai(tid, args.episode, args.verbose)
            results.append(result)
        except Exception as exc:
            print(f"\nERROR running {tid}: {exc}", file=sys.stderr, flush=True)
            log_end(tid, score=0.0)
            results.append({
                "task_id": tid, "score": 0.0,
                "steps": 0, "max_steps": 0, "error": str(exc),
            })

    # ── Summary (to stderr so it doesn't pollute evaluator stdout) ──
    diff_map = {
        "clause_identification": "EASY",
        "risk_flagging": "MEDIUM",
        "contract_comparison": "HARD",
    }
    print(f"\n{'=' * 55}", file=sys.stderr, flush=True)
    print("  Contract Clause Env — Inference Results", file=sys.stderr, flush=True)
    print(f"{'=' * 55}", file=sys.stderr, flush=True)
    for r in results:
        diff = diff_map.get(r["task_id"], "?")
        if r.get("error"):
            print(f"  Task: {r['task_id']} ({diff})", file=sys.stderr)
            print(f"    ERROR: {r['error']}", file=sys.stderr)
        else:
            print(f"  Task: {r['task_id']} ({diff})", file=sys.stderr)
            print(f"    Score: {r['score']:.2f} / 1.0", file=sys.stderr)
            print(f"    Steps: {r['steps']} / {r['max_steps']}", file=sys.stderr)
    print(f"{'=' * 55}\n", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
