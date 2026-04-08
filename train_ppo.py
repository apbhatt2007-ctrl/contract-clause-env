"""
Deep Reinforcement Learning (PyTorch) using Stable Baselines 3.
Trains a PPO agent on the FastAPI Contract Clause Environment.
"""

import os
import argparse
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.monitor import Monitor

from env_wrapper import ContractClauseGymEnv

def train(episodes=5000, save_path="agent_ppo"):
    print(f"Initializing PyTorch PPO Agent...")
    
    # Wrap with Monitor for episode logging
    env = Monitor(ContractClauseGymEnv(task_id="clause_identification", contract_index=0))
    
    # Verify environment follows gymnasium interface
    check_env(env)
    
    # Initialize PPO model
    # MlpPolicy uses a standard feed-forward PyTorch neural network
    model = PPO(
        "MlpPolicy", 
        env, 
        verbose=1,
        learning_rate=0.001,
        n_steps=128,          # Small n_steps for quick learning on short episodes
        batch_size=64,
        n_epochs=4,
        gamma=0.95
    )
    
    # Approx steps = episodes * max_steps_per_episode (we have ~10 steps per success, max 50)
    total_timesteps = episodes * 20 
    
    print(f"\nEvaluating baseline before training...")
    # Just evaluating built-in randomly initialized policy
    mean_reward, _ = evaluate(model, env, n_eval_episodes=5)
    print(f"Pre-training Mean Reward: {mean_reward:.2f}")

    print(f"\nTraining for {total_timesteps} timesteps...")
    model.learn(total_timesteps=total_timesteps, progress_bar=True)
    
    print(f"\nSaving model to {save_path}.zip...")
    model.save(save_path)
    
    print(f"\nEvaluating trained policy...")
    mean_reward, _ = evaluate(model, env, n_eval_episodes=10)
    print(f"Post-training Mean Reward: {mean_reward:.2f}")
    
    # Verify Grader Score
    print("\n--- Final Grader Score ---")
    import httpx
    try:
        resp = httpx.get("http://localhost:7860/grader", timeout=10)
        print(f"Final Episode Scored: {resp.json().get('score')} / 1.0")
    except Exception as e:
        print(f"Could not connect to grader: {e}")

def evaluate(model, env, n_eval_episodes=5):
    episode_rewards = []
    for ep in range(n_eval_episodes):
        obs, _ = env.reset()
        done = False
        total_reward = 0.0
        while not done:
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            total_reward += reward
        episode_rewards.append(total_reward)
    
    mean_reward = sum(episode_rewards) / len(episode_rewards)
    return mean_reward, episode_rewards

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=1000, help="Number of approximate training episodes")
    args = parser.parse_args()
    
    train(episodes=args.episodes)
