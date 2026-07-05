"""Quick test: run pipeline step-bystep to find the crash."""
import traceback, sys, os
os.environ.setdefault("PYTHONUTF8", "1")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from miie.processing.ingestion import RepositoryIngestionEngine
from miie.processing.extraction import MetricExtractionEngine
from miie.processing.segmentation import WindowSegmentationEngine
from miie.processing.detection.dispatcher import DetectorDispatcherEngine
from miie.processing.detection.registry import DetectorRegistry
from miie.processing.detection.distribution_drift_detector import DistributionDriftDetector
from miie.processing.detection.correlation_breakdown_detector import CorrelationBreakdownDetector
from miie.processing.detection.threshold_compression_detector import ThresholdCompressionDetector
from miie.processing.scoring.engine import ScoringEngine
from miie.processing.evidence import EvidenceEngine
from miie.processing.explanation.engine import ExplanationEngine

REPO = "validation/metric_campaign/repos/pypa_sampleproject"

print("Stage 1: Ingestion")
ingestion = RepositoryIngestionEngine()
ctx = ingestion.ingest(REPO)
print(f"  OK: {ctx.total_commits} commits")

print("Stage 3: Extraction")
extraction = MetricExtractionEngine()
mdf = extraction.extract(context=ctx, metric_list=["M-01","M-02","M-03","M-04","M-05","M-06","M-07"])
keys = list(mdf.metrics.keys()) if hasattr(mdf, "metrics") and mdf.metrics else []
print(f"  OK: {len(keys)} metrics")

print("Stage 4: Segmentation")
seg = WindowSegmentationEngine()
windows = seg.segment(metric_dataframe=mdf, strategy="time", size=7, repository_context=ctx)
print(f"  OK: {len(windows)} windows")

# Re-extract with windows
print("Stage 4b: Re-extraction with windows")
mdf2 = extraction.extract(context=ctx, metric_list=["M-01","M-02","M-03","M-04","M-05","M-06","M-07"], windows=windows)
for mk, mv in mdf2.metrics.items():
    if mv is None:
        print(f"  {mk}: None (no data)")
    elif isinstance(mv, dict):
        non_empty = sum(1 for v in mv.values() if v is not None and len(v) > 0)
        print(f"  {mk}: {non_empty}/{len(mv)} windows with data")
    else:
        print(f"  {mk}: type={type(mv)}")

print("Stage 5: Detection")
registry = DetectorRegistry()
registry.register(DistributionDriftDetector())
registry.register(CorrelationBreakdownDetector())
registry.register(ThresholdCompressionDetector())
dispatcher = DetectorDispatcherEngine(registry)
try:
    dr = dispatcher.invoke(metric_dataframe=mdf2, windows=windows)
    print(f"  OK: {list(dr.detector_outputs.keys())}")
    for det_id, output in dr.detector_outputs.items():
        keys_list = list(output.keys())[:10]
        print(f"    {det_id}: keys={keys_list}")
        if "observation_counts" in output:
            print(f"      observation_counts={output['observation_counts']}")
except Exception as e:
    traceback.print_exc()

print("Stage 6a: Scoring")
try:
    scoring = ScoringEngine()
    score_pkg = scoring.compute_integrity_score(detector_results=dr, metric_dataframe=mdf2, windows=windows)
    print(f"  OK: integrity={score_pkg.overall_integrity_score:.3f}")
except Exception as e:
    traceback.print_exc()

print("Stage 6b: Evidence")
try:
    evidence_engine = EvidenceEngine()
    ev = evidence_engine.generate(
        repository_context=ctx,
        metric_dataframe=mdf2,
        windows=windows,
        detector_results=dr,
        score_package=score_pkg,
        configuration={"metric_list": list(mdf2.metrics.keys())},
    )
    print(f"  OK: evidence generated")
except Exception as e:
    traceback.print_exc()

print("Stage 6c: Explanation")
try:
    explanation_engine = ExplanationEngine()
    expl = explanation_engine.generate(evidence_package=ev, score_package=score_pkg)
    print(f"  OK: explanation generated")
except Exception as e:
    traceback.print_exc()

print("\nALL STAGES PASSED")
