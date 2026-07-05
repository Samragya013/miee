import json
from pathlib import Path
reports = sorted(Path("benchmarks/pr14/results/top5/pympler_pympler").glob("analysis_report_*.json"))
with open(reports[-1]) as f:
    data = json.load(f)
ar = data["analysis_result"]
outputs = ar["detector_results"]["detector_outputs"]
for det_id, out in outputs.items():
    if isinstance(out, dict):
        print(f"{det_id}: keys={list(out.keys())[:10]}")
        detected = out.get("detected", "N/A")
        severity = out.get("severity", "N/A")
        events = out.get("events", [])
        print(f"  detected={detected}, severity={severity}, events={len(events)}")
    else:
        print(f"{det_id}: type={type(out)}, val={str(out)[:100]}")

# Check metric_dataframe structure
mdf = ar.get("metric_dataframe", {})
print(f"\nmetric_dataframe type: {type(mdf)}")
if isinstance(mdf, dict):
    print(f"  keys: {list(mdf.keys())[:10]}")
    if "metrics" in mdf:
        for mk, mv in mdf["metrics"].items():
            if mv is None:
                print(f"  {mk}: None")
            elif isinstance(mv, dict):
                non_empty = sum(1 for v in mv.values() if v is not None and len(v) > 0)
                print(f"  {mk}: {non_empty}/{len(mv)} windows with data")
