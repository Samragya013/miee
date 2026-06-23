# MIIE Benchmarks

This directory contains benchmark datasets, ground truth data, annotations, and metadata for the MIIE (Minimal Invariant Information Extraction) project.

## Directory Structure

```
benchmarks/
├── datasets/
│   └── candidates/
│       ├── candidate_001/
│       ├── candidate_002/
│       └── ... (up to candidate_030)
├── ground_truth/
│   └── draft/
├── annotations/
│   ├── reviewer_a/
│   ├── reviewer_b/
│   └── adjudication/
└── metadata/
    └── candidate_manifest.json
```

## Benchmark Candidates

There are 30 synthetic benchmark candidates in `benchmarks/datasets/candidates/` labeled `candidate_001` through `candidate_030`. Each candidate represents a synthetic repository with specific characteristics designed to test different aspects of the MIIE analysis pipeline.

## Annotation Workflow

See `benchmarks/annotations/annotation_workflow.md` for the detailed annotation process used to establish ground truth for benchmark candidates.

## Metadata

The `benchmarks/metadata/candidate_manifest.json` file contains metadata for all benchmark candidates including their properties, seeds, and characteristics.

## Usage

These benchmarks are used for:
- Testing and validating MIIE detector algorithms
- Establishing performance baselines
- Research into invariant information extraction techniques
- Regression testing during development

## Generation

The benchmark candidates were generated using deterministic procedures with fixed seeds to ensure reproducibility.