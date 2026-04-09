"""
Core environment logic for the Contract Clause Analysis OpenEnv environment.

Implements ContractClauseEnv with reset(), step(), state(), grade() methods,
dense per-step rewards, and deterministic grading for all 3 tasks.
"""

from __future__ import annotations

import uuid
from typing import Any

from models import (
    ContractAction,
    ContractObservation,
)
from data import get_contracts


def clamp_score(score: float) -> float:
    """Ensure score is strictly within (0, 1), never exactly 0.0 or 1.0."""
    try:
        v = float(score)
    except (TypeError, ValueError):
        return 0.001
    if v != v or v == float("inf") or v == float("-inf"):
        return 0.001
    return max(0.001, min(0.999, v))


# ═══════════════════════════════════════════════════════════
# Semantic aliases for clause-type fuzzy matching (easy task)
# ═══════════════════════════════════════════════════════════
CLAUSE_ALIASES: dict[str, set[str]] = {
    "position": {"role", "duties", "appointment", "job", "responsibilities"},
    "compensation": {"salary", "pay", "wages", "remuneration", "earnings"},
    "termination": {"ending", "dismissal", "separation", "exit"},
    "confidentiality": {"nda", "non_disclosure", "nondisclosure", "secrecy", "trade_secret"},
    "non_compete": {"noncompete", "non_competition", "restrictive_covenant", "covenant_not_to_compete"},
    "ip_assignment": {"intellectual_property", "ip", "work_product", "inventions", "copyright_assignment"},
    "benefits": {"perquisites", "perks", "insurance", "retirement", "401k", "pto", "vacation"},
    "governing_law": {"jurisdiction", "applicable_law", "choice_of_law", "venue"},
    "dispute_resolution": {"arbitration", "mediation", "litigation", "conflict_resolution"},
    "probation": {"probationary_period", "trial_period", "initial_assessment"},
    "notice_period": {"notice", "resignation_notice", "termination_notice"},
}

SEVERITY_LEVELS = ["low", "medium", "high", "critical"]

TASK_CONFIGS = {
    "clause_identification": {
        "name": "Clause Identification",
        "difficulty": "easy",
        "description": (
            "Given a clean employment contract with 5-7 sections, identify and classify "
            "each clause type. Valid types: position, compensation, termination, "
            "confidentiality, non_compete, ip_assignment, benefits, governing_law, "
            "dispute_resolution, probation, notice_period."
        ),
        "max_steps": 10,
    },
    "risk_flagging": {
        "name": "Risk Flagging & Analysis",
        "difficulty": "medium",
        "description": (
            "Given a vendor/service contract with hidden risky clauses, identify risks, "
            "classify severity (low/medium/high/critical), and explain why they are risky."
        ),
        "max_steps": 25,
    },
    "contract_comparison": {
        "name": "Multi-Contract Comparison & Redlining",
        "difficulty": "hard",
        "description": (
            "Given two versions of a contract (original + revised), find all changes, "
            "assess whether each is favorable/neutral/unfavorable, suggest counter-"
            "amendments for unfavorable changes, and produce an executive summary."
        ),
        "max_steps": 50,
    },
}


class ContractClauseEnv:
    """OpenEnv-compatible environment for contract clause analysis."""

    def __init__(self) -> None:
        self._episode_id: str = ""
        self._task_id: str = ""
        self._contract: dict[str, Any] = {}
        self._step_count: int = 0
        self._max_steps: int = 10
        self._done: bool = False
        self._current_section_idx: int = 0
        self._cumulative_reward: float = 0.0

        # Accumulated agent work products
        self._identified_clauses: list[dict] = []
        self._flagged_risks: list[dict] = []
        self._detected_changes: list[dict] = []
        self._amendments_suggested: list[dict] = []
        self._summary_points: list[str] = []

        self._last_feedback: str = ""
        self._action_history: list[dict] = []

    # ───────────────────────────────────────────────────
    # reset
    # ───────────────────────────────────────────────────

    def reset(
        self,
        task_id: str = "clause_identification",
        contract_index: int = 0,
    ) -> ContractObservation:
        """Reset environment to a clean state for a new episode."""
        if task_id not in TASK_CONFIGS:
            raise ValueError(
                f"Unknown task_id: {task_id!r}. "
                f"Valid: {list(TASK_CONFIGS.keys())}"
            )

        cfg = TASK_CONFIGS[task_id]
        self._episode_id = str(uuid.uuid4())
        self._task_id = task_id
        self._contract = get_contracts(task_id, contract_index)
        self._step_count = 0
        self._max_steps = cfg["max_steps"]
        self._done = False
        self._current_section_idx = 0
        self._cumulative_reward = 0.0

        self._identified_clauses = []
        self._flagged_risks = []
        self._detected_changes = []
        self._amendments_suggested = []
        self._summary_points = []
        self._last_feedback = "Environment reset. Begin reviewing the contract."
        self._action_history = []

        return self._build_observation(reward=0.0)

    # ───────────────────────────────────────────────────
    # step
    # ───────────────────────────────────────────────────

    def step(self, action: ContractAction) -> dict:
        """Execute one action and return observation, reward, done, info."""
        if self._done:
            return {
                "observation": self._build_observation(reward=0.0).model_dump(),
                "reward": 0.0,
                "done": True,
                "info": {"message": "Episode already completed."},
            }

        self._step_count += 1
        reward = 0.0

        # Check for redundant actions
        action_sig = (action.action_type, action.clause_index, action.clause_type)
        is_redundant = any(
            (h["action_type"], h.get("clause_index"), h.get("clause_type")) == action_sig
            for h in self._action_history
        )

        self._action_history.append(action.model_dump())

        if is_redundant and action.action_type not in ("next_section", "submit"):
            reward = -0.03
            self._last_feedback = "Redundant action — you already did this."
        else:
            reward = self._process_action(action)

        # Max steps enforcement
        if self._step_count >= self._max_steps and not self._done:
            self._done = True
            reward -= 0.10
            self._last_feedback += " | Episode timeout — max steps reached."

        self._cumulative_reward += reward
        obs = self._build_observation(reward=reward)

        return {
            "observation": obs.model_dump(),
            "reward": reward,
            "done": self._done,
            "info": {
                "step": self._step_count,
                "cumulative_reward": self._cumulative_reward,
            },
        }

    # ───────────────────────────────────────────────────
    # state
    # ───────────────────────────────────────────────────

    def state(self) -> dict:
        return {
            "episode_id": self._episode_id,
            "task_id": self._task_id,
            "step_count": self._step_count,
            "max_steps": self._max_steps,
            "done": self._done,
            "total_reward": round(self._cumulative_reward, 4),
        }

    # ───────────────────────────────────────────────────
    # grade
    # ───────────────────────────────────────────────────

    def grade(self) -> float:
        """Deterministic grading — same input always gives same output."""
        if self._task_id == "clause_identification":
            return clamp_score(self._grade_easy())
        elif self._task_id == "risk_flagging":
            return clamp_score(self._grade_medium())
        elif self._task_id == "contract_comparison":
            return clamp_score(self._grade_hard())
        return clamp_score(0.001)

    # ═══════════════════════════════════════════════════
    # Private: action processing
    # ═══════════════════════════════════════════════════

    def _process_action(self, action: ContractAction) -> float:
        """Dispatch and process each action type, return step reward."""
        atype = action.action_type

        if atype == "identify_clause":
            return self._do_identify_clause(action)
        elif atype == "flag_risk":
            return self._do_flag_risk(action)
        elif atype == "assess_severity":
            return self._do_assess_severity(action)
        elif atype == "explain_risk":
            return self._do_explain_risk(action)
        elif atype == "suggest_amendment":
            return self._do_suggest_amendment(action)
        elif atype == "detect_change":
            return self._do_detect_change(action)
        elif atype == "assess_impact":
            return self._do_assess_impact(action)
        elif atype == "generate_summary":
            return self._do_generate_summary(action)
        elif atype == "next_section":
            return self._do_next_section()
        elif atype == "submit":
            return self._do_submit()
        else:
            self._last_feedback = f"Unknown action type: {atype}"
            return -0.05

    # ───── identify_clause ─────

    def _do_identify_clause(self, action: ContractAction) -> float:
        if action.clause_index is None or action.clause_type is None:
            self._last_feedback = "identify_clause requires clause_index and clause_type."
            return -0.05

        gt = self._contract.get("ground_truth", {})
        truth = gt.get(str(action.clause_index))

        if truth is None:
            self._last_feedback = (
                f"Section {action.clause_index} not found in ground truth."
            )
            return -0.05

        guess = action.clause_type.lower().strip()

        self._identified_clauses.append({
            "index": action.clause_index,
            "type": guess,
        })

        if guess == truth:
            self._last_feedback = (
                f"Correct! Section {action.clause_index} identified as '{truth}'."
            )
            return 0.10
        elif self._is_semantic_match(guess, truth):
            self._last_feedback = (
                f"Close! Section {action.clause_index} is '{truth}', "
                f"'{guess}' is semantically similar."
            )
            return 0.05
        else:
            self._last_feedback = (
                f"Incorrect. Section {action.clause_index} is '{truth}', "
                f"not '{guess}'."
            )
            return -0.05

    # ───── flag_risk ─────

    def _do_flag_risk(self, action: ContractAction) -> float:
        if action.clause_index is None:
            self._last_feedback = "flag_risk requires clause_index."
            return -0.05

        gt_risks = self._contract.get("ground_truth_risks", [])
        gt_indices = {r["section_index"] for r in gt_risks}

        self._flagged_risks.append({
            "index": action.clause_index,
            "type": action.clause_type or "unknown",
        })

        if action.clause_index in gt_indices:
            gt_risk = next(
                r for r in gt_risks if r["section_index"] == action.clause_index
            )
            if (action.clause_type or "").lower() == gt_risk["risk_type"]:
                self._last_feedback = (
                    f"Correct! Section {action.clause_index} contains a "
                    f"'{gt_risk['risk_type']}' risk."
                )
                return 0.15
            else:
                self._last_feedback = (
                    f"Section {action.clause_index} is risky, but the type is "
                    f"'{gt_risk['risk_type']}', not '{action.clause_type}'."
                )
                return 0.05
        else:
            self._last_feedback = (
                f"Section {action.clause_index} does not contain a known risk. "
                f"False positive."
            )
            return -0.10

    # ───── assess_severity ─────

    def _do_assess_severity(self, action: ContractAction) -> float:
        if action.clause_index is None or action.risk_level is None:
            self._last_feedback = "assess_severity requires clause_index and risk_level."
            return -0.05

        gt_risks = self._contract.get("ground_truth_risks", [])
        gt_risk = next(
            (r for r in gt_risks if r["section_index"] == action.clause_index),
            None,
        )

        if gt_risk is None:
            self._last_feedback = (
                f"Section {action.clause_index} has no known risk to assess."
            )
            return -0.05

        true_sev = gt_risk["severity"]
        guess_sev = action.risk_level

        # Update existing flagged risk with severity
        for fr in self._flagged_risks:
            if fr["index"] == action.clause_index:
                fr["severity"] = guess_sev
                break

        if guess_sev == true_sev:
            self._last_feedback = (
                f"Correct severity! Section {action.clause_index} is '{true_sev}'."
            )
            return 0.10
        else:
            diff = abs(
                SEVERITY_LEVELS.index(guess_sev) - SEVERITY_LEVELS.index(true_sev)
            )
            if diff == 1:
                self._last_feedback = (
                    f"Close — severity is '{true_sev}', not '{guess_sev}'."
                )
                return -0.03
            else:
                self._last_feedback = (
                    f"Incorrect severity — '{true_sev}', not '{guess_sev}'."
                )
                return -0.08

    # ───── explain_risk ─────

    def _do_explain_risk(self, action: ContractAction) -> float:
        if action.clause_index is None or not action.reasoning:
            self._last_feedback = "explain_risk requires clause_index and reasoning."
            return -0.05

        sections = self._contract.get("sections", [])
        section = next(
            (s for s in sections if s["index"] == action.clause_index), None
        )

        if section is None or not section.get("risk_keywords"):
            self._last_feedback = (
                f"Section {action.clause_index} has no risk keywords to match."
            )
            return -0.02

        keywords = section["risk_keywords"]
        reasoning_lower = action.reasoning.lower()
        matches = sum(1 for kw in keywords if kw.lower() in reasoning_lower)

        for fr in self._flagged_risks:
            if fr["index"] == action.clause_index:
                fr["reasoning"] = action.reasoning
                break

        if matches >= len(keywords) * 0.5:
            self._last_feedback = (
                f"Good reasoning — matched {matches}/{len(keywords)} key concepts."
            )
            return 0.10
        elif matches > 0:
            self._last_feedback = (
                f"Partial reasoning — matched {matches}/{len(keywords)} key concepts."
            )
            return 0.04
        else:
            self._last_feedback = "Poor reasoning — no key legal concepts mentioned."
            return -0.02

    # ───── suggest_amendment ─────

    def _do_suggest_amendment(self, action: ContractAction) -> float:
        if action.clause_index is None or not action.amendment_text:
            self._last_feedback = (
                "suggest_amendment requires clause_index and amendment_text."
            )
            return -0.05

        self._amendments_suggested.append({
            "index": action.clause_index,
            "text": action.amendment_text,
        })

        if self._task_id == "contract_comparison":
            gt_changes = self._contract.get("ground_truth_changes", [])
            gt_change = next(
                (c for c in gt_changes if c["section_index"] == action.clause_index),
                None,
            )
            if gt_change and gt_change.get("amendment_keywords"):
                text_lower = action.amendment_text.lower()
                kw_matches = sum(
                    1 for kw in gt_change["amendment_keywords"]
                    if kw.lower() in text_lower
                )
                total_kw = len(gt_change["amendment_keywords"])
                if kw_matches >= total_kw * 0.5:
                    self._last_feedback = (
                        f"Good amendment — matched {kw_matches}/{total_kw} keywords."
                    )
                    return 0.15
                elif kw_matches > 0:
                    self._last_feedback = (
                        f"Partial amendment — matched {kw_matches}/{total_kw} keywords."
                    )
                    return 0.07
                else:
                    self._last_feedback = "Amendment does not address key concerns."
                    return -0.10
            else:
                self._last_feedback = "No ground truth amendment for this section."
                return 0.02
        else:
            self._last_feedback = "Amendment suggestion recorded."
            return 0.05

    # ───── detect_change ─────

    def _do_detect_change(self, action: ContractAction) -> float:
        if action.clause_index is None:
            self._last_feedback = "detect_change requires clause_index."
            return -0.05

        gt_changes = self._contract.get("ground_truth_changes", [])
        gt_indices = {c["section_index"] for c in gt_changes}

        self._detected_changes.append({
            "index": action.clause_index,
            "type": action.clause_type or "modified",
        })

        if action.clause_index in gt_indices:
            self._last_feedback = (
                f"Correct! Change detected in section {action.clause_index}."
            )
            return 0.12
        else:
            self._last_feedback = (
                f"Section {action.clause_index} has no meaningful change. "
                f"False positive."
            )
            return -0.05

    # ───── assess_impact ─────

    def _do_assess_impact(self, action: ContractAction) -> float:
        if action.clause_index is None or action.impact is None:
            self._last_feedback = "assess_impact requires clause_index and impact."
            return -0.05

        gt_changes = self._contract.get("ground_truth_changes", [])
        gt_change = next(
            (c for c in gt_changes if c["section_index"] == action.clause_index),
            None,
        )

        if gt_change is None:
            self._last_feedback = f"No known change at section {action.clause_index}."
            return -0.05

        # Update detected changes with impact
        for dc in self._detected_changes:
            if dc["index"] == action.clause_index:
                dc["impact"] = action.impact
                break

        if action.impact == gt_change["impact"]:
            self._last_feedback = (
                f"Correct impact assessment: '{action.impact}' for section "
                f"{action.clause_index}."
            )
            return 0.10
        else:
            self._last_feedback = (
                f"Incorrect. Impact is '{gt_change['impact']}', not '{action.impact}'."
            )
            return -0.05

    # ───── generate_summary ─────

    def _do_generate_summary(self, action: ContractAction) -> float:
        if not action.summary_text:
            self._last_feedback = "generate_summary requires summary_text."
            return -0.05

        self._summary_points.append(action.summary_text)

        if self._task_id == "contract_comparison":
            key_points = self._contract.get("summary_key_points", [])
            text_lower = action.summary_text.lower()
            matched = any(
                _partial_text_match(kp.lower(), text_lower) for kp in key_points
            )
            if matched:
                self._last_feedback = "Good summary point — matches a key point."
                return 0.08
            else:
                self._last_feedback = "Summary point does not match any key point."
                return 0.01
        else:
            self._last_feedback = "Summary point recorded."
            return 0.03

    # ───── next_section ─────

    def _do_next_section(self) -> float:
        sections = self._get_sections()
        if self._current_section_idx < len(sections) - 1:
            self._current_section_idx += 1
            self._last_feedback = (
                f"Advanced to section {self._current_section_idx}."
            )
            return 0.01
        else:
            self._last_feedback = "Already at the last section."
            return 0.00

    # ───── submit ─────

    def _do_submit(self) -> float:
        self._done = True

        # Determine completeness
        completeness = self._compute_completeness()
        if completeness < 0.3:
            self._last_feedback = (
                f"Submitted with low completeness ({completeness:.0%}). "
                f"Penalty applied."
            )
            reward = -0.10
        else:
            self._last_feedback = (
                f"Work submitted. Completeness: {completeness:.0%}."
            )
            reward = 0.05

        # Efficiency bonus
        if self._step_count < self._max_steps / 2:
            reward += 0.05
            self._last_feedback += " Efficiency bonus (+0.05)!"
        elif self._step_count < self._max_steps * 0.75:
            reward += 0.02
            self._last_feedback += " Efficiency bonus (+0.02)."

        return reward

    # ═══════════════════════════════════════════════════
    # Private: grading (deterministic)
    # ═══════════════════════════════════════════════════

    def _grade_easy(self) -> float:
        """Score = correct_identifications / total_clauses."""
        gt = self._contract.get("ground_truth", {})
        if not gt:
            return clamp_score(0.001)

        total = len(gt)
        score = 0.0

        for idx_str, truth in gt.items():
            # Find agent's identification for this index
            agent_guess = None
            for ic in self._identified_clauses:
                if str(ic["index"]) == idx_str:
                    agent_guess = ic["type"]
                    break  # take first identification

            if agent_guess is None:
                continue

            if agent_guess == truth:
                score += 1.0
            elif self._is_semantic_match(agent_guess, truth):
                score += 0.5

        return clamp_score(score / total)

    def _grade_medium(self) -> float:
        """Weighted: 40% risks_found, 30% severity, 30% reasoning."""
        gt_risks = self._contract.get("ground_truth_risks", [])
        if not gt_risks:
            return clamp_score(0.001)

        # Risks found (40%)
        gt_indices = {r["section_index"] for r in gt_risks}
        correctly_flagged = []
        false_positives = 0
        for fr in self._flagged_risks:
            if fr["index"] in gt_indices:
                correctly_flagged.append(fr)
            else:
                false_positives += 1

        risks_found_score = clamp_score(len(correctly_flagged) / len(gt_risks) if gt_risks else 0.0)

        # Severity accuracy (30%)
        severity_correct = 0
        for fr in correctly_flagged:
            gt_risk = next(
                r for r in gt_risks if r["section_index"] == fr["index"]
            )
            if fr.get("severity") == gt_risk["severity"]:
                severity_correct += 1

        severity_score = clamp_score(
            severity_correct / len(correctly_flagged) if correctly_flagged else 0.0
        )

        # Reasoning quality (30%)
        sections = self._contract.get("sections", [])
        reasoning_scores = []
        for fr in correctly_flagged:
            section = next(
                (s for s in sections if s["index"] == fr["index"]), None
            )
            if section and section.get("risk_keywords") and fr.get("reasoning"):
                keywords = section["risk_keywords"]
                reasoning_lower = fr["reasoning"].lower()
                matches = sum(1 for kw in keywords if kw.lower() in reasoning_lower)
                if matches >= len(keywords) * 0.5:
                    reasoning_scores.append(clamp_score(1.0))
                elif matches > 0:
                    reasoning_scores.append(clamp_score(0.5))
                else:
                    reasoning_scores.append(clamp_score(0.0))
            else:
                reasoning_scores.append(clamp_score(0.0))

        reasoning_score = clamp_score(
            sum(reasoning_scores) / len(reasoning_scores)
            if reasoning_scores
            else 0.0
        )

        # False positive penalty
        fp_penalty = false_positives * 0.1

        final = (
            0.4 * risks_found_score
            + 0.3 * severity_score
            + 0.3 * reasoning_score
            - fp_penalty
        )
        return clamp_score(final)

    def _grade_hard(self) -> float:
        """Multi-component: changes(30%), impact(25%), amendments(25%), summary(20%)."""
        gt_changes = self._contract.get("ground_truth_changes", [])
        key_points = self._contract.get("summary_key_points", [])

        if not gt_changes:
            return clamp_score(0.001)

        gt_indices = {c["section_index"] for c in gt_changes}

        # Changes found (30%)
        correctly_detected = [
            dc for dc in self._detected_changes if dc["index"] in gt_indices
        ]
        false_positives = sum(
            1 for dc in self._detected_changes if dc["index"] not in gt_indices
        )
        changes_found_score = clamp_score(len(correctly_detected) / len(gt_changes))

        # Impact assessment (25%)
        impact_correct = 0
        for dc in correctly_detected:
            gt_change = next(
                c for c in gt_changes if c["section_index"] == dc["index"]
            )
            if dc.get("impact") == gt_change["impact"]:
                impact_correct += 1
        impact_score = clamp_score(
            impact_correct / len(correctly_detected) if correctly_detected else 0.0
        )

        # Amendment quality (25%)
        amendment_scores = []
        for am in self._amendments_suggested:
            gt_change = next(
                (c for c in gt_changes if c["section_index"] == am["index"]),
                None,
            )
            if gt_change and gt_change.get("amendment_keywords"):
                text_lower = am["text"].lower()
                kw = gt_change["amendment_keywords"]
                matches = sum(1 for k in kw if k.lower() in text_lower)
                amendment_scores.append(clamp_score(matches / len(kw) if kw else 0.0))
        amendment_score = clamp_score(
            sum(amendment_scores) / len(amendment_scores)
            if amendment_scores
            else 0.0
        )

        # Summary completeness (20%)
        if key_points:
            points_mentioned = 0
            for kp in key_points:
                kp_lower = kp.lower()
                for sp in self._summary_points:
                    if _partial_text_match(kp_lower, sp.lower()):
                        points_mentioned += 1
                        break
            summary_score = clamp_score(points_mentioned / len(key_points))
        else:
            summary_score = clamp_score(0.0)

        fp_penalty = false_positives * 0.05

        final = (
            0.30 * changes_found_score
            + 0.25 * impact_score
            + 0.25 * amendment_score
            + 0.20 * summary_score
            - fp_penalty
        )
        return clamp_score(final)

    # ═══════════════════════════════════════════════════
    # Private: helpers
    # ═══════════════════════════════════════════════════

    def _get_sections(self) -> list[dict]:
        """Return sections list from current contract."""
        if self._task_id == "contract_comparison":
            return self._contract.get("original_sections", [])
        return self._contract.get("sections", [])

    def _get_current_section(self) -> dict:
        sections = self._get_sections()
        if 0 <= self._current_section_idx < len(sections):
            return sections[self._current_section_idx]
        return {"index": 0, "heading": "N/A", "text": "No section available."}

    def _build_observation(self, reward: float) -> ContractObservation:
        section = self._get_current_section()
        sections = self._get_sections()
        total = len(sections)

        # For comparison tasks, show both original and revised text
        section_text = section.get("text", "")
        if self._task_id == "contract_comparison":
            revised = self._contract.get("revised_sections", [])
            if 0 <= self._current_section_idx < len(revised):
                r_section = revised[self._current_section_idx]
                section_text = (
                    f"=== ORIGINAL ===\n{section.get('text', '')}\n\n"
                    f"=== REVISED ===\n{r_section.get('text', '')}"
                )

        progress = (
            (self._current_section_idx + 1) / total if total > 0 else 0.0
        )

        title = self._contract.get(
            "title",
            self._contract.get("pair_id", "Unknown"),
        )
        parties = self._contract.get("parties", {})
        task_cfg = TASK_CONFIGS.get(self._task_id, {})

        return ContractObservation(
            contract_title=title,
            contract_parties=parties,
            current_section_index=self._current_section_idx,
            current_section_heading=section.get("heading", ""),
            current_section_text=section_text,
            total_sections=total,
            identified_clauses=list(self._identified_clauses),
            flagged_risks=list(self._flagged_risks),
            detected_changes=list(self._detected_changes),
            amendments_suggested=list(self._amendments_suggested),
            summary_points=list(self._summary_points),
            system_feedback=self._last_feedback,
            task_id=self._task_id,
            task_description=task_cfg.get("description", ""),
            step_count=self._step_count,
            max_steps=self._max_steps,
            progress=round(progress, 3),
            reward=round(reward, 4),
            cumulative_reward=round(self._cumulative_reward, 4),
            done=self._done,
        )

    def _compute_completeness(self) -> float:
        """Fraction of the work completed."""
        sections = self._get_sections()
        total = len(sections)
        if total == 0:
            return 0.0

        if self._task_id == "clause_identification":
            return len(self._identified_clauses) / total
        elif self._task_id == "risk_flagging":
            gt_risks = self._contract.get("ground_truth_risks", [])
            if not gt_risks:
                return 0.0
            return len(self._flagged_risks) / len(gt_risks)
        elif self._task_id == "contract_comparison":
            gt_changes = self._contract.get("ground_truth_changes", [])
            if not gt_changes:
                return 0.0
            return len(self._detected_changes) / len(gt_changes)
        return 0.0

    @staticmethod
    def _is_semantic_match(guess: str, truth: str) -> bool:
        """Check if guess is a known alias/synonym for truth."""
        aliases = CLAUSE_ALIASES.get(truth, set())
        return guess in aliases


def _partial_text_match(needle: str, haystack: str) -> bool:
    """Check if enough words from needle appear in haystack."""
    words = [w for w in needle.split() if len(w) > 3]
    if not words:
        return False
    matches = sum(1 for w in words if w in haystack)
    return matches >= len(words) * 0.4
