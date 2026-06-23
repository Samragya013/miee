"""Check API shapes"""
from miie.processing.ingestion import RepositoryIngestionEngine
from miie.processing.extraction import MetricExtractionEngine
from miie.processing.segmentation import WindowSegmentationEngine
from miie.processing.detection.dispatcher import DetectorDispatcherEngine
from miie.processing.scoring.engine import ScoringEngine
from miie.processing.evidence import EvidenceEngine
from miie.processing.explanation.engine import ExplanationEngine
import inspect

ctx = RepositoryIngestionEngine().ingest(".")
df = MetricExtractionEngine().extract(ctx, metric_list=["M-02", "M-06"])

print("MetricDataFrame type:", type(df))
print("MetricDataFrame attrs:", [a for a in dir(df) if not a.startswith("_")])
print("Metrics:", list(df.metrics.keys()))
print()

seg = WindowSegmentationEngine()
windows = seg.segment(ctx, strategy="time", size=7)
print("Windows type:", type(windows))
print("Windows len:", len(windows))
if windows:
    w = windows[0]
    print("Window type:", type(w))
    print("Window attrs:", [a for a in dir(w) if not a.startswith("_")])
print()

# Check dispatcher.invoke
print("Dispatcher invoke sig:", inspect.signature(DetectorDispatcherEngine.invoke))
# Try calling it
dispatcher = DetectorDispatcherEngine()
det_results = dispatcher.invoke(df, windows, enabled_detectors=["D-01", "D-02", "D-03"])
print("DetResults type:", type(det_results))
print("DetResults attrs:", [a for a in dir(det_results) if not a.startswith("_")])
print("Detector outputs:", list(det_results.detector_outputs.keys()))
print()

# Check scoring
scorer = ScoringEngine()
score_result = scorer.compute_integrity_score(det_results, df, windows)
print("ScorePackage type:", type(score_result))
print("ScorePackage attrs:", [a for a in dir(score_result) if not a.startswith("_")])
print("Overall score:", score_result.overall_score)
print("Components:", score_result.component_scores)
print()

# Check evidence
evidence_engine = EvidenceEngine()
evidence = evidence_engine.generate(ctx, df, windows, det_results, score_result, {})
print("Evidence type:", type(evidence))
print("Evidence attrs:", [a for a in dir(evidence) if not a.startswith("_")])
print()

# Check explanation
explainer = ExplanationEngine()
explanation = explainer.generate(evidence, score_result)
print("Explanation type:", type(explanation))
print("Explanation attrs:", [a for a in dir(explanation) if not a.startswith("_")])
print("Narratives:", len(explanation.narratives))
print("Recommendations:", len(explanation.recommendations))
print()

print("ALL STAGES WORK!")
