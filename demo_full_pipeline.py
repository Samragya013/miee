"""MIIE v1.0.0 — Full Pipeline Demo"""
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
import time

print("=" * 60)
print("  MIIE v1.0.0 - Full Pipeline Demo")
print("=" * 60)
print()

# Step 1: Ingestion
print("Stage 1/8: Repository Ingestion")
t0 = time.time()
ctx = RepositoryIngestionEngine().ingest(".")
print(f"  Repo ID:       {ctx.repo_id[:32]}...")
print(f"  Commits:       {ctx.total_commits}")
print(f"  Contributors:  {ctx.contributor_count}")
print(f"  Local path:    {ctx.local_path}")
print(f"  Time: {time.time()-t0:.2f}s")
print()

# Step 2: Extraction
print("Stage 2/8: Metric Extraction (M-02, M-06)")
t0 = time.time()
df = MetricExtractionEngine().extract(ctx, metric_list=["M-02", "M-06"])
print(f"  Metrics: {list(df.metrics.keys())}")
for name, vals in df.metrics.items():
    if vals is None:
        print(f"    {name}: None")
    else:
        print(f"    {name}: {len(vals)} values")
print(f"  Time: {time.time()-t0:.2f}s")
print()

# Step 3: Segmentation
print("Stage 3/8: Window Segmentation")
t0 = time.time()
seg = WindowSegmentationEngine()
windows = seg.segment(df, strategy="time", size=7)
print(f"  Strategy: time, size=7")
print(f"  Windows: {len(windows)}")
for w in windows[:3]:
    print(f"    {w.window_id}: {w.start_date} to {w.end_date}")
print(f"  Time: {time.time()-t0:.2f}s")
print()

# Step 4: Detection
print("Stage 4/8: Anomaly Detection (D-01, D-02, D-03)")
t0 = time.time()
registry = DetectorRegistry()
registry.register(DistributionDriftDetector())
registry.register(CorrelationBreakdownDetector())
registry.register(ThresholdCompressionDetector())
dispatcher = DetectorDispatcherEngine(registry)
det_results = dispatcher.invoke(df, windows, enabled_detectors=["D-01", "D-02", "D-03"])
print(f"  Detectors run: {list(det_results.detector_outputs.keys())}")
for det_id, det_out in det_results.detector_outputs.items():
    anomalies = det_out.get("anomaly_count", 0)
    print(f"    {det_id}: {anomalies} anomalies detected")
print(f"  Time: {time.time()-t0:.2f}s")
print()

# Step 5: Scoring
print("Stage 5/8: Integrity Scoring")
t0 = time.time()
scorer = ScoringEngine()
score_result = scorer.compute_integrity_score(det_results, df, windows)
print(f"  Integrity:  {score_result.integrity['overall']:.4f}")
print(f"  Confidence: {score_result.confidence['overall']:.4f}")
print(f"  Per-metric integrity:")
for metric, val in score_result.integrity["per_metric"].items():
    print(f"    {metric}: {val:.4f}")
print(f"  Confidence factors:")
for factor, val in score_result.confidence["factors"].items():
    print(f"    {factor}: {val:.4f}")
print(f"  Formula version: {score_result.formula_version}")
print(f"  Time: {time.time()-t0:.2f}s")
print()

# Step 6: Evidence
print("Stage 6/8: Evidence Package")
t0 = time.time()
evidence_engine = EvidenceEngine()
evidence = evidence_engine.generate(ctx, df, windows, det_results, score_result, {})
print(f"  Provenance:   {evidence.provenance.miie_version}")
print(f"  Windows:      {len(evidence.windows)}")
print(f"  Metrics:      {list(evidence.metrics.keys())}")
print(f"  Detectors:    {list(evidence.detector_outputs.detector_outputs.keys())}")
print(f"  Time: {time.time()-t0:.2f}s")
print()

# Step 7: Explanation
print("Stage 7/8: Explanation Generation")
t0 = time.time()
explainer = ExplanationEngine()
explanation = explainer.generate(evidence, score_result)
print(f"  Narratives:    {len(explanation.narratives)}")
print(f"  Recommendations: {len(explanation.recommendations)}")
for i, rec in enumerate(explanation.recommendations[:3], 1):
    short = rec[:80] + "..." if len(rec) > 80 else rec
    print(f"    {i}. {short}")
print(f"  Time: {time.time()-t0:.2f}s")
print()

print("=" * 60)
print("  Pipeline Complete - All 7 stages executed successfully")
print("=" * 60)
