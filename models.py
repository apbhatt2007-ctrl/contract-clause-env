"""
Pydantic v2 models for the Contract Clause Analysis OpenEnv environment.

Defines the Action, Observation, and supporting data models used by the
environment, server, baseline, and client.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# ═══════════════════════════════════════════════════════════
# Action Model
# ═══════════════════════════════════════════════════════════

class ContractAction(BaseModel):
    """Action the agent can take in the contract review environment."""

    action_type: Literal[
        "identify_clause",
        "flag_risk",
        "assess_severity",
        "explain_risk",
        "suggest_amendment",
        "detect_change",
        "assess_impact",
        "generate_summary",
        "next_section",
        "submit",
    ]
    clause_index: Optional[int] = None
    clause_type: Optional[str] = None
    risk_level: Optional[Literal["low", "medium", "high", "critical"]] = None
    reasoning: Optional[str] = None
    amendment_text: Optional[str] = None
    impact: Optional[Literal["favorable", "neutral", "unfavorable"]] = None
    summary_text: Optional[str] = None
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)

    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════
# Observation Model
# ═══════════════════════════════════════════════════════════

class ContractObservation(BaseModel):
    """What the agent sees after each action."""

    contract_title: str
    contract_parties: dict
    current_section_index: int
    current_section_heading: str
    current_section_text: str
    total_sections: int
    identified_clauses: list[dict] = Field(default_factory=list)
    flagged_risks: list[dict] = Field(default_factory=list)
    detected_changes: list[dict] = Field(default_factory=list)
    amendments_suggested: list[dict] = Field(default_factory=list)
    summary_points: list[str] = Field(default_factory=list)
    system_feedback: str = ""
    task_id: str
    task_description: str
    step_count: int = 0
    max_steps: int = 10
    progress: float = 0.0
    reward: float = 0.0
    cumulative_reward: float = 0.0
    done: bool = False

    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════
# Supporting Models
# ═══════════════════════════════════════════════════════════

class StepResult(BaseModel):
    """Return type of environment.step()."""

    observation: ContractObservation
    reward: float
    done: bool
    info: dict = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class EpisodeState(BaseModel):
    """Lightweight snapshot of episode progress."""

    episode_id: str
    task_id: str
    step_count: int
    max_steps: int
    done: bool
    total_reward: float

    model_config = ConfigDict(from_attributes=True)


class TaskDefinition(BaseModel):
    """Metadata describing a single task."""

    task_id: str
    name: str
    difficulty: Literal["easy", "medium", "hard"]
    description: str
    max_steps: int

    model_config = ConfigDict(from_attributes=True)


class ContractSection(BaseModel):
    """A single section/clause within a contract."""

    index: int
    heading: str
    text: str
    clause_type: Optional[str] = None
    has_risk: bool = False
    risk_type: Optional[str] = None
    severity: Optional[Literal["low", "medium", "high", "critical"]] = None
    risk_keywords: list[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ContractData(BaseModel):
    """Full contract with all sections and ground truth."""

    contract_id: str
    title: str
    parties: dict
    sections: list[ContractSection]
    ground_truth: Optional[dict] = None
    ground_truth_risks: Optional[list[dict]] = None

    model_config = ConfigDict(from_attributes=True)


class ContractPairData(BaseModel):
    """A pair of contracts for comparison tasks."""

    pair_id: str
    title: str
    parties: dict
    original_sections: list[ContractSection]
    revised_sections: list[ContractSection]
    ground_truth_changes: list[dict]
    summary_key_points: list[str]

    model_config = ConfigDict(from_attributes=True)
