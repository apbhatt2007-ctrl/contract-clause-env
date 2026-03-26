# Contract Clause Analysis — OpenEnv Environment

An OpenEnv reinforcement learning environment for legal contract clause analysis,
built for the **Meta PyTorch OpenEnv Hackathon** (Scaler School of Technology).

An AI agent reviews legal contracts in a simulated workplace workflow:
identifying clause types, flagging hidden risks, comparing contract versions,
and producing analysis summaries.

---

## Quick Start

```bash
# Install dependencies
pip install -r server/requirements.txt

# Start the server
uvicorn server.app:app --host 0.0.0.0 --port 7860

# Test health endpoint
curl http://localhost:7860/health
# → {"status": "ok"}
```

### Docker

```bash
docker build -t contract-clause-env -f server/Dockerfile .
docker run -p 7860:7860 contract-clause-env
```

---

## Tasks

| Task | Difficulty | Max Steps | Description |
|------|-----------|-----------|-------------|
| `clause_identification` | Easy | 10 | Identify & classify clause types in employment contracts |
| `risk_flagging` | Medium | 25 | Flag hidden risks in vendor contracts with severity & reasoning |
| `contract_comparison` | Hard | 50 | Compare contract versions, assess impacts, suggest amendments |

---

## Observation Space

| Field | Type | Description |
|-------|------|-------------|
| `contract_title` | `str` | Title of the current contract |
| `contract_parties` | `dict` | Parties involved |
| `current_section_index` | `int` | Current section being reviewed |
| `current_section_heading` | `str` | Section heading |
| `current_section_text` | `str` | Full section text (for comparison: original + revised) |
| `total_sections` | `int` | Total sections in the contract |
| `identified_clauses` | `list[dict]` | Agent's clause identifications so far |
| `flagged_risks` | `list[dict]` | Agent's flagged risks so far |
| `detected_changes` | `list[dict]` | Agent's detected changes (hard task) |
| `amendments_suggested` | `list[dict]` | Agent's amendment suggestions |
| `summary_points` | `list[str]` | Agent's summary points |
| `system_feedback` | `str` | Feedback from the environment |
| `step_count` / `max_steps` | `int` | Current step and maximum |
| `reward` | `float` | Current step reward |
| `cumulative_reward` | `float` | Running total |
| `done` | `bool` | Whether episode is complete |

---

## Action Space

| Action Type | Required Fields | Description |
|-------------|-----------------|-------------|
| `identify_clause` | `clause_index`, `clause_type` | Classify a section's clause type |
| `flag_risk` | `clause_index`, `clause_type` | Flag a section as containing a risk |
| `assess_severity` | `clause_index`, `risk_level` | Rate risk severity |
| `explain_risk` | `clause_index`, `reasoning` | Provide reasoning for a flagged risk |
| `suggest_amendment` | `clause_index`, `amendment_text` | Propose alternative clause language |
| `detect_change` | `clause_index` | Flag a change between contract versions |
| `assess_impact` | `clause_index`, `impact` | Rate change impact |
| `generate_summary` | `summary_text` | Add a summary point |
| `next_section` | — | Advance to next section |
| `submit` | — | Submit work for grading |

---

## Reward Function

Dense per-step rewards that provide signal at every step:

| Event | Reward |
|-------|--------|
| Correct clause identification | +0.10 |
| Semantically close identification | +0.05 |
| Wrong identification | −0.05 |
| Correct risk flag | +0.15 |
| Correct severity | +0.10 |
| Good reasoning (keywords match ≥50%) | +0.10 |
| Correct change detection | +0.12 |
| Correct impact assessment | +0.10 |
| Good amendment suggestion | +0.15 |
| Good summary point | +0.08 |
| Redundant action | −0.03 |
| Invalid action | −0.05 |
| Submit (complete) | +0.05 |
| Submit (incomplete) | −0.10 |
| Efficiency bonus (< 50% steps) | +0.05 |
| Episode timeout | −0.10 |

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check → `{"status": "ok"}` |
| `/tasks` | GET | List all tasks with metadata |
| `/reset` | POST | Reset with `{"task_id": "...", "contract_index": 0}` |
| `/step` | POST | Take action with `ContractAction` JSON |
| `/state` | GET | Current episode state |
| `/grader` | GET | Deterministic grade `[0.0, 1.0]` |
| `/baseline` | GET | Baseline script info |
| `/ws` | WebSocket | Real-time interaction |

---

## Baseline Inference

The baseline runs **100% free** using rule-based keyword matching (no API key needed):

```bash
# Free rule-based mode (default)
python baseline.py --verbose                              # Run all tasks
python baseline.py --task clause_identification --verbose  # Run one task

# Optional: OpenAI mode (costs ~$0.01-0.05)
# export OPENAI_API_KEY=sk-proj-your-key-here
# python baseline.py --mode openai --verbose
```

### Baseline Scores (Rule-Based)

| Task | Difficulty | Score |
|------|-----------|-------|
| Clause Identification | Easy | 0.57 / 1.0 |
| Risk Flagging | Medium | 0.60 / 1.0 |
| Contract Comparison | Hard | 0.46 / 1.0 |

---

## Deployment (HF Spaces)

```bash
pip install huggingface_hub
huggingface-cli login
openenv push --repo-id yourusername/contract-clause-env
```

---

## Project Structure

```
contract_clause_env/
├── models.py                 # Pydantic v2 models
├── openenv.yaml              # Environment manifest
├── pyproject.toml             # Package config
├── baseline.py               # Rule-based baseline (free, no API key)
├── client.py                 # Async HTTP client
├── data/
│   ├── __init__.py            # Data loader
│   ├── contracts_easy.py      # 5 employment contracts
│   ├── contracts_medium.py    # 5 vendor contracts
│   └── contracts_hard.py      # 3 contract pairs
├── graders/
│   ├── __init__.py
│   └── grader.py              # Deterministic scoring
├── tasks/
│   └── __init__.py
└── server/
    ├── __init__.py
    ├── app.py                 # FastAPI server
    ├── environment.py         # Core env logic
    ├── requirements.txt
    └── Dockerfile
```

---

## License

MIT
