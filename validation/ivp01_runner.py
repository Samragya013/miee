"""IVP-01 Validation Campaign Runner v2."""

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

REPOS_DIR = Path(__file__).parent.parent / "benchmarks" / "pr14" / "repos"
OUTPUT_DIR = Path(__file__).parent / "results"

CORPUS = [
    {"name": "kennethreitz_maya", "lang": "Python", "category": "mature", "size": "small"},
    {"name": "pallets_itsdangerous", "lang": "Python", "category": "mature", "size": "small"},
    {"name": "tartley_colorama", "lang": "Python", "category": "mature", "size": "small"},
    {"name": "encode_httpx", "lang": "Python", "category": "active", "size": "medium"},
    {"name": "scrapy_scrapy", "lang": "Python", "category": "active", "size": "medium"},
    {"name": "expressjs_express", "lang": "JavaScript", "category": "mature", "size": "medium"},
    {"name": "dapr_dapr", "lang": "Go", "category": "active", "size": "medium"},
    {"name": "serde-rs_serde", "lang": "Rust", "category": "mature", "size": "medium"},
    {"name": "containerd_containerd", "lang": "Go", "category": "active", "size": "large"},
    {"name": "etcd-io_etcd", "lang": "Go", "category": "active", "size": "large"},
    {"name": "rust-lang_rust", "lang": "Rust", "category": "active", "size": "large"},
    {"name": "kubernetes_kubernetes", "lang": "Go", "category": "active", "size": "large"},
]

ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
TIMEOUT = 600  # 10 min per repo


def find_json(output_dir: Path):
    for f in output_dir.glob("analysis_report_*.json"):
        with open(f) as fh:
            return json.load(fh)
    return None


def strip_timestamps(obj):
    """Remove timestamp/metadata fields that break determinism comparison."""
    if isinstance(obj, dict):
        return {k: strip_timestamps(v) for k, v in obj.items()
                if k not in ("timestamp", "generated_at", "config_hash", "run_id", "repo_id")}
    if isinstance(obj, list):
        return [strip_timestamps(i) for i in obj]
    return obj


def extract_metrics(rj: Dict) -> Dict:
    r = rj.get("analysis_result", rj)
    sp = r.get("score_package", {}) or {}
    det_out = r.get("detector_results", {}).get("detector_outputs", {})
    findings = []
    for dv in det_out.values():
        findings.extend(dv.get("drift_events", []))
        findings.extend(dv.get("breakdown_events", []))
        findings.extend(dv.get("compression_events", []))
    integrity = sp.get("integrity", {})
    confidence = sp.get("confidence", {})
    return {
        "integrity_score": integrity.get("overall") if isinstance(integrity, dict) else None,
        "confidence_score": confidence.get("overall") if isinstance(confidence, dict) else None,
        "findings_count": len(findings),
        "detectors_run": list(det_out.keys()),
        "windows_count": len(r.get("windows", [])),
    }


def run_cli(repo_path: str, output_dir: str) -> Dict:
    cmd = [
        sys.executable, "-m", "miie", "analyze", repo_path,
        "-m", "M-02", "-m", "M-06",
        "-d", "D-01", "-d", "D-02", "-d", "D-03",
        "-o", output_dir, "-f", "json", "--seed", "42",
    ]
    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd, capture_output=True, timeout=TIMEOUT,
            cwd=str(Path(__file__).parent.parent), env=ENV,
            encoding="utf-8", errors="replace",
        )
        elapsed = time.time() - t0
        rj = find_json(Path(output_dir))
        rc = proc.returncode
        # returncode 3 = insufficient windows (expected for small repos)
        return {
            "status": "success" if rc in (0, 3) else "error",
            "returncode": rc,
            "execution_time_s": round(elapsed, 3),
            "result_json": rj,
            "exit_code": rc,
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "execution_time_s": TIMEOUT}
    except Exception as e:
        return {"status": "error", "error": str(e)[:500]}


def run_determinism(repo_path: str) -> Dict:
    outputs = []
    for i in range(2):
        out = OUTPUT_DIR / f"det_{i}"
        if out.exists(): shutil.rmtree(out)
        out.mkdir(parents=True)
        r = run_cli(repo_path, str(out))
        if r["result_json"]:
            outputs.append(strip_timestamps(r["result_json"]))
        else:
            outputs.append(None)
    if all(o is not None for o in outputs):
        return {"deterministic": outputs[0] == outputs[1], "runs": 2}
    return {"deterministic": False, "error": "no JSON output"}


def run_robustness() -> List[Dict]:
    checks = []
    # Empty repo
    ed = OUTPUT_DIR / "test_empty"
    if ed.exists(): shutil.rmtree(ed)
    ed.mkdir(parents=True)
    try:
        subprocess.run(["git", "init", str(ed)], capture_output=True, timeout=10, env=ENV)
        od = OUTPUT_DIR / "test_empty_out"
        if od.exists(): shutil.rmtree(od)
        od.mkdir(parents=True)
        r = run_cli(str(ed), str(od))
        checks.append({"test": "empty_repo", "status": r["status"],
                       "exit_code": r.get("exit_code"), "note": "expected error (no commits)"})
    except Exception as e:
        checks.append({"test": "empty_repo", "status": "error", "error": str(e)[:300]})
    finally:
        shutil.rmtree(ed, ignore_errors=True)
        shutil.rmtree(OUTPUT_DIR / "test_empty_out", ignore_errors=True)

    # Single commit
    sd = OUTPUT_DIR / "test_single"
    if sd.exists(): shutil.rmtree(sd)
    sd.mkdir(parents=True)
    try:
        subprocess.run(["git", "init", str(sd)], capture_output=True, timeout=10, env=ENV)
        (sd / "README.md").write_text("# Test")
        subprocess.run(["git", "-C", str(sd), "add", "."], capture_output=True, timeout=10, env=ENV)
        subprocess.run(["git", "-C", str(sd), "commit", "-m", "init"], capture_output=True, timeout=10, env=ENV)
        od = OUTPUT_DIR / "test_single_out"
        if od.exists(): shutil.rmtree(od)
        od.mkdir(parents=True)
        r = run_cli(str(sd), str(od))
        checks.append({"test": "single_commit", "status": r["status"],
                       "exit_code": r.get("exit_code"), "note": "expected: insufficient windows or success"})
    except Exception as e:
        checks.append({"test": "single_commit", "status": "error", "error": str(e)[:300]})
    finally:
        shutil.rmtree(sd, ignore_errors=True)
        shutil.rmtree(OUTPUT_DIR / "test_single_out", ignore_errors=True)
    return checks


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    print(f"IVP-01 Campaign: {len(CORPUS)} repos")
    print("=" * 60)

    for ri in CORPUS:
        rn = ri["name"]
        rp = REPOS_DIR / rn
        if not rp.exists():
            print(f"  SKIP {rn}")
            results.append({"repo": rn, "status": "not_found"})
            continue
        od = OUTPUT_DIR / rn
        if od.exists(): shutil.rmtree(od)
        od.mkdir(parents=True)
        print(f"  {rn}...", end=" ", flush=True)
        r = run_cli(str(rp), str(od))
        m = extract_metrics(r["result_json"]) if r["result_json"] else {}
        entry = {"repo": rn, "language": ri["lang"], "category": ri["category"],
                 "size_class": ri["size"], "status": r["status"],
                 "execution_time_s": r["execution_time_s"], "exit_code": r.get("exit_code"), **m}
        results.append(entry)
        print(f"{entry['status']} ({entry['execution_time_s']}s, {m.get('findings_count','?')} findings, exit={entry['exit_code']})")

    print("\nDeterminism...")
    determinism = []
    for ri in CORPUS[:3]:
        rp = REPOS_DIR / ri["name"]
        if rp.exists():
            print(f"  {ri['name']}...", end=" ", flush=True)
            d = run_determinism(str(rp))
            determinism.append({"repo": ri["name"], **d})
            print(d["deterministic"])

    print("\nRobustness...")
    robustness = run_robustness()
    for rb in robustness:
        print(f"  {rb['test']}: {rb['status']} (exit={rb.get('exit_code')})")

    output = {"campaign": "IVP-01", "version": "2.0.0",
              "corpus_size": len(CORPUS), "results": results,
              "determinism": determinism, "robustness": robustness}
    out_file = OUTPUT_DIR / "ivp01_results.json"
    with open(out_file, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nSaved: {out_file}")

    ok = sum(1 for r in results if r["status"] == "success")
    err = sum(1 for r in results if r["status"] == "error")
    timeout = sum(1 for r in results if r["status"] == "timeout")
    det = sum(1 for d in determinism if d["deterministic"])
    print(f"\n{ok} success, {err} errors, {timeout} timeouts, {det}/{len(determinism)} deterministic")


if __name__ == "__main__":
    main()
