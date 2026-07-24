# Monitoring Setup Guide: MIIE

**Team:** MIIE Development | **Tech lead:** Samragya
**Stack:** Python 3.10-3.12 / Click CLI + FastAPI on Windows (local execution)
**Monitoring platform:** Application-level logging + structured JSON (no external APM yet)
**Date:** 2026-07-24 | **Review cycle:** Quarterly

---

## 1. Monitoring Philosophy

Good monitoring answers three questions:
1. **Is the service healthy right now?** (alerting)
2. **Was it healthy in the past, and is it trending worse?** (dashboards + SLO tracking)
3. **Why did something fail?** (logs + traces)

This guide defines the answers for MIIE. Every alert must be actionable — if an on-call engineer cannot take a specific action in response to the alert, the alert should not exist.

**Key user journeys monitored:**
- Journey 1: `miie analyze <repo>` — Full pipeline (ingest → extract → detect → score → report)
- Journey 2: `miie detect <repo>` — Quick detection (ingest → extract → detect, no scoring)
- Journey 3: API `POST /v1/analyze` → `GET /v1/jobs/{id}` — Async analysis via REST
- Journey 4: `miie benchmark` — Benchmark execution against ground truth

---

## 2. The Four Golden Signals

### Latency

| Metric | Description | Source | Dimensions |
|---|---|---|---|
| `miie.pipeline.duration_seconds` | End-to-end pipeline execution time | `time.perf_counter()` in CLI | `command`, `repo_size` |
| `miie.ingestion.duration_seconds` | Repository clone/ingest time | `RepositoryIngestionEngine` | `source` (local/github), `shallow` |
| `miie.extraction.duration_seconds` | Metric extraction time | `ExtractionEngine` | `metrics_count`, `max_commits` |
| `miie.detection.duration_seconds` | Detector execution time | `DetectorDispatcherEngine` | `detectors_count`, `windows_count` |
| `miie.scoring.duration_seconds` | Scoring + evidence time | `ScoringEngine` | `metrics_count` |

**Latency SLO targets:**

| Operation | p50 target | p95 target | p99 target |
|---|---|---|---|
| `miie analyze` (small repo <1K commits) | <10s | <30s | <60s |
| `miie analyze` (medium repo 1K-10K) | <30s | <90s | <180s |
| `miie analyze` (large repo 10K+) | <60s | <180s | <300s |
| `miie detect` | <15s | <45s | <90s |
| `GET /v1/health` | <10ms | <20ms | <50ms |

### Traffic

| Metric | Description | Source |
|---|---|---|
| `miie.command.count` | Commands executed | CLI wrapper / API middleware |
| `miie.command.count_by_type` | Commands by type (analyze, detect, etc.) | CLI wrapper |
| `miie.api.request.count` | API requests per endpoint | FastAPI middleware |
| `miie.api.request.count_by_status` | API requests by HTTP status | FastAPI middleware |

**Traffic baselines:**

| Time period | Expected commands/day | Low floor | Spike ceiling |
|---|---|---|---|
| Active development | 50-200 | 10 | 500 |
| CI/CD pipeline | 10-50 | 0 | 200 |

### Errors

| Metric | Description | Alert on? |
|---|---|---|
| `miie.pipeline.error_rate` | Pipeline failures / total runs | Yes |
| `miie.api.error_rate` | 5xx errors / total API requests | Yes |
| `miie.detection.detector_failure_rate` | Failed detectors / total detectors | Yes |
| `miie.ingestion.clone_failure_rate` | Failed clones / total clones | Yes |

### Saturation

| Resource | Metric | Alert threshold | Source |
|---|---|---|---|
| Memory | `miie.runtime.memory_mb` | >500MB sustained | `psutil` |
| Disk | `miie.output.disk_mb` | >1GB output accumulation | `os.path.getsize` |
| Git subprocess | `miie.git.timeout_count` | >0 (any timeout) | Git utils |
| Commit limit | `miie.extraction.max_commits_hit` | >0 (hit limit) | Extraction engine |

---

## 3. Business Metrics

| Metric | Description | Source | Alert? |
|---|---|---|---|
| `miie.analysis.success_rate` | Successful analyses / total | Pipeline | Yes — if drops <95% |
| `miie.confidence.band_distribution` | % of analyses with high/medium/low confidence | Scoring engine | No — informational |
| `miie.integrity.score_distribution` | Distribution of integrity scores | Scoring engine | No — informational |
| `miie.detection.trigger_rate` | Detections triggered / total analyses | Detection engine | No — informational |
| `miie.report.generation_rate` | Reports generated successfully | Report generator | Yes — if <99% |

---

## 4. Log Strategy

### Structured Logging Schema

All logs must be structured JSON in production mode. CLI output uses Rich for human-readable display.

**Mandatory fields (every log line):**

```json
{
  "timestamp": "2026-07-24T10:23:45.123Z",
  "level": "info",
  "service": "miie",
  "version": "1.6.1",
  "command": "analyze",
  "repo_path": "/path/to/repo",
  "message": "Pipeline stage completed"
}
```

**Pipeline stage log:**

```json
{
  "timestamp": "...",
  "level": "info",
  "service": "miie",
  "event": "pipeline_stage",
  "command": "analyze",
  "stage": "extraction",
  "duration_seconds": 12.5,
  "metrics_extracted": 7,
  "total_commits": 1500,
  "message": "Metric extraction completed"
}
```

**Error log:**

```json
{
  "timestamp": "...",
  "level": "error",
  "service": "miie",
  "event": "pipeline_error",
  "command": "analyze",
  "stage": "detection",
  "error_code": "DETECTOR-FAILED",
  "error_message": "D-01 distribution drift detector failed",
  "stack_trace": "...",
  "repo_path": "/path/to/repo",
  "message": "Detection stage failed"
}
```

### Log Levels

| Level | Use when | Example |
|---|---|---|
| `error` | Pipeline failure, detector crash, git timeout | Database query failed, clone timeout |
| `warn` | Degraded execution, retry succeeded | Fallback to sequential extraction, cache miss |
| `info` | Stage completion, analysis results | Pipeline completed, scores computed |
| `debug` | Detailed diagnostics (off by default) | Individual metric values, window boundaries |

### What NOT to Log

- GitHub tokens or auth credentials (even masked)
- Full repository contents or file diffs
- User PII (email, name from git log)
- Temporary file paths (use relative paths only)

---

## 5. Instrumentation Checklist

```
[ ] CLI timing instrumentation:
    [x] time.perf_counter() around each pipeline stage (in _run_pipeline_rich)
    [ ] Wrap individual detector calls with timing
    [ ] Add timing to ingestion (clone vs local)

[ ] API request logging:
    [x] FastAPI middleware for request/response logging
    [ ] Add request_id tracking across async jobs
    [ ] Log job creation, completion, and failure events

[ ] Error tracking:
    [x] try/except with structured error output in CLI
    [x] HTTPException handlers with RFC 7807 format in API
    [ ] Add error categorization (transient vs permanent)

[ ] Resource monitoring:
    [ ] Memory usage at pipeline start/end
    [ ] Disk usage for output directory
    [ ] Git subprocess timeout tracking

[ ] Output:
    [x] JSON report generation
    [x] Markdown report generation
    [x] CSV report generation
    [ ] Add report file size tracking
```

---

## 6. Alert Rules Specification

### Alert Definitions

| Alert name | Condition | Threshold | Severity | On-call action |
|---|---|---|---|---|
| `MIIEHighErrorRate` | Pipeline failure rate, 1-hour window | >10% for 2 consecutive windows | P1 | Check recent deploys; inspect error logs in output/ |
| `MIIECloneFailureRate` | GitHub clone failures / total clones | >20% over 1 hour | P1 | Check GitHub API status; verify GITHUB_TOKEN validity |
| `MIIEDetectorFailureRate` | Detector failures / total detectors run | >30% over 1 hour | P2 | Check detector logs; verify input data quality |
| `MIIEPipelineTimeout` | Any pipeline execution >300s | >300s | P2 | Check repo size; verify --max-commits setting |
| `MIIEHighMemoryUsage` | Pipeline memory >500MB | >500MB sustained | P2 | Check for memory leaks; reduce --max-commits |
| `MIIEOutputDiskFull` | Output directory >1GB | >1GB | P3 | Clean old reports; check --output-dir setting |
| `MIIEAPIErrorRate` | API 5xx rate | >5% over 5 min | P1 | Check API logs; verify server health |
| `MIIEAPILatencyHigh` | API p99 latency | >2s for 3 min | P2 | Check server load; verify database connectivity |
| `MIIEConfidenceLow` | % of analyses with low confidence | >50% over 1 day | P3 | Review default window settings; check repo sizes |

---

## 7. End-to-End Verification

### CLI Commands to Test

```bash
# 1. System health check
miie status

# 2. Validate installation
miie validate

# 3. Dry-run analysis (no git operations)
miie analyze ./test-repo --dry-run

# 4. Full analysis on small repo
miie analyze ./test-repo -m M-02 -m M-06 -d D-01 -d D-02 -d D-03

# 5. Detection only
miie detect ./test-repo

# 6. API server health
curl http://127.0.0.1:8000/v1/health

# 7. API analysis job
curl -X POST http://127.0.0.1:8000/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"repo": "https://github.com/pallets/flask.git"}'
```

### Expected Results

| Command | Expected Exit Code | Expected Output |
|---|---|---|
| `miie status` | 0 | System status with version, Python, dependencies |
| `miie validate` | 0 | Validation report |
| `miie analyze --dry-run` | 0 | Pipeline plan display |
| `miie analyze <repo>` | 0 (success) or 1 (integrity issues) | Full analysis report |
| `miie detect <repo>` | 0 | Detection results |
| `GET /v1/health` | 200 | `{"status": "healthy", "version": "1.6.1"}` |
| `POST /v1/analyze` | 202 | `{"job_id": "...", "status": "created"}` |

---

## 8. Observability Debt Analysis

| Gap | Impact | Priority | Effort | Owner | Target date |
|---|---|---|---|---|---|
| No distributed tracing — can't see cross-service latency | High — blind to API → CLI latency | P1 | 2 days | Samragya | 2026-08-01 |
| No structured logging in CLI output | Medium — hard to parse logs | P2 | 1 day | Samragya | 2026-08-08 |
| No memory/resource monitoring during pipeline | Medium — can't detect OOM risk | P2 | 4 hours | Samragya | 2026-08-08 |
| No API request_id tracking across async jobs | Medium — hard to correlate logs | P2 | 4 hours | Samragya | 2026-08-15 |
| No alert thresholds calibrated to production baselines | Medium — alert fatigue or missed alerts | P2 | 1 day | Samragya | 2026-08-15 |
| No dashboard for pipeline health visualization | Low — harder to spot trends | P3 | 2 days | Samragya | 2026-08-22 |

**Total observability debt: 6 items | Estimated effort: 7.5 days**

---

## Quality Checks

- [x] Every alert has a named on-call action — no alert says "investigate" without specifying what to investigate first
- [ ] Alert thresholds are calibrated against production baselines — need 2+ weeks of production data
- [ ] Structured logging is implemented — CLI uses Rich, not JSON (acceptable for CLI tool)
- [ ] PII is explicitly excluded from logs — verified: git author info not logged
- [ ] Distributed tracing is propagating trace IDs — not yet implemented
- [x] The primary dashboard answers "is the service healthy?" in under 10 seconds — `miie status` command
- [ ] Business metrics are tracked alongside infrastructure metrics — need to add success_rate, confidence distribution
- [x] Observability debt items have owners and dates — tracked in Section 8

## Anti-Patterns

- [x] No alerts without specific on-call actions
- [ ] Alert thresholds not calibrated to production baselines — need baseline data
- [x] No PII in logs — verified
- [x] Business metrics tracked (confidence, integrity scores)
- [ ] Distributed tracing not yet implemented — partial tracing is worse than none
