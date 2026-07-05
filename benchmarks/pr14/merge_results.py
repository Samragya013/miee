"""Merge fix results into existing benchmark results and regenerate reports."""
import csv, json, os, sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("PYTHONUTF8", "1")

RESULTS_DIR = Path(__file__).resolve().parent / "results"
ALL_METRIC_IDS = ["M-01", "M-02", "M-03", "M-04", "M-05", "M-06", "M-07"]
ALL_DETECTOR_IDS = ["D-01", "D-02", "D-03"]

# Load existing results
existing = {}
with open(RESULTS_DIR / "repositories.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        existing[row["repo_id"]] = row

# Load fix results
with open(RESULTS_DIR / "fix_results.json", encoding="utf-8") as f:
    fixes = json.load(f)

# Merge
for fix in fixes:
    repo_id = fix["repo_id"]
    if fix["success"]:
        # Update existing entry
        if repo_id in existing:
            existing[repo_id]["success"] = "True"
            existing[repo_id]["error"] = ""
            existing[repo_id]["metrics_computed"] = sum(1 for v in fix["metric_values"].values() if v is not None)
            existing[repo_id]["integrity_score"] = fix["integrity_score"]
            existing[repo_id]["confidence_score"] = fix["confidence_score"]
            existing[repo_id]["confidence_band"] = fix["confidence_band"]
            existing[repo_id]["pipeline_time_s"] = f"{fix['pipeline_time_s']:.2f}"
            existing[repo_id]["clone_time_s"] = f"{fix['clone_time_s']:.2f}"
        else:
            # Add new entry
            existing[repo_id] = {
                "repo_id": repo_id,
                "category": fix["category"],
                "size": fix["size"],
                "language": fix["language"],
                "success": "True",
                "error": "",
                "observations": 0,
                "metrics_computed": sum(1 for v in fix["metric_values"].values() if v is not None),
                "windows": fix.get("windows_count", 0),
                "integrity_score": fix["integrity_score"],
                "confidence_score": fix["confidence_score"],
                "confidence_band": fix["confidence_band"],
                "pipeline_time_s": f"{fix['pipeline_time_s']:.2f}",
                "clone_time_s": f"{fix['clone_time_s']:.2f}",
                "deterministic_match": "False",
                "warnings": 0,
            }

# Count
total = len(existing)
successful = sum(1 for r in existing.values() if r["success"] == "True")
print(f"Total: {total}, Successful: {successful}")

# Rewrite repositories.csv
with open(RESULTS_DIR / "repositories.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "repo_id", "category", "size", "language", "success", "error",
        "observations", "metrics_computed", "windows", "integrity_score",
        "confidence_score", "confidence_band", "pipeline_time_s",
        "clone_time_s", "deterministic_match", "warnings",
    ])
    writer.writeheader()
    for repo_id in sorted(existing.keys()):
        writer.writerow(existing[repo_id])

# Load fix metrics and merge into metrics.csv
# Load existing metrics.csv
existing_metrics = []
with open(RESULTS_DIR / "metrics.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        existing_metrics.append(row)

# Add fix metrics
for fix in fixes:
    if fix["success"]:
        # Remove old entries for this repo
        existing_metrics = [m for m in existing_metrics if m["repo_id"] != fix["repo_id"]]
        # Add new entries
        for mid in ALL_METRIC_IDS:
            v = fix["metric_values"].get(mid)
            if v is not None:
                existing_metrics.append({
                    "repo_id": fix["repo_id"],
                    "metric_id": mid,
                    "value": f"{v:.6f}",
                    "confidence": "",
                })

with open(RESULTS_DIR / "metrics.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["repo_id", "metric_id", "value", "confidence"])
    writer.writeheader()
    for row in existing_metrics:
        writer.writerow(row)

# Merge detectors.csv
existing_detectors = []
with open(RESULTS_DIR / "detectors.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        existing_detectors.append(row)

for fix in fixes:
    if fix["success"]:
        existing_detectors = [d for d in existing_detectors if d["repo_id"] != fix["repo_id"]]
        for det_id in ALL_DETECTOR_IDS:
            det = fix["detector_results"].get(det_id, {})
            existing_detectors.append({
                "repo_id": fix["repo_id"],
                "detector_id": det_id,
                "detected": det.get("detected", False),
                "severity": det.get("severity", 0.0),
                "events_count": det.get("events_count", 0),
                "executed": fix["detector_execution"].get(det_id, False),
            })

with open(RESULTS_DIR / "detectors.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["repo_id", "detector_id", "detected", "severity", "events_count", "executed"])
    writer.writeheader()
    for row in existing_detectors:
        writer.writerow(row)

# Merge scores.csv
existing_scores = []
with open(RESULTS_DIR / "scores.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        existing_scores.append(row)

for fix in fixes:
    if fix["success"]:
        existing_scores = [s for s in existing_scores if s["repo_id"] != fix["repo_id"]]
        existing_scores.append({
            "repo_id": fix["repo_id"],
            "integrity_score": fix["integrity_score"],
            "confidence_score": fix["confidence_score"],
            "confidence_band": fix["confidence_band"],
        })

with open(RESULTS_DIR / "scores.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["repo_id", "integrity_score", "confidence_score", "confidence_band"])
    writer.writeheader()
    for row in existing_scores:
        writer.writerow(row)

# Regenerate coverage.csv from scratch
fix_repos = {f["repo_id"] for f in fixes if f["success"]}

# Read existing coverage data
existing_coverage = []
try:
    with open(RESULTS_DIR / "coverage.csv", encoding="utf-8") as f2:
        reader = csv.reader(f2)
        next(reader)  # skip header
        for row in reader:
            if row[0] not in fix_repos:
                existing_coverage.append(row)
except (FileNotFoundError, StopIteration):
    pass

with open(RESULTS_DIR / "coverage.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["repo_id", "metric_id", "has_value"])
    for fix in fixes:
        if fix["success"]:
            for mid in ALL_METRIC_IDS:
                writer.writerow([fix["repo_id"], mid, fix["metric_values"].get(mid) is not None])
    for row in existing_coverage:
        writer.writerow(row)

# Regenerate summary.json
successful_repos = [r for r in existing.values() if r["success"] == "True"]
n_ok = len(successful_repos)

metric_coverage = {}
for mid in ALL_METRIC_IDS:
    # Count from metrics.csv
    has_val = sum(1 for m in existing_metrics if m["metric_id"] == mid)
    metric_coverage[mid] = has_val / n_ok if n_ok else 0

det_exec = {}
for det_id in ALL_DETECTOR_IDS:
    ran = sum(1 for d in existing_detectors if d["detector_id"] == det_id and d["executed"] == "True")
    det_exec[det_id] = ran / n_ok if n_ok else 0

det_rates = {}
for det_id in ALL_DETECTOR_IDS:
    detected = sum(1 for d in existing_detectors if d["detector_id"] == det_id and d["detected"] == "True")
    det_rates[det_id] = detected / n_ok if n_ok else 0

is_scores = [float(r["integrity_score"]) for r in successful_repos if r["integrity_score"]]
cs_scores = [float(r["confidence_score"]) for r in successful_repos if r["confidence_score"]]
pipeline_times = [float(r["pipeline_time_s"]) for r in successful_repos if r["pipeline_time_s"]]

def _stats(vals):
    if not vals:
        return {"mean": None, "min": None, "max": None, "count": 0}
    return {"mean": sum(vals)/len(vals), "min": min(vals), "max": max(vals), "count": len(vals)}

category_breakdown = {}
for cat in set(r["category"] for r in existing.values()):
    cat_repos = [r for r in existing.values() if r["category"] == cat]
    cat_ok = sum(1 for r in cat_repos if r["success"] == "True")
    category_breakdown[cat] = {"total": len(cat_repos), "successful": cat_ok, "success_rate": cat_ok/len(cat_repos) if cat_repos else 0}

language_breakdown = {}
for lang in set(r["language"] for r in existing.values()):
    lang_repos = [r for r in existing.values() if r["language"] == lang]
    lang_ok = sum(1 for r in lang_repos if r["success"] == "True")
    language_breakdown[lang] = {"total": len(lang_repos), "successful": lang_ok, "success_rate": lang_ok/len(lang_repos) if lang_repos else 0}

summary = {
    "campaign": "PR-14 Large-Scale Scientific Benchmark",
    "version": "1.6",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "seed": 42,
    "catalogue_size": total,
    "successful": n_ok,
    "failed": total - n_ok,
    "success_rate": n_ok / total if total else 0,
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
    "determinism_verified": 4,
}

with open(RESULTS_DIR / "summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, default=str)

print("Reports regenerated.")
print(f"Success rate: {n_ok}/{total} ({n_ok/total*100:.1f}%)")
