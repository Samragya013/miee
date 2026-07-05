import json
from pathlib import Path
reports = sorted(Path("benchmarks/pr14/results/test_full_fix").glob("analysis_report_*.json"))
with open(reports[-1]) as f:
    data = json.load(f)
ar = data["analysis_result"]
outputs = ar["detector_results"]["detector_outputs"]
for det_id, out in outputs.items():
    print(f"{det_id}: {json.dumps(out)[:200]}")
sp = ar["score_package"]
print(f"Integrity: {sp['integrity']['overall']:.3f}")
print(f"Confidence: {sp['confidence']['overall']:.3f}")
print(f"Band: {sp['confidence']['band']}")
print(f"Per-metric integrity: {sp['integrity']['per_metric']}")
