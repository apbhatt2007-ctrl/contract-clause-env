"""
Async HTTP client for the Contract Clause Analysis OpenEnv environment.

Usage:
    async with ContractEnvClient("http://localhost:7860") as client:
        obs = await client.reset("clause_identification")
        result = await client.step({"action_type": "identify_clause", ...})
        state = await client.state()
        score = await client.grade()
"""

from __future__ import annotations

from typing import Any

import httpx


class ContractEnvClient:
    """Async HTTP client for the Contract Clause Env API."""

    def __init__(self, base_url: str = "http://localhost:7860", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> ContractEnvClient:
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError(
                "Client not initialised. Use 'async with ContractEnvClient() as c:'"
            )
        return self._client

    async def health(self) -> dict:
        """Check server health."""
        resp = await self.client.get("/health")
        resp.raise_for_status()
        return resp.json()

    async def tasks(self) -> list[dict]:
        """List available tasks."""
        resp = await self.client.get("/tasks")
        resp.raise_for_status()
        return resp.json().get("tasks", [])

    async def reset(
        self,
        task_id: str = "clause_identification",
        contract_index: int = 0,
    ) -> dict:
        """Reset environment to a new episode."""
        resp = await self.client.post(
            "/reset",
            json={"task_id": task_id, "contract_index": contract_index},
        )
        resp.raise_for_status()
        return resp.json()

    async def step(self, action: dict) -> dict:
        """Take a single step."""
        resp = await self.client.post("/step", json=action)
        resp.raise_for_status()
        return resp.json()

    async def state(self) -> dict:
        """Get current episode state."""
        resp = await self.client.get("/state")
        resp.raise_for_status()
        return resp.json()

    async def grade(self) -> float:
        """Get deterministic grade for current episode."""
        resp = await self.client.get("/grader")
        resp.raise_for_status()
        return resp.json().get("score", 0.0)
