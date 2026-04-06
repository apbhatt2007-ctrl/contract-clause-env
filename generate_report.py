#!/usr/bin/env python3
"""
Generate a comprehensive test report for the Contract Clause Env project.
Outputs: RESULTS.md — a detailed markdown file with scores, ratings, and diagnostics.

Usage:
    1. Start server:  python -m uvicorn server.app:app --port 7860
    2. Run report:    python generate_report.py
"""

import io
import json
import os
import subprocess
import sys
import time
import platform
from datetime import datetime

# Force UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import httpx

ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")
HF_SPACE_URL = "https://atharva4-openenvhackathon.hf.space"
TASK_IDS = ["clause_identification", "risk_flagging", "contract_comparison"]
TASK_META = {
    "clause_identification": {"name": "Clause Identification", "difficulty": "Easy", "emoji": "🟢", "max_steps": 10},
    "risk_flagging":         {"name": "Risk Flagging & Analysis", "difficulty": "Medium", "emoji": "🟡", "max_steps": 25},
    "contract_comparison":   {"name": "Contract Comparison & Redlining", "difficulty": "Hard", "emoji": "🔴", "max_steps": 50},
}

# ── Helpers ───────────────────────────────────────────────────────

def rating_stars(score: float) -> str:
    """Convert 0-1 score to a 5-star rating."""
    stars = round(score * 5)
    return "★" * stars + "☆" * (5 - stars)

def rating_label(score: float) -> str:
    if score >= 0.8: return "Excellent"
    if score >= 0.6: return "Good"
    if score >= 0.4: return "Fair"
    if score >= 0.2: return "Needs Work"
    return "Poor"

def grade_letter(score: float) -> str:
    if score >= 0.9: return "A+"
    if score >= 0.8: return "A"
    if score >= 0.7: return "B+"
    if score >= 0.6: return "B"
    if score >= 0.5: return "C+"
    if score >= 0.4: return "C"
    if score >= 0.3: return "D"
    return "F"

def check_endpoint(client, method, path, json_data=None):
    """Test an endpoint and return (status_code, response_time_ms, body_preview)."""
    start = time.time()
    try:
        if method == "GET":
            r = client.get(path, timeout=15)
        else:
            r = client.post(path, json=json_data or {}, timeout=15)
        elapsed = (time.time() - start) * 1000
        body = r.text[:200]
        return r.status_code, round(elapsed, 1), body
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        return 0, round(elapsed, 1), str(e)[:200]

def run_inference_task(task_id: str) -> dict:
    """Run a single task with rule-based mode and capture full details."""
    result = subprocess.run(
        [sys.executable, "inference.py", "--mode", "rule", "--task", task_id, "--verbose"],
        capture_output=True, text=True, timeout=120, encoding="utf-8", errors="replace",
    )
    stdout = result.stdout
    lines = stdout.splitlines()

    start_lines = [l for l in lines if l.strip().startswith("[START]")]
    step_lines  = [l for l in lines if l.strip().startswith("[STEP]")]
    end_lines   = [l for l in lines if l.strip().startswith("[END]")]

    # Parse steps
    steps_detail = []
    for line in step_lines:
        try:
            tag_end = line.index("]") + 1
            data = json.loads(line[tag_end:].strip())
            steps_detail.append(data)
        except Exception:
            steps_detail.append({"raw": line[:120]})

    # Parse score
    score = 0.0
    total_steps = 0
    for line in end_lines:
        try:
            tag_end = line.index("]") + 1
            data = json.loads(line[tag_end:].strip())
            score = data.get("score", 0.0)
            total_steps = data.get("steps", 0)
        except Exception:
            pass

    # Validate JSON in all log lines
    json_valid = 0
    json_invalid = 0
    for line in start_lines + step_lines + end_lines:
        try:
            tag_end = line.index("]") + 1
            json.loads(line[tag_end:].strip())
            json_valid += 1
        except Exception:
            json_invalid += 1

    return {
        "task_id": task_id,
        "score": score,
        "steps": total_steps,
        "steps_detail": steps_detail,
        "start_count": len(start_lines),
        "step_count": len(step_lines),
        "end_count": len(end_lines),
        "json_valid": json_valid,
        "json_invalid": json_invalid,
        "exit_code": result.returncode,
        "stdout": stdout,
        "stderr": result.stderr,
    }


# ── Main Report Generator ────────────────────────────────────────

def main():
    print("Generating comprehensive test report...")
    print(f"Server: {ENV_BASE_URL}")

    report_lines = []
    def w(line=""):
        report_lines.append(line)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")

    # ═══════════════════════════════════════════════════════════════
    # HEADER
    # ═══════════════════════════════════════════════════════════════
    w("# Contract Clause Env — Comprehensive Test Report")
    w()
    w(f"> **Generated:** {timestamp}  ")
    w(f"> **Machine:** {platform.node()} ({platform.system()} {platform.release()})  ")
    w(f"> **Python:** {platform.python_version()}  ")
    w(f"> **Server:** `{ENV_BASE_URL}`  ")
    w(f"> **HF Space:** `{HF_SPACE_URL}`")
    w()
    w("---")
    w()

    # ═══════════════════════════════════════════════════════════════
    # SECTION 1: FILE STRUCTURE
    # ═══════════════════════════════════════════════════════════════
    w("## 1. Project Structure Validation")
    w()
    required_files = {
        "inference.py": "Main inference script (entry point for the hackathon grader)",
        "openenv.yaml": "OpenEnv manifest — declares tasks, endpoints, docker config",
        "Dockerfile": "Container definition for HuggingFace Spaces deployment",
        "requirements.txt": "Python dependencies",
        "server/app.py": "FastAPI server — provides /reset, /step, /state, /grader endpoints",
        "server/environment.py": "Core RL environment logic, grading, contract data",
        "models.py": "Pydantic models for ContractAction, TaskDefinition, etc.",
        "data/contracts_easy.py": "Contract dataset for clause_identification (Easy)",
        "data/contracts_medium.py": "Contract dataset for risk_flagging (Medium)",
        "data/contracts_hard.py": "Contract dataset for contract_comparison (Hard)",
    }
    w("| File | Status | Description |")
    w("|------|--------|-------------|")
    all_files_ok = True
    for f, desc in required_files.items():
        exists = os.path.isfile(f)
        status = "✅ Present" if exists else "❌ Missing"
        if not exists:
            all_files_ok = False
        size = ""
        if exists:
            sz = os.path.getsize(f)
            size = f" ({sz:,} bytes)"
        w(f"| `{f}` | {status}{size} | {desc} |")
    w()
    w(f"**Result:** {'✅ All required files present' if all_files_ok else '❌ Some files missing'}")
    w()
    w("---")
    w()

    # ═══════════════════════════════════════════════════════════════
    # SECTION 2: OPENENV.YAML VALIDATION
    # ═══════════════════════════════════════════════════════════════
    w("## 2. OpenEnv Configuration (`openenv.yaml`)")
    w()
    with open("openenv.yaml", "r") as f:
        yaml_content = f.read()

    yaml_checks = [
        ("inference_script: inference.py", "inference_script" in yaml_content and "inference.py" in yaml_content),
        ("Tasks section defined", "tasks:" in yaml_content),
        ("clause_identification task", "clause_identification" in yaml_content),
        ("risk_flagging task", "risk_flagging" in yaml_content),
        ("contract_comparison task", "contract_comparison" in yaml_content),
        ("Docker section defined", "docker:" in yaml_content),
        ("Dockerfile referenced", "Dockerfile" in yaml_content),
        ("Port 7860 configured", "7860" in yaml_content),
        ("HF Space URL present", "hf_space_url" in yaml_content),
        ("Server entrypoint defined", "server/app.py" in yaml_content),
    ]
    w("| Check | Status |")
    w("|-------|--------|")
    yaml_pass = 0
    for label, ok in yaml_checks:
        w(f"| {label} | {'✅ Pass' if ok else '❌ Fail'} |")
        if ok:
            yaml_pass += 1
    w()
    w(f"**Result:** {yaml_pass}/{len(yaml_checks)} checks passed")
    w()
    w("---")
    w()

    # ═══════════════════════════════════════════════════════════════
    # SECTION 3: ENDPOINT TESTING
    # ═══════════════════════════════════════════════════════════════
    w("## 3. API Endpoint Testing")
    w()
    print("  Testing endpoints...")
    endpoints = [
        ("GET",  "/health", None),
        ("GET",  "/tasks", None),
        ("GET",  "/", None),
        ("POST", "/reset", {"task_id": "clause_identification", "contract_index": 0}),
        ("GET",  "/state", None),
        ("POST", "/step", {"action_type": "next_section"}),
        ("GET",  "/grader", None),
        ("GET",  "/baseline", None),
    ]
    w("| Method | Endpoint | Status | Response Time | Response Preview |")
    w("|--------|----------|--------|---------------|------------------|")
    ep_pass = 0
    with httpx.Client(base_url=ENV_BASE_URL, timeout=15) as client:
        for method, path, body in endpoints:
            code, ms, preview = check_endpoint(client, method, path, body)
            ok = code in (200, 400, 422)
            status = f"✅ {code}" if ok else f"❌ {code}"
            if ok:
                ep_pass += 1
            # Escape pipe chars in preview
            preview_safe = preview.replace("|", "\\|").replace("\n", " ")[:80]
            w(f"| {method} | `{path}` | {status} | {ms}ms | `{preview_safe}` |")

    w()
    w(f"**Result:** {ep_pass}/{len(endpoints)} endpoints responding correctly")
    w()
    w("---")
    w()

    # ═══════════════════════════════════════════════════════════════
    # SECTION 4: INFERENCE EXECUTION (per-task detail)
    # ═══════════════════════════════════════════════════════════════
    w("## 4. Inference Execution — Detailed Per-Task Results")
    w()

    task_results = []
    for tid in TASK_IDS:
        print(f"  Running task: {tid}...")
        result = run_inference_task(tid)
        task_results.append(result)

    for result in task_results:
        tid = result["task_id"]
        meta = TASK_META[tid]
        score = result["score"]
        steps = result["steps"]

        w(f"### {meta['emoji']} {meta['name']} (`{tid}`)")
        w()
        w(f"| Metric | Value |")
        w(f"|--------|-------|")
        w(f"| Difficulty | **{meta['difficulty']}** |")
        w(f"| Score | **{score:.4f}** / 1.0 |")
        w(f"| Grade | **{grade_letter(score)}** |")
        w(f"| Rating | {rating_stars(score)} ({rating_label(score)}) |")
        w(f"| Steps Used | {steps} / {meta['max_steps']} |")
        w(f"| Step Efficiency | {(steps / meta['max_steps'] * 100):.0f}% of budget used |")
        w(f"| Exit Code | {result['exit_code']} |")
        w(f"| [START] lines | {result['start_count']} |")
        w(f"| [STEP] lines | {result['step_count']} |")
        w(f"| [END] lines | {result['end_count']} |")
        w(f"| JSON Valid | {result['json_valid']} |")
        w(f"| JSON Invalid | {result['json_invalid']} |")
        w()

        # Step-by-step breakdown
        if result["steps_detail"]:
            w("<details>")
            w(f"<summary>Step-by-Step Breakdown ({len(result['steps_detail'])} steps)</summary>")
            w()
            w("| Step | Action | Reward | Section | Feedback | Reasoning |")
            w("|------|--------|--------|---------|----------|-----------|")
            for sd in result["steps_detail"]:
                step_num = sd.get("step", "?")
                action = sd.get("action", {})
                atype = action.get("action_type", "?")
                ctype = action.get("clause_type", "")
                action_str = f"`{atype}`"
                if ctype:
                    action_str += f" ({ctype})"
                reward = sd.get("reward", 0.0)
                reward_str = f"{reward:+.3f}" if reward != 0 else "0.000"
                obs = sd.get("obs", {})
                sec_idx = obs.get("section_index", "-")
                sec_head = obs.get("section_heading", "")[:30].replace("|", "/")
                feedback = (obs.get("system_feedback", "") or "")[:40].replace("|", "/")
                reasoning = (sd.get("reasoning", "") or "")[:40].replace("|", "/")
                w(f"| {step_num} | {action_str} | {reward_str} | {sec_idx}: {sec_head} | {feedback} | {reasoning} |")
            w()
            w("</details>")
            w()

    w("---")
    w()

    # ═══════════════════════════════════════════════════════════════
    # SECTION 5: SCORE SUMMARY & OVERALL RATING
    # ═══════════════════════════════════════════════════════════════
    w("## 5. Overall Score Summary")
    w()

    scores = {r["task_id"]: r["score"] for r in task_results}
    total_score = sum(scores.values())
    avg_score = total_score / len(scores) if scores else 0

    w("### Score Table")
    w()
    w("| Task | Difficulty | Score | Grade | Rating | Stars |")
    w("|------|-----------|-------|-------|--------|-------|")
    for tid in TASK_IDS:
        meta = TASK_META[tid]
        s = scores.get(tid, 0.0)
        w(f"| {meta['name']} | {meta['emoji']} {meta['difficulty']} | **{s:.4f}** | {grade_letter(s)} | {rating_label(s)} | {rating_stars(s)} |")
    w(f"| **TOTAL** | | **{total_score:.4f} / 3.0** | **{grade_letter(avg_score)}** | **{rating_label(avg_score)}** | {rating_stars(avg_score)} |")
    w()

    # Visual bar chart
    w("### Score Visualization")
    w()
    w("```")
    for tid in TASK_IDS:
        meta = TASK_META[tid]
        s = scores.get(tid, 0.0)
        bar_len = int(s * 40)
        bar = "█" * bar_len + "░" * (40 - bar_len)
        w(f"  {meta['name'][:25]:<25} |{bar}| {s:.4f}")
    w()
    total_bar_len = int((total_score / 3.0) * 40)
    total_bar = "█" * total_bar_len + "░" * (40 - total_bar_len)
    w(f"  {'OVERALL':<25} |{total_bar}| {total_score:.4f}/3.0")
    w("```")
    w()
    w("---")
    w()

    # ═══════════════════════════════════════════════════════════════
    # SECTION 6: LOGGING FORMAT VALIDATION
    # ═══════════════════════════════════════════════════════════════
    w("## 6. Logging Format Compliance")
    w()
    w("The OpenEnv validator requires strict `[START]`, `[STEP]`, `[END]` logging with valid JSON payloads.")
    w()
    total_valid = sum(r["json_valid"] for r in task_results)
    total_invalid = sum(r["json_invalid"] for r in task_results)
    w("| Task | [START] | [STEP] | [END] | JSON Valid | JSON Invalid |")
    w("|------|---------|--------|-------|------------|--------------|")
    for r in task_results:
        tid = r["task_id"]
        w(f"| `{tid}` | {r['start_count']} | {r['step_count']} | {r['end_count']} | {r['json_valid']} | {r['json_invalid']} |")
    w(f"| **Total** | {sum(r['start_count'] for r in task_results)} | {sum(r['step_count'] for r in task_results)} | {sum(r['end_count'] for r in task_results)} | **{total_valid}** | **{total_invalid}** |")
    w()
    if total_invalid == 0:
        w("**Result:** ✅ All log lines contain valid JSON — compliant with OpenEnv validator")
    else:
        w(f"**Result:** ❌ {total_invalid} log lines with invalid JSON — NEEDS FIX before submission")
    w()
    w("---")
    w()

    # ═══════════════════════════════════════════════════════════════
    # SECTION 7: DOCKERFILE VALIDATION
    # ═══════════════════════════════════════════════════════════════
    w("## 7. Docker Configuration")
    w()
    with open("Dockerfile", "r") as f:
        dockerfile = f.read()
    w("### Dockerfile Contents")
    w("```dockerfile")
    w(dockerfile.strip())
    w("```")
    w()
    docker_checks = [
        ("Base image (python:3.11-slim)", "python:3.11" in dockerfile),
        ("WORKDIR /app", "WORKDIR" in dockerfile),
        ("COPY requirements.txt", "requirements.txt" in dockerfile),
        ("pip install", "pip install" in dockerfile),
        ("COPY . .", "COPY . ." in dockerfile),
        ("EXPOSE 7860", "7860" in dockerfile),
        ("CMD with uvicorn", "uvicorn" in dockerfile),
    ]
    w("| Check | Status |")
    w("|-------|--------|")
    docker_pass = 0
    for label, ok in docker_checks:
        w(f"| {label} | {'✅ Pass' if ok else '❌ Fail'} |")
        if ok:
            docker_pass += 1
    w()
    w(f"**Result:** {docker_pass}/{len(docker_checks)} checks passed")
    w()

    # Check if Docker image exists
    try:
        dr = subprocess.run(
            ["docker", "images", "contract-clause-env", "--format", "{{.Size}} {{.CreatedAt}}"],
            capture_output=True, text=True, timeout=10
        )
        if dr.stdout.strip():
            w(f"**Docker Image:** Built — {dr.stdout.strip()}")
        else:
            w("**Docker Image:** Not built locally (run `docker build -t contract-clause-env .`)")
    except Exception:
        w("**Docker Image:** Docker not available on this machine")
    w()
    w("---")
    w()

    # ═══════════════════════════════════════════════════════════════
    # SECTION 8: HUGGING FACE SPACE
    # ═══════════════════════════════════════════════════════════════
    w("## 8. HuggingFace Space Status")
    w()
    print("  Checking HuggingFace Space...")
    hf_checks = {}
    try:
        r = httpx.get(f"{HF_SPACE_URL}/health", timeout=15)
        hf_checks["health"] = (r.status_code == 200, r.text[:100])
    except Exception as e:
        hf_checks["health"] = (False, str(e)[:100])

    try:
        r = httpx.get(f"{HF_SPACE_URL}/tasks", timeout=15)
        hf_checks["tasks"] = (r.status_code == 200, r.text[:200])
    except Exception as e:
        hf_checks["tasks"] = (False, str(e)[:100])

    try:
        r = httpx.get(f"{HF_SPACE_URL}/", timeout=15)
        hf_checks["root"] = (r.status_code == 200, r.text[:200])
    except Exception as e:
        hf_checks["root"] = (False, str(e)[:100])

    w(f"**Space URL:** [{HF_SPACE_URL}]({HF_SPACE_URL})")
    w()
    w("| Endpoint | Status | Response |")
    w("|----------|--------|----------|")
    hf_pass = 0
    for ep, (ok, body) in hf_checks.items():
        status = "✅ Live" if ok else "❌ Down"
        body_safe = body.replace("|", "\\|").replace("\n", " ")[:80]
        w(f"| `/{ep}` | {status} | `{body_safe}` |")
        if ok:
            hf_pass += 1
    w()
    w(f"**Result:** {hf_pass}/{len(hf_checks)} endpoints reachable on HuggingFace Space")
    w()
    w("---")
    w()

    # ═══════════════════════════════════════════════════════════════
    # SECTION 9: REQUIREMENTS VALIDATION
    # ═══════════════════════════════════════════════════════════════
    w("## 9. Dependencies (`requirements.txt`)")
    w()
    with open("requirements.txt", "r") as f:
        req_lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    w("| Package | Specified Version | Purpose |")
    w("|---------|------------------|---------|")
    pkg_purposes = {
        "openai": "OpenAI SDK for LLM inference",
        "httpx": "HTTP client for environment API calls",
        "python-dotenv": "Load .env files for local development",
        "pydantic": "Data validation and Pydantic models",
        "uvicorn": "ASGI server for FastAPI",
        "fastapi": "Web framework for the environment server",
        "websockets": "WebSocket support for real-time interface",
    }
    for req in req_lines:
        name = req.split(">=")[0].split("==")[0].split(">")[0].split("<")[0].strip()
        purpose = pkg_purposes.get(name, "")
        w(f"| `{name}` | `{req}` | {purpose} |")
    w()
    w("---")
    w()

    # ═══════════════════════════════════════════════════════════════
    # SECTION 10: GIT STATUS
    # ═══════════════════════════════════════════════════════════════
    w("## 10. Git Repository Status")
    w()
    try:
        gr = subprocess.run(["git", "log", "-5", "--oneline"], capture_output=True, text=True, timeout=10)
        w("### Recent Commits")
        w("```")
        w(gr.stdout.strip())
        w("```")
        w()
    except Exception:
        w("Git log unavailable.")
        w()

    try:
        gs = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, timeout=10)
        status_out = gs.stdout.strip()
        if status_out:
            w("### Uncommitted Changes")
            w("```")
            w(status_out)
            w("```")
            w()
            w("> ⚠️ **Warning:** Commit and push these changes before submitting!")
        else:
            w("✅ Working tree is clean — all changes committed.")
    except Exception:
        w("Git status unavailable.")
    w()
    try:
        gb = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True, timeout=10)
        remote_out = gb.stdout.strip()
        # Redact any embedded tokens/passwords in URLs
        import re as _re
        remote_out = _re.sub(r'://[^@]+@', '://', remote_out)
        w("### Remote")
        w("```")
        w(remote_out)
        w("```")

    except Exception:
        pass
    w()
    w("---")
    w()

    # ═══════════════════════════════════════════════════════════════
    # SECTION 11: FINAL VERDICTS
    # ═══════════════════════════════════════════════════════════════
    w("## 11. Final Verdict & Submission Readiness")
    w()

    verdicts = [
        ("Project Files", all_files_ok),
        ("OpenEnv Config", yaml_pass == len(yaml_checks)),
        ("API Endpoints", ep_pass >= 6),
        ("Inference Execution", all(r["exit_code"] == 0 for r in task_results)),
        ("Logging Compliance", total_invalid == 0),
        ("Docker Config", docker_pass >= 5),
        ("HuggingFace Space", hf_pass >= 2),
        (f"Score > 0 on all tasks", all(r["score"] > 0 for r in task_results)),
    ]

    w("| Category | Status | Details |")
    w("|----------|--------|---------|")
    all_pass = True
    for label, ok in verdicts:
        status = "✅ PASS" if ok else "❌ FAIL"
        if not ok:
            all_pass = False
        w(f"| {label} | {status} | |")
    w()

    passed_count = sum(1 for _, ok in verdicts if ok)
    w(f"### Overall: {passed_count}/{len(verdicts)} categories passed")
    w()

    if all_pass:
        w("```")
        w("  ╔══════════════════════════════════════════════════╗")
        w("  ║                                                  ║")
        w("  ║   ✅  ALL CHECKS PASSED — READY TO SUBMIT! ✅   ║")
        w("  ║                                                  ║")
        w("  ╚══════════════════════════════════════════════════╝")
        w("```")
    else:
        w("```")
        w("  ╔══════════════════════════════════════════════════╗")
        w("  ║                                                  ║")
        w("  ║  ⚠️  SOME CHECKS FAILED — FIX BEFORE SUBMIT ⚠️  ║")
        w("  ║                                                  ║")
        w("  ╚══════════════════════════════════════════════════╝")
        w("```")
    w()
    w(f"**Total Score: {total_score:.4f} / 3.0 ({avg_score*100:.1f}%)**  ")
    w(f"**Overall Grade: {grade_letter(avg_score)}**  ")
    w(f"**Overall Rating: {rating_stars(avg_score)} ({rating_label(avg_score)})**")
    w()
    w("---")
    w()
    w(f"*Report generated by `generate_report.py` at {timestamp}*")

    # ── Write to file ──
    report_content = "\n".join(report_lines)
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "RESULTS.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"\n  Report saved to: {output_path}")
    print(f"  Total Score: {total_score:.4f} / 3.0")
    print(f"  Grade: {grade_letter(avg_score)}")
    print(f"  Verdict: {'READY TO SUBMIT' if all_pass else 'NEEDS FIXES'}")


if __name__ == "__main__":
    main()
