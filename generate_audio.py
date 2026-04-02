from gtts import gTTS

text = """
Hello team! This is a quick wrap-up of what we built for the Meta and Scaler OpenEnv Hackathon.

First, to be clear: we did not build an AI agent that reads contracts. Instead, we built the game environment that an AI agent plays inside.

We created a legal contract simulator. The AI agent connects to our server, gets a contract section, and tries to guess what clause it is, or flags hidden risks. If the AI guesses correctly, our server gives it a positive reward, like plus 0.10. If it is wrong, it gets a negative penalty. This is how Reinforcement Learning works.

How will the judges test this? They have automated scripts that will hit our environment endpoints. They will try calling "reset" to start a new contract. They will try calling "step" to send an action and check if the reward math is correct. Finally, they will call "grader" to make sure our scoring system is deterministic, which it is. They will also plug their own AI agents into our environment to see if their AI can learn to get a high score.

What about Docker? Docker is just a way to package our Python code, our specific libraries, and our server into a single sealed box. This guarantees it will run exactly the same on the judges' computers without crashing over missing dependencies.

Lastly, we included a baseline script. The baseline is a simple rule-based bot that plays our game using keyword matching. It proves our environment is fully playable, but it only gets an average score, leaving plenty of room for Meta engineers to build a smarter AI that beats it.

Everything is pushed to GitHub and ready for submission. Great job!
"""

print("Generating audio...")
tts = gTTS(text=text, lang='en', slow=False)
tts.save("Team_Explanation_Audio.mp3")
print("Audio saved successfully to Team_Explanation_Audio.mp3")
