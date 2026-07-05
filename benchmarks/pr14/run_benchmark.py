"""
PR-14 Benchmark Runner — Executes the full MIIE pipeline on all catalogue repos.

Uses the proven CLI pipeline via subprocess for reliability.
Collects results from JSON reports and generates certification matrices.
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"


# ---------------------------------------------------------------------------
# Secure .env loading
# ---------------------------------------------------------------------------
def _load_dotenv_secure() -> None:
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
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            if key:
                os.environ.setdefault(key, value)
    except Exception:
        pass


_load_dotenv_secure()

# ---------------------------------------------------------------------------
# Catalogue import
# ---------------------------------------------------------------------------
from repository_catalogue import (
    CATALOGUE,
    RepoSpec,
    get_catalogue_size,
    get_category_counts,
    get_language_counts,
    get_size_counts,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CAMPAIGN_DIR = Path(__file__).resolve().parent
REPOS_DIR = CAMPAIGN_DIR / "repos"
RESULTS_DIR = CAMPAIGN_DIR / "results"
ALL_METRIC_IDS = ["M-01", "M-02", "M-03", "M-04", "M-05", "M-06", "M-07"]
ALL_DETECTOR_IDS = ["D-01", "D-02", "D-03"]
SEED = 42
CLONE_TIMEOUT = 120
PIPELINE_TIMEOUT = 180


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class RepoResult:
    spec: RepoSpec
    success: bool = False
    error: str = ""
    clone_time_s: float = 0.0
    pipeline_time_s: float = 0.0
    total_time_s: float = 0.0
    observations_extracted: int = 0
    metrics_computed: int = 0
    metric_values: Dict[str, Optional[float]] = field(default_factory=dict)
    metric_confidences: Dict[str, Optional[float]] = field(default_factory=dict)
    detector_results: Dict[str, Any] = field(default_factory=dict)
    detector_execution: Dict[str, bool] = field(default_factory=dict)
    integrity_score: Optional[float] = None
    confidence_score: Optional[float] = None
    confidence_band: str = ""
    windows_count: int = 0
    stage_timings: Dict[str, float] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    deterministic_match: bool = False
    report_path: str = ""


# ---------------------------------------------------------------------------
# Clone
# ---------------------------------------------------------------------------
def clone_repo(spec: RepoSpec) -> tuple[bool, str, float]:
    """Clone a repository. Returns (success, message, time_s)."""
    clone_path = REPOS_DIR / spec.repo_id.replace("/", "_")
    if clone_path.exists() and (clone_path / ".git").exists():
        return True, "cached", 0.0

    url = f"https://github.com/{spec.repo_id}.git"
    t0 = time.time()
    try:
        result = subprocess.run(
            ["git", "clone", "--depth=500", "--single-branch", url, str(clone_path)],
            capture_output=True, text=True, timeout=CLONE_TIMEOUT,
        )
        elapsed = time.time() - t0
        if result.returncode != 0:
            return False, f"git clone failed: {result.stderr[:200]}", elapsed
        return True, "cloned", elapsed
    except subprocess.TimeoutExpired:
        return False, "timeout", time.time() - t0
    except Exception as e:
        return False, str(e)[:200], time.time() - t0


# ---------------------------------------------------------------------------
# Pipeline execution via CLI
# ---------------------------------------------------------------------------
def run_pipeline(spec: RepoSpec) -> RepoResult:
    """Execute the full MIIE pipeline via CLI subprocess."""
    result = RepoResult(spec=spec)
    start_total = time.time()

    # Clone
    t0 = time.time()
    ok, msg, clone_time = clone_repo(spec)
    result.clone_time_s = clone_time
    result.stage_timings["clone"] = clone_time
    if not ok:
        result.error = f"Clone failed: {msg}"
        result.total_time_s = time.time() - start_total
        return result

    repo_path = REPOS_DIR / spec.repo_id.replace("/", "_")
    output_dir = RESULTS_DIR / "runs" / spec.repo_id.replace("/", "_")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run CLI pipeline
    t0 = time.time()
    cmd = [
        sys.executable, "-m", "miie.cli", "analyze",
        str(repo_path),
        "-m", "M-01", "-m", "M-02", "-m", "M-03", "-m", "M-04",
        "-m", "M-05", "-m", "M-06", "-m", "M-07",
        "-d", "D-01", "-d", "D-02", "-d", "D-03",
        "-o", str(output_dir),
        "--seed", str(SEED),
        "-f", "json",
        "--window-size", "7",
    ]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True, text=True,
            timeout=PIPELINE_TIMEOUT,
            cwd=str(REPO_ROOT),
        )
        result.stage_timings["pipeline"] = time.time() - t0
        result.pipeline_time_s = result.stage_timings["pipeline"]

        if proc.returncode != 0:
            stderr = proc.stderr[:500] if proc.stderr else proc.stdout[:500]
            result.error = f"Pipeline exit {proc.returncode}: {stderr}"
            result.total_time_s = time.time() - start_total
            return result

    except subprocess.TimeoutExpired:
        result.error = f"Pipeline timeout ({PIPELINE_TIMEOUT}s)"
        result.total_time_s = time.time() - start_total
        return result
    except Exception as e:
        result.error = f"Pipeline error: {str(e)[:200]}"
        result.total_time_s = time.time() - start_total
        return result

    # Parse JSON report
    try:
        report_files = list(output_dir.glob("analysis_report_*.json"))
        if not report_files:
            result.error = "No JSON report found"
            result.total_time_s = time.time() - start_total
            return result

        report_path = sorted(report_files)[-1]
        result.report_path = str(report_path)
        with open(report_path, encoding="utf-8") as f:
            report = json.load(f)

        # Navigate to analysis_result (CLI wraps results under this key)
        ar = report.get("analysis_result", report)

        # Extract metrics — structure: {"M-01": {"w00": [value]}, ...}
        metrics = ar.get("metric_dataframe", {}).get("metrics", {})
        for mid in ALL_METRIC_IDS:
            mdata = metrics.get(mid)
            if mdata and isinstance(mdata, dict):
                w00 = mdata.get("w00")
                if w00 and len(w00) > 0 and w00[0] is not None:
                    result.metric_values[mid] = w00[0]
                    result.metric_confidences[mid] = None  # Not in report format
                else:
                    result.metric_values[mid] = None
                    result.metric_confidences[mid] = None
            else:
                result.metric_values[mid] = None
                result.metric_confidences[mid] = None
        result.metrics_computed = sum(1 for v in result.metric_values.values() if v is not None)

        # Extract observations
        result.observations_extracted = ar.get("analysis_summary", {}).get("total_observations", 0) if ar.get("analysis_summary") else 0

        # Extract windows — windows is a list of window objects
        windows_data = ar.get("windows", [])
        result.windows_count = len(windows_data) if isinstance(windows_data, list) else 0

        # Extract detector results — structure: {"D-01": {...}, "D-02": {...}, "D-03": {...}}
        det_outputs = ar.get("detector_results", {}).get("detector_outputs", {})
        for det_id in ALL_DETECTOR_IDS:
            det_out = det_outputs.get(det_id, {})
            if det_out:
                # Check for error/skipped status
                is_error = det_out.get("status") in ("error", "skipped")
                if is_error:
                    result.detector_results[det_id] = {
                        "detected": False,
                        "severity": 0.0,
                        "events_count": 0,
                        "status": det_out["status"],
                        "reason": det_out.get("reason", ""),
                    }
                    result.detector_execution[det_id] = False
                else:
                    # Determine detection type by detector
                    detected_key = {
                        "D-01": "drift_detected",
                        "D-02": "breakdown_detected",
                        "D-03": "compression_detected",
                    }.get(det_id, "detected")
                    detected = det_out.get(detected_key, False)
                    events_key = {
                        "D-01": "drift_events",
                        "D-02": "breakdown_events",
                        "D-03": "compression_events",
                    }.get(det_id, "events")
                    result.detector_results[det_id] = {
                        "detected": detected,
                        "severity": det_out.get("severity", 0.0),
                        "events_count": len(det_out.get(events_key, [])),
                        "status": "executed",
                    }
                    result.detector_execution[det_id] = True
            else:
                result.detector_results[det_id] = {"detected": False, "severity": 0.0, "events_count": 0, "status": "missing"}
                result.detector_execution[det_id] = False

        # Extract scores — structure: score_package.integrity.overall, score_package.confidence.overall
        sp = ar.get("score_package", {})
        result.integrity_score = sp.get("integrity", {}).get("overall")
        result.confidence_score = sp.get("confidence", {}).get("overall")
        result.confidence_band = sp.get("confidence", {}).get("band", "")

        # Stage timings
        timings = ar.get("stage_timings", {})
        for stage, t in timings.items():
            result.stage_timings[stage] = t

        result.success = True
    except Exception as e:
        result.error = f"Report parsing failed: {str(e)[:200]}"

    result.total_time_s = time.time() - start_total
    return result


# ---------------------------------------------------------------------------
# Determinism verification
# ---------------------------------------------------------------------------
def verify_determinism(spec: RepoSpec, first_result: RepoResult) -> bool:
    """Re-run the pipeline and check metric values match (within tolerance)."""
    second = run_pipeline(spec)
    if not second.success:
        return False
    for mid in ALL_METRIC_IDS:
        v1 = first_result.metric_values.get(mid)
        v2 = second.metric_values.get(mid)
        if v1 is None and v2 is None:
            continue
        if v1 is None or v2 is None:
            return False
        # Allow 0.1% tolerance for float comparison
        if abs(v1 - v2) > max(1e-9, 0.001 * abs(v1)):
            return False
    return True


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------
def generate_reports(results: List[RepoResult]) -> None:
    """Generate all certification matrices and aggregate reports."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    successful = [r for r in results if r.success]
    n_ok = len(successful)
    n_total = len(results)

    # --- repositories.csv ---
    with open(RESULTS_DIR / "repositories.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "repo_id", "category", "size", "language", "success", "error",
            "observations", "metrics_computed", "windows", "integrity_score",
            "confidence_score", "confidence_band", "pipeline_time_s",
            "clone_time_s", "deterministic_match", "warnings",
        ])
        for r in results:
            writer.writerow([
                r.spec.repo_id, r.spec.category.value, r.spec.size.value,
                r.spec.language.value, r.success, r.error[:100],
                r.observations_extracted, r.metrics_computed, r.windows_count,
                r.integrity_score, r.confidence_score, r.confidence_band,
                f"{r.pipeline_time_s:.2f}", f"{r.clone_time_s:.2f}",
                r.deterministic_match, len(r.warnings),
            ])

    # --- metrics.csv ---
    with open(RESULTS_DIR / "metrics.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["repo_id", "metric_id", "value", "confidence"])
        for r in successful:
            for mid in ALL_METRIC_IDS:
                v = r.metric_values.get(mid)
                c = r.metric_confidences.get(mid)
                if v is not None:
                    writer.writerow([r.spec.repo_id, mid, f"{v:.6f}", f"{c:.6f}" if c else ""])

    # --- detectors.csv ---
    with open(RESULTS_DIR / "detectors.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["repo_id", "detector_id", "detected", "severity", "events_count", "executed"])
        for r in successful:
            for det_id in ALL_DETECTOR_IDS:
                det = r.detector_results.get(det_id, {})
                writer.writerow([
                    r.spec.repo_id, det_id,
                    det.get("detected", False),
                    det.get("severity", 0.0),
                    det.get("events_count", 0),
                    r.detector_execution.get(det_id, False),
                ])

    # --- scores.csv ---
    with open(RESULTS_DIR / "scores.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["repo_id", "integrity_score", "confidence_score", "confidence_band"])
        for r in successful:
            writer.writerow([r.spec.repo_id, r.integrity_score, r.confidence_score, r.confidence_band])

    # --- coverage.csv ---
    with open(RESULTS_DIR / "coverage.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["repo_id", "metric_id", "has_value"])
        for r in successful:
            for mid in ALL_METRIC_IDS:
                writer.writerow([r.spec.repo_id, mid, r.metric_values.get(mid) is not None])

    # --- performance.csv ---
    with open(RESULTS_DIR / "performance.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["repo_id", "stage", "time_s"])
        for r in results:
            for stage, t in r.stage_timings.items():
                writer.writerow([r.spec.repo_id, stage, f"{t:.3f}"])

    # --- summary.json ---
    metric_coverage = {}
    for mid in ALL_METRIC_IDS:
        has_val = sum(1 for r in successful if r.metric_values.get(mid) is not None)
        metric_coverage[mid] = has_val / n_ok if n_ok else 0

    det_exec = {}
    for det_id in ALL_DETECTOR_IDS:
        ran = sum(1 for r in successful if r.detector_execution.get(det_id, False))
        det_exec[det_id] = ran / n_ok if n_ok else 0

    det_rates = {}
    for det_id in ALL_DETECTOR_IDS:
        detected = sum(1 for r in successful if r.detector_results.get(det_id, {}).get("detected", False))
        det_rates[det_id] = detected / n_ok if n_ok else 0

    is_scores = [r.integrity_score for r in successful if r.integrity_score is not None]
    cs_scores = [r.confidence_score for r in successful if r.confidence_score is not None]
    pipeline_times = [r.pipeline_time_s for r in successful]

    def _stats(vals):
        if not vals:
            return {"mean": None, "min": None, "max": None, "count": 0}
        return {
            "mean": sum(vals) / len(vals),
            "min": min(vals),
            "max": max(vals),
            "count": len(vals),
        }

    category_breakdown = {}
    for cat in set(r.spec.category.value for r in results):
        cat_results = [r for r in results if r.spec.category.value == cat]
        cat_ok = sum(1 for r in cat_results if r.success)
        category_breakdown[cat] = {
            "total": len(cat_results),
            "successful": cat_ok,
            "success_rate": cat_ok / len(cat_results) if cat_results else 0,
        }

    language_breakdown = {}
    for lang in set(r.spec.language.value for r in results):
        lang_results = [r for r in results if r.spec.language.value == lang]
        lang_ok = sum(1 for r in lang_results if r.success)
        language_breakdown[lang] = {
            "total": len(lang_results),
            "successful": lang_ok,
            "success_rate": lang_ok / len(lang_results) if lang_results else 0,
        }

    summary = {
        "campaign": "PR-14 Large-Scale Scientific Benchmark",
        "version": "1.6",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "seed": SEED,
        "catalogue_size": n_total,
        "successful": n_ok,
        "failed": n_total - n_ok,
        "success_rate": n_ok / n_total if n_total else 0,
        "metric_coverage": metric_coverage,
        "detector_execution_rates": det_exec,
        "detection_rates": det_rates,
        "score_statistics": {
            "integrity_score": _stats(is_scores),
            "confidence_score": _stats(cs_scores),
        },
        "performance": {
            "mean_pipeline_time_s": _stats(pipeline_times)["mean"],
            "max_pipeline_time_s": _stats(pipeline_times)["max"],
            "min_pipeline_time_s": _stats(pipeline_times)["min"],
            "total_time_s": sum(pipeline_times),
        },
        "category_breakdown": category_breakdown,
        "language_breakdown": language_breakdown,
        "determinism_verified": sum(1 for r in results if r.deterministic_match),
    }

    with open(RESULTS_DIR / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\nReports generated in {RESULTS_DIR}/")
    for fn in ["repositories.csv", "metrics.csv", "detectors.csv", "scores.csv",
               "coverage.csv", "performance.csv", "summary.json"]:
        print(f"  {fn}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 72)
    print("PR-14 — Large-Scale Scientific Benchmark & Detector Certification")
    print("=" * 72)
    print(f"Date: {datetime.now(timezone.utc).isoformat()}")
    print(f"Catalogue: {get_catalogue_size()} repositories")
    print(f"Categories: {get_category_counts()}")
    print(f"Languages: {get_language_counts()}")
    print(f"Sizes: {get_size_counts()}")
    print()

    REPOS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    results: List[RepoResult] = []
    start_campaign = time.time()

    for i, spec in enumerate(CATALOGUE, 1):
        print(f"[{i}/{get_catalogue_size()}] {spec.repo_id} ({spec.category.value}/{spec.language.value})", end=" ", flush=True)
        result = run_pipeline(spec)
        results.append(result)

        if result.success:
            n_met = result.metrics_computed
            det_flags = "".join(
                "!" if result.detector_results.get(d, {}).get("detected") else "."
                for d in ALL_DETECTOR_IDS
            )
            is_str = f"{result.integrity_score:.3f}" if result.integrity_score is not None else "—"
            cs_str = f"{result.confidence_score:.3f}" if result.confidence_score is not None else "—"
            print(
                f"OK [{n_met}/7, IS={is_str}, CS={cs_str}, {det_flags}] "
                f"({result.pipeline_time_s:.1f}s)"
            )
        else:
            print(f"FAIL: {result.error[:80]}")

    # Determinism check on first 5 successful repos
    successful = [r for r in results if r.success]
    if successful:
        print(f"\n{'=' * 60}")
        print("Determinism verification (first 5 successful repos)...")
        for r in successful[:5]:
            print(f"  {r.spec.repo_id}...", end=" ", flush=True)
            match = verify_determinism(r.spec, r)
            r.deterministic_match = match
            print("PASS" if match else "FAIL")

    campaign_time = time.time() - start_campaign
    generate_reports(results)

    # Final summary
    n_ok = sum(1 for r in results if r.success)
    print(f"\n{'=' * 72}")
    print("CAMPAIGN COMPLETE")
    print(f"{'=' * 72}")
    print(f"Total time: {campaign_time:.0f}s ({campaign_time/60:.1f} min)")
    print(f"Success: {n_ok}/{len(results)} ({n_ok/len(results)*100:.1f}%)")
    print(f"Determinism: {sum(1 for r in results if r.deterministic_match)}/{min(5, n_ok)} verified")


if __name__ == "__main__":
    main()
