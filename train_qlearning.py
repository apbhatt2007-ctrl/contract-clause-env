"""
Tabular Q-Learning Agent for OpenEnv Hackathon.
Trains on the clause_identification task to demonstrate RL depth.
"""
import httpx
import json
import random

BASE_URL = "http://localhost:7860"
TASK_ID = "clause_identification"
EPISODES = 500
ALPHA = 0.2
GAMMA = 0.95
EPSILON = 0.2

CLAUSES = [
    "position", "compensation", "termination", "confidentiality",
    "non_compete", "ip_assignment", "benefits", "governing_law",
    "dispute_resolution", "probation", "notice_period"
]

def main():
    print(f"Starting Q-Learning training for {EPISODES} episodes on {TASK_ID}...")
    Q = {}
    
    def get_q(s, a):
        if s not in Q:
            Q[s] = {action: 0.0 for action in CLAUSES + ["next_section"]}
        return Q[s][a]
        
    def get_max_q(s):
        if s not in Q:
            Q[s] = {action: 0.0 for action in CLAUSES + ["next_section"]}
        return max(Q[s].values())

    rewards_history = []

    with httpx.Client(base_url=BASE_URL, timeout=10) as client:
        for episode in range(EPISODES):
            try:
                resp = client.post("/reset", json={"task_id": TASK_ID, "contract_index": 0})
                resp.raise_for_status()
                obs = resp.json()
            except Exception as e:
                print(f"Error connecting to env: {e}")
                return
            
            done = False
            total_reward = 0.0
            has_identified = False
            
            while not done:
                state = f"{obs.get('current_section_index', 0)}_{has_identified}"
                
                # Epsilon-greedy
                if random.random() < EPSILON:
                    action_key = random.choice(CLAUSES + ["next_section"])
                else:
                    if state not in Q:
                        Q[state] = {a: 0.0 for a in CLAUSES + ["next_section"]}
                    action_key = max(Q[state], key=Q[state].get)
                
                # Format action
                if action_key == "next_section":
                    action = {"action_type": "next_section", "confidence": 1.0}
                else:
                    action = {
                        "action_type": "identify_clause",
                        "clause_index": obs.get("current_section_index", 0),
                        "clause_type": action_key,
                        "confidence": 1.0
                    }
                
                res = client.post("/step", json=action).json()
                next_obs = res.get("observation", {})
                reward = res.get("reward", 0.0)
                done = next_obs.get("done", True)
                
                next_has_identified = has_identified
                if action_key == "next_section":
                    next_has_identified = False
                elif action_key != "next_section":
                    next_has_identified = True
                
                next_state = f"{next_obs.get('current_section_index', 0)}_{next_has_identified}"
                best_next_q = 0.0 if done else get_max_q(next_state)
                
                current_q = get_q(state, action_key)
                new_q = current_q + ALPHA * (reward + GAMMA * best_next_q - current_q)
                Q[state][action_key] = new_q
                
                total_reward += reward
                obs = next_obs
                has_identified = next_has_identified
                
            rewards_history.append(total_reward)
            
            if (episode + 1) % 20 == 0:
                avg_r = sum(rewards_history[-20:]) / 20.0
                print(f"Episode {episode + 1}/{EPISODES} | Avg Reward (last 20): {avg_r:.3f}")
                
        # Save Q-table
        with open("q_table.json", "w") as f:
            json.dump(Q, f, indent=2)
            
        # Save learning curve
        with open("learning_curve.csv", "w") as f:
            f.write("episode,total_reward\n")
            for i, r in enumerate(rewards_history):
                f.write(f"{i+1},{r}\n")
                
        print("\nTraining complete! Saved q_table.json and learning_curve.csv")
        print("Add `q_table.json` and `learning_curve.csv` to git.")

if __name__ == "__main__":
    main()
