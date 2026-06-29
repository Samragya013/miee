import json
from datetime import datetime, timezone
from pathlib import Path

base = Path("benchmarks/datasets/candidates")
manifest = {
    "benchmark_info": {
        "name": "MIIE Synthetic Benchmark Candidates",
        "version": "1.0.0",
        "description": "Synthetic benchmark candidates for testing MIIE detector algorithms",
        "generation_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "total_candidates": 120,
        "status": "candidate",
    },
    "candidates": {},
}

for cdir in sorted(base.iterdir()):
    if not cdir.is_dir():
        continue
    meta_path = cdir / "metadata.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        cid = cdir.name
        manifest["candidates"][cid] = {
            "id": cid,
            "name": cid,
            "repo_id": meta.get("repo_id", ""),
            "anomaly_present": meta.get("anomaly_present", False),
            "anomaly_type": meta.get("anomaly_type"),
            "expected_metrics": meta.get("expected_metrics", []),
            "tags": ["synthetic"],
            "path": "datasets/candidates/" + cid,
        }

manifest_path = Path("benchmarks/metadata/candidate_manifest.json")
manifest_path.parent.mkdir(parents=True, exist_ok=True)
manifest_path.write_text(json.dumps(manifest, indent=2))
count = len(manifest["candidates"])
print("Manifest updated with " + str(count) + " candidates")
