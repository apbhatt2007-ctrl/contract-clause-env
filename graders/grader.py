"""
Deterministic grading functions for the Contract Clause Analysis environment.

All graders produce the same output for the same input — no randomness.
These functions are used by the environment's grade() method.
"""

from __future__ import annotations


def clamp_score(score: float) -> float:
    """Ensure score is strictly within (0, 1), never exactly 0.0 or 1.0."""
    return max(0.001, min(1 - 0.001, float(score)))


CLAUSE_ALIASES: dict[str, set[str]] = {
    "position": {"role", "duties", "appointment", "job", "responsibilities"},
    "compensation": {"salary", "pay", "wages", "remuneration", "earnings"},
    "termination": {"ending", "dismissal", "separation", "exit"},
    "confidentiality": {"nda", "non_disclosure", "nondisclosure", "secrecy", "trade_secret"},
    "non_compete": {"noncompete", "non_competition", "restrictive_covenant"},
    "ip_assignment": {"intellectual_property", "ip", "work_product", "inventions"},
    "benefits": {"perquisites", "perks", "insurance", "retirement", "401k"},
    "governing_law": {"jurisdiction", "applicable_law", "choice_of_law", "venue"},
    "dispute_resolution": {"arbitration", "mediation", "litigation"},
    "probation": {"probationary_period", "trial_period"},
    "notice_period": {"notice", "resignation_notice"},
}


def is_semantic_match(guess: str, truth: str) -> bool:
    """Check if guess is a known alias/synonym for truth."""
    aliases = CLAUSE_ALIASES.get(truth, set())
    return guess.lower().strip() in aliases


def grade_clause_identification(
    identified_clauses: list[dict],
    ground_truth: dict[str, str],
) -> float:
    """
    Grade the clause identification task.

    Score = sum(per_clause_score) / total_clauses, clamped [0, 1].
    Exact match = 1.0, semantic match = 0.5, wrong = 0.0.
    """
    if not ground_truth:
        return clamp_score(0.0)

    total = len(ground_truth)
    score = 0.0

    for idx_str, truth in ground_truth.items():
        agent_guess = None
        for ic in identified_clauses:
            if str(ic.get("index")) == idx_str:
                agent_guess = ic.get("type", "").lower().strip()
                break

        if agent_guess is None:
            continue

        if agent_guess == truth:
            score += 1.0
        elif is_semantic_match(agent_guess, truth):
            score += 0.5

    return clamp_score(score / total)


def grade_risk_flagging(
    flagged_risks: list[dict],
    ground_truth_risks: list[dict],
    sections: list[dict],
) -> float:
    """
    Grade the risk flagging task.

    Weighted: 40% risks_found + 30% severity + 30% reasoning − false_positive_penalty.
    """
    if not ground_truth_risks:
        return clamp_score(0.0)

    gt_indices = {r["section_index"] for r in ground_truth_risks}

    correctly_flagged = [fr for fr in flagged_risks if fr.get("index") in gt_indices]
    false_positives = sum(1 for fr in flagged_risks if fr.get("index") not in gt_indices)

    # Risks found (40%)
    risks_found_score = clamp_score(len(correctly_flagged) / len(ground_truth_risks))

    # Severity accuracy (30%)
    severity_correct = 0
    for fr in correctly_flagged:
        gt_risk = next(r for r in ground_truth_risks if r["section_index"] == fr["index"])
        if fr.get("severity") == gt_risk.get("severity"):
            severity_correct += 1
    severity_score = clamp_score(severity_correct / len(correctly_flagged) if correctly_flagged else 0.0)

    # Reasoning quality (30%)
    reasoning_scores = []
    for fr in correctly_flagged:
        section = next((s for s in sections if s.get("index") == fr["index"]), None)
        if section and section.get("risk_keywords") and fr.get("reasoning"):
            keywords = section["risk_keywords"]
            reasoning_lower = fr["reasoning"].lower()
            matches = sum(1 for kw in keywords if kw.lower() in reasoning_lower)
            ratio = matches / len(keywords) if keywords else 0.0
            reasoning_scores.append(clamp_score(1.0) if ratio >= 0.5 else (clamp_score(0.5) if matches > 0 else clamp_score(0.0)))
        else:
            reasoning_scores.append(clamp_score(0.0))
    reasoning_score = clamp_score(sum(reasoning_scores) / len(reasoning_scores) if reasoning_scores else 0.0)

    fp_penalty = false_positives * 0.1

    final = 0.4 * risks_found_score + 0.3 * severity_score + 0.3 * reasoning_score - fp_penalty
    return clamp_score(final)


def grade_contract_comparison(
    detected_changes: list[dict],
    amendments_suggested: list[dict],
    summary_points: list[str],
    ground_truth_changes: list[dict],
    summary_key_points: list[str],
) -> float:
    """
    Grade the contract comparison task.

    Weighted: 30% changes_found + 25% impact + 25% amendments + 20% summary
    − false_positive_penalty.
    """
    if not ground_truth_changes:
        return clamp_score(0.0)

    gt_indices = {c["section_index"] for c in ground_truth_changes}
    correctly_detected = [dc for dc in detected_changes if dc.get("index") in gt_indices]
    false_positives = sum(1 for dc in detected_changes if dc.get("index") not in gt_indices)

    # Changes found (30%)
    changes_found_score = clamp_score(len(correctly_detected) / len(ground_truth_changes))

    # Impact assessment (25%)
    impact_correct = 0
    for dc in correctly_detected:
        gt_change = next(c for c in ground_truth_changes if c["section_index"] == dc["index"])
        if dc.get("impact") == gt_change.get("impact"):
            impact_correct += 1
    impact_score = clamp_score(impact_correct / len(correctly_detected) if correctly_detected else 0.0)

    # Amendment quality (25%)
    amendment_scores = []
    for am in amendments_suggested:
        gt_change = next(
            (c for c in ground_truth_changes if c["section_index"] == am.get("index")),
            None,
        )
        if gt_change and gt_change.get("amendment_keywords"):
            kw = gt_change["amendment_keywords"]
            text_lower = am.get("text", "").lower()
            matches = sum(1 for k in kw if k.lower() in text_lower)
            amendment_scores.append(clamp_score(matches / len(kw) if kw else 0.0))
    amendment_score = clamp_score(sum(amendment_scores) / len(amendment_scores) if amendment_scores else 0.0)

    # Summary (20%)
    if summary_key_points:
        points_mentioned = 0
        for kp in summary_key_points:
            kp_lower = kp.lower()
            kp_words = [w for w in kp_lower.split() if len(w) > 3]
            for sp in summary_points:
                sp_lower = sp.lower()
                matches = sum(1 for w in kp_words if w in sp_lower)
                if kp_words and matches >= len(kp_words) * 0.4:
                    points_mentioned += 1
                    break
        summary_score = clamp_score(points_mentioned / len(summary_key_points))
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
