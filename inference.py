import os
import json
import httpx
from openai import OpenAI

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Hackathon Requirements: Env Vars & OpenAI SDK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")

llm_client = OpenAI(
    base_url=os.getenv("API_BASE_URL"),
    api_key=os.getenv("HF_TOKEN")
)
MODEL_NAME = os.getenv("MODEL_NAME")

TASK_IDS = ["clause_identification", "risk_flagging", "contract_comparison"]

def main():
    # Start of script logging exactly as required
    print("[START] inference.py contract-clause-env", flush=True)
    
    total_score = 0.0
    
    # Minimalist prompts targeting JSON schemas
    prompts = {
        "clause_identification": (
            "You are a legal parsing agent. Analyze the text and identify the clause. "
            "Output valid JSON. Format example: {\"action_type\": \"identify_clause\", \"clause_index\": <int>, \"clause_type\": \"<type>\", \"confidence\": 0.9} "
            "If no clause applies, use: {\"action_type\": \"next_section\"}"
        ),
        "risk_flagging": (
            "You are a legal risk parsing agent. "
            "If risky: {\"action_type\": \"flag_risk\", \"clause_index\": <int>, \"clause_type\": \"<type>\", \"confidence\": 0.9} "
            "If safe or done: {\"action_type\": \"next_section\"}"
        ),
        "contract_comparison": (
            "You are a redlining and impact agent. "
            "If modified: {\"action_type\": \"detect_change\", \"clause_index\": <int>, \"clause_type\": \"modified\", \"impact\": \"unfavorable\", \"confidence\": 0.9} "
            "If unchanged: {\"action_type\": \"next_section\"}"
        )
    }

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Dual-Client Architecture Loop: Local HTTPX Logic
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with httpx.Client(timeout=30, base_url=BASE_URL) as client:
        for task_id in TASK_IDS:
            
            # Start of task logging exactly as required
            print(f"[START] task={task_id} episode=0", flush=True)
            
            try:
                resp = client.post("/reset", json={"task_id": task_id, "contract_index": 0})
                obs = resp.json()
            except Exception as e:
                # Failing to connect to OpenEnv server
                print(f"Failed to reset environment: {e}")
                continue
                
            steps = 0
            max_steps = obs.get("max_steps", 15)
            
            while not obs.get("done", False) and steps < max_steps:
                section_text = obs.get("current_section_text", "")
                section_heading = obs.get("current_section_heading", "")
                section_idx = obs.get("current_section_index", 0)
                
                user_msg = f"Section Index {section_idx}:\n{section_heading}\n{section_text}"
                
                # Default fallback action
                action_dict = {"action_type": "next_section"}
                
                try:
                    # Communicate with the LLM via OpenAI SDK
                    response = llm_client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {"role": "system", "content": prompts.get(task_id, "")},
                            {"role": "user", "content": user_msg}
                        ],
                        temperature=0.1,
                        max_tokens=256
                    )
                    content = response.choices[0].message.content.strip()
                    
                    # Robust simple JSON extraction block
                    start = content.find("{")
                    end = content.rfind("}") + 1
                    if start >= 0 and end > start:
                        parsed = json.loads(content[start:end])
                        if "action_type" in parsed:
                            action_dict = parsed
                except Exception:
                    # Fallback to next_section if the LLM API fails, as requested
                    pass
                
                # Act on OpenEnv Environment state based on decision
                try:
                    resp = client.post("/step", json=action_dict)
                    result = resp.json()
                    obs = result.get("observation", obs)
                    reward = result.get("reward", 0.0)
                    steps += 1
                    
                    # Every step log formatted exactly as required
                    print(f"[STEP] task={task_id} step={steps} action={action_dict.get('action_type', 'unknown')} reward={reward:.4f}", flush=True)
                except Exception as e:
                    break

            # Force Submission if task failed to naturally finish
            if not obs.get("done", False):
                resp = client.post("/step", json={"action_type": "submit"})
                result = resp.json()
                reward = result.get("reward", 0.0)
                steps += 1
                print(f"[STEP] task={task_id} step={steps} action=submit reward={reward:.4f}", flush=True)

            # Hit Grader
            try:
                resp = client.get("/grader")
                score = resp.json().get("score", 0.0)
            except Exception:
                score = 0.0
            total_score += score
            
            # End of task logging exactly as required
            print(f"[END] task={task_id} score={score:.4f} steps={steps}", flush=True)
            
    # End of script logging exactly as required
    avg = total_score / len(TASK_IDS)
    print(f"[END] all_tasks_complete avg_score={avg:.4f}", flush=True)

if __name__ == "__main__":
    main()
