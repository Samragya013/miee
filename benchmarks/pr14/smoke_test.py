"""Quick smoke test: 3 repos to verify runner before full benchmark."""
import json, os, subprocess, sys, time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("PYTHONUTF8", "1")

from run_benchmark import run_pipeline, generate_reports, ALL_METRIC_IDS, ALL_DETECTOR_IDS
from repository_catalogue import RepoSpec, RepoCategory, RepoSize, RepoLanguage

TEST_REPOS = [
    RepoSpec("pallets/flask", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.PYTHON),
    RepoSpec("pympler/pympler", RepoCategory.HIGH_RISK, RepoSize.SMALL, RepoLanguage.PYTHON),
    RepoSpec("expressjs/express", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.JAVASCRIPT),
]

results = []
for i, spec in enumerate(TEST_REPOS, 1):
    print(f"[{i}/3] {spec.repo_id} ({spec.category.value}/{spec.language.value})", end=" ", flush=True)
    r = run_pipeline(spec)
    results.append(r)
    if r.success:
        n_met = r.metrics_computed
        is_s = f"{r.integrity_score:.3f}" if r.integrity_score is not None else "N/A"
        cs_s = f"{r.confidence_score:.3f}" if r.confidence_score is not None else "N/A"
        det = []
        for d in ALL_DETECTOR_IDS:
            dr = r.detector_results.get(d, {})
            st = dr.get("status", "?")
            if st == "error": det.append("ERR")
            elif dr.get("detected"): det.append("DET!")
            else: det.append("ok")
        print(f"OK [{n_met}/7, IS={is_s}, CS={cs_s}, {','.join(det)}] ({r.pipeline_time_s:.1f}s)")
    else:
        print(f"FAIL: {r.error[:100]}")

# Generate reports
RESULTS_DIR = Path(__file__).resolve().parent / "results"
generate_reports(results)

# Show summary
print("\n--- Metric Values ---")
for r in results:
    if not r.success: continue
    print(f"  {r.spec.repo_id.split('/')[-1]}:")
    for mid in ALL_METRIC_IDS:
        v = r.metric_values.get(mid)
        if v is not None:
            print(f"    {mid}: {v:.4f}")
