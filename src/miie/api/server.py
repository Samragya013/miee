"""MIIE REST API server — Measurement Integrity Intelligence Engine.

Implements the 6 frozen endpoints per TFS §14.3.
"""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from .. import __version__
from .dependencies import (
    _run_analyze_job,
    _run_benchmark_job,
    get_job_store,
    get_uptime,
)
from .models import (
    AnalyzeRequest,
    BenchmarkRequest,
    ExplainRequest,
    ExplainResponse,
    ExportRequest,
    ExportResponse,
    HealthResponse,
    JobAccepted,
    JobCompletedResponse,
    JobStatusResponse,
    ProblemDetail,
)

app = FastAPI(
    title="MIIE API",
    version=__version__,
    description="Measurement Integrity Intelligence Engine",
)


# ---------------------------------------------------------------------------
# RFC 7807 error handler
# ---------------------------------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    body = ProblemDetail(
        type=(
            f"https://miie.dev/errors/{exc.detail.get('error_code', 'unknown')}"
            if isinstance(exc.detail, dict)
            else f"https://miie.dev/errors/http-{exc.status_code}"
        ),
        title=(exc.detail.get("title", "Error") if isinstance(exc.detail, dict) else str(exc.detail)),
        status=exc.status_code,
        detail=(exc.detail.get("detail", str(exc.detail)) if isinstance(exc.detail, dict) else str(exc.detail)),
        instance=str(request.url.path),
    )
    return JSONResponse(status_code=exc.status_code, content=body.model_dump())


# ---------------------------------------------------------------------------
# GET /v1/health
# ---------------------------------------------------------------------------
@app.get("/v1/health", response_model=HealthResponse, tags=["system"])
def health_check():
    """Return service health (TFS §14.3)."""
    return HealthResponse(
        status="healthy",
        version=__version__,
        uptime_seconds=get_uptime(),
    )


# ---------------------------------------------------------------------------
# POST /v1/analyze
# ---------------------------------------------------------------------------
@app.post("/v1/analyze", response_model=JobAccepted, status_code=202, tags=["analysis"])
def analyze(request: AnalyzeRequest):
    """Accept an analysis job and run it in the background (TFS §14.3)."""
    store = get_job_store()
    job_id = store.create_job("analyze", request.model_dump())

    import threading

    thread = threading.Thread(target=_run_analyze_job, args=(job_id, request), daemon=True)
    thread.start()

    return JobAccepted(
        job_id=job_id,
        status="created",
        poll_url=f"/v1/jobs/{job_id}",
    )


# ---------------------------------------------------------------------------
# GET /v1/jobs/{job_id}
# ---------------------------------------------------------------------------
@app.get("/v1/jobs/{job_id}", tags=["jobs"])
def get_job_status(job_id: str):
    """Return job status — 200 if completed, 202 if running (TFS §14.3)."""
    store = get_job_store()
    job = store.get_job(job_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": "JOB-NOT-FOUND",
                "title": "Job Not Found",
                "detail": f"No job found with ID {job_id}.",
            },
        )

    status = job["status"]

    if status == "completed":
        result = job.get("result", {})
        return JobCompletedResponse(
            job_id=job_id,
            status=status,
            created_at=job["created_at"],
            completed_at=job.get("completed_at", ""),
            results_url=f"/v1/jobs/{job_id}/results",
            summary={
                "overall_integrity_score": result.get("integrity_overall"),
                "overall_confidence": result.get("confidence_overall"),
                "metrics_analyzed": len(result.get("integrity_per_metric", {})),
            },
        )

    if status == "failed":
        error = job.get("error", {})
        raise HTTPException(
            status_code=500,
            detail=(
                error
                if error
                else {
                    "error_code": "JOB-FAILED",
                    "title": "Job Failed",
                    "detail": "The job encountered an error.",
                }
            ),
        )

    # running / created / queued
    return JobStatusResponse(
        job_id=job_id,
        status=status,
        progress=job.get("progress", 0.0),
        stage=job.get("stage"),
    )


# ---------------------------------------------------------------------------
# GET /v1/jobs/{job_id}/results
# ---------------------------------------------------------------------------
@app.get("/v1/jobs/{job_id}/results", tags=["jobs"])
def get_job_results(job_id: str):
    """Return full analysis results (TFS §14.3)."""
    store = get_job_store()
    job = store.get_job(job_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": "JOB-NOT-FOUND",
                "title": "Job Not Found",
                "detail": f"No job found with ID {job_id}.",
            },
        )
    if job["status"] != "completed":
        raise HTTPException(
            status_code=409,
            detail={
                "error_code": "JOB-NOT-COMPLETED",
                "title": "Job Not Completed",
                "detail": f"Job {job_id} is still {job['status']}.",
            },
        )
    return job.get("result", {})


# ---------------------------------------------------------------------------
# POST /v1/benchmark
# ---------------------------------------------------------------------------
@app.post("/v1/benchmark", response_model=JobAccepted, status_code=202, tags=["benchmark"])
def benchmark(request: BenchmarkRequest):
    """Accept a benchmark job and run it in the background (TFS §14.3)."""
    store = get_job_store()
    job_id = store.create_job("benchmark", request.model_dump())

    import threading

    thread = threading.Thread(target=_run_benchmark_job, args=(job_id, request), daemon=True)
    thread.start()

    return JobAccepted(
        job_id=job_id,
        status="created",
        poll_url=f"/v1/jobs/{job_id}",
    )


# ---------------------------------------------------------------------------
# POST /v1/explain
# ---------------------------------------------------------------------------
@app.post("/v1/explain", response_model=ExplainResponse, tags=["analysis"])
def explain(request: ExplainRequest):
    """Generate an explanation from a completed analysis (TFS §14.3)."""
    store = get_job_store()
    job = store.get_job(request.job_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": "JOB-NOT-FOUND",
                "title": "Job Not Found",
                "detail": f"No job found with ID {request.job_id}.",
            },
        )
    if job["status"] != "completed":
        raise HTTPException(
            status_code=409,
            detail={
                "error_code": "JOB-NOT-COMPLETED",
                "title": "Job Not Completed",
                "detail": f"Job {request.job_id} is still {job['status']}.",
            },
        )

    result = job.get("result", {})
    return ExplainResponse(
        explanation=f"Analysis of repository {result.get('repo_id', 'unknown')} completed. "
        f"Overall integrity: {result.get('integrity_overall', 0.0):.4f}.",
        rule_fired="default",
        evidence_refs=[],
        metric=request.metric or "all",
        detector=request.detector or "all",
    )


# ---------------------------------------------------------------------------
# POST /v1/export
# ---------------------------------------------------------------------------
@app.post("/v1/export", response_model=ExportResponse, tags=["export"])
def export(request: ExportRequest):
    """Export results in specified formats (TFS §14.3)."""
    store = get_job_store()
    job = store.get_job(request.job_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": "JOB-NOT-FOUND",
                "title": "Job Not Found",
                "detail": f"No job found with ID {request.job_id}.",
            },
        )
    if job["status"] != "completed":
        raise HTTPException(
            status_code=409,
            detail={
                "error_code": "JOB-NOT-COMPLETED",
                "title": "Job Not Completed",
                "detail": f"Job {request.job_id} is still {job['status']}.",
            },
        )

    urls = {}
    for fmt in request.formats:
        urls[fmt] = f"/v1/jobs/{request.job_id}/export/{fmt}"

    return ExportResponse(download_urls=urls)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def main():
    """Run the MIIE API server."""
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
