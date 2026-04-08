"""
Unit tests for the Contract Clause Analysis graders.

Tests deterministic grading across all three task types:
- clause_identification: accuracy with semantic matching
- risk_flagging: multi-component weighted scoring
- contract_comparison: changes + impact + amendments + summary

Run: pytest tests/test_graders.py -v
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graders.grader import (
    grade_clause_identification,
    grade_risk_flagging,
    grade_contract_comparison,
    is_semantic_match,
)


# ═══════════════════════════════════════════════════════════
# Semantic matching tests
# ═══════════════════════════════════════════════════════════


class TestSemanticMatch:
    def test_exact_match_is_not_alias(self):
        # Exact match is handled separately, aliases are for synonyms
        assert not is_semantic_match("position", "position")

    def test_known_alias(self):
        assert is_semantic_match("salary", "compensation")
        assert is_semantic_match("nda", "confidentiality")
        assert is_semantic_match("jurisdiction", "governing_law")

    def test_unknown_alias(self):
        assert not is_semantic_match("banana", "compensation")

    def test_case_insensitive(self):
        assert is_semantic_match("Salary", "compensation")


# ═══════════════════════════════════════════════════════════
# Clause identification grading tests
# ═══════════════════════════════════════════════════════════


class TestClauseIdentification:
    def test_perfect_score(self):
        gt = {"0": "position", "1": "compensation", "2": "termination"}
        identified = [
            {"index": 0, "type": "position"},
            {"index": 1, "type": "compensation"},
            {"index": 2, "type": "termination"},
        ]
        assert grade_clause_identification(identified, gt) == 1.0

    def test_all_wrong(self):
        gt = {"0": "position", "1": "compensation"}
        identified = [
            {"index": 0, "type": "termination"},
            {"index": 1, "type": "confidentiality"},
        ]
        assert grade_clause_identification(identified, gt) == 0.0

    def test_partial_with_semantic_match(self):
        gt = {"0": "compensation", "1": "governing_law"}
        identified = [
            {"index": 0, "type": "salary"},  # semantic match -> 0.5
            {"index": 1, "type": "governing_law"},  # exact -> 1.0
        ]
        score = grade_clause_identification(identified, gt)
        assert score == pytest.approx(0.75, abs=0.01)

    def test_missing_identification(self):
        gt = {"0": "position", "1": "compensation", "2": "termination"}
        identified = [{"index": 0, "type": "position"}]  # only 1/3
        score = grade_clause_identification(identified, gt)
        assert score == pytest.approx(1.0 / 3, abs=0.01)

    def test_empty_ground_truth(self):
        assert grade_clause_identification([], {}) == 0.0

    def test_empty_identifications(self):
        gt = {"0": "position"}
        assert grade_clause_identification([], gt) == 0.0

    def test_score_clamped_to_01(self):
        gt = {"0": "position"}
        identified = [{"index": 0, "type": "position"}]
        score = grade_clause_identification(identified, gt)
        assert 0.0 <= score <= 1.0


# ═══════════════════════════════════════════════════════════
# Risk flagging grading tests
# ═══════════════════════════════════════════════════════════


class TestRiskFlagging:
    def test_perfect_score(self):
        gt_risks = [
            {"section_index": 2, "risk_type": "auto_renewal", "severity": "high"},
        ]
        sections = [
            {"index": 2, "risk_keywords": ["auto", "renewal"]},
        ]
        flagged = [
            {"index": 2, "type": "auto_renewal", "severity": "high",
             "reasoning": "This clause has auto renewal with hidden terms."},
        ]
        score = grade_risk_flagging(flagged, gt_risks, sections)
        assert score == pytest.approx(1.0, abs=0.01)

    def test_no_risks_flagged(self):
        gt_risks = [{"section_index": 2, "risk_type": "auto_renewal", "severity": "high"}]
        score = grade_risk_flagging([], gt_risks, [])
        assert score == 0.0

    def test_false_positive_penalty(self):
        gt_risks = [{"section_index": 2, "risk_type": "auto_renewal", "severity": "high"}]
        flagged = [
            {"index": 2, "type": "auto_renewal", "severity": "high"},
            {"index": 5, "type": "fake_risk"},  # false positive
        ]
        score = grade_risk_flagging(flagged, gt_risks, [])
        # Should be penalized for false positive
        assert score < 1.0

    def test_wrong_severity(self):
        gt_risks = [{"section_index": 2, "risk_type": "auto_renewal", "severity": "high"}]
        flagged = [{"index": 2, "type": "auto_renewal", "severity": "low"}]
        score = grade_risk_flagging(flagged, gt_risks, [])
        # Risk found (40%) but severity wrong (0%), no reasoning (0%)
        assert score == pytest.approx(0.4, abs=0.01)

    def test_empty_ground_truth(self):
        assert grade_risk_flagging([], [], []) == 0.0


# ═══════════════════════════════════════════════════════════
# Contract comparison grading tests
# ═══════════════════════════════════════════════════════════


class TestContractComparison:
    def test_perfect_detection(self):
        gt_changes = [
            {"section_index": 0, "impact": "unfavorable", "amendment_keywords": ["restore"]},
        ]
        detected = [{"index": 0, "type": "modified", "impact": "unfavorable"}]
        amendments = [{"index": 0, "text": "We propose to restore the original terms."}]
        summary = ["Major changes to licensing"]
        key_points = ["Major changes to licensing terms"]

        score = grade_contract_comparison(detected, amendments, summary, gt_changes, key_points)
        assert score > 0.8

    def test_no_detections(self):
        gt_changes = [{"section_index": 0, "impact": "unfavorable", "amendment_keywords": ["restore"]}]
        score = grade_contract_comparison([], [], [], gt_changes, [])
        assert score == 0.0

    def test_false_positive_penalty(self):
        gt_changes = [{"section_index": 0, "impact": "unfavorable", "amendment_keywords": []}]
        detected = [
            {"index": 0, "type": "modified", "impact": "unfavorable"},
            {"index": 99, "type": "modified"},  # false positive
        ]
        score = grade_contract_comparison(detected, [], [], gt_changes, [])
        assert score < grade_contract_comparison(
            [{"index": 0, "type": "modified", "impact": "unfavorable"}], [], [], gt_changes, []
        )

    def test_wrong_impact(self):
        gt_changes = [{"section_index": 0, "impact": "unfavorable", "amendment_keywords": []}]
        detected = [{"index": 0, "type": "modified", "impact": "favorable"}]
        score = grade_contract_comparison(detected, [], [], gt_changes, [])
        # Changes found (30%) but impact wrong (0%) = 0.30
        assert score == pytest.approx(0.30, abs=0.01)

    def test_score_clamped(self):
        gt_changes = [{"section_index": 0, "impact": "unfavorable", "amendment_keywords": []}]
        detected = [{"index": 0, "type": "modified", "impact": "unfavorable"}]
        score = grade_contract_comparison(detected, [], [], gt_changes, [])
        assert 0.0 <= score <= 1.0


# ═══════════════════════════════════════════════════════════
# Determinism tests — same input = same output, always
# ═══════════════════════════════════════════════════════════


class TestDeterminism:
    def test_clause_grading_is_deterministic(self):
        gt = {"0": "position", "1": "compensation"}
        identified = [{"index": 0, "type": "position"}, {"index": 1, "type": "salary"}]
        scores = [grade_clause_identification(identified, gt) for _ in range(10)]
        assert len(set(scores)) == 1, "Grading must be deterministic"

    def test_risk_grading_is_deterministic(self):
        gt_risks = [{"section_index": 2, "risk_type": "auto_renewal", "severity": "high"}]
        flagged = [{"index": 2, "type": "auto_renewal", "severity": "high"}]
        scores = [grade_risk_flagging(flagged, gt_risks, []) for _ in range(10)]
        assert len(set(scores)) == 1, "Grading must be deterministic"
