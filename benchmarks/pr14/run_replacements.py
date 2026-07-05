"""Re-run only the failed repos with replacements. Merge into existing results."""
import csv, json, os, subprocess, sys, time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("PYTHONUTF8", "1")

from run_benchmark import run_pipeline, ALL_METRIC_IDS, ALL_DETECTOR_IDS
from repository_catalogue import RepoSpec, RepoCategory, RepoSize, RepoLanguage

# Failed repos and their replacements
REPLACEMENTS = [
    # Pipeline exit 2 (now fixed)
    ("numpy/numpy", "healthy", "large", "python", "Numerical computing"),
    ("twisted/twisted", "enterprise", "large", "python", "Networking engine"),
    ("rails/rails", "healthy", "large", "ruby", "Web framework"),
    # Clone failures - replacements
    ("labmlai/announcements", "experimental", "small", "python", "ML announcements"),
    ("antonio-halerpo/coursera-ml-spec", "experimental", "small", "python", "ML course"),
    ("pytorch/pytorch", "high-risk", "large", "python", "Deep learning"),
    ("kennethreitz/lego", "archived", "small", "python", "Lego project"),
    ("kennethreitz/gallows", "archived", "small", "python", "Hangman game"),
    ("webpack/webpack", "healthy", "large", "javascript", "Module bundler"),
    ("microsoft/TypeScript", "healthy", "large", "typescript", "TypeScript compiler"),
    ("vercel/next.js", "healthy", "large", "typescript", "React framework"),
    ("prisma/prisma", "healthy", "large", "typescript", "ORM toolkit"),
    ("stitches-dev/stitches", "experimental", "small", "typescript", "CSS-in-JS"),
    ("VanillaExtractCS/vanilla-extract", "healthy", "medium", "typescript", "CSS-in-JS"),
    ("kubernetes/kubernetes", "enterprise", "large", "go", "Container orchestration"),
    ("moby/moby", "enterprise", "large", "go", "Container engine"),
    ("hashicorp/terraform", "enterprise", "large", "go", "Infrastructure as Code"),
    ("grafana/grafana", "healthy", "large", "go", "Observability platform"),
    ("rust-lang/rust", "healthy", "large", "rust", "Rust compiler"),
    ("spring-projects/spring-boot", "healthy", "large", "java", "Spring framework"),
    ("elastic/elasticsearch", "healthy", "large", "java", "Search engine"),
]

CAT_MAP = {
    "healthy": RepoCategory.HEALTHY,
    "enterprise": RepoCategory.ENTERPRISE,
    "experimental": RepoCategory.EXPERIMENTAL,
    "high-risk": RepoCategory.HIGH_RISK,
    "archived": RepoCategory.ARCHIVED,
}
SIZE_MAP = {
    "large": RepoSize.LARGE,
    "medium": RepoSize.MEDIUM,
    "small": RepoSize.SMALL,
}
LANG_MAP = {
    "python": RepoLanguage.PYTHON,
    "javascript": RepoLanguage.JAVASCRIPT,
    "typescript": RepoLanguage.TYPESCRIPT,
    "go": RepoLanguage.GO,
    "rust": RepoLanguage.RUST,
    "java": RepoLanguage.JAVA,
    "ruby": RepoLanguage.RUBY,
    "c++": RepoLanguage.CPP,
}

REPLACEMENT_REPOS = [
    ("paramiko/paramiko", "experimental", "small", "python", "SSH library"),
    ("lpil/ancyr", "experimental", "small", "python", "Gleam"),
    ("pallets/itsdangerous", "experimental", "small", "python", "Data signing"),
    ("kennethreitz/pendulum", "experimental", "small", "python", "DateTime"),
    ("kennethreitz/tabula-pula", "archived", "small", "python", "Data"),
    ("rollup/rollup", "healthy", "large", "javascript", "Module bundler"),
    ("sveltejs/svelte", "healthy", "large", "typescript", "UI framework"),
    ("drizzle-team/drizzle-orm", "healthy", "medium", "typescript", "ORM"),
    ("chakra-ui/chakra-ui", "experimental", "medium", "typescript", "UI components"),
    ("vanilla-extract-css/vanilla-extract", "healthy", "medium", "typescript", "CSS-in-JS"),
    ("distribution/distribution", "enterprise", "medium", "go", "Container distribution"),
    ("hashicorp/consul", "enterprise", "large", "go", "Service mesh"),
    ("BurntSushi/ripgrep", "healthy", "medium", "rust", "Grep tool"),
    ("apache/lucene", "healthy", "large", "java", "Search library"),
    ("google/guava", "healthy", "large", "java", "Core libraries"),
]

print("=" * 72)
print("PR-14 — Re-running failed repos with replacements")
print("=" * 72)

results = []
for i, (repo_id, cat, size, lang, desc) in enumerate(REPLACEMENT_REPOS, 1):
    spec = RepoSpec(repo_id, CAT_MAP[cat], SIZE_MAP[size], LANG_MAP[lang], desc)
    print(f"[{i}/{len(REPLACEMENT_REPOS)}] {repo_id} ({cat}/{lang})", end=" ", flush=True)
    r = run_pipeline(spec)
    results.append(r)
    if r.success:
        n_met = r.metrics_computed
        is_s = f"{r.integrity_score:.3f}" if r.integrity_score is not None else "N/A"
        cs_s = f"{r.confidence_score:.3f}" if r.confidence_score is not None else "N/A"
        print(f"OK [{n_met}/7, IS={is_s}, CS={cs_s}] ({r.pipeline_time_s:.1f}s)")
    else:
        print(f"FAIL: {r.error[:100]}")

# Save replacement results
RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

replacement_data = []
for r in results:
    replacement_data.append({
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
    })

with open(RESULTS_DIR / "replacement_results.json", "w", encoding="utf-8") as f:
    json.dump(replacement_data, f, indent=2, default=str)

n_ok = sum(1 for r in results if r.success)
print(f"\nReplacement results: {n_ok}/{len(results)} successful")
