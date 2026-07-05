"""Re-run the 3 repos that failed with exit 2 (now fixed), merge into results."""
import json, os, subprocess, sys, time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("PYTHONUTF8", "1")

from run_benchmark import run_pipeline, ALL_METRIC_IDS, ALL_DETECTOR_IDS
from repository_catalogue import RepoSpec, RepoCategory, RepoSize, RepoLanguage

FIX_REPOS = [
    ("numpy/numpy", "healthy", "large", "python", "Numerical computing"),
    ("twisted/twisted", "enterprise", "large", "python", "Networking engine"),
    ("rails/rails", "healthy", "large", "ruby", "Web framework"),
]

CAT_MAP = {"healthy": RepoCategory.HEALTHY, "enterprise": RepoCategory.ENTERPRISE,
           "experimental": RepoCategory.EXPERIMENTAL, "high-risk": RepoCategory.HIGH_RISK,
           "archived": RepoCategory.ARCHIVED}
SIZE_MAP = {"large": RepoSize.LARGE, "medium": RepoSize.MEDIUM, "small": RepoSize.SMALL}
LANG_MAP = {"python": RepoLanguage.PYTHON, "javascript": RepoLanguage.JAVASCRIPT,
            "typescript": RepoLanguage.TYPESCRIPT, "go": RepoLanguage.GO,
            "rust": RepoLanguage.RUST, "java": RepoLanguage.JAVA,
            "ruby": RepoLanguage.RUBY, "c++": RepoLanguage.CPP}

RESULTS_DIR = Path(__file__).resolve().parent / "results"

results = []
for i, (repo_id, cat, size, lang, desc) in enumerate(FIX_REPOS, 1):
    spec = RepoSpec(repo_id, CAT_MAP[cat], SIZE_MAP[size], LANG_MAP[lang], desc)
    print(f"[{i}/3] {repo_id} ({cat}/{lang})", end=" ", flush=True)
    r = run_pipeline(spec)
    results.append(r)
    if r.success:
        n_met = r.metrics_computed
        is_s = f"{r.integrity_score:.3f}" if r.integrity_score is not None else "N/A"
        cs_s = f"{r.confidence_score:.3f}" if r.confidence_score is not None else "N/A"
        print(f"OK [{n_met}/7, IS={is_s}, CS={cs_s}] ({r.pipeline_time_s:.1f}s)")
    else:
        print(f"FAIL: {r.error[:100]}")

# Save
fix_data = []
for r in results:
    fix_data.append({
        "repo_id": r.spec.repo_id,
        "category": r.spec.category.value,
        "size": r.spec.size.value,
        "language": r.spec.language.value,
        "success": r.success,
        "metric_values": r.metric_values,
        "detector_results": r.detector_results,
        "detector_execution": r.detector_execution,
        "integrity_score": r.integrity_score,
        "confidence_score": r.confidence_score,
        "confidence_band": r.confidence_band,
        "pipeline_time_s": r.pipeline_time_s,
        "clone_time_s": r.clone_time_s,
        "windows_count": r.windows_count,
    })

with open(RESULTS_DIR / "fix_results.json", "w", encoding="utf-8") as f:
    json.dump(fix_data, f, indent=2, default=str)

n_ok = sum(1 for r in results if r.success)
print(f"\nFix results: {n_ok}/{len(results)} successful")
