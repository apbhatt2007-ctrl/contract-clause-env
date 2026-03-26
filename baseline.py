"""
Baseline inference script for the Contract Clause Analysis OpenEnv environment.

Two modes:
  --mode rule   (DEFAULT) — Free, no API key needed. Uses keyword matching.
  --mode openai           — Uses OpenAI API (costs ~$0.01-0.05).

Usage:
    python baseline.py                          # Free rule-based, all tasks
    python baseline.py --verbose                # Free, with step details
    python baseline.py --task clause_identification --verbose
    python baseline.py --mode openai --verbose  # Uses OpenAI (needs API key)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

TASK_IDS = ["clause_identification", "risk_flagging", "contract_comparison"]


# ═══════════════════════════════════════════════════════════
# Rule-Based Agent (100% FREE — no API key needed)
# ═══════════════════════════════════════════════════════════

# Keywords for clause type identification
CLAUSE_KEYWORDS = {
    "position": ["position", "duties", "role", "responsibilities", "reporting to", "appointed", "shall serve as", "shall perform"],
    "compensation": ["salary", "compensation", "pay", "bonus", "remuneration", "$", "per annum", "payable", "commission", "stock option", "rsu", "equity"],
    "termination": ["terminat", "dismissal", "separation", "resign", "severance", "cause", "without cause"],
    "confidentiality": ["confidential", "non-disclosure", "nda", "trade secret", "proprietary", "shall not disclose"],
    "non_compete": ["non-compete", "noncompete", "shall not.*engage", "shall not.*employed by", "competitive", "non-solicitation", "solicit"],
    "ip_assignment": ["intellectual property", "ip assignment", "work product", "inventions", "assigns to", "copyright", "patent", "work made for hire"],
    "benefits": ["benefits", "insurance", "401(k)", "vacation", "paid time off", "pto", "health", "dental", "retirement", "perquisites"],
    "governing_law": ["governing law", "governed by", "jurisdiction", "venue", "laws of the state", "applicable law"],
    "dispute_resolution": ["dispute", "arbitration", "mediation", "arbitrator", "aaa", "jams"],
    "probation": ["probation", "probationary", "trial period", "initial assessment"],
    "notice_period": ["notice period", "notice of.*days", "garden leave", "resignation notice"],
}

# Keywords for risk type identification
RISK_KEYWORDS = {
    "unlimited_liability": ["not be limited", "not be subject to a fixed cap", "sole discretion", "aggregate liability", "case-by-case", "uncapped", "no limit", "lesser of", "$25,000"],
    "auto_renewal_trap": ["automatically renew", "auto-renew", "120 days", "90 days", "notice of non-renewal", "prevailing rate", "cancellation.*days prior"],
    "unilateral_amendment": ["reserves the right to modify", "amend.*at any time", "unilateral", "posting.*website", "deemed accepted", "continued use.*acceptance", "without consent"],
    "broad_indemnification": ["indemnify.*regardless", "regardless of.*negligence", "regardless of.*defects", "hold harmless.*errors", "indemnify.*vendor.*fault"],
    "excessive_penalty": ["200%", "shortfall penalty", "early termination fee.*remaining", "25% surcharge", "disproportionate", "liquidated damages.*$1"],
    "data_ownership_grab": ["perpetual.*license.*data", "irrevocable.*license", "derivative works", "commercialize.*data", "machine learning.*model", "without.*consent.*commercial", "insights derived"],
    "non_compete_overreach": ["36 months", "24 months following", "all.*personnel", "regardless of.*involvement", "$100,000 per", "$150,000 per", "any individual"],
    "jurisdiction_trap": ["singapore", "cayman islands", "george town", "foreign.*arbitration", "notwithstanding.*domiciled", "waives.*objection.*forum"],
}

SEVERITY_KEYWORDS = {
    "critical": ["sole discretion", "irrevocable", "perpetual", "no fixed cap", "cayman", "singapore", "200%", "unilateral right", "all right.*title", "$25,000"],
    "high": ["automatically renew", "90 days", "120 days", "regardless of", "hold harmless", "liquidated damages", "25% surcharge", "36 months"],
    "medium": ["may adjust", "at its discretion", "restocking fee"],
}


def rule_classify_clause(text: str) -> str:
    """Classify a clause using keyword matching."""
    text_lower = text.lower()
    best_type = "position"
    best_score = 0

    for clause_type, keywords in CLAUSE_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if re.search(kw, text_lower):
                score += 1
        if score > best_score:
            best_score = score
            best_type = clause_type

    return best_type


def rule_detect_risk(text: str) -> tuple[bool, str, str]:
    """Detect if text has a risk, return (has_risk, risk_type, severity)."""
    text_lower = text.lower()

    best_risk = None
    best_score = 0

    for risk_type, keywords in RISK_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if re.search(kw, text_lower):
                score += 1
        if score > best_score:
            best_score = score
            best_risk = risk_type

    if best_score < 2:
        return False, "", ""

    # Determine severity
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
    """Compare two texts and detect if there's a meaningful change."""
    if original.strip() == revised.strip():
        return False, "neutral"

    orig_lower = original.lower()
    rev_lower = revised.lower()

    # Check for price/number changes
    orig_numbers = set(re.findall(r'\$[\d,]+|\d+%|\d+ (?:days|months|years)', orig_lower))
    rev_numbers = set(re.findall(r'\$[\d,]+|\d+%|\d+ (?:days|months|years)', rev_lower))

    if orig_numbers != rev_numbers:
        # If numbers changed, probably unfavorable (conservative assumption)
        return True, "unfavorable"

    # Check for restrictive language additions
    restrictive = ["sole discretion", "shall not", "may not", "without prior", "no obligation", "immediately"]
    orig_restrictive = sum(1 for r in restrictive if r in orig_lower)
    rev_restrictive = sum(1 for r in restrictive if r in rev_lower)

    if rev_restrictive > orig_restrictive:
        return True, "unfavorable"

    # Check for general text differences
    orig_words = set(orig_lower.split())
    rev_words = set(rev_lower.split())
    diff_ratio = len(orig_words.symmetric_difference(rev_words)) / max(len(orig_words | rev_words), 1)

    if diff_ratio > 0.15:
        return True, "unfavorable"
    elif diff_ratio > 0.05:
        return True, "neutral"

    return False, "neutral"


# ═══════════════════════════════════════════════════════════
# OpenAI Agent (optional, costs money)
# ═══════════════════════════════════════════════════════════

def call_openai(messages: list[dict], retries: int = 3) -> str:
    """Send messages to OpenAI API with retry logic."""
    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not set. Use --mode rule for free mode.")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 1024,
    }

    for attempt in range(1, retries + 1):
        try:
            with httpx.Client(timeout=60) as client:
                resp = client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]
        except Exception as exc:
            print(f"  [Attempt {attempt}/{retries}] OpenAI error: {exc}")
            if attempt < retries:
                time.sleep(2 ** attempt)
    return "{}"


def parse_action(raw: str) -> dict | None:
    """Parse LLM output into an action dict."""
    raw = raw.strip()
    if "```" in raw:
        parts = raw.split("```")
        for part in parts:
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
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(raw[start:end])
            except json.JSONDecodeError:
                pass
    return None


# ═══════════════════════════════════════════════════════════
# Task Runners
# ═══════════════════════════════════════════════════════════

def run_task_rule_based(task_id: str, verbose: bool = False) -> dict:
    """Run a task using the FREE rule-based agent."""
    print(f"\n{'=' * 55}")
    print(f"  Task: {task_id} (rule-based — FREE)")
    print(f"{'=' * 55}")

    with httpx.Client(timeout=30, base_url=BASE_URL) as client:
        resp = client.post("/reset", json={"task_id": task_id, "contract_index": 0})
        resp.raise_for_status()
        obs = resp.json()

        steps = 0
        max_steps = obs.get("max_steps", 10)
        prev_section_idx = -1

        while not obs.get("done", False) and steps < max_steps:
            section_text = obs.get("current_section_text", "")
            section_idx = obs.get("current_section_index", 0)

            # If we're stuck on the same section, submit
            if section_idx == prev_section_idx:
                if verbose:
                    print(f"  All sections reviewed. Submitting...")
                resp = client.post("/step", json={"action_type": "submit"})
                resp.raise_for_status()
                result = resp.json()
                obs = result.get("observation", obs)
                steps += 1
                break
            prev_section_idx = section_idx

            if task_id == "clause_identification":
                clause_type = rule_classify_clause(section_text)
                action = {
                    "action_type": "identify_clause",
                    "clause_index": section_idx,
                    "clause_type": clause_type,
                    "confidence": 0.8,
                }

                if verbose:
                    print(f"  Step {steps+1}: identify section {section_idx} -> '{clause_type}'")

                resp = client.post("/step", json=action)
                resp.raise_for_status()
                result = resp.json()
                obs = result.get("observation", obs)
                steps += 1

                if verbose:
                    print(f"    reward={result.get('reward', 0):.3f}  {obs.get('system_feedback', '')[:60]}")

                # Move to next section
                if not obs.get("done", False):
                    resp = client.post("/step", json={"action_type": "next_section"})
                    resp.raise_for_status()
                    result = resp.json()
                    obs = result.get("observation", obs)
                    steps += 1

            elif task_id == "risk_flagging":
                has_risk, risk_type, severity = rule_detect_risk(section_text)

                if has_risk:
                    # Flag the risk
                    action = {
                        "action_type": "flag_risk",
                        "clause_index": section_idx,
                        "clause_type": risk_type,
                        "confidence": 0.8,
                    }
                    if verbose:
                        print(f"  Step {steps+1}: RISK at section {section_idx} -> '{risk_type}'")

                    resp = client.post("/step", json=action)
                    resp.raise_for_status()
                    result = resp.json()
                    obs = result.get("observation", obs)
                    steps += 1

                    if verbose:
                        print(f"    reward={result.get('reward', 0):.3f}  {obs.get('system_feedback', '')[:60]}")

                    # Assess severity
                    if not obs.get("done", False):
                        sev_action = {
                            "action_type": "assess_severity",
                            "clause_index": section_idx,
                            "risk_level": severity,
                            "confidence": 0.7,
                        }
                        resp = client.post("/step", json=sev_action)
                        resp.raise_for_status()
                        result = resp.json()
                        obs = result.get("observation", obs)
                        steps += 1

                        if verbose:
                            print(f"    severity={severity}  reward={result.get('reward', 0):.3f}")
                else:
                    if verbose:
                        print(f"  Step {steps+1}: section {section_idx} -> no risk")

                # Move to next section
                if not obs.get("done", False):
                    resp = client.post("/step", json={"action_type": "next_section"})
                    resp.raise_for_status()
                    result = resp.json()
                    obs = result.get("observation", obs)
                    steps += 1

            elif task_id == "contract_comparison":
                # Split the text into original + revised
                parts = section_text.split("=== REVISED ===")
                if len(parts) == 2:
                    orig_part = parts[0].replace("=== ORIGINAL ===", "").strip()
                    rev_part = parts[1].strip()
                    has_change, impact = rule_detect_change(orig_part, rev_part)
                else:
                    has_change, impact = False, "neutral"

                if has_change:
                    # Detect change
                    action = {
                        "action_type": "detect_change",
                        "clause_index": section_idx,
                        "clause_type": "modified",
                        "confidence": 0.7,
                    }
                    if verbose:
                        print(f"  Step {steps+1}: CHANGE at section {section_idx} -> '{impact}'")

                    resp = client.post("/step", json=action)
                    resp.raise_for_status()
                    result = resp.json()
                    obs = result.get("observation", obs)
                    steps += 1

                    if verbose:
                        print(f"    reward={result.get('reward', 0):.3f}")

                    # Assess impact
                    if not obs.get("done", False):
                        impact_action = {
                            "action_type": "assess_impact",
                            "clause_index": section_idx,
                            "impact": impact,
                            "confidence": 0.7,
                        }
                        resp = client.post("/step", json=impact_action)
                        resp.raise_for_status()
                        result = resp.json()
                        obs = result.get("observation", obs)
                        steps += 1

                        if verbose:
                            print(f"    impact={impact}  reward={result.get('reward', 0):.3f}")
                else:
                    if verbose:
                        print(f"  Step {steps+1}: section {section_idx} -> no change")

                # Move to next section
                if not obs.get("done", False):
                    resp = client.post("/step", json={"action_type": "next_section"})
                    resp.raise_for_status()
                    result = resp.json()
                    obs = result.get("observation", obs)
                    steps += 1

        # Submit
        if not obs.get("done", False):
            resp = client.post("/step", json={"action_type": "submit"})
            resp.raise_for_status()
            steps += 1

        # Grade
        resp = client.get("/grader")
        resp.raise_for_status()
        grade = resp.json()

        return {
            "task_id": task_id,
            "score": grade.get("score", 0.0),
            "steps": steps,
            "max_steps": max_steps,
        }


def run_task_openai(task_id: str, verbose: bool = False) -> dict:
    """Run a task using OpenAI API (costs money)."""
    print(f"\n{'=' * 55}")
    print(f"  Task: {task_id} (OpenAI — {MODEL})")
    print(f"{'=' * 55}")

    prompts = {
        "clause_identification": (
            "You are a legal analyst. Identify the clause type. "
            "Valid types: position, compensation, termination, confidentiality, "
            "non_compete, ip_assignment, benefits, governing_law, dispute_resolution, "
            "probation, notice_period.\n"
            'Respond ONLY with JSON: {"action_type": "identify_clause", "clause_index": <int>, '
            '"clause_type": "<type>", "confidence": <float>}'
        ),
        "risk_flagging": (
            "You are a legal risk analyst. Determine if the section has a hidden risk.\n"
            "Risk types: unlimited_liability, auto_renewal_trap, unilateral_amendment, "
            "broad_indemnification, excessive_penalty, data_ownership_grab, "
            "non_compete_overreach, jurisdiction_trap.\n"
            'If risky: {"action_type": "flag_risk", "clause_index": <int>, "clause_type": "<risk_type>", "confidence": <float>}\n'
            'If not risky: {"action_type": "next_section"}'
        ),
        "contract_comparison": (
            "You are a contract redlining specialist. Detect changes between original and revised.\n"
            'Respond: {"action_type": "detect_change", "clause_index": <int>, "clause_type": "modified", '
            '"impact": "favorable|neutral|unfavorable", "confidence": <float>}'
        ),
    }

    with httpx.Client(timeout=30, base_url=BASE_URL) as client:
        resp = client.post("/reset", json={"task_id": task_id, "contract_index": 0})
        resp.raise_for_status()
        obs = resp.json()

        system_prompt = prompts.get(task_id, "You are a legal analyst.")
        steps = 0
        max_steps = obs.get("max_steps", 10)

        while not obs.get("done", False) and steps < max_steps:
            user_msg = (
                f"Section {obs['current_section_index']}: "
                f"{obs['current_section_heading']}\n\n"
                f"{obs['current_section_text']}"
            )

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ]

            llm_output = call_openai(messages)
            action_dict = parse_action(llm_output) or {"action_type": "next_section"}

            if verbose:
                atype = action_dict.get("action_type", "?")
                print(f"  Step {steps+1}: {atype} -> idx={action_dict.get('clause_index', '-')}")

            resp = client.post("/step", json=action_dict)
            resp.raise_for_status()
            result = resp.json()
            obs = result.get("observation", obs)
            steps += 1

            if verbose:
                print(f"    reward={result.get('reward', 0):.3f}  {obs.get('system_feedback', '')[:60]}")

            # Auto-advance after main action
            main_actions = {"identify_clause", "flag_risk", "detect_change"}
            if action_dict.get("action_type") in main_actions and not obs.get("done", False):
                resp = client.post("/step", json={"action_type": "next_section"})
                resp.raise_for_status()
                result = resp.json()
                obs = result.get("observation", obs)
                steps += 1

        if not obs.get("done", False):
            resp = client.post("/step", json={"action_type": "submit"})
            resp.raise_for_status()
            steps += 1

        resp = client.get("/grader")
        resp.raise_for_status()
        grade = resp.json()

        return {
            "task_id": task_id,
            "score": grade.get("score", 0.0),
            "steps": steps,
            "max_steps": max_steps,
        }


# ═══════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Run baseline inference for Contract Clause Env"
    )
    parser.add_argument(
        "--task", type=str, default=None, choices=TASK_IDS,
        help="Run a specific task (default: all)",
    )
    parser.add_argument(
        "--mode", type=str, default="rule", choices=["rule", "openai"],
        help="Agent mode: 'rule' (free) or 'openai' (costs money). Default: rule",
    )
    parser.add_argument("--verbose", action="store_true", help="Step-by-step output")
    parser.add_argument("--base-url", type=str, default=None, help="Override server URL")
    args = parser.parse_args()

    global BASE_URL
    if args.base_url:
        BASE_URL = args.base_url

    tasks = [args.task] if args.task else TASK_IDS
    run_fn = run_task_rule_based if args.mode == "rule" else run_task_openai

    print(f"\n  Mode: {'Rule-Based (FREE)' if args.mode == 'rule' else f'OpenAI ({MODEL})'}")

    results = []
    for tid in tasks:
        try:
            results.append(run_fn(tid, verbose=args.verbose))
        except Exception as exc:
            print(f"\nERROR running {tid}: {exc}")
            results.append({"task_id": tid, "score": 0.0, "steps": 0, "max_steps": 0, "error": str(exc)})

    # Results table
    diff_map = {"clause_identification": "EASY", "risk_flagging": "MEDIUM", "contract_comparison": "HARD"}
    print(f"\n{'=' * 55}")
    print("  Contract Clause Env — Baseline Results")
    print(f"{'=' * 55}")
    for r in results:
        diff = diff_map.get(r["task_id"], "?")
        if r.get("error"):
            print(f"  Task: {r['task_id']} ({diff})")
            print(f"    ERROR: {r['error']}")
        else:
            print(f"  Task: {r['task_id']} ({diff})")
            print(f"    Score: {r['score']:.2f} / 1.0")
            print(f"    Steps: {r['steps']} / {r['max_steps']}")
    print(f"{'=' * 55}\n")


if __name__ == "__main__":
    main()
