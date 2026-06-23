# MIIE Benchmark Annotation Workflow

This document describes the annotation workflow used to establish ground truth for the 30 synthetic benchmark candidates in the MIIE project.

## Overview

The annotation process involves three stages:
1. Initial annotation by Reviewer A
2. Independent annotation by Reviewer B
3. Adjudication to resolve discrepancies

## Stage 1: Reviewer A Annotation

Reviewer A examines each benchmark candidate and assigns labels based on predefined criteria:
- Anomaly presence (yes/no)
- Anomaly type (drift, correlation breakdown, threshold compression, etc.)
- Severity level (low, medium, high)
- Confidence in assessment (0.0-1.0)

Annotations are saved as JSON files in `benchmarks/annotations/reviewer_a/` with naming convention:
`candidate_{id}_annotation.json`

## Stage 2: Reviewer B Annotation

Reviewer B independently examines the same candidates without access to Reviewer A's annotations.
Reviewer B uses the same criteria and produces annotations in `benchmarks/annotations/reviewer_b/` with the same naming convention.

## Stage 3: Adjudication

An adjudicator reviews the annotations from both reviewers and:
- Identifies discrepancies
- Resolves conflicts based on evidence and discussion
- Produces final ground truth annotations

Final ground truth annotations are saved in `benchmarks/annotations/adjudication/` with naming convention:
`candidate_{id}_ground_truth.json`

## Annotation Schema

Each annotation file follows this JSON schema:

```json
{
  "candidate_id": "string",
  "annotator": "string",
  "timestamp": "ISO 8601 datetime",
  "annotations": {
    "anomaly_present": boolean,
    "anomaly_types": ["string"],
    "severity": "low|medium|high",
    "confidence": float,
    "notes": "string",
    "metrics_affected": ["string"],
    "windows_affected": ["string"]
  }
}
```

## Quality Control

- Inter-rater agreement is calculated between Reviewer A and Reviewer B
- Adjudication notes are maintained for transparency
- All annotators are trained on the same annotation guidelines
- Benchmark candidates are designed with clear, detectable characteristics to minimize ambiguity

## Ground Truth Usage

The final ground truth annotations from the adjudication stage are used to:
- Evaluate detector performance in the MIIE benchmark suite
- Calculate precision, recall, and F1 scores for anomaly detection
- Validate the effectiveness of the analysis pipeline