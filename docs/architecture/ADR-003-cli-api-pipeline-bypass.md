# ADR-003: CLI/API Pipeline Bypass Classification

**Status:** Accepted  
**Date:** 2026-07-10  
**SRP:** SRP-03 (Severity Classification)  
**Work Package:** WP2 (Architecture Classification)

---

## Context

RSCA H2 finding identified that CLI and API bypass the `AnalysisPipeline` orchestration layer by directly instantiating and calling processing engines.

## Classification

### CLI Bypass — INTENTIONAL

**Evidence:**

PRD v1.5 §3.2 explicitly states:

> 1. **`AnalysisPipeline` class** (`orchestration/pipeline.py`) — formal orchestrator with injected engine interfaces. **Not used by CLI.**
> 2. **`_run_pipeline()` function** (`cli.py:331-811`) — inline implementation used by CLI. Calls engines directly.
>
> Both follow the same flow but the CLI version includes additional logic for progress reporting, privacy filtering, and terminal output.

**Justification:**

The CLI requires UI/UX-specific logic that the formal orchestrator does not provide:
- Progress bar reporting with stage-by-stage updates
- Privacy filtering for sensitive fields in output
- Terminal-specific formatting and error handling
- Rich console integration for visual feedback

This is a legitimate architectural decision. The CLI is an interface layer that legitimately needs behavior beyond what the orchestration layer provides.

**Classification:** INTENTIONAL — No action required.

---

### API Bypass — TECHNICAL DEBT

**Evidence:**

- `api/dependencies.py:_run_analyze_job()` directly instantiates and calls processing engines (lines 91-160)
- `docs/API_GUIDE.md` shows the recommended API usage pattern is through `AnalysisPipeline`:
  ```python
  from miie.orchestration.pipeline import AnalysisPipeline
  pipeline = AnalysisPipeline(config)
  results = pipeline.run("/path/to/repo")
  ```
- No specification explicitly states that the API should bypass orchestration
- The API bypass duplicates engine instantiation logic that exists in `AnalysisPipeline`

**Justification:**

Unlike the CLI, the API does not have legitimate UI/UX reasons to bypass orchestration. The background job worker could use `AnalysisPipeline` directly, which would:
- Reduce code duplication
- Ensure consistent behavior between API and programmatic usage
- Simplify maintenance

**Classification:** TECHNICAL DEBT — Should be addressed in a future SRP.

**Recommended Future Action:**

Refactor `api/dependencies.py:_run_analyze_job()` to use `AnalysisPipeline` instead of directly instantiating engines. This is a separate, well-scoped SRP with its own scientific and engineering justification.

---

## Summary

| Interface | Classification | Action |
|-----------|---------------|--------|
| CLI bypass | INTENTIONAL | None — documented in PRD v1.5 |
| API bypass | TECHNICAL DEBT | Future SRP — refactor to use AnalysisPipeline |

---

## Appendix: Current Implementation

### CLI (`cli/__init__.py:323-811`)

```python
def _run_pipeline(...):
    """Execute all pipeline stages with progress feedback."""
    # Directly instantiates and calls processing engines
    ingestion = RepositoryIngestionEngine(auth_token=resolved_token)
    repository_context = ingestion.ingest(repo_path=repo_path, ...)
    # ... more direct engine calls ...
```

### API (`api/dependencies.py:85-171`)

```python
def _run_analyze_job(job_id: str, request: AnalyzeRequest) -> None:
    """Background worker for POST /v1/analyze."""
    # Directly instantiates and calls processing engines
    ingestion = RepositoryIngestionEngine()
    ctx = ingestion.ingest(repo_path=request.repo)
    # ... more direct engine calls ...
```

### AnalysisPipeline (`orchestration/pipeline.py`)

```python
class AnalysisPipeline:
    """Orchestrates the execution of MIIE analysis engines."""
    
    def run_analysis(self, repo_path, metric_list, ...):
        """Run complete analysis pipeline."""
        # Uses injected engine interfaces
        repository_context = self.ingestion_engine.ingest(...)
        # ... orchestrated engine calls ...
```
