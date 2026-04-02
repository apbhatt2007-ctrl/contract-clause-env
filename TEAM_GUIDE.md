# Team Guide: How Our OpenEnv Hackathon Project Works

Hey team! This guide explains exactly what we built for the Meta PyTorch OpenEnv Hackathon, how the judges will test it, and what Docker is actually doing.

## 1. What Did We Actually Build?
We didn't build an AI that reads contracts. Let me repeat that: **We did not build the AI player.**
We built the **GAME** that the AI plays.

In Reinforcement Learning (RL), an AI agent needs an "Environment" to practice inside. Think of it like a flight simulator. We built a legal contract review simulator.
- The **Actions** the AI can take: identifying a clause, flagging a risk, suggesting an amendment.
- The **Observation** the AI sees: the text of the contract, section by section.
- The **Reward**: the points we give the AI when it gets it right (+0.10) or wrong (-0.05).

## 2. How Will The Hackathon Judges Test It?
The Meta evaluators have a suite of test scripts (unit tests). When we submit, their automated systems will do the following to our code:

1. **Test `reset()`**: Their script will call our `/reset` endpoint. It checks if our environment successfully returns a starting contract and wipe the slate clean.
2. **Test `step()`**: Their script will send random or calculated actions to our `/step` endpoint. They will check if our environment correctly updates the state (moving to the next section) and returns a valid reward number.
3. **Test `grader()`**: They will run a whole task start-to-finish, and then call `/grader`. They want to see if our grading is deterministic (meaning if the AI does the exact same actions twice, it gets the exact same score. Our rule-based grader guarantees this).
4. **Test the LLM Agent**: They will connect their own LLM agents (like Llama-3 or GPT-4) to our environment. They will see if their agent can actually learn to get a high score using our reward signals.

## 3. What is Docker and Why Did We Use It?
If we just zip up our Python files and send them to the judges, it might break. Maybe they have a different version of Python. Maybe they don't have FastAPI installed. 

**Docker fixes this.** 
Docker creates a "Container" — think of it as a mini virtual computer that has our exact Python version (3.11), our exact libraries (installed from `requirements.txt`), and our code, all locked inside a box. 
When the judges run our Dockerfile, they are spinning up an exact clone of the server that is running on our laptop right now. It guarantees 100% that our code will run on the judge's computers or on Hugging Face Spaces without any "it works on my machine" errors.

## 4. What is the Baseline?
To prove our "game" works, we include a `baseline.py` script. This is like a very basic bot that plays our game to show that the game isn't broken. Our baseline uses simple keyword matching (if it sees the word "salary", it guesses "compensation"). It scores around 0.50 out of 1.0. This is perfect, because it proves the game is playable, but leaves room for the Meta engineers to build a *smarter* AI that gets a 1.0!
