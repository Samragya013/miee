## Orchestration Structure Audit

Files
- src/miie/orchestration/pipeline.py
- src/miie/orchestration/workflow.py

Classes
- AnalysisPipeline (in pipeline.py)
- WorkflowType (Enum, in workflow.py)
- WorkflowDispatcher (in workflow.py)

Methods
AnalysisPipeline:
- __init__(self, ingestion_engine, extraction_engine, segmentation_engine, detection_engine, scoring_engine, evidence_engine, explanation_engine, report_generator, benchmark_engine=None, evaluation_engine=None)
- run_analysis(self, repo_path, metric_list, cache_dir=None, keep_cache=False, shallow_depth=None, since=None, until=None, exclude_bots=False, segmentation_strategy="time", segmentation_size=7, detector_config=None, enabled_detectors=None, detector_weights=None, output_formats=None, output_dir=None)
- run_benchmark(self, suite_id, detector_ids, config, seed=42)
- evaluate_benchmark(self, benchmark_run, ground_truth)

WorkflowType (Enum):
- WF_01 = "basic_analysis"
- WF_02 = "with_evidence"
- WF_03 = "full_analysis"
- WF_04 = "benchmark_only"
- WF_05 = "evaluation_only"

WorkflowDispatcher:
- __init__(self, pipeline)
- execute_workflow(self, workflow_type, repo_path=None, metric_list=None, **kwargs)
- _execute_wf_01(self, repo_path, metric_list, **kwargs) [WF_01: Basic analysis workflow]
- _execute_wf_02(self, repo_path, metric_list, **kwargs) [WF_02: Analysis with evidence generation]
- _execute_wf_03(self, repo_path, metric_list, **kwargs) [WF_03: Full analysis workflow]
- _execute_wf_04(self, **kwargs) [WF_04: Benchmark execution only]
- _execute_wf_05(self, **kwargs) [WF_05: Evaluation of benchmark results]
- _record_workflow(self, result)
- get_workflow_history(self)
- clear_workflow_history(self)

Status: FILES_EXIST (both required files present)