import json
from pathlib import Path
reports = sorted(Path("benchmarks/pr14/results/top5/pympler_pympler").glob("analysis_report_*.json"))
with open(reports[-1]) as f:
    data = json.load(f)
ar = data["analysis_result"]
outputs = ar["detector_results"]["detector_outputs"]
for det_id, out in outputs.items():
    print(f"{det_id}: {json.dumps(out)[:300]}")
