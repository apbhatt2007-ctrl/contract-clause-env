"""
FastAPI server for the Contract Clause Analysis OpenEnv environment.

Provides REST endpoints and WebSocket for agent interaction.
"""

from __future__ import annotations

import asyncio
import json
import sys
import os

# Ensure project root is on sys.path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from models import ContractAction, TaskDefinition
from server.environment import ContractClauseEnv, TASK_CONFIGS


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Lifespan â€” initialise the shared environment instance
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

env = ContractClauseEnv()


@asynccontextmanager
async def lifespan(application: FastAPI):
    yield


app = FastAPI(
    title="Contract Clause Analysis â€” OpenEnv",
    description="RL environment for legal contract review, risk flagging, and comparison.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Request models
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class ResetRequest(BaseModel):
    task_id: str = "clause_identification"
    contract_index: int = 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# REST Endpoints
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@app.get("/")
async def root():
    return {
        "name": "Contract Clause Analysis - OpenEnv",
        "team": "antigravity",
        "version": "1.0.0",
        "status": "running",
        "endpoints": ["/health", "/tasks", "/reset", "/step", "/state", "/grader"],
        "hackathon": "Scalar x Meta PyTorch Hackathon",
        "space": "https://huggingface.co/spaces/Atharva4/OpenEnvhackathon"
    }
@app.get("/health")
async def health():
    """Health check."""
    return {"status": "ok"}


@app.get("/tasks")
async def list_tasks():
    """List all available tasks with metadata."""
    tasks = []
    for tid, cfg in TASK_CONFIGS.items():
        tasks.append(
            TaskDefinition(
                task_id=tid,
                name=cfg["name"],
                difficulty=cfg["difficulty"],
                description=cfg["description"],
                max_steps=cfg["max_steps"],
            ).model_dump()
        )
    return {"tasks": tasks}


@app.post("/reset")
async def reset(req: ResetRequest):
    """Reset environment with a specific task and contract."""
    try:
        obs = env.reset(task_id=req.task_id, contract_index=req.contract_index)
        return obs.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/step")
async def step(action: ContractAction):
    """Take one step in the environment."""
    try:
        result = env.step(action)
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/state")
async def get_state():
    """Get current episode state."""
    return env.state()


@app.get("/grader")
async def get_grade():
    """Return deterministic grade for the current episode."""
    score = env.grade()
    return {"score": round(score, 4)}


@app.get("/baseline")
async def run_baseline():
    """Trigger a simple baseline run (informational)."""
    return {
        "message": "Use baseline.py for full baseline inference.",
        "command": "python baseline.py --task clause_identification --verbose",
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# WebSocket
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """WebSocket interface for real-time interaction."""
    await ws.accept()
    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send_json({"error": "Invalid JSON"})
                continue

            cmd = msg.get("command", "")

            if cmd == "reset":
                task_id = msg.get("task_id", "clause_identification")
                contract_index = msg.get("contract_index", 0)
                try:
                    obs = env.reset(task_id=task_id, contract_index=contract_index)
                    await ws.send_json({"type": "reset", "data": obs.model_dump()})
                except ValueError as exc:
                    await ws.send_json({"type": "error", "message": str(exc)})

            elif cmd == "step":
                action_data = msg.get("action", {})
                try:
                    action = ContractAction(**action_data)
                    result = env.step(action)
                    await ws.send_json({"type": "step", "data": result})
                except Exception as exc:
                    await ws.send_json({"type": "error", "message": str(exc)})

            elif cmd == "state":
                await ws.send_json({"type": "state", "data": env.state()})

            elif cmd == "grade":
                score = env.grade()
                await ws.send_json({"type": "grade", "data": {"score": round(score, 4)}})

            else:
                await ws.send_json({"type": "error", "message": f"Unknown command: {cmd}"})

    except WebSocketDisconnect:
        pass


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Entry point
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, reload=True)

