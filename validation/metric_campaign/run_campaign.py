"""
PR-12A — Scientific Metric Validation & GitHub Repository Certification Campaign

Executes the full provider → orchestrator → graph → metric engine pipeline
against real public GitHub repositories. No mocked observations.

Produces:
  - validation/metric_campaign/01_REPOSITORY_SELECTION.md
  - validation/metric_campaign/02_EXECUTION_MATRIX.md
  - validation/metric_campaign/03_PROVIDER_COVERAGE.md
  - validation/metric_campaign/04_METRIC_RESULTS.md
  - validation/metric_campaign/05_METRIC_VALIDATION.md
  - validation/metric_campaign/06_CONFIDENCE_ANALYSIS.md
  - validation/metric_campaign/07_RANGE_ANALYSIS.md
  - validation/metric_campaign/08_DETERMINISM_REPORT.md
  - validation/metric_campaign/09_PERFORMANCE_REPORT.md
  - validation/metric_campaign/10_SCIENTIFIC_CERTIFICATION.md
  - validation/metric_campaign/repository_metrics.csv
  - validation/metric_campaign/metric_results.csv
  - validation/metric_campaign/provider_coverage.csv
  - validation/metric_campaign/metric_statistics.csv
  - validation/metric_campaign/scientific_certification.json
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Add src to path
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

# Force UTF-8 on Windows to prevent CP1252 encoding errors in subprocess
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"


# ---------------------------------------------------------------------------
# Secure .env loading (never overwrites existing env vars, never logs values)
# ---------------------------------------------------------------------------
def _load_dotenv_secure() -> None:
    """Load .env file from project root without overwriting existing env vars.

    Security measures:
    - Uses os.environ.setdefault() — never overwrites already-set vars
    - Never prints, logs, or exposes token values
    - Skips comments, blank lines, and malformed entries
    - Only reads from the project-root .env file (no recursive search)
    """
    env_path = REPO_ROOT / ".env"
    if not env_path.is_file():
        return

    try:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in stripped:
                continue
            key, _, value = stripped.partition("=")
            key = key.strip()
            value = value.strip()
            # Strip surrounding quotes if present
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            if key:
                os.environ.setdefault(key, value)
    except Exception:
        # Silently ignore — .env loading is best-effort
        pass


_load_dotenv_secure()

from miie.metrics.engine import MetricEngine  # noqa: E402
from miie.metrics.models import MetricCollection  # noqa: E402
from miie.observation_graph.builder import (  # noqa: E402
    GraphBuilderConfig,
    ObservationGraphBuilder,
)
from miie.processing.observation.models import (  # noqa: E402
    Observation,
    ObservationCollection,
    ObservationProvenance,
    ObservationWindow,
    generate_observation_id,
)

# ---------------------------------------------------------------------------
# MIIE imports
# ---------------------------------------------------------------------------
from miie.providers.context import ExtractionResult  # noqa: E402
from miie.providers.context import (  # noqa: E402
    PriorityLevel,
    ProviderCapability,
    ProviderContext,
)
from miie.providers.git import PROVIDER_ID as GIT_PROVIDER_ID  # noqa: E402
from miie.providers.git import (
    GitObservationProvider,
    git_provider_capabilities,
)
from miie.providers.github import (  # noqa: E402
    GITHUB_PR_PROVIDER_ID,
    GitHubPullRequestProvider,
    github_pr_provider_capabilities,
)
from miie.providers.github.authentication import (  # noqa: E402
    GitHubAuth,
    summarize_auth_status,
)
from miie.providers.orchestrator import (  # noqa: E402
    ObservationOrchestrator,
    OrchestratorConfig,
)
from miie.providers.registry import DeterministicRegistry  # noqa: E402
from miie.providers.repository import (  # noqa: E402
    REPO_METADATA_PROVIDER_ID,
    RepositoryMetadataProvider,
    repository_metadata_provider_capabilities,
)
from miie.schemas.models import RepositoryContext  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CAMPAIGN_DIR = Path(__file__).resolve().parent
REPOS_DIR = CAMPAIGN_DIR / "repos"
ALL_METRIC_IDS = ["M-01", "M-02", "M-03", "M-04", "M-05", "M-06", "M-07"]

METRIC_INFO = {
    "M-01": {
        "name": "Commit Entropy Ratio",
        "unit": "ratio",
        "bounds": (0.0, 1.0),
        "aggregation": "mean",
        "min_obs": 1,
    },
    "M-02": {
        "name": "Commit Count",
        "unit": "count",
        "bounds": (0.0, float("inf")),
        "aggregation": "sum",
        "min_obs": 1,
    },
    "M-03": {"name": "Code Churn Ratio", "unit": "ratio", "bounds": (0.0, 1.0), "aggregation": "mean", "min_obs": 5},
    "M-04": {"name": "Test Coverage Ratio", "unit": "ratio", "bounds": (0.0, 1.0), "aggregation": "mean", "min_obs": 1},
    "M-05": {
        "name": "Review Latency",
        "unit": "hours",
        "bounds": (0.0, float("inf")),
        "aggregation": "mean",
        "min_obs": 2,
    },
    "M-06": {
        "name": "File Change Count",
        "unit": "count",
        "bounds": (0.0, float("inf")),
        "aggregation": "sum",
        "min_obs": 1,
    },
    "M-07": {
        "name": "Branch Freshness Ratio",
        "unit": "ratio",
        "bounds": (0.0, 1.0),
        "aggregation": "mean",
        "min_obs": 1,
    },
}


# ---------------------------------------------------------------------------
# Repository Catalogue
# ---------------------------------------------------------------------------
@dataclass
class RepoSpec:
    """Specification for a repository to include in the campaign."""

    repo_id: str  # owner/repo
    category: str  # small | medium | large | archived | experimental
    rationale: str  # why this repo was selected
    clone_url: str = ""
    branch: str = "main"
    skip_github_api: bool = False  # True = skip PR/Metadata providers (e.g. archived)

    def __post_init__(self):
        if not self.clone_url:
            self.clone_url = f"https://github.com/{self.repo_id}.git"


REPOSITORIES: List[RepoSpec] = [
    # --- Small (< 100 commits) ---
    RepoSpec(
        repo_id="tiangolo/typer",
        category="small",
        rationale="Popular CLI framework, moderate PR activity, ~100+ commits, Python",
    ),
    RepoSpec(
        repo_id="tiangolo/full-stack-fastapi-template",
        category="small",
        rationale="FastAPI full-stack template, good test coverage, moderate commit history",
    ),
    RepoSpec(
        repo_id="pypa/sampleproject",
        category="small",
        rationale="Python Packaging Authority sample project, very small, ideal baseline",
    ),
    # --- Medium (100-500 commits) ---
    RepoSpec(
        repo_id="tiangolo/uvicorn",
        category="medium",
        rationale="ASGI server, well-maintained, moderate PR count, Python",
    ),
    RepoSpec(
        repo_id="encode/httpx",
        category="medium",
        rationale="HTTP client library, active development, good PR review history",
    ),
    RepoSpec(
        repo_id="encode/starlette",
        category="medium",
        rationale="ASGI framework, consistent commit patterns, good PR reviews",
    ),
    # --- Large (500+ commits, high activity) ---
    RepoSpec(
        repo_id="pallets/flask",
        category="large",
        rationale="Major Python web framework, extensive history, many PRs",
        skip_github_api=False,
    ),
    RepoSpec(
        repo_id="psf/requests",
        category="large",
        rationale="Most popular HTTP library, extensive history, many PRs",
        skip_github_api=False,
    ),
    # --- Archived / Low Activity ---
    RepoSpec(
        repo_id="pypa/pip",
        category="archived",
        rationale="Python package installer, archived history, many commits",
        skip_github_api=False,
    ),
    # --- Experimental / Minimal ---
    RepoSpec(
        repo_id="python/cpython",
        category="experimental",
        rationale="CPython reference implementation, massive scale, tests large repo handling",
        skip_github_api=True,  # Too many PRs for anonymous API
    ),
]


# ---------------------------------------------------------------------------
# Clone Management
# ---------------------------------------------------------------------------
def clone_repo(spec: RepoSpec, dest_dir: Path) -> Tuple[bool, str]:
    """Clone a repository. Returns (success, message)."""
    repo_dir = dest_dir / spec.repo_id.replace("/", "_")

    if repo_dir.exists() and (repo_dir / ".git").exists():
        return True, f"Already cloned at {repo_dir}"

    repo_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "500",  # Shallow clone for speed
                "--branch",
                spec.branch,
                spec.clone_url,
                str(repo_dir),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            return True, f"Cloned to {repo_dir}"
        else:
            # Try without --branch (branch might be master)
            result2 = subprocess.run(
                ["git", "clone", "--depth", "500", spec.clone_url, str(repo_dir)],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result2.returncode == 0:
                # Detect default branch
                head = subprocess.run(
                    ["git", "symbolic-ref", "refs/remotes/origin/HEAD", "--short"],
                    capture_output=True,
                    text=True,
                    cwd=str(repo_dir),
                )
                if head.returncode == 0:
                    spec.branch = head.stdout.strip().replace("origin/", "")
                return True, f"Cloned to {repo_dir} (default branch)"
            return False, f"Clone failed: {result2.stderr[:500]}"
    except subprocess.TimeoutExpired:
        return False, "Clone timed out after 120s"
    except Exception as e:
        return False, f"Clone error: {e}"


# ---------------------------------------------------------------------------
# Observation → Collection Bridge
# ---------------------------------------------------------------------------
def extraction_result_to_collection(
    result: ExtractionResult,
    repository_id: str,
    analysis_id: str,
) -> ObservationCollection:
    """Convert an ExtractionResult to an ObservationCollection.

    This is the bridge between the orchestrator output and the graph builder input.
    Mirrors ExtractionEngine._build_collection() logic.
    """
    observations: List[Observation] = list(result.observations)

    now_iso = datetime.now(timezone.utc).isoformat()

    if not observations:
        empty_window = ObservationWindow(
            window_id="w00",
            window_index=0,
            strategy="commit_count",
            start_boundary=now_iso,
            end_boundary=now_iso,
            observations=[],
            metadata={"total_commits": "0"},
        )
        return ObservationCollection(
            collection_id=generate_observation_id("commit", "empty", "M-02"),
            repository_id=repository_id,
            analysis_id=analysis_id,
            windows=[empty_window],
            total_observations=0,
            total_metrics=0,
            extraction_timestamp=now_iso,
        )

    timestamps = [o.timestamp for o in observations if o.timestamp]
    start_boundary = min(timestamps) if timestamps else now_iso
    end_boundary = max(timestamps) if timestamps else now_iso

    source_shas = []
    seen_shas: set = set()
    for obs in observations:
        if obs.source_id not in seen_shas:
            seen_shas.add(obs.source_id)
            source_shas.append(obs.source_id)

    metrics_present = sorted({obs.metric_id for obs in observations})

    first_sha = source_shas[0] if source_shas else "empty"
    last_sha = source_shas[-1] if source_shas else "empty"

    window = ObservationWindow(
        window_id="w00",
        window_index=0,
        strategy="commit_count",
        start_boundary=start_boundary,
        end_boundary=end_boundary,
        observations=observations,
        start_commit=last_sha,
        end_commit=first_sha,
        metrics_present=metrics_present,
        metadata={"total_commits": str(len(source_shas))},
    )

    return ObservationCollection(
        collection_id=generate_observation_id("commit", first_sha, "M-02"),
        repository_id=repository_id,
        analysis_id=analysis_id,
        windows=[window],
        total_observations=len(observations),
        total_metrics=len(metrics_present),
        extraction_timestamp=now_iso,
    )


# ---------------------------------------------------------------------------
# Pipeline Execution
# ---------------------------------------------------------------------------
@dataclass
class RepoResult:
    """Complete result for a single repository."""

    spec: RepoSpec
    success: bool
    clone_time_s: float = 0.0
    clone_path: str = ""
    clone_message: str = ""
    provider_results: Dict[str, Any] = field(default_factory=dict)
    orchestrator_time_s: float = 0.0
    graph_build_time_s: float = 0.0
    metric_engine_time_s: float = 0.0
    total_time_s: float = 0.0
    metric_collection: Optional[MetricCollection] = None
    graph_diagnostics: Optional[Any] = None
    orchestrator_diagnostics: Optional[Any] = None
    observations_extracted: int = 0
    providers_succeeded: List[str] = field(default_factory=list)
    providers_failed: List[str] = field(default_factory=list)
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    # Per-metric detail
    metric_details: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # Determinism
    second_run_collection: Optional[MetricCollection] = None
    second_run_match: Optional[bool] = None


def run_pipeline(spec: RepoSpec, clone_dir: Path) -> RepoResult:
    """Execute the full pipeline for one repository."""
    result = RepoResult(spec=spec, success=False)
    start_total = time.time()

    # --- Step 1: Clone ---
    t0 = time.time()
    ok, msg = clone_repo(spec, clone_dir)
    result.clone_time_s = time.time() - t0
    result.clone_message = msg

    if not ok:
        result.error = f"Clone failed: {msg}"
        result.total_time_s = time.time() - start_total
        return result

    # Find the actual clone path
    repo_path = clone_dir / spec.repo_id.replace("/", "_")
    if not repo_path.exists():
        # Try finding it
        for d in clone_dir.iterdir():
            if d.is_dir() and (d / ".git").exists():
                repo_path = d
                break
    result.clone_path = str(repo_path)

    # --- Step 2: Register Providers ---
    try:
        auth = GitHubAuth()  # Auto-discovers GITHUB_TOKEN/GH_TOKEN/GITHUB_PAT

        registry = DeterministicRegistry()

        # Git provider (always available)
        registry.register(
            GitObservationProvider(),
            git_provider_capabilities(),
            PriorityLevel.HIGH,
        )

        # GitHub PR provider (needs API)
        if not spec.skip_github_api:
            try:
                gh_client = GitHubPullRequestProvider(auth=auth)
                registry.register(
                    gh_client,
                    github_pr_provider_capabilities(),
                    PriorityLevel.MEDIUM,
                )
            except Exception as e:
                result.warnings.append(f"GitHub PR provider init failed: {e}")

            # Repository metadata provider (needs API)
            try:
                repo_client = RepositoryMetadataProvider(auth=auth)
                registry.register(
                    repo_client,
                    repository_metadata_provider_capabilities(),
                    PriorityLevel.LOW,
                )
            except Exception as e:
                result.warnings.append(f"Repository Metadata provider init failed: {e}")
    except Exception as e:
        result.error = f"Provider registration failed: {e}"
        result.total_time_s = time.time() - start_total
        return result

    # --- Step 3: Build ProviderContext ---
    analysis_id = hashlib.sha256(
        f"campaign:{spec.repo_id}:{datetime.now(timezone.utc).isoformat()}".encode()
    ).hexdigest()[:16]

    context = ProviderContext(
        repo_path=str(repo_path),
        repository_id=spec.repo_id,
        analysis_id=analysis_id,
    )

    # --- Step 4: Run Orchestrator ---
    try:
        orchestrator = ObservationOrchestrator(registry)
        t0 = time.time()
        extraction_result, orch_diag = orchestrator.orchestrate(context, ALL_METRIC_IDS)
        result.orchestrator_time_s = time.time() - t0
        result.orchestrator_diagnostics = orch_diag
        result.observations_extracted = extraction_result.observation_count

        # Track which providers succeeded/failed
        for pr in orch_diag.provider_results:
            if pr.success:
                result.providers_succeeded.append(pr.provider_id)
            else:
                result.providers_failed.append(f"{pr.provider_id}: {pr.error or 'unknown'}")
    except Exception as e:
        result.error = f"Orchestrator failed: {e}\n{traceback.format_exc()}"
        result.total_time_s = time.time() - start_total
        return result

    # --- Step 5: Convert to ObservationCollection ---
    try:
        collection = extraction_result_to_collection(
            extraction_result,
            repository_id=spec.repo_id,
            analysis_id=analysis_id,
        )
        result.provider_results["collection_observations"] = collection.total_observations
        result.provider_results["collection_metrics"] = collection.total_metrics
    except Exception as e:
        result.error = f"Collection conversion failed: {e}"
        result.total_time_s = time.time() - start_total
        return result

    # --- Step 6: Build Observation Graph ---
    try:
        graph_builder = ObservationGraphBuilder()
        t0 = time.time()
        graph_result = graph_builder.build(
            repository_id=spec.repo_id,
            analysis_id=analysis_id,
            collections=[collection],
        )
        result.graph_build_time_s = time.time() - t0
        result.graph_diagnostics = graph_result.diagnostics
    except Exception as e:
        result.error = f"Graph build failed: {e}\n{traceback.format_exc()}"
        result.total_time_s = time.time() - start_total
        return result

    # --- Step 7: Run Metric Engine ---
    try:
        engine = MetricEngine()
        t0 = time.time()
        metric_collection = engine.compute_from_graph(
            graph_result.graph,
            repository_id=spec.repo_id,
            analysis_id=analysis_id,
        )
        result.metric_engine_time_s = time.time() - t0
        result.metric_collection = metric_collection
    except Exception as e:
        result.error = f"Metric engine failed: {e}\n{traceback.format_exc()}"
        result.total_time_s = time.time() - start_total
        return result

    # --- Step 8: Per-metric details ---
    for metric_id in ALL_METRIC_IDS:
        mr = metric_collection.get_result(metric_id)
        if mr is not None:
            result.metric_details[metric_id] = {
                "value": mr.value,
                "unit": mr.unit,
                "confidence": mr.confidence,
                "observation_count": mr.observation_count,
                "provider_count": mr.provider_count,
                "quality_distribution": dict(mr.quality_distribution),
                "computation_method": mr.computation_method,
                "computation_time_ms": 0.0,
            }
        else:
            result.metric_details[metric_id] = {
                "value": None,
                "unit": METRIC_INFO[metric_id]["unit"],
                "confidence": 0.0,
                "observation_count": 0,
                "provider_count": 0,
                "quality_distribution": {},
                "computation_method": "none",
                "computation_time_ms": 0.0,
            }

    result.success = True
    result.total_time_s = time.time() - start_total
    return result


# ---------------------------------------------------------------------------
# Determinism Verification
# ---------------------------------------------------------------------------
def verify_determinism(spec: RepoSpec, clone_dir: Path) -> RepoResult:
    """Run the pipeline a second time and compare results."""
    result = run_pipeline(spec, clone_dir)
    return result


# ---------------------------------------------------------------------------
# Report Generation
# ---------------------------------------------------------------------------
def generate_reports(results: List[RepoResult]) -> None:
    """Generate all certification campaign reports."""
    print("\n" + "=" * 72)
    print("GENERATING REPORTS")
    print("=" * 72)

    _write_repository_selection(results)
    _write_execution_matrix(results)
    _write_provider_coverage(results)
    _write_metric_results(results)
    _write_metric_validation(results)
    _write_confidence_analysis(results)
    _write_range_analysis(results)
    _write_determinism_report(results)
    _write_performance_report(results)
    _write_scientific_certification(results)
    _write_csv_files(results)
    _write_json_certification(results)


def _write_repository_selection(results: List[RepoResult]) -> None:
    lines = ["# 01 — Repository Selection\n"]
    lines.append(f"**Campaign Date:** {datetime.now(timezone.utc).isoformat()}\n")
    lines.append(f"**Total Repositories:** {len(results)}\n\n")
    lines.append("| # | Repository | Category | Rationale | Status |\n")
    lines.append("|---|-----------|----------|-----------|--------|\n")
    for i, r in enumerate(results, 1):
        status = "✅ Cloned" if r.clone_path else "❌ Failed"
        lines.append(f"| {i} | `{r.spec.repo_id}` | {r.spec.category} | {r.spec.rationale} | {status} |\n")

    lines.append("\n## Selection Criteria\n")
    lines.append("- **Small:** < 100 commits, minimal PR activity, baseline validation\n")
    lines.append("- **Medium:** 100-500 commits, moderate PR activity, cross-provider validation\n")
    lines.append("- **Large:** 500+ commits, high activity, stress testing\n")
    lines.append("- **Archived:** Historical commits, inactive PRs\n")
    lines.append("- **Experimental:** Massive scale, API rate limit handling\n")

    (CAMPAIGN_DIR / "01_REPOSITORY_SELECTION.md").write_text("".join(lines), encoding="utf-8")
    print("  [OK] 01_REPOSITORY_SELECTION.md")


def _write_execution_matrix(results: List[RepoResult]) -> None:
    lines = ["# 02 — Execution Matrix\n"]
    lines.append(
        "| Repository | Clone | Git Provider | GH PR Provider | Metadata Provider | Orchestrator | Graph | Metric Engine | Final |\n"
    )
    lines.append(
        "|-----------|-------|-------------|----------------|-------------------|-------------|-------|--------------|-------|\n"
    )

    for r in results:
        clone = "✅" if r.clone_path else "❌"
        git_prov = "✅" if "git.observation.v1" in r.providers_succeeded else ("⏭️" if r.spec.skip_github_api else "❌")
        gh_prov = (
            "✅" if "github.pr.observation.v1" in r.providers_succeeded else ("⏭️" if r.spec.skip_github_api else "❌")
        )
        meta_prov = (
            "✅"
            if "repository.metadata.observation.v1" in r.providers_succeeded
            else ("⏭️" if r.spec.skip_github_api else "❌")
        )
        orch = "✅" if r.orchestrator_time_s > 0 else "❌"
        graph = "✅" if r.graph_build_time_s > 0 else "❌"
        metric = "✅" if r.metric_engine_time_s > 0 else "❌"
        final = "✅" if r.success else "❌"
        lines.append(
            f"| `{r.spec.repo_id}` | {clone} | {git_prov} | {gh_prov} | {meta_prov} | {orch} | {graph} | {metric} | {final} |\n"
        )

    (CAMPAIGN_DIR / "02_EXECUTION_MATRIX.md").write_text("".join(lines), encoding="utf-8")
    print("  [OK] 02_EXECUTION_MATRIX.md")


def _write_provider_coverage(results: List[RepoResult]) -> None:
    lines = ["# 03 — Provider Coverage\n"]
    lines.append(
        "| Repository | Git (M-02,M-06) | GH PR (M-02,M-05) | Metadata (M-02,M-05) | Total Obs | Providers OK |\n"
    )
    lines.append(
        "|-----------|----------------|-------------------|----------------------|-----------|-------------|\n"
    )

    for r in results:
        git_ok = "✅" if "git.observation.v1" in r.providers_succeeded else "❌"
        gh_ok = "✅" if "github.pr.observation.v1" in r.providers_succeeded else "❌"
        meta_ok = "✅" if "repository.metadata.observation.v1" in r.providers_succeeded else "❌"
        n_ok = len(r.providers_succeeded)
        lines.append(
            f"| `{r.spec.repo_id}` | {git_ok} | {gh_ok} | {meta_ok} | {r.observations_extracted} | {n_ok}/3 |\n"
        )

    lines.append("\n## Provider Failure Analysis\n")
    for r in results:
        if r.providers_failed:
            lines.append(f"### {r.spec.repo_id}\n")
            for f in r.providers_failed:
                lines.append(f"- {f}\n")

    (CAMPAIGN_DIR / "03_PROVIDER_COVERAGE.md").write_text("".join(lines), encoding="utf-8")
    print("  [OK] 03_PROVIDER_COVERAGE.md")


def _write_metric_results(results: List[RepoResult]) -> None:
    lines = ["# 04 — Metric Results\n"]
    lines.append("| Repository | M-01 | M-02 | M-03 | M-04 | M-05 | M-06 | M-07 |\n")
    lines.append("|-----------|------|------|------|------|------|------|------|\n")

    for r in results:
        vals = []
        for mid in ALL_METRIC_IDS:
            d = r.metric_details.get(mid, {})
            v = d.get("value")
            if v is not None:
                if isinstance(v, float):
                    vals.append(f"{v:.4f}")
                else:
                    vals.append(str(v))
            else:
                vals.append("—")
        lines.append(f"| `{r.spec.repo_id}` | {' | '.join(vals)} |\n")

    lines.append("\n## Raw Values\n")
    for r in results:
        if r.success:
            lines.append(f"### {r.spec.repo_id}\n")
            for mid in ALL_METRIC_IDS:
                d = r.metric_details.get(mid, {})
                v = d.get("value")
                c = d.get("confidence", 0)
                n = d.get("observation_count", 0)
                pc = d.get("provider_count", 0)
                lines.append(f"- **{mid}**: value={v}, confidence={c:.3f}, obs={n}, providers={pc}\n")

    (CAMPAIGN_DIR / "04_METRIC_RESULTS.md").write_text("".join(lines), encoding="utf-8")
    print("  [OK] 04_METRIC_RESULTS.md")


def _write_metric_validation(results: List[RepoResult]) -> None:
    lines = ["# 05 — Metric Validation\n"]
    lines.append("## Range Validation\n\n")
    lines.append("| Repository | Metric | Value | Unit | Lower | Upper | In Range? |\n")
    lines.append("|-----------|--------|-------|------|-------|-------|----------|\n")

    for r in results:
        if not r.success:
            continue
        for mid in ALL_METRIC_IDS:
            d = r.metric_details.get(mid, {})
            v = d.get("value")
            unit = METRIC_INFO[mid]["unit"]
            lo, hi = METRIC_INFO[mid]["bounds"]
            if v is not None:
                in_range = lo <= v <= hi
                mark = "✅" if in_range else "❌"
                lines.append(f"| `{r.spec.repo_id}` | {mid} | {v} | {unit} | {lo} | {hi} | {mark} |\n")
            else:
                lines.append(f"| `{r.spec.repo_id}` | {mid} | — | {unit} | {lo} | {hi} | ⏭️ Missing |\n")

    lines.append("\n## Unit Consistency\n\n")
    for mid in ALL_METRIC_IDS:
        info = METRIC_INFO[mid]
        lines.append(
            f"- **{mid} ({info['name']})**: unit={info['unit']}, aggregation={info['aggregation']}, min_obs={info['min_obs']}\n"
        )

    (CAMPAIGN_DIR / "05_METRIC_VALIDATION.md").write_text("".join(lines), encoding="utf-8")
    print("  [OK] 05_METRIC_VALIDATION.md")


def _write_confidence_analysis(results: List[RepoResult]) -> None:
    lines = ["# 06 — Confidence Analysis\n"]
    lines.append("| Repository | Metric | Confidence | Obs Count | Providers |\n")
    lines.append("|-----------|--------|-----------|-----------|----------|\n")

    for r in results:
        if not r.success:
            continue
        for mid in ALL_METRIC_IDS:
            d = r.metric_details.get(mid, {})
            c = d.get("confidence", 0)
            n = d.get("observation_count", 0)
            pc = d.get("provider_count", 0)
            lines.append(f"| `{r.spec.repo_id}` | {mid} | {c:.3f} | {n} | {pc} |\n")

    lines.append("\n## Confidence Summary\n")
    lines.append("| Repository | Overall Confidence | Coverage | Observations |\n")
    lines.append("|-----------|-------------------|----------|-------------|\n")
    for r in results:
        if r.metric_collection:
            oc = r.metric_collection.overall_confidence
            cov = r.metric_collection.coverage
            lines.append(f"| `{r.spec.repo_id}` | {oc:.3f} | {cov:.1%} | {r.observations_extracted} |\n")

    (CAMPAIGN_DIR / "06_CONFIDENCE_ANALYSIS.md").write_text("".join(lines), encoding="utf-8")
    print("  [OK] 06_CONFIDENCE_ANALYSIS.md")


def _write_range_analysis(results: List[RepoResult]) -> None:
    lines = ["# 07 — Range Analysis\n"]
    lines.append("## Per-Metric Value Distribution\n\n")

    for mid in ALL_METRIC_IDS:
        info = METRIC_INFO[mid]
        lines.append(f"### {mid} — {info['name']}\n")
        lines.append(f"- Unit: {info['unit']}\n")
        lines.append(f"- Expected range: [{info['bounds'][0]}, {info['bounds'][1]}]\n")
        lines.append(f"- Aggregation: {info['aggregation']}\n\n")

        values = []
        for r in results:
            if not r.success:
                continue
            d = r.metric_details.get(mid, {})
            v = d.get("value")
            if v is not None:
                values.append((r.spec.repo_id, v))

        if values:
            vals = [v for _, v in values]
            lines.append(f"| Repository | Value |\n|-----------|-------|\n")
            for rid, v in values:
                lines.append(f"| `{rid}` | {v} |\n")
            lines.append(f"\n- Min: {min(vals)}\n")
            lines.append(f"- Max: {max(vals)}\n")
            lines.append(f"- Mean: {sum(vals)/len(vals):.4f}\n")
        else:
            lines.append("- No values computed\n")
        lines.append("\n")

    (CAMPAIGN_DIR / "07_RANGE_ANALYSIS.md").write_text("".join(lines), encoding="utf-8")
    print("  [OK] 07_RANGE_ANALYSIS.md")


def _write_determinism_report(results: List[RepoResult]) -> None:
    lines = ["# 08 — Determinism Report\n"]
    lines.append("| Repository | Run 1 Value | Run 2 Value | Match | Metric |\n")
    lines.append("|-----------|------------|------------|-------|--------|\n")

    all_match = True
    for r in results:
        if r.second_run_collection is None:
            continue
        for mid in ALL_METRIC_IDS:
            d1 = r.metric_details.get(mid, {})
            v1 = d1.get("value")
            if v1 is None:
                continue
            mr2 = r.second_run_collection.get_result(mid)
            v2 = mr2.value if mr2 else None
            match = "✅" if v1 == v2 else "❌"
            if v1 != v2:
                all_match = False
            lines.append(f"| `{r.spec.repo_id}` | {v1} | {v2} | {match} | {mid} |\n")

    lines.append(f"\n## Determinism Verdict: {'✅ PASS' if all_match else '❌ FAIL'}\n")

    (CAMPAIGN_DIR / "08_DETERMINISM_REPORT.md").write_text("".join(lines), encoding="utf-8")
    print("  [OK] 08_DETERMINISM_REPORT.md")


def _write_performance_report(results: List[RepoResult]) -> None:
    lines = ["# 09 — Performance Report\n"]
    lines.append(
        "| Repository | Clone (s) | Orchestrator (s) | Graph (s) | Metric Engine (s) | Total (s) | Obs | Providers |\n"
    )
    lines.append(
        "|-----------|----------|-----------------|----------|------------------|----------|-----|----------|\n"
    )

    for r in results:
        n_prov = len(r.providers_succeeded)
        lines.append(
            f"| `{r.spec.repo_id}` | {r.clone_time_s:.2f} | {r.orchestrator_time_s:.2f} | "
            f"{r.graph_build_time_s:.3f} | {r.metric_engine_time_s:.3f} | "
            f"{r.total_time_s:.2f} | {r.observations_extracted} | {n_prov}/3 |\n"
        )

    # Totals
    total_clone = sum(r.clone_time_s for r in results)
    total_orch = sum(r.orchestrator_time_s for r in results)
    total_graph = sum(r.graph_build_time_s for r in results)
    total_metric = sum(r.metric_engine_time_s for r in results)
    total_all = sum(r.total_time_s for r in results)
    total_obs = sum(r.observations_extracted for r in results)

    lines.append(
        f"\n**Totals:** Clone={total_clone:.1f}s, Orchestrator={total_orch:.1f}s, "
        f"Graph={total_graph:.2f}s, MetricEngine={total_metric:.2f}s, "
        f"Total={total_all:.1f}s, Observations={total_obs}\n"
    )

    (CAMPAIGN_DIR / "09_PERFORMANCE_REPORT.md").write_text("".join(lines), encoding="utf-8")
    print("  [OK] 09_PERFORMANCE_REPORT.md")


def _write_scientific_certification(results: List[RepoResult]) -> None:
    lines = ["# 10 — Scientific Certification\n"]
    lines.append(f"**Campaign Date:** {datetime.now(timezone.utc).isoformat()}\n\n")

    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    lines.append("## Summary\n\n")
    lines.append(f"- **Total repositories:** {len(results)}\n")
    lines.append(f"- **Successful:** {len(successful)}\n")
    lines.append(f"- **Failed:** {len(failed)}\n")
    lines.append(f"- **Success rate:** {len(successful)/len(results):.0%}\n\n")

    # Per-repo certification
    lines.append("## Repository Certifications\n\n")
    for r in results:
        if r.success:
            mc = r.metric_collection
            oc = mc.overall_confidence if mc else 0.0
            cov = mc.coverage if mc else 0.0
            n_metrics = sum(1 for mid in ALL_METRIC_IDS if r.metric_details.get(mid, {}).get("value") is not None)

            # Determine certification level
            if cov >= 0.7 and oc >= 0.5 and n_metrics >= 5:
                cert = "🥇 CERTIFIED"
            elif cov >= 0.4 and oc >= 0.3 and n_metrics >= 3:
                cert = "🥈 PARTIAL"
            else:
                cert = "🥉 MINIMAL"

            lines.append(f"### {r.spec.repo_id} — {cert}\n")
            lines.append(f"- Coverage: {cov:.0%}\n")
            lines.append(f"- Confidence: {oc:.3f}\n")
            lines.append(f"- Metrics computed: {n_metrics}/7\n")
            lines.append(f"- Providers succeeded: {len(r.providers_succeeded)}/3\n")
            lines.append(f"- Observations: {r.observations_extracted}\n")
            lines.append(f"- Warnings: {len(r.warnings)}\n\n")
        else:
            lines.append(f"### {r.spec.repo_id} — ❌ FAILED\n")
            lines.append(f"- Error: {r.error}\n\n")

    # Overall verdict
    n_certified = sum(1 for r in successful if r.metric_collection and r.metric_collection.coverage >= 0.7)
    n_partial = sum(1 for r in successful if r.metric_collection and 0.4 <= r.metric_collection.coverage < 0.7)
    n_minimal = sum(1 for r in successful if r.metric_collection and r.metric_collection.coverage < 0.4)

    lines.append("## Overall Verdict\n\n")
    lines.append(f"- 🥇 Certified: {n_certified}\n")
    lines.append(f"- 🥈 Partial: {n_partial}\n")
    lines.append(f"- 🥉 Minimal: {n_minimal}\n")
    lines.append(f"- ❌ Failed: {len(failed)}\n\n")

    if n_certified > 0:
        lines.append("**The scientific metric pipeline is operational.**\n")
    else:
        lines.append("**The scientific metric pipeline requires further investigation.**\n")

    (CAMPAIGN_DIR / "10_SCIENTIFIC_CERTIFICATION.md").write_text("".join(lines), encoding="utf-8")
    print("  [OK] 10_SCIENTIFIC_CERTIFICATION.md")


def _write_csv_files(results: List[RepoResult]) -> None:
    # repository_metrics.csv
    with open(CAMPAIGN_DIR / "repository_metrics.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "repository",
                "category",
                "success",
                "clone_time_s",
                "orchestrator_time_s",
                "graph_time_s",
                "metric_time_s",
                "total_time_s",
                "observations",
                "providers_ok",
                "overall_confidence",
                "coverage",
            ]
        )
        for r in results:
            oc = r.metric_collection.overall_confidence if r.metric_collection else 0
            cov = r.metric_collection.coverage if r.metric_collection else 0
            w.writerow(
                [
                    r.spec.repo_id,
                    r.spec.category,
                    r.success,
                    f"{r.clone_time_s:.2f}",
                    f"{r.orchestrator_time_s:.2f}",
                    f"{r.graph_build_time_s:.3f}",
                    f"{r.metric_engine_time_s:.3f}",
                    f"{r.total_time_s:.2f}",
                    r.observations_extracted,
                    len(r.providers_succeeded),
                    f"{oc:.3f}",
                    f"{cov:.3f}",
                ]
            )

    # metric_results.csv
    with open(CAMPAIGN_DIR / "metric_results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "repository",
                "metric_id",
                "value",
                "unit",
                "confidence",
                "observation_count",
                "provider_count",
                "computation_time_ms",
            ]
        )
        for r in results:
            for mid in ALL_METRIC_IDS:
                d = r.metric_details.get(mid, {})
                w.writerow(
                    [
                        r.spec.repo_id,
                        mid,
                        d.get("value", ""),
                        METRIC_INFO[mid]["unit"],
                        f"{d.get('confidence', 0):.3f}",
                        d.get("observation_count", 0),
                        d.get("provider_count", 0),
                        f"{d.get('computation_time_ms', 0):.1f}",
                    ]
                )

    # provider_coverage.csv
    with open(CAMPAIGN_DIR / "provider_coverage.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["repository", "provider_id", "status", "metric_ids", "observations"])
        for r in results:
            for pid in [GIT_PROVIDER_ID, GITHUB_PR_PROVIDER_ID, REPO_METADATA_PROVIDER_ID]:
                status = "succeeded" if pid in r.providers_succeeded else "failed"
                w.writerow([r.spec.repo_id, pid, status, "", ""])

    # metric_statistics.csv
    with open(CAMPAIGN_DIR / "metric_statistics.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric_id", "min_value", "max_value", "mean_value", "count", "unit"])
        for mid in ALL_METRIC_IDS:
            vals = []
            for r in results:
                if r.success:
                    d = r.metric_details.get(mid, {})
                    v = d.get("value")
                    if v is not None:
                        vals.append(v)
            if vals:
                w.writerow(
                    [mid, min(vals), max(vals), f"{sum(vals)/len(vals):.4f}", len(vals), METRIC_INFO[mid]["unit"]]
                )

    print("  [OK] CSV files written")


def _write_json_certification(results: List[RepoResult]) -> None:
    cert = {
        "campaign_date": datetime.now(timezone.utc).isoformat(),
        "total_repositories": len(results),
        "successful": sum(1 for r in results if r.success),
        "failed": sum(1 for r in results if not r.success),
        "repositories": [],
    }
    for r in results:
        repo_cert = {
            "repository": r.spec.repo_id,
            "category": r.spec.category,
            "success": r.success,
            "clone_time_s": r.clone_time_s,
            "orchestrator_time_s": r.orchestrator_time_s,
            "graph_time_s": r.graph_build_time_s,
            "metric_time_s": r.metric_engine_time_s,
            "total_time_s": r.total_time_s,
            "observations": r.observations_extracted,
            "providers_succeeded": r.providers_succeeded,
            "providers_failed": r.providers_failed,
            "metrics": {},
        }
        for mid in ALL_METRIC_IDS:
            d = r.metric_details.get(mid, {})
            repo_cert["metrics"][mid] = {
                "value": d.get("value"),
                "confidence": d.get("confidence", 0),
                "observation_count": d.get("observation_count", 0),
                "provider_count": d.get("provider_count", 0),
            }
        if r.metric_collection:
            repo_cert["overall_confidence"] = r.metric_collection.overall_confidence
            repo_cert["coverage"] = r.metric_collection.coverage
        cert["repositories"].append(repo_cert)

    (CAMPAIGN_DIR / "scientific_certification.json").write_text(
        json.dumps(cert, indent=2, default=str), encoding="utf-8"
    )
    print("  [OK] scientific_certification.json")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 72)
    print("PR-12B -- Scientific Metric Validation & Repository Certification Campaign")
    print("=" * 72)
    print(f"Date: {datetime.now(timezone.utc).isoformat()}")
    print(f"Repositories: {len(REPOSITORIES)}")

    # Report auth status
    auth = GitHubAuth()
    print(f"GitHub Auth: {summarize_auth_status(auth)}")
    print()

    REPOS_DIR.mkdir(parents=True, exist_ok=True)

    results: List[RepoResult] = []

    for i, spec in enumerate(REPOSITORIES, 1):
        print(f"\n{'=' * 60}")
        print(f"[{i}/{len(REPOSITORIES)}] Processing: {spec.repo_id} ({spec.category})")
        print(f"{'=' * 60}")

        result = run_pipeline(spec, REPOS_DIR)
        results.append(result)

        if result.success:
            mc = result.metric_collection
            n_metrics = sum(1 for mid in ALL_METRIC_IDS if result.metric_details.get(mid, {}).get("value") is not None)
            print(
                f"  [OK] SUCCESS -- {result.observations_extracted} obs, {n_metrics}/7 metrics, "
                f"confidence={mc.overall_confidence:.3f}, coverage={mc.coverage:.0%}"
            )
        else:
            print(f"  [FAIL] FAILED -- {result.error[:200]}")

    # Determinism verification (second run on first successful repo)
    first_ok = next((r for r in results if r.success), None)
    if first_ok:
        print(f"\n{'=' * 60}")
        print(f"Determinism check: running {first_ok.spec.repo_id} again...")
        print(f"{'=' * 60}")
        second = verify_determinism(first_ok.spec, REPOS_DIR)
        first_ok.second_run_collection = second.metric_collection
        if second.metric_collection and first_ok.metric_collection:
            # Compare metric values
            all_match = True
            for mid in ALL_METRIC_IDS:
                mr1 = first_ok.metric_collection.get_result(mid)
                mr2 = second.metric_collection.get_result(mid)
                if mr1 and mr2:
                    if mr1.value != mr2.value:
                        all_match = False
                        print(f"  [FAIL] {mid} mismatch: {mr1.value} vs {mr2.value}")
            first_ok.second_run_match = all_match
            print(f"  Determinism: {'[OK] PASS' if all_match else '[FAIL] FAIL'}")

    # Generate reports
    generate_reports(results)

    # Summary
    print("\n" + "=" * 72)
    print("CAMPAIGN COMPLETE")
    print("=" * 72)
    n_ok = sum(1 for r in results if r.success)
    print(f"Success: {n_ok}/{len(results)}")
    for r in results:
        status = "[OK]" if r.success else "[FAIL]"
        print(f"  {status} {r.spec.repo_id}")


if __name__ == "__main__":
    main()
