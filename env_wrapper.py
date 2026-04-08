"""
Gymnasium Wrapper for the Contract Clause Environment API
Allows Stable Baselines 3 (PyTorch) to interact with the environment.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import httpx
import time

class ContractClauseGymEnv(gym.Env):
    """
    Custom Environment that follows gym interface.
    Wraps the underlying FastAPI JSON environment.
    """
    def __init__(self, base_url="http://localhost:7860", task_id="clause_identification", contract_index=0):
        super(ContractClauseGymEnv, self).__init__()
        
        self.base_url = base_url
        self.task_id = task_id
        self.contract_index = contract_index
        self.client = httpx.Client(base_url=self.base_url, timeout=10)
        
        self.clauses = [
            "position", "compensation", "termination", "confidentiality",
            "non_compete", "ip_assignment", "benefits", "governing_law",
            "dispute_resolution", "probation", "notice_period"
        ]
        
        # Action space: 0 = next_section, 1..11 = identify_clause for each type
        self.action_space = spaces.Discrete(len(self.clauses) + 1)
        
        # Observation space: array mapping [current_section_index, has_identified_flag]
        # MultiDiscrete([15, 2]) means index can be 0-14, flag can be 0-1
        self.observation_space = spaces.MultiDiscrete([15, 2])
        
        self.current_section = 0
        self.has_identified = 0
        self.steps = 0
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        resp = self.client.post("/reset", json={
            "task_id": self.task_id, 
            "contract_index": self.contract_index
        })
        resp.raise_for_status()
        obs_data = resp.json()
        
        self.current_section = obs_data.get("current_section_index", 0)
        self.has_identified = 0
        self.steps = 0
        
        obs = np.array([self.current_section, self.has_identified], dtype=np.int64)
        info = {"max_steps": obs_data.get("max_steps", 50)}
        return obs, info

    def step(self, action):
        action_idx = int(action)
        
        if action_idx == 0:
            act_payload = {"action_type": "next_section", "confidence": 1.0}
            next_has_identified = 0
        else:
            clause_type = self.clauses[action_idx - 1]
            act_payload = {
                "action_type": "identify_clause",
                "clause_index": self.current_section,
                "clause_type": clause_type,
                "confidence": 1.0
            }
            next_has_identified = 1
            
        resp = self.client.post("/step", json=act_payload)
        resp.raise_for_status()
        result = resp.json()
        
        obs_data = result.get("observation", {})
        reward = result.get("reward", 0.0)
        terminated = obs_data.get("done", True)
        truncated = False
        
        self.current_section = obs_data.get("current_section_index", 0)
        self.has_identified = next_has_identified
        self.steps += 1
        
        obs = np.array([self.current_section, self.has_identified], dtype=np.int64)
        info = {"steps": self.steps}
        
        return obs, float(reward), terminated, truncated, info

    def close(self):
        self.client.close()
