"""
Extreme stress test for Contract Clause Analysis OpenEnv Hackathon submission.
Tests all endpoints, deterministic grading, edge cases, and error handling.
Uses the CORRECT ContractAction schema fields.
"""

import httpx
import json
import time
import traceback

BASE_URL = "https://atharva4-openenvhackathon.hf.space"
TIMEOUT = 30
results = []


def log(level, test, msg, details=None):
    entry = {"level": level, "test": test, "msg": msg}
    if details:
        entry["details"] = details
    results.append(entry)
    icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "INFO": "ℹ️"}.get(level, "•")
    print(f"  {icon} [{test}] {msg}")


def section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


client = httpx.Client(base_url=BASE_URL, timeout=TIMEOUT)

# ======================================================================
# 1. INFRASTRUCTURE TESTS
# ======================================================================
section("1. INFRASTRUCTURE & ENDPOINT AVAILABILITY")

try:
    r = client.get("/health")
    data = r.json()
    if r.status_code == 200 and data.get("status") == "ok":
        log("PASS", "health", f"GET /health → 200 ({r.elapsed.total_seconds():.2f}s)")
    else:
        log("FAIL", "health", f"Unexpected: {r.status_code} {data}")
except Exception as e:
    log("FAIL", "health", f"Exception: {e}")

try:
    r = client.get("/tasks")
    tasks = r.json()
    task_ids = [t["task_id"] for t in tasks]
    expected = {"clause_identification", "risk_flagging", "contract_comparison"}
    if set(task_ids) == expected:
        log("PASS", "tasks", f"All 3 tasks present: {task_ids}")
    else:
        log("FAIL", "tasks", f"Missing tasks. Got: {task_ids}")
    for t in tasks:
        if all(k in t for k in ["task_id", "name", "difficulty", "description", "max_steps"]):
            log("PASS", f"tasks/{t['task_id']}", f"Schema valid. max_steps={t['max_steps']}")
        else:
            log("FAIL", f"tasks/{t['task_id']}", f"Missing fields: {t}")
except Exception as e:
    log("FAIL", "tasks", f"Exception: {e}")

try:
    r = client.get("/baseline")
    data = r.json()
    if "inference.py" in data.get("command", "") or "inference.py" in data.get("message", ""):
        log("PASS", "baseline", f"References inference.py correctly")
    else:
        log("WARN", "baseline", f"No inference.py reference: {data}")
except Exception as e:
    log("FAIL", "baseline", f"Exception: {e}")

try:
    r = client.get("/state")
    if r.status_code in [200, 400, 422]:
        log("PASS", "state_pre_reset", f"Handles pre-reset state: {r.status_code}")
    else:
        log("WARN", "state_pre_reset", f"Unexpected status: {r.status_code}")
except Exception as e:
    log("FAIL", "state_pre_reset", f"Exception: {e}")


# ======================================================================
# 2. EASY TASK: CLAUSE IDENTIFICATION (5 contracts)
# ======================================================================
section("2. EASY TASK — CLAUSE IDENTIFICATION")

CLAUSE_MAP = {
    0: {0: "position", 1: "compensation", 2: "termination", 3: "confidentiality", 4: "ip_assignment", 5: "non_compete", 6: "governing_law"},
    1: {0: "position", 1: "compensation", 2: "benefits", 3: "confidentiality", 4: "termination", 5: "dispute_resolution"},
    2: {0: "position", 1: "compensation", 2: "probation", 3: "confidentiality", 4: "notice_period"},
    3: {0: "position", 1: "compensation", 2: "benefits", 3: "non_compete", 4: "termination", 5: "ip_assignment", 6: "governing_law"},
    4: {0: "position", 1: "compensation", 2: "ip_assignment", 3: "confidentiality", 4: "termination", 5: "governing_law"},
}

easy_scores = []
for ci, clause_map in CLAUSE_MAP.items():
    try:
        r = client.post("/reset", json={"task_id": "clause_identification", "contract_index": ci})
        obs = r.json()
        for sec_idx, clause_type in clause_map.items():
            client.post("/step", json={"action_type": "identify_clause", "clause_index": sec_idx, "clause_type": clause_type, "confidence": 1.0})
        for _ in range(3):
            r = client.post("/step", json={"action_type": "next_section", "confidence": 1.0})
            if r.json().get("observation", {}).get("done", False):
                break
        score = client.get("/grader").json().get("score", 0.0)
        easy_scores.append(score)
        log("PASS" if score >= 0.95 else "FAIL", f"easy/c{ci}", f"Score: {score:.4f}")
    except Exception as e:
        log("FAIL", f"easy/c{ci}", f"Exception: {e}")
        easy_scores.append(0.0)

avg_easy = sum(easy_scores) / len(easy_scores) if easy_scores else 0.0
log("INFO", "easy_avg", f"Average easy score: {avg_easy:.4f}")


# ======================================================================
# 2b. DETERMINISM TEST
# ======================================================================
section("2b. DETERMINISM VERIFICATION")

det_scores = []
for run in range(3):
    client.post("/reset", json={"task_id": "clause_identification", "contract_index": 0})
    for sidx, ctype in CLAUSE_MAP[0].items():
        client.post("/step", json={"action_type": "identify_clause", "clause_index": sidx, "clause_type": ctype, "confidence": 1.0})
    for _ in range(3):
        r = client.post("/step", json={"action_type": "next_section", "confidence": 1.0})
        if r.json().get("observation", {}).get("done", False):
            break
    det_scores.append(client.get("/grader").json().get("score", 0.0))

if len(set(det_scores)) == 1:
    log("PASS", "determinism", f"3 runs identical: {det_scores}")
else:
    log("FAIL", "determinism", f"Non-deterministic! Scores: {det_scores}")


# ======================================================================
# 3. MEDIUM TASK: RISK FLAGGING
# Uses correct ContractAction fields:
#   flag_risk     → clause_index + clause_type (for risk type)
#   assess_severity → clause_index + risk_level
#   explain_risk  → clause_index + reasoning
# ======================================================================
section("3. MEDIUM TASK — RISK FLAGGING")

# Risk keywords from the data files for high-quality reasoning
RISK_KEYWORDS = {
    (0, 2): ["auto renewal", "automatically renew", "120 days", "prevailing rate", "vendor discretion"],
    (0, 4): ["uncapped liability", "sole discretion", "no fixed cap", "aggregate liability", "case-by-case"],
    (0, 6): ["perpetual license", "irrevocable", "derivative works", "data ownership", "machine learning models", "without consent"],
    (1, 2): ["early termination fee", "remaining retainers", "25% surcharge", "penalty"],
    (1, 4): ["indemnify", "regardless of negligence", "hold harmless", "agency negligence"],
    (1, 5): ["unilateral", "modify at any time", "continued use constitutes acceptance", "sole remedy"],
    (1, 6): ["non-compete", "24 months", "36 months", "liquidated damages", "$150,000"],
    (2, 3): ["commercialize", "anonymized data", "retain right", "aggregate data", "derived from"],
    (2, 5): ["indemnify", "regardless of defects", "vendor errors", "hold harmless", "downstream liabilities"],
    (2, 6): ["Singapore", "inconvenient jurisdiction", "foreign arbitration", "waives objection"],
    (3, 2): ["auto renewal", "automatically renew", "90 days notice", "bound for current term"],
    (3, 4): ["200%", "shortfall penalty", "minimum order", "account maintenance fee"],
    (3, 5): ["unilateral right", "amend any provision", "posting on website", "irrevocable acceptance"],
    (3, 6): ["indemnify", "product defects", "safety standards", "vendor failure", "hold harmless"],
    (3, 7): ["36 months", "all personnel", "regardless of involvement", "$100,000", "liquidated damages"],
    (4, 3): ["retain all right", "insights derived", "other clients", "without attribution"],
    (4, 4): ["limited to lesser", "$25,000 cap", "waives right", "malpractice cap"],
}

RISK_MAP = {
    0: [
        {"index": 2, "risk_type": "auto_renewal_trap", "severity": "high"},
        {"index": 4, "risk_type": "unlimited_liability", "severity": "critical"},
        {"index": 6, "risk_type": "data_ownership_grab", "severity": "critical"},
    ],
    1: [
        {"index": 2, "risk_type": "excessive_penalty", "severity": "high"},
        {"index": 4, "risk_type": "broad_indemnification", "severity": "high"},
        {"index": 5, "risk_type": "unilateral_amendment", "severity": "critical"},
        {"index": 6, "risk_type": "non_compete_overreach", "severity": "high"},
    ],
    2: [
        {"index": 3, "risk_type": "data_ownership_grab", "severity": "high"},
        {"index": 5, "risk_type": "broad_indemnification", "severity": "critical"},
        {"index": 6, "risk_type": "jurisdiction_trap", "severity": "high"},
    ],
    3: [
        {"index": 2, "risk_type": "auto_renewal_trap", "severity": "medium"},
        {"index": 4, "risk_type": "excessive_penalty", "severity": "critical"},
        {"index": 5, "risk_type": "unilateral_amendment", "severity": "critical"},
        {"index": 6, "risk_type": "broad_indemnification", "severity": "high"},
        {"index": 7, "risk_type": "non_compete_overreach", "severity": "high"},
    ],
    4: [
        {"index": 3, "risk_type": "data_ownership_grab", "severity": "high"},
        {"index": 4, "risk_type": "unlimited_liability", "severity": "critical"},
    ],
}

medium_scores = []

for ci, risks in RISK_MAP.items():
    try:
        r = client.post("/reset", json={"task_id": "risk_flagging", "contract_index": ci})
        obs = r.json()

        for risk in risks:
            # Navigate to section
            while obs.get("current_section_index", 0) < risk["index"]:
                r = client.post("/step", json={"action_type": "next_section", "confidence": 1.0})
                obs = r.json().get("observation", obs)

            # Step 1: flag_risk using clause_index + clause_type
            r = client.post("/step", json={
                "action_type": "flag_risk",
                "clause_index": risk["index"],
                "clause_type": risk["risk_type"],
                "confidence": 1.0,
            })
            obs = r.json().get("observation", obs)

            # Step 2: assess_severity using clause_index + risk_level
            r = client.post("/step", json={
                "action_type": "assess_severity",
                "clause_index": risk["index"],
                "risk_level": risk["severity"],
                "confidence": 1.0,
            })
            obs = r.json().get("observation", obs)

            # Step 3: explain_risk using clause_index + reasoning (with keywords)
            kws = RISK_KEYWORDS.get((ci, risk["index"]), [])
            reasoning = f"This section contains {risk['risk_type'].replace('_', ' ')} risk. Key issues: {', '.join(kws)}"
            r = client.post("/step", json={
                "action_type": "explain_risk",
                "clause_index": risk["index"],
                "reasoning": reasoning,
                "confidence": 1.0,
            })
            obs = r.json().get("observation", obs)

        # Navigate to end
        for _ in range(15):
            r = client.post("/step", json={"action_type": "next_section", "confidence": 1.0})
            if r.json().get("observation", {}).get("done", False):
                break

        score = client.get("/grader").json().get("score", 0.0)
        medium_scores.append(score)
        log("PASS" if score >= 0.6 else ("WARN" if score >= 0.3 else "FAIL"), f"medium/c{ci}", f"Score: {score:.4f}")

    except Exception as e:
        log("FAIL", f"medium/c{ci}", f"Exception: {e}")
        traceback.print_exc()
        medium_scores.append(0.0)

avg_medium = sum(medium_scores) / len(medium_scores) if medium_scores else 0.0
log("INFO", "medium_avg", f"Average medium score: {avg_medium:.4f}")


# ======================================================================
# 4. HARD TASK: CONTRACT COMPARISON
# Uses correct ContractAction fields:
#   detect_change     → clause_index + clause_type ("modified")
#   assess_impact     → clause_index + impact
#   suggest_amendment → clause_index + amendment_text
#   generate_summary  → summary_text
# ======================================================================
section("4. HARD TASK — CONTRACT COMPARISON")

# Amendment keyword lists from contracts_hard.py
AMENDMENT_KW = {
    (0, 0): ["restore", "250 users", "multi-location", "tiered", "scale"],
    (0, 1): ["phased", "gradual", "cap", "incremental", "CPI"],
    (0, 2): ["Net-45", "compromise", "quarterly", "installment", "cash flow"],
    (0, 3): ["99.9%", "restore SLA", "uptime", "credit", "service level"],
    (0, 5): ["mutual termination", "30 days", "no fee", "free export", "restore"],
    (1, 0): ["two parking", "restore", "free hours", "conference", "include"],
    (1, 1): ["two renewals", "180 days", "cap", "5%", "restore options"],
    (1, 2): ["counter", "$76", "3.5%", "two months", "step-up"],
    (1, 3): ["$45", "restore allowance", "reasonable", "60 days", "not unreasonably"],
    (1, 4): ["include in rent", "define timeframe", "4 hours", "specific SLA"],
    (1, 5): ["not unreasonably", "15 days", "50/50", "equal share", "restore"],
    (1, 6): ["10 days", "30 days", "mitigate", "cure period", "restore"],
    (2, 0): ["equal", "joint decision", "restore", "mutual", "partnership"],
    (2, 1): ["equal contribution", "50/50", "10%", "unanimous", "cap fee"],
    (2, 2): ["co-ownership", "joint IP", "no royalty", "equal rights", "background IP"],
    (2, 3): ["equal representation", "3 each", "supermajority", "joint appointment"],
    (2, 4): ["5 years", "mutual termination", "co-ownership", "perpetual license", "restore"],
}

COMPARISON_MAP = {
    0: {
        "changes": [
            {"index": 0, "impact": "unfavorable"},
            {"index": 1, "impact": "unfavorable"},
            {"index": 2, "impact": "unfavorable"},
            {"index": 3, "impact": "unfavorable"},
            {"index": 4, "impact": "neutral"},
            {"index": 5, "impact": "unfavorable"},
        ],
        "summary": [
            "License fee increased by 50% from $50,000 to $75,000",
            "User count reduced from 250 to 150 and restricted to single location",
            "Payment terms shortened from Net-60 to Net-30 with higher late penalty",
            "SLA uptime reduced from 99.9% to 99.5% with lower service credits",
            "Termination rights became asymmetric with early termination fee added",
            "New reverse-engineering restriction clause strengthened",
        ],
    },
    1: {
        "changes": [
            {"index": 0, "impact": "unfavorable"},
            {"index": 1, "impact": "unfavorable"},
            {"index": 2, "impact": "unfavorable"},
            {"index": 3, "impact": "unfavorable"},
            {"index": 4, "impact": "unfavorable"},
            {"index": 5, "impact": "unfavorable"},
            {"index": 6, "impact": "unfavorable"},
        ],
        "summary": [
            "Base rent increased from $72 to $82 per square foot (14% increase)",
            "Annual rent escalation increased from 3% to 4.5%",
            "Security deposit increased from 2 to 3 months' rent",
            "Tenant improvement allowance reduced from $45 to $30 per square foot",
            "Renewal options reduced from two 36-month terms to one 24-month term",
            "Subletting consent changed from 'not unreasonably withheld' to 'sole discretion'",
            "Landlord removed obligation to mitigate damages upon default",
        ],
    },
    2: {
        "changes": [
            {"index": 0, "impact": "unfavorable"},
            {"index": 1, "impact": "unfavorable"},
            {"index": 2, "impact": "unfavorable"},
            {"index": 3, "impact": "unfavorable"},
            {"index": 4, "impact": "unfavorable"},
        ],
        "summary": [
            "Partnership structure changed from equal to SynergyWorks-dominated",
            "NovaTech's financial contribution doubled while SynergyWorks' decreased",
            "Revenue split shifted from 50/50 to 55/45 in favor of SynergyWorks",
            "Joint IP ownership transferred entirely to SynergyWorks",
            "Governance changed to give SynergyWorks majority control",
        ],
    },
}

hard_scores = []

for ci, spec in COMPARISON_MAP.items():
    try:
        r = client.post("/reset", json={"task_id": "contract_comparison", "contract_index": ci})
        obs = r.json()

        for change in spec["changes"]:
            # Navigate to section
            while obs.get("current_section_index", 0) < change["index"]:
                r = client.post("/step", json={"action_type": "next_section", "confidence": 1.0})
                obs = r.json().get("observation", obs)

            # Step 1: detect_change → clause_index + clause_type
            r = client.post("/step", json={
                "action_type": "detect_change",
                "clause_index": change["index"],
                "clause_type": "modified",
                "confidence": 1.0,
            })
            obs = r.json().get("observation", obs)

            # Step 2: assess_impact → clause_index + impact
            r = client.post("/step", json={
                "action_type": "assess_impact",
                "clause_index": change["index"],
                "impact": change["impact"],
                "confidence": 1.0,
            })
            obs = r.json().get("observation", obs)

            # Step 3: suggest_amendment for unfavorable changes
            if change["impact"] == "unfavorable":
                kws = AMENDMENT_KW.get((ci, change["index"]), [])
                amendment = f"Restore original terms. Key: {', '.join(kws)}"
                r = client.post("/step", json={
                    "action_type": "suggest_amendment",
                    "clause_index": change["index"],
                    "amendment_text": amendment,
                    "confidence": 1.0,
                })
                obs = r.json().get("observation", obs)

        # Summary points using generate_summary action
        for sp in spec["summary"]:
            r = client.post("/step", json={
                "action_type": "generate_summary",
                "summary_text": sp,
                "confidence": 1.0,
            })
            obs = r.json().get("observation", obs)

        # Submit
        r = client.post("/step", json={"action_type": "submit", "confidence": 1.0})

        score = client.get("/grader").json().get("score", 0.0)
        hard_scores.append(score)
        log("PASS" if score >= 0.5 else ("WARN" if score >= 0.2 else "FAIL"), f"hard/c{ci}", f"Score: {score:.4f}")

    except Exception as e:
        log("FAIL", f"hard/c{ci}", f"Exception: {e}")
        traceback.print_exc()
        hard_scores.append(0.0)

avg_hard = sum(hard_scores) / len(hard_scores) if hard_scores else 0.0
log("INFO", "hard_avg", f"Average hard score: {avg_hard:.4f}")


# ======================================================================
# 5. EDGE CASE & ERROR HANDLING TESTS
# ======================================================================
section("5. EDGE CASES & ERROR HANDLING")

# 5.1 Invalid task_id
try:
    r = client.post("/reset", json={"task_id": "nonexistent_task", "contract_index": 0})
    log("PASS" if r.status_code in [400, 422] else "FAIL", "invalid_task", f"Status: {r.status_code}")
except Exception as e:
    log("FAIL", "invalid_task", f"Exception: {e}")

# 5.2 Out-of-range contract_index
try:
    r = client.post("/reset", json={"task_id": "clause_identification", "contract_index": 999})
    log("PASS" if r.status_code in [400, 422] else "FAIL", "invalid_index", f"Status: {r.status_code}")
except Exception as e:
    log("FAIL", "invalid_index", f"Exception: {e}")

# 5.3 Invalid action_type
try:
    client.post("/reset", json={"task_id": "clause_identification", "contract_index": 0})
    r = client.post("/step", json={"action_type": "destroy_contract", "confidence": 1.0})
    if r.status_code in [400, 422]:
        log("PASS", "invalid_action", f"Rejected invalid action: {r.status_code}")
    elif r.status_code == 200 and r.json().get("reward", 0) <= 0:
        log("PASS", "invalid_action", f"Invalid action handled gracefully")
    else:
        log("FAIL", "invalid_action", f"Unexpected: {r.status_code}")
except Exception as e:
    log("FAIL", "invalid_action", f"Exception: {e}")

# 5.4 Empty action body
try:
    r = client.post("/step", json={})
    log("PASS" if r.status_code in [400, 422] else "WARN", "empty_action", f"Status: {r.status_code}")
except Exception as e:
    log("FAIL", "empty_action", f"Exception: {e}")

# 5.5 Negative contract index
try:
    r = client.post("/reset", json={"task_id": "clause_identification", "contract_index": -1})
    log("PASS" if r.status_code in [400, 422] else "WARN", "neg_index", f"Status: {r.status_code}")
except Exception as e:
    log("FAIL", "neg_index", f"Exception: {e}")

# 5.6 Semantic alias test
try:
    client.post("/reset", json={"task_id": "clause_identification", "contract_index": 0})
    r = client.post("/step", json={"action_type": "identify_clause", "clause_index": 0, "clause_type": "duties", "confidence": 1.0})
    step = r.json()
    log("PASS" if step.get("reward", 0) > 0 else "WARN", "semantic_match", f"Reward: {step.get('reward')}")
except Exception as e:
    log("FAIL", "semantic_match", f"Exception: {e}")

# 5.7 Wrong clause type
try:
    client.post("/reset", json={"task_id": "clause_identification", "contract_index": 0})
    r = client.post("/step", json={"action_type": "identify_clause", "clause_index": 0, "clause_type": "banana_clause", "confidence": 1.0})
    step = r.json()
    log("PASS" if step.get("reward", 0) <= 0 else "FAIL", "wrong_clause", f"Reward: {step.get('reward')}")
except Exception as e:
    log("FAIL", "wrong_clause", f"Exception: {e}")

# 5.8 Grader returns 0 before any steps
try:
    client.post("/reset", json={"task_id": "clause_identification", "contract_index": 0})
    score = client.get("/grader").json().get("score", -1)
    log("PASS" if score == 0.0 else "WARN", "grader_no_steps", f"Score: {score}")
except Exception as e:
    log("FAIL", "grader_no_steps", f"Exception: {e}")

# 5.9 Redundant action penalty
try:
    client.post("/reset", json={"task_id": "clause_identification", "contract_index": 0})
    client.post("/step", json={"action_type": "identify_clause", "clause_index": 0, "clause_type": "position", "confidence": 1.0})
    r = client.post("/step", json={"action_type": "identify_clause", "clause_index": 0, "clause_type": "position", "confidence": 1.0})
    step = r.json()
    log("PASS" if step.get("reward", 0) < 0 else "WARN", "redundant_penalty", f"Reward: {step.get('reward')}")
except Exception as e:
    log("FAIL", "redundant_penalty", f"Exception: {e}")

# 5.10 Episode completion check
try:
    client.post("/reset", json={"task_id": "clause_identification", "contract_index": 0})
    r = client.post("/step", json={"action_type": "submit", "confidence": 1.0})
    step = r.json()
    if step.get("done", False):
        log("PASS", "submit_done", "Submit correctly ends episode")
    else:
        log("FAIL", "submit_done", "Submit did not end episode")
except Exception as e:
    log("FAIL", "submit_done", f"Exception: {e}")

# 5.11 Step after done
try:
    r = client.post("/step", json={"action_type": "next_section", "confidence": 1.0})
    step = r.json()
    if step.get("done", False) and step.get("reward", -1) == 0.0:
        log("PASS", "step_after_done", "Returns done=True, reward=0.0 after episode ends")
    else:
        log("WARN", "step_after_done", f"done={step.get('done')}, reward={step.get('reward')}")
except Exception as e:
    log("FAIL", "step_after_done", f"Exception: {e}")


# ======================================================================
# 6. RAPID-FIRE LOAD TEST
# ======================================================================
section("6. RAPID-FIRE LOAD TEST")

try:
    client.post("/reset", json={"task_id": "clause_identification", "contract_index": 0})
    start = time.time()
    successes = 0
    for i in range(20):
        r = client.post("/step", json={"action_type": "identify_clause", "clause_index": 0, "clause_type": "position", "confidence": 1.0})
        if r.status_code == 200:
            successes += 1
    elapsed = time.time() - start
    log("PASS" if successes == 20 else "WARN", "load_test", f"{successes}/20 in {elapsed:.2f}s ({20/elapsed:.1f} req/s)")
except Exception as e:
    log("FAIL", "load_test", f"Exception: {e}")


# ======================================================================
# 7. LATENCY BENCHMARK
# ======================================================================
section("7. LATENCY BENCHMARK")

for endpoint in ["/health", "/tasks", "/state", "/grader"]:
    try:
        start = time.time()
        r = client.get(endpoint)
        elapsed = time.time() - start
        log("PASS" if elapsed < 2.0 else "WARN", f"latency{endpoint}", f"{elapsed*1000:.0f}ms")
    except Exception as e:
        log("FAIL", f"latency{endpoint}", f"Error: {e}")

client.close()


# ======================================================================
# FINAL SUMMARY
# ======================================================================
section("FINAL SUMMARY")

pass_count = sum(1 for r in results if r["level"] == "PASS")
fail_count = sum(1 for r in results if r["level"] == "FAIL")
warn_count = sum(1 for r in results if r["level"] == "WARN")
total_tests = pass_count + fail_count + warn_count

print(f"\n  Total tests: {total_tests}")
print(f"  ✅ PASS: {pass_count}")
print(f"  ❌ FAIL: {fail_count}")
print(f"  ⚠️  WARN: {warn_count}")
print(f"\n  Easy avg:   {avg_easy:.4f}")
print(f"  Medium avg: {avg_medium:.4f}")
print(f"  Hard avg:   {avg_hard:.4f}")
overall = (avg_easy + avg_medium + avg_hard) / 3
print(f"  Overall:    {overall:.4f}")

with open("stress_test_results.json", "w") as f:
    json.dump({
        "results": results,
        "scores": {
            "easy_scores": easy_scores, "medium_scores": medium_scores, "hard_scores": hard_scores,
            "avg_easy": avg_easy, "avg_medium": avg_medium, "avg_hard": avg_hard, "overall": overall,
        },
        "summary": {"total_tests": total_tests, "pass": pass_count, "fail": fail_count, "warn": warn_count},
    }, f, indent=2)
print(f"\n  Results saved to stress_test_results.json")
