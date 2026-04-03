---
title: OpenEnv Hackathon
emoji: ⚖️
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# Your existing README content starts here...# Contract Clause Analysis — OpenEnv Environment

> **Meta PyTorch OpenEnv Hackathon** · Scaler School of Technology  
> **Team:** Atharva Bhatt

A reinforcement learning environment where an AI agent learns to review legal contracts — identifying clause types, detecting hidden risks, and comparing contract revisions like a junior associate at a law firm would.

## Why This Problem?

Legal contract review is tedious, error-prone, and expensive. Junior lawyers spend hours combing through vendor agreements looking for auto-renewal traps, liability caps, and unfavorable amendments. This environment lets RL agents practice that exact workflow — reading sections sequentially, making judgments, and receiving feedback — across three difficulty tiers.

---

## Getting Started

### Prerequisites
- Python 3.11+
- pip

### Installation & Run

```bash
pip install -r server/requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

Verify it's running:
```bash
curl http://localhost:7860/health
# {"status": "ok"}
```

### Docker

```bash
docker build -t contract-clause-env -f server/Dockerfile .
docker run -p 7860:7860 contract-clause-env
```

---

## Environment Design

### Tasks

| Task ID | Difficulty | Max Steps | What the Agent Does |
|---------|-----------|-----------|---------------------|
| `clause_identification` | Easy | 10 | Classify each section (position, compensation, termination, etc.) |
| `risk_flagging` | Medium | 25 | Find hidden risky clauses, rate severity, explain why |
| `contract_comparison` | Hard | 50 | Diff two contract versions, assess impact, suggest counter-amendments |

### Data

All contract data is embedded directly in Python — no external files needed:
- **Easy:** 5 realistic employment contracts (30+ clause sections)
- **Medium:** 5 vendor/service contracts with 17+ subtle embedded risks
- **Hard:** 3 contract pairs (original vs. revised) with ground truth changes

### Observation Space

The agent receives a structured observation at each step containing:
- Current section text and heading
- Contract metadata (title, parties)
- Agent's accumulated work (identified clauses, flagged risks, etc.)
- Step count, progress, cumulative reward
- System feedback on the last action

### Action Space

| Action | Purpose |
|--------|---------|
| `identify_clause` | Label a section's clause type |
| `flag_risk` | Mark a section as containing a risk |
| `assess_severity` | Rate risk as low/medium/high/critical |
| `explain_risk` | Provide reasoning for why a clause is risky |
| `suggest_amendment` | Propose alternative language |
| `detect_change` | Identify a modification between contract versions |
| `assess_impact` | Rate a change as favorable/neutral/unfavorable |
| `generate_summary` | Add a key takeaway to the summary |
| `next_section` | Move to the next contract section |
| `submit` | Finish and submit work for grading |

### Reward Signal

Dense per-step rewards — the agent gets feedback on every action, not just at the end:

- **Correct identification:** +0.10
- **Correct risk flag:** +0.15  
- **Correct severity / impact:** +0.10
- **Good reasoning (≥50% keyword match):** +0.10
- **Wrong answer:** −0.05
- **Redundant action:** −0.03
- **Efficiency bonus** for finishing under the step budget

### Grading

Fully deterministic — same actions always produce the same score. Each task has a weighted rubric:

- **Easy:** accuracy of clause identifications (with partial credit for synonyms)
- **Medium:** 40% risk detection + 30% severity accuracy + 30% reasoning quality − false positive penalty
- **Hard:** 30% changes found + 25% impact assessment + 25% amendment quality + 20% summary coverage

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Server status |
| `/tasks` | GET | List available tasks |
| `/reset` | POST | Start new episode (`task_id`, `contract_index`) |
| `/step` | POST | Execute an action |
| `/state` | GET | Current episode metadata |
| `/grader` | GET | Get deterministic score [0.0, 1.0] |
| `/ws` | WebSocket | Real-time interaction |

---

## Rule-Based Agent

The baseline uses rule-based keyword matching — no API keys or external services needed:

```bash
python inference.py --mode rule --verbose                                # All 3 tasks
python inference.py --mode rule --task clause_identification --verbose    # Single task
```

### Results

| Task | Difficulty | Score |
|------|-----------|-------|
| Clause Identification | Easy | 0.57 |
| Risk Flagging | Medium | 0.60 |
| Contract Comparison | Hard | 0.46 |

These scores leave significant room for improvement — a well-designed RL agent should be able to beat the baseline substantially.

---

## Project Structure

```
contract_clause_env/
├── models.py                  # Pydantic v2 data models
├── inference.py               # Main OpenEnv AI script and baseline agent
├── client.py                  # Async HTTP client
├── openenv.yaml               # OpenEnv manifest
├── pyproject.toml              # Package config
├── data/
│   ├── __init__.py             # Unified data loader
│   ├── contracts_easy.py       # Employment contracts
│   ├── contracts_medium.py     # Vendor contracts (with hidden risks)
│   └── contracts_hard.py       # Contract pairs for comparison
├── graders/
│   └── grader.py               # Deterministic scoring functions
├── server/
│   ├── app.py                  # FastAPI server
│   ├── environment.py          # Core environment logic
│   ├── requirements.txt
│   └── Dockerfile
└── tasks/
    └── __init__.py
```

## Tech Stack

- **Server:** FastAPI + Uvicorn
- **Models:** Pydantic v2
- **Containerization:** Docker (HF Spaces compatible, port 7860)
- **Protocol:** REST + WebSocket

---

## License

MIT
