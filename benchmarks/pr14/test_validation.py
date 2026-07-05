"""Test 5 repos across categories — full pipeline validation."""
import json, os, subprocess, sys, time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
os.environ.setdefault("PYTHONUTF8", "1")

REPOS = [
    ("pympler/pympler", "python", "small", "high-risk"),
    ("tqdm/tqdm", "python", "small", "high-risk"),
    ("scrapy/scrapy", "python", "large", "high-risk"),
    ("dani-garcia/vaultwarden", "rust", "medium", "high-risk"),
    ("pallets/flask", "python", "medium", "healthy"),
]
REPOS_DIR = Path(__file__).resolve().parent / "repos"
RESULTS_DIR = Path(__file__).resolve().parent / "results" / "validation"
METRICS = ["M-01", "M-02", "M-03", "M-04", "M-05", "M-06", "M-07"]
DETECTORS = ["D-01", "D-02", "D-03"]
TIMEOUT = 300

def clone_repo(repo_id):
    clone_path = REPOS_DIR / repo_id.replace("/", "_")
    if clone_path.exists() and (clone_path / ".git").exists():
        r = subprocess.run(["git", "-C", str(clone_path), "rev-parse", "HEAD"],
                           capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            return clone_path, 0.0, "cached"
    url = f"https://github.com/{repo_id}.git"
    t0 = time.time()
    r = subprocess.run(["git", "clone", "--depth=500", "--single-branch", url, str(clone_path)],
                       capture_output=True, text=True, timeout=120)
    elapsed = time.time() - t0
    if r.returncode != 0:
        raise RuntimeError(f"Clone failed: {r.stderr[:200]}")
    return clone_path, elapsed, "cloned"

def run_analysis(repo_path, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-m", "miie.cli", "analyze", str(repo_path)]
    for m in METRICS:
        cmd.extend(["-m", m])
    for d in DETECTORS:
        cmd.extend(["-d", d])
    cmd.extend(["-o", str(output_dir), "--seed", "42", "-f", "json", "-V"])

    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT, cwd=str(REPO_ROOT))
    elapsed = time.time() - t0
    if proc.returncode != 0:
        raise RuntimeError(f"Exit {proc.returncode}: {proc.stdout[-300:]}")

    reports = sorted(output_dir.glob("analysis_report_*.json"))
    if not reports:
        raise RuntimeError("No JSON report found")
    with open(reports[-1], encoding="utf-8") as f:
        return json.load(f), elapsed

results = []
for i, (repo_id, lang, size, cat) in enumerate(REPOS, 1):
    print(f"\n[{i}/5] {repo_id} ({cat}/{lang}/{size})", flush=True)
    result = {"repo_id": repo_id, "language": lang, "size": size, "category": cat}

    try:
        repo_path, clone_t, clone_msg = clone_repo(repo_id)
        print(f"  Clone: {clone_msg} ({clone_t:.1f}s)", flush=True)

        out = RESULTS_DIR / repo_id.replace("/", "_")
        report, pipeline_t = run_analysis(repo_path, out)
        print(f"  Pipeline: {pipeline_t:.1f}s", flush=True)

        ar = report.get("analysis_result", report)
        sp = ar.get("score_package", {})
        dr = ar.get("detector_results", {}).get("detector_outputs", {})
        mdf = ar.get("metric_dataframe", {}).get("metrics", {})

        result["success"] = True
        result["clone_time"] = clone_t
        result["pipeline_time"] = pipeline_t
        result["integrity_score"] = sp.get("integrity", {}).get("overall")
        result["confidence_score"] = sp.get("confidence", {}).get("overall")
        result["confidence_band"] = sp.get("confidence", {}).get("band")

        # Metrics with data
        metrics_with_data = sum(1 for v in mdf.values() if v is not None)
        result["metrics_with_data"] = metrics_with_data
        result["total_metrics"] = len(mdf)

        # Detectors
        for d in DETECTORS:
            ddata = dr.get(d, {})
            result[f"{d}_status"] = ddata.get("status", "executed")
            result[f"{d}_detected"] = ddata.get("drift_detected") or ddata.get("breakdown_detected") or ddata.get("compression_detected", False)
            result[f"{d}_error"] = ddata.get("reason", "")[:80] if ddata.get("status") == "error" else ""

        is_str = f"{result['integrity_score']:.3f}" if result["integrity_score"] is not None else "N/A"
        cs_str = f"{result['confidence_score']:.3f}" if result["confidence_score"] is not None else "N/A"
        band = result.get("confidence_band", "?")
        m_data = f"{metrics_with_data}/7"
        det_summary = []
        for d in DETECTORS:
            st = result.get(f"{d}_status", "?")
            if st == "error":
                det_summary.append("ERR")
            elif result.get(f"{d}_detected"):
                det_summary.append("DET!")
            else:
                det_summary.append("ok")
        print(f"  IS={is_str} CS={cs_str} ({band}) | metrics={m_data} | D={'/'.join(det_summary)}", flush=True)

    except Exception as e:
        result["success"] = False
        result["error"] = str(e)[:200]
        print(f"  FAIL: {result['error'][:100]}", flush=True)

    results.append(result)

# Save
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
with open(RESULTS_DIR / "validation_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

# Summary table
print(f"\n{'='*100}")
print("PIPELINE VALIDATION RESULTS")
print(f"{'='*100}")
print(f"{'Repo':25s} {'Cat':>10s} {'IS':>6s} {'CS':>6s} {'Band':>6s} {'Met':>5s} {'D-01':>8s} {'D-02':>8s} {'D-03':>8s} {'Time':>6s}")
print(f"{'-'*25} {'-'*10} {'-'*6} {'-'*6} {'-'*6} {'-'*5} {'-'*8} {'-'*8} {'-'*8} {'-'*6}")
for r in results:
    repo = r["repo_id"].split("/")[-1]
    is_s = f"{r['integrity_score']:.3f}" if r.get("integrity_score") is not None else "N/A"
    cs_s = f"{r['confidence_score']:.3f}" if r.get("confidence_score") is not None else "N/A"
    band = r.get("confidence_band", "?") or "?"
    met = f"{r.get('metrics_with_data', 0)}/7"
    def det_s(d):
        st = r.get(f"{d}_status", "?")
        if st == "error": return "ERR"
        if r.get(f"{d}_detected"): return "DETECT!"
        return "ok"
    pt = f"{r['pipeline_time']:.1f}s" if r.get("pipeline_time") else "FAIL"
    print(f"{repo:25s} {r['category']:>10s} {is_s:>6s} {cs_s:>6s} {band:>6s} {met:>5s} {det_s('D-01'):>8s} {det_s('D-02'):>8s} {det_s('D-03'):>8s} {pt:>6s}")
