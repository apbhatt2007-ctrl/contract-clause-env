#!/usr/bin/env python3
"""Pre-submission validator for OpenEnv Contract Clause Env.

Runs all validation checks locally before pushing to GitHub/HuggingFace.
Usage: python test_presubmit.py
"""

import io
import json
import os
import re
import subprocess
import sys
import time

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import httpx

ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")
REQUIRED_FILES = ["inference.py", "openenv.yaml", "Dockerfile", "requirements.txt"]
REQUIRED_ENDPOINTS = ["/health", "/tasks", "/reset", "/state", "/grader"]
TASK_IDS = ["clause_identification", "risk_flagging", "contract_comparison"]

PASS = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"


def header(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def check(label: str, ok: bool, detail: str = ""):
    status = PASS if ok else FAIL
    print(f"  {status}  {label}")
    if detail and not ok:
        print(f"         → {detail}")
    return ok


# ─── Check 1: Required files exist ───────────────────────────────
def check_files() -> bool:
    header("Check 1: Required Files")
    all_ok = True
    for f in REQUIRED_FILES:
        exists = os.path.isfile(f)
        all_ok &= check(f"File exists: {f}", exists)
    return all_ok


# ─── Check 2: openenv.yaml structure ─────────────────────────────
def check_openenv_yaml() -> bool:
    header("Check 2: openenv.yaml Validation")
    try:
        import yaml
    except ImportError:
        # Fallback: just check the file is readable and has key fields
        with open("openenv.yaml", "r") as f:
            content = f.read()
        has_inference = "inference_script" in content
        has_tasks = "tasks:" in content
        has_docker = "docker:" in content
        ok = has_inference and has_tasks and has_docker
        check("Contains inference_script", has_inference)
        check("Contains tasks section", has_tasks)
        check("Contains docker section", has_docker)
        return ok

    with open("openenv.yaml", "r") as f:
        cfg = yaml.safe_load(f)

    ok = True
    ok &= check("inference_script defined",
                 cfg.get("inference_script") == "inference.py",
                 f"Got: {cfg.get('inference_script')}")
    ok &= check("tasks section present",
                 isinstance(cfg.get("tasks"), list) and len(cfg["tasks"]) >= 3,
                 f"Expected >=3 tasks, got {len(cfg.get('tasks', []))}")
    ok &= check("docker section present",
                 cfg.get("docker", {}).get("dockerfile") == "Dockerfile")
    return ok


# ─── Check 3: Server health ──────────────────────────────────────
def check_server_health() -> bool:
    header("Check 3: Server Health")
    try:
        resp = httpx.get(f"{ENV_BASE_URL}/health", timeout=10)
        data = resp.json()
        return check("/health responds",
                      resp.status_code == 200 and data.get("status") == "ok",
                      f"Status: {resp.status_code}, Body: {data}")
    except Exception as e:
        return check("/health responds", False,
                      f"Server unreachable: {e}")


# ─── Check 4: All endpoints respond ──────────────────────────────
def check_endpoints() -> bool:
    header("Check 4: Endpoint Availability")
    all_ok = True
    with httpx.Client(timeout=15, base_url=ENV_BASE_URL) as client:
        for ep in ["/health", "/tasks"]:
            try:
                r = client.get(ep)
                all_ok &= check(f"GET {ep} → {r.status_code}", r.status_code == 200)
            except Exception as e:
                all_ok &= check(f"GET {ep}", False, str(e))

        # /reset (POST)
        try:
            r = client.post("/reset", json={"task_id": "clause_identification", "contract_index": 0})
            all_ok &= check(f"POST /reset → {r.status_code}", r.status_code == 200)
        except Exception as e:
            all_ok &= check("POST /reset", False, str(e))

        # /state (GET)
        try:
            r = client.get("/state")
            all_ok &= check(f"GET /state → {r.status_code}", r.status_code == 200)
        except Exception as e:
            all_ok &= check("GET /state", False, str(e))

        # /step (POST) with a simple action
        try:
            r = client.post("/step", json={"action_type": "next_section"})
            all_ok &= check(f"POST /step → {r.status_code}",
                            r.status_code in (200, 400, 422))
        except Exception as e:
            all_ok &= check("POST /step", False, str(e))

        # /grader (GET)
        try:
            r = client.get("/grader")
            all_ok &= check(f"GET /grader → {r.status_code}", r.status_code == 200)
            if r.status_code == 200:
                data = r.json()
                all_ok &= check("  /grader returns 'score' field",
                                "score" in data, f"Body: {data}")
        except Exception as e:
            all_ok &= check("GET /grader", False, str(e))

    return all_ok


# ─── Check 5: Tasks list ─────────────────────────────────────────
def check_tasks_list() -> bool:
    header("Check 5: Tasks Configuration")
    try:
        resp = httpx.get(f"{ENV_BASE_URL}/tasks", timeout=10)
        tasks = resp.json()
        all_ok = check("/tasks returns a list", isinstance(tasks, list))
        task_ids = [t.get("task_id") for t in tasks]
        for tid in TASK_IDS:
            all_ok &= check(f"  Task '{tid}' present", tid in task_ids)
        return all_ok
    except Exception as e:
        return check("/tasks endpoint", False, str(e))


# ─── Check 6: Run inference (rule-based) & validate logging ──────
def check_inference_run() -> bool:
    header("Check 6: Inference Script (rule-based, all tasks)")
    print("  Running: python inference.py --mode rule ...")

    try:
        result = subprocess.run(
            [sys.executable, "inference.py", "--mode", "rule"],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return check("Inference completed within 120s", False, "Timeout!")

    stdout = result.stdout
    stderr = result.stderr
    exit_code = result.returncode

    print(f"  Exit code: {exit_code}")

    all_ok = check("Exit code is 0", exit_code == 0,
                    f"Exit code={exit_code}, stderr={stderr[:200]}")

    # Check logging format
    start_lines = [l for l in stdout.splitlines() if l.strip().startswith("[START]")]
    step_lines = [l for l in stdout.splitlines() if l.strip().startswith("[STEP]")]
    end_lines = [l for l in stdout.splitlines() if l.strip().startswith("[END]")]

    all_ok &= check(f"[START] lines: {len(start_lines)} (expected ≥3)",
                     len(start_lines) >= 3)
    all_ok &= check(f"[STEP] lines: {len(step_lines)} (expected >0)",
                     len(step_lines) > 0)
    all_ok &= check(f"[END] lines: {len(end_lines)} (expected ≥3)",
                     len(end_lines) >= 3)

    # Validate JSON in log lines
    json_errors = 0
    for line in start_lines + step_lines + end_lines:
        tag_end = line.index("]") + 1
        json_part = line[tag_end:].strip()
        try:
            json.loads(json_part)
        except (json.JSONDecodeError, ValueError):
            json_errors += 1
            if json_errors <= 3:
                print(f"         → Invalid JSON: {line[:100]}")

    all_ok &= check(f"All log lines have valid JSON ({json_errors} errors)",
                     json_errors == 0)

    # Extract scores from [END] lines
    scores = {}
    for line in end_lines:
        tag_end = line.index("]") + 1
        json_part = line[tag_end:].strip()
        try:
            data = json.loads(json_part)
            tid = data.get("task_id", "unknown")
            score = data.get("score", 0.0)
            scores[tid] = score
        except Exception:
            pass

    if scores:
        print(f"\n  {'─' * 50}")
        print(f"  Scores Summary:")
        total = 0
        for tid in TASK_IDS:
            s = scores.get(tid, 0.0)
            total += s
            emoji = "🟢" if s > 0.5 else ("🟡" if s > 0.2 else "🔴")
            print(f"    {emoji}  {tid}: {s:.4f}")
        print(f"    ──────────────────────────")
        print(f"    Total: {total:.4f} / 3.0")
        print(f"  {'─' * 50}")

    return all_ok


# ─── Check 7: Dockerfile syntax ──────────────────────────────────
def check_dockerfile() -> bool:
    header("Check 7: Dockerfile Validation")
    with open("Dockerfile", "r") as f:
        content = f.read()

    all_ok = True
    all_ok &= check("Has FROM instruction", "FROM" in content)
    all_ok &= check("Exposes port 7860", "7860" in content)
    all_ok &= check("Has CMD or ENTRYPOINT",
                     "CMD" in content or "ENTRYPOINT" in content)
    all_ok &= check("Copies requirements.txt",
                     "requirements.txt" in content)
    return all_ok


# ─── Check 8: Git status ─────────────────────────────────────────
def check_git_status() -> bool:
    header("Check 8: Git Repository Status")
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=10
        )
        dirty = result.stdout.strip()
        if dirty:
            changed_files = dirty.splitlines()[:5]
            print(f"  {WARN}  Uncommitted changes ({len(dirty.splitlines())} files):")
            for f in changed_files:
                print(f"         {f}")
            if len(dirty.splitlines()) > 5:
                print(f"         ... and {len(dirty.splitlines()) - 5} more")
            return True  # Warning, not failure

        return check("Working tree is clean", True)
    except Exception as e:
        return check("Git available", False, str(e))


# ─── Main ─────────────────────────────────────────────────────────
def main():
    print("\n" + "█" * 60)
    print("  OpenEnv Contract Clause Env — Pre-Submission Validator")
    print("█" * 60)
    print(f"  Server: {ENV_BASE_URL}")
    print(f"  Time:   {time.strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}
    results["files"] = check_files()
    results["yaml"] = check_openenv_yaml()
    results["health"] = check_server_health()

    if not results["health"]:
        print(f"\n{FAIL}  Server not reachable. Start it first:")
        print(f"     python -m uvicorn server.app:app --port 7860")
        print(f"     Then rerun this script.\n")
        sys.exit(1)

    results["endpoints"] = check_endpoints()
    results["tasks"] = check_tasks_list()
    results["inference"] = check_inference_run()
    results["dockerfile"] = check_dockerfile()
    results["git"] = check_git_status()

    # ── Final summary ──
    header("FINAL RESULTS")
    all_pass = True
    for name, ok in results.items():
        status = PASS if ok else FAIL
        print(f"  {status}  {name}")
        all_pass &= ok

    if all_pass:
        print(f"\n  🎉 ALL CHECKS PASSED — Ready to submit!")
    else:
        print(f"\n  ⚠️  Some checks failed. Fix issues above before submitting.")

    print()
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
