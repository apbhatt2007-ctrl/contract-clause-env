import os
import sys
import json
import httpx
import argparse
import time
from typing import Dict, Any, Tuple, Optional
from openai import OpenAI

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENV VARS & CLIENT (Strict Hackathon Requirements)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN", "")

BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")
TASK_IDS = ["clause_identification", "risk_flagging", "contract_comparison"]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LOGGING (Exactly as requested)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def log_start(task_id):
    print(f"[START] task={task_id} episode=0", flush=True)

def log_step(task_id, step, action, reward):
    print(f"[STEP] task={task_id} step={step} action={action} reward={reward:.4f}", flush=True)

def log_end(task_id, score, steps):
    print(f"[END] task={task_id} score={score:.4f} steps={steps}", flush=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PROMPTS (Upgrades 1 & 2: Chain of Thought + Few Shot)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SYSTEM_PROMPTS = {
    "clause_identification": """[ROLE]
You are a legal parsing agent specializing in employment contracts.

[VALID VALUES]
clause_type: compensation, termination, confidentiality, non_compete, position, benefits, general_obligations

[OUTPUT FORMAT]
You must perform a two-pass approach.
Pass 1: Reason about the text in a <reasoning> tag.
Pass 2: Output valid JSON exactly matching the Schema. No markdown outside the JSON.
Schema: {"action_type": "identify_clause", "clause_index": <int>, "clause_type": "<type>", "confidence": <float>}
If no clause matches, output: {"action_type": "next_section"}

[EXAMPLES]
Example 1 (correct):
  Input: "Section 2:\nThe Employee shall receive a base salary of $120,000..."
  Output: 
  <reasoning>
  The text explicitly mentions base salary which is core compensation.
  </reasoning>
  {"action_type": "identify_clause", "clause_index": 2, "clause_type": "compensation", "confidence": 0.95}

Example 2 (tricky near-miss):
  Input: "Section 3:\nThe Employee will report to the VP of Engineering..."
  Output:
  <reasoning>
  Reporting structure describes the position/role, not compensation.
  </reasoning>
  {"action_type": "identify_clause", "clause_index": 3, "clause_type": "position", "confidence": 0.90}

[CONSTRAINTS]
- clause_index must match the integer in "Section <n>:" of the input
- confidence must be between 0.0 and 1.0
""",

    "risk_flagging": """[ROLE]
You are a vendor contract risk parsing agent.

[VALID VALUES]
clause_type: uncapped_liability, auto_renewal, unilateral_termination, data_sharing, outsourcing, ip_transfer

[OUTPUT FORMAT]
You must perform a two-pass approach.
Pass 1: Reason about the text in a <reasoning> tag. Identify if it poses a risk.
Pass 2: Output valid JSON exactly matching the Schema. No markdown outside the JSON.
Schema (if risky): {"action_type": "flag_risk", "clause_index": <int>, "clause_type": "<type>", "confidence": <float>}
Schema (if safe): {"action_type": "next_section"}

[EXAMPLES]
Example 1 (correct):
  Input: "Section 4:\nVendor may share anonymized data with third parties."
  Output:
  <reasoning>
  Sharing data with third parties is a data_sharing risk.
  </reasoning>
  {"action_type": "flag_risk", "clause_index": 4, "clause_type": "data_sharing", "confidence": 0.95}

[CONSTRAINTS]
- clause_index must match the integer in "Section <n>:" of the input
- confidence must be between 0.0 and 1.0
""",

    "contract_comparison": """[ROLE]
You are a contract redlining agent comparing original and revised text.

[VALID VALUES]
impact: favorable, neutral, unfavorable

[OUTPUT FORMAT]
Pass 1: Reason about changes between original and revised text in a <reasoning> tag. 
Pass 2: Output valid JSON exactly matching the Schema.
Schema (if changed): {"action_type": "detect_change", "clause_index": <int>, "clause_type": "modified", "impact": "unfavorable", "confidence": <float>}
Schema (if unchanged): {"action_type": "next_section"}

[EXAMPLES]
Example 1:
  Input: "Section 1:\nOriginal: 30 days notice.\nRevised: 90 days notice."
  Output:
  <reasoning>
  Notice period extended, which is unfavorable to us depending on context.
  </reasoning>
  {"action_type": "detect_change", "clause_index": 1, "clause_type": "modified", "impact": "unfavorable", "confidence": 0.90}

[CONSTRAINTS]
- clause_index must match the integer in "Section <n>:" of the input
"""
}

SUB_PROMPTS = {
    "assess_severity_and_explain": """[ROLE]
You are a risk severity assessor.
Based on the text, output a JSON action containing severity, explanation, and an amendment.

[VALID VALUES]
risk_level: low, medium, high, critical

[OUTPUT FORMAT]
Output ONLY valid JSON.
Schema: {
  "severity_action": {"action_type": "assess_severity", "risk_level": "<level>", "confidence": <float>},
  "explain_action": {"action_type": "explain_risk", "explanation": "<reason>", "confidence": <float>},
  "amend_action": {"action_type": "suggest_amendment", "amendment": "<text>", "confidence": <float>}
}
""",
    "assess_impact_and_amend": """[ROLE]
You are an impact assessor for contract redlines.

[VALID VALUES]
impact: favorable, neutral, unfavorable

[OUTPUT FORMAT]
Output ONLY valid JSON.
Schema: {
  "impact_action": {"action_type": "assess_impact", "impact": "<level>", "confidence": <float>},
  "amend_action": {"action_type": "suggest_amendment", "amendment": "<text>", "confidence": <float>}
}
"""
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LLM HELPER FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def extract_json(content: str) -> dict:
    if "{" not in content or "}" not in content:
        return {}
    start = content.find("{")
    end = content.rfind("}") + 1
    try:
        return json.loads(content[start:end])
    except Exception: # Includes HTML parsing failures
        return {}

def call_llm(client: OpenAI, system_msg: str, user_msg: str, temperature: float = 0.1, max_retries: int = 3) -> dict:
    for _ in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                temperature=temperature,
                max_tokens=500
            )
            content = resp.choices[0].message.content.strip()
            parsed = extract_json(content)
            if parsed:
                return parsed
        except Exception:
            pass
        time.sleep(1) # Upgrade 9: Wait and retry
    return {}

def call_llm_voted(client: OpenAI, system_msg: str, user_msg: str) -> dict:
    # Upgrade 4: LLM Self-Consistency Voting for borderline cases
    votes = []
    for _ in range(3):
        res = call_llm(client, system_msg, user_msg, temperature=0.3, max_retries=1)
        if res and "clause_type" in res:
            votes.append(res)
    if not votes:
        return {}
    counts = {}
    for v in votes:
        ct = v.get("clause_type")
        counts[ct] = counts.get(ct, 0) + 1
    best_ct = max(counts, key=counts.get)
    for v in votes:
        if v.get("clause_type") == best_ct:
            return v
    return votes[0]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RULE-BASED FALLBACK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def rule_based_fallback(task_id: str, section_text: str, section_idx: int) -> dict:
    text_lower = section_text.lower()
    if task_id == "clause_identification":
        if "salary" in text_lower or "compensation" in text_lower:
            return {"action_type": "identify_clause", "clause_index": section_idx, "clause_type": "compensation", "confidence": 0.8}
        if "terminate" in text_lower:
            return {"action_type": "identify_clause", "clause_index": section_idx, "clause_type": "termination", "confidence": 0.8}
        return {"action_type": "identify_clause", "clause_index": section_idx, "clause_type": "general_obligations", "confidence": 0.6}
    elif task_id == "risk_flagging":
        if "liability" in text_lower:
            return {"action_type": "flag_risk", "clause_index": section_idx, "clause_type": "uncapped_liability", "confidence": 0.8}
        if "outsource" in text_lower:
            return {"action_type": "flag_risk", "clause_index": section_idx, "clause_type": "outsourcing", "confidence": 0.8}
        return {"action_type": "next_section"}
    elif task_id == "contract_comparison":
        if "amended" in text_lower or "revised" in text_lower:
             return {"action_type": "detect_change", "clause_index": section_idx, "clause_type": "modified", "impact": "unfavorable", "confidence": 0.8}
        return {"action_type": "next_section"}
    return {"action_type": "next_section"}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENVIRONMENT INTERACTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def send_step(http_client: httpx.Client, action_dict: dict, task_id: str, steps: int) -> Tuple[Optional[dict], float, int]:
    try:
        resp = http_client.post("/step", json=action_dict)
        # HTTP 422 Edge Case Handling Check
        if resp.status_code == 422:
            print(f"[WARN] task={task_id} step={steps} Validation Error: {resp.text}", flush=True)
            return None, 0.0, steps
            
        resp.raise_for_status()
        res = resp.json()
        reward = res.get("reward", 0.0)
        obs = res.get("observation", {})
        steps += 1
        log_step(task_id, steps, action_dict.get("action_type", "unknown"), reward)
        return obs, reward, steps
    except httpx.HTTPStatusError as e:
        print(f"[WARN] HTTP state error: {e}", flush=True)
        return None, 0.0, steps
    except httpx.RequestError as e:
        print(f"[WARN] HTTP logic error: {e}", flush=True)
        return None, 0.0, steps

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LLM TASK RUNNER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def run_task_openai(task_id: str, http_client: httpx.Client, llm_client: OpenAI) -> float:
    log_start(task_id)
    try:
        resp = http_client.post("/reset", json={"task_id": task_id, "contract_index": 0})
        obs = resp.json()
    except Exception as e:
        print(f"Failed to reset environment: {e}")
        return 0.0

    steps = 0
    max_steps = obs.get("max_steps", 15)
    history = []
    changes_found = []

    # Upgrade 8: Step Budget Management Priority Logic
    # (A simple simulated prioritization; real prompt would add overhead, but we do basic skipping if running low)

    while not obs.get("done", False) and steps < max_steps:
        section_idx = obs.get("current_section_index", 0)
        section_text = obs.get("current_section_text", "")
        section_heading = obs.get("current_section_heading", "")
        
        # Upgrade 6: Dynamic Context Window
        history_str = ", ".join(history) if history else "None"
        user_msg = f"Section Index {section_idx}:\n{section_heading}\n{section_text}\n\nAlready identified clauses: [{history_str}]. Do NOT re-flag these."
        
        system_msg = SYSTEM_PROMPTS.get(task_id, "")
        action = call_llm(llm_client, system_msg, user_msg)
        
        # Upgrades 7 & 9: Retry with empty generation and confidence gating
        if not action or "action_type" not in action:
            print(f"[WARN] task={task_id} step={steps+1} action=llm_fail reward=0.0", flush=True) # LLM Failing output
            action = rule_based_fallback(task_id, section_text, section_idx)
            print(f"[WARN] task={task_id} step={steps+1} fallback=rule", flush=True)
        else:
            conf = action.get("confidence", 1.0)
            if conf < 0.6:
                print(f"[WARN] task={task_id} step={steps+1} fallback=rule", flush=True)
                action = rule_based_fallback(task_id, section_text, section_idx)
            elif conf < 0.7 and action.get("action_type") != "next_section":
                voted_action = call_llm_voted(llm_client, system_msg, user_msg)
                if voted_action:
                    action = voted_action

        # Keep history
        if action.get("action_type") in ["identify_clause", "flag_risk", "detect_change"]:
            ctype = action.get("clause_type")
            if ctype:
                history.append(f"{ctype} §{section_idx}")
        
        if action.get("action_type") == "detect_change":
            changes_found.append(f"Section {section_idx}")

        obs_new, reward, steps = send_step(http_client, action, task_id, steps)
        if obs_new is None or obs_new.get("done", False) or steps >= max_steps:
             if obs_new: obs = obs_new
             break
        obs = obs_new
        
        # Upgrades 3 & 10: Multi-Action Episodes & LLM-Generated Combos
        if action.get("action_type") == "flag_risk":
            sub_sys = SUB_PROMPTS["assess_severity_and_explain"]
            sub_action = call_llm(llm_client, sub_sys, user_msg)
            if sub_action and isinstance(sub_action, dict):
                for key in ["severity_action", "explain_action", "amend_action"]:
                    sub_act = sub_action.get(key)
                    if sub_act and steps < max_steps and not obs.get("done", False):
                        sub_act["clause_index"] = section_idx
                        obs_new, _, steps = send_step(http_client, sub_act, task_id, steps)
                        if obs_new: obs = obs_new

        elif action.get("action_type") == "detect_change":
            sub_sys = SUB_PROMPTS["assess_impact_and_amend"]
            sub_action = call_llm(llm_client, sub_sys, user_msg)
            if sub_action and isinstance(sub_action, dict):
                imp = sub_action.get("impact_action")
                if imp and steps < max_steps and not obs.get("done", False):
                    imp["clause_index"] = section_idx
                    obs_new, _, steps = send_step(http_client, imp, task_id, steps)
                    if obs_new: obs = obs_new
                    
                amd = sub_action.get("amend_action")
                if amd and steps < max_steps and not obs.get("done", False) and imp and imp.get("impact") == "unfavorable":
                    amd["clause_index"] = section_idx
                    obs_new, _, steps = send_step(http_client, amd, task_id, steps)
                    if obs_new: obs = obs_new

    # Upgrade 5: Generating a summary at the end
    if task_id == "contract_comparison" and not obs.get("done", False) and steps < max_steps:
        if changes_found:
            sum_msg = "Generate a 3-sentence executive summary based on these changes: " + ", ".join(changes_found)
            summary_resp = call_llm(llm_client, "You are an executive summarizer. Output Schema: {\"summary\": \"<text>\"}", sum_msg)
            summary_text = summary_resp.get("summary", "Various changes detected across sections.")
            obs_new, _, steps = send_step(http_client, {"action_type": "generate_summary", "summary": summary_text}, task_id, steps)
            if obs_new: obs = obs_new

    if not obs.get("done", False) and steps < max_steps:
        obs_new, _, steps = send_step(http_client, {"action_type": "submit"}, task_id, steps)
        if obs_new: obs = obs_new

    try:
        resp = http_client.get("/grader")
        if resp.status_code == 400: # HTTP 400 Edge Case (no active episode)
            score = 0.0
        else:
            score = resp.json().get("score", 0.0)
    except Exception:
        score = 0.0
    
    log_end(task_id, score, steps)
    return score

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RULE-BASED TASK RUNNER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def run_task_rule(task_id: str, http_client: httpx.Client) -> float:
    log_start(task_id)
    try:
        resp = http_client.post("/reset", json={"task_id": task_id, "contract_index": 0})
        obs = resp.json()
    except Exception as e:
        print(f"Failed to reset environment: {e}")
        return 0.0

    steps = 0
    max_steps = obs.get("max_steps", 15)

    while not obs.get("done", False) and steps < max_steps:
        section_idx = obs.get("current_section_index", 0)
        section_text = obs.get("current_section_text", "")
        
        action = rule_based_fallback(task_id, section_text, section_idx)
        obs_new, _, steps = send_step(http_client, action, task_id, steps)
        if obs_new is None or obs_new.get("done", False) or steps >= max_steps:
             if obs_new: obs = obs_new
             break
        obs = obs_new

    if not obs.get("done", False) and steps < max_steps:
        obs_new, _, steps = send_step(http_client, {"action_type": "submit"}, task_id, steps)
        if obs_new: obs = obs_new
        
    try:
        resp = http_client.get("/grader")
        if resp.status_code == 400:
            score = 0.0
        else:
            score = resp.json().get("score", 0.0)
    except Exception:
        score = 0.0
    log_end(task_id, score, steps)
    return score

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN CLI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="openai", choices=["openai", "rule"])
    parser.add_argument("--task", type=str, default="all")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    # Pre-flight Check on HF_TOKEN
    if args.mode == "openai" and not HF_TOKEN:
        print("ERROR: HF_TOKEN not set", flush=True)
        sys.exit(1)

    # Initialize SDK
    llm_client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "dummy-token")

    tasks_to_run = TASK_IDS if args.task == "all" else [args.task]
    if args.task != "all" and args.task not in TASK_IDS:
        print(f"ERROR: Task ID '{args.task}' not found.", flush=True)
        sys.exit(1)

    total_score = 0.0
    with httpx.Client(timeout=60, base_url=BASE_URL) as http_client:
        try:
             http_client.get("/health")
        except httpx.ConnectError:
             print("Server not running", flush=True)
             sys.exit(1)

        for task_id in tasks_to_run:
            if args.mode == "openai":
                score = run_task_openai(task_id, http_client, llm_client)
            else:
                score = run_task_rule(task_id, http_client)
            total_score += score
            
if __name__ == "__main__":
    main()
