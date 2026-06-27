# Phase 7: Root Cause Analysis Register

**MIIE v1.0 Release Certification**
**Date:** 2026-06-25
**Author:** Root Cause Analyst (MIIE Loop Governance Board)

---

## Executive Summary

This register documents the root cause analysis for all failures and issues identified during the MIIE v1.0 Release Certification. Four external failure categories (clone failures, timeouts, authority partial compliance) and four internal implementation defects (D-1 through D-4) were analyzed using Five Whys methodology, code tracing, and authority tracing.

---

## 1. External Failure: AutoGPT Clone Failure

### Symptom
`[WinError 5] Access is denied` when cloning `Significant-Gravitas/AutoGPT` on `.git/objects/pack/*.idx` files.

### Five Whys Analysis

| # | Question | Answer |
|---|----------|--------|
| 1 | Why did the clone fail? | Windows denied write access to `.git/objects/pack/*.idx` during `git clone` |
| 2 | Why was write access denied? | Another process (antivirus, Windows Search Indexer, or Git Credential Manager) held a file lock on the pack index |
| 3 | Why did a file lock exist? | Git pack files are memory-mapped by Windows; concurrent access during shallow clone triggers lock contention |
| 4 | Why did this happen specifically with AutoGPT? | AutoGPT is a large repo (~400MB pack file); the shallow clone takes longer, extending the lock window |
| 5 | Why wasn't this handled? | `GitCloner` uses `subprocess.run(check=True)` without retry logic or `--no-checkout` fallback |

### Root Cause
**File lock contention on Windows** during shallow clone of large repositories. The `GitCloner` class (`src/miie/utils/git.py:146-159`) does not implement retry logic, `GIT_LOCKED` error handling, or `--filter=blob:none` partial clone fallback.

### Code Trace
```
src/miie/utils/git.py:146-159
  subprocess.run(cmd, capture_output=True, text=True, check=True)
  → CalledProcessError raised on WinError 5
  → No retry, no lock detection, no fallback
```

### Authority Trace
- **AFD §Step 5 (Ingestion):** "Clone or local path resolution" — no authority guidance on Windows file locking
- **TFS §9.2:** CLI option `--auth-token` for private repos — no mention of Windows-specific clone resilience

### Classification
**Environment Issue** — Windows-specific file locking behavior not accounted for in cross-platform tool.

### Fix Recommendation
Add retry-with-backoff and `--filter=blob:none` (partial clone) fallback in `GitCloner.clone()`.

---

## 2. External Failure: autogen Clone Failure

### Symptom
Same `[WinError 5] Access is denied` on `.git/objects/pack/*.idx` when cloning `microsoft/autogen`.

### Five Whys Analysis

| # | Question | Answer |
|---|----------|--------|
| 1 | Why did the clone fail? | Same Windows file lock contention as AutoGPT |
| 2 | Why did this recur? | The root cause (no retry logic) was not fixed after the first failure |
| 3 | Why wasn't it fixed? | The clone failures were logged but not treated as blocking for certification |
| 4 | Why wasn't it blocking? | The MIIE pipeline treats clone failures as soft errors (returns empty analysis) |
| 5 | Why soft errors? | The pipeline design assumes local repos are primary; GitHub URLs are convenience |

### Root Cause
**Same as RC-01.** Additionally, the pipeline's error handling at `src/miie/cli.py:90-150` converts `RuntimeError` from `GitCloner` into exit code 2 (system error), but does not differentiate between "repo doesn't exist" and "temporary lock contention."

### Code Trace
```
src/miie/utils/git.py:155-159
  except subprocess.CalledProcessError as e:
      raise RuntimeError(error_msg)  # No WinError detection

src/miie/cli.py:90-150
  analyze() → no specific clone retry logic
```

### Classification
**Implementation Bug** — clone failure handling lacks platform-specific resilience.

### Fix Recommendation
Unified fix with RC-01: add retry logic and lock detection in `GitCloner`.

---

## 3. External Failure: Large Repository Timeouts

### Symptom
Repos `torvalds/linux`, `kubernetes/kubernetes`, `python/cpython`, `hashicorp/terraform` all timed out at 180s during clone.

### Five Whys Analysis

| # | Question | Answer |
|---|----------|--------|
| 1 | Why did the clones time out? | Shallow clone (`--depth 1`) of repos with >1GB pack files exceeded 180s |
| 2 | Why 180s? | Default `subprocess.run()` timeout (no explicit timeout set) plus OS-level socket timeout |
| 3 | Why didn't MIIE handle this? | `GitCloner` has no `timeout` parameter; `subprocess.run()` blocks indefinitely |
| 4 | Why no timeout? | The cloner was designed for "Day 7 foundation" with small-to-medium repos only |
| 5 | Why weren't large repos excluded? | No pre-clone size estimation or repo tier classification in the pipeline |

### Root Cause
**No timeout enforcement in `GitCloner`** and **no repo size estimation before clone**. The `subprocess.run()` call at `git.py:147` has no `timeout` parameter. Large repos with multi-GB pack files cannot complete a shallow clone within acceptable time on Windows.

### Code Trace
```
src/miie/utils/git.py:147
  subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', check=True)
  → No timeout parameter

benchmarks/repository_fixture_requirements.md
  Large tier: 100-1000 MB, 5000+ commits
  → No pre-clone validation against these limits
```

### Authority Trace
- **TFS §4.1:** Benchmark candidates must fit size tiers
- **AFD §Step 5:** "Clone or local path — local path preferred" — no guidance on remote clone limits
- **Benchmark fixture requirements:** Large tier allows 100-1000 MB repos

### Classification
**Implementation Bug** — `GitCloner` lacks timeout parameter and large-repo handling.

### Fix Recommendation
1. Add `timeout` parameter to `GitCloner` (default 120s)
2. Add `--filter=blob:limit=1m` for partial blob cloning
3. Add pre-clone size check via GitHub API (`/repos/{owner}/{repo}` → `size` field)
4. Classify repos into tiers and skip large repos for quick analysis

---

## 4. External Failure: Authority Partial Compliance (Module Count Granularity)

### Symptom
2 requirements marked as partial in authority compliance audit:
- **IConfigurationLoader (M-12)**: Not found in contracts
- **IRegistryManager (M-13)**: Not found in contracts

### Five Whys Analysis

| # | Question | Answer |
|---|----------|--------|
| 1 | Why were M-12 and M-13 marked partial? | No interface contracts defined for configuration loading or registry management |
| 2 | Why weren't they defined? | The contracts layer was built incrementally; M-12/M-13 were deferred as "not needed for v1.0 core" |
| 3 | Why deferred? | The operating plan prioritized M-02, M-06 (extraction), D-01/D-02/D-03 (detection) |
| 4 | Why didn't the authority audit flag this earlier? | The FERA authority audit (`FERA_AUTHORITY_AUDIT.md`) identified it but didn't escalate to blocking |
| 5 | Why not blocking? | M-12 is `config/loader.py` (exists but no formal interface), M-13 is `metric_registry.py` (exists but no formal interface) |

### Root Cause
**Implementation exists but lacks formal interface contracts.** `ConfigurationLoader` is implemented in `src/miie/config/loader.py` and `MetricRegistry` in `src/miie/schemas/metric_registry.py`, but neither has a corresponding `IConfigurationLoader` or `IRegistryManager` interface in `contracts/interfaces.py`.

### Code Trace
```
src/miie/config/loader.py — ConfigurationLoader class exists
  → No IConfigurationLoader interface in contracts/interfaces.py

src/miie/schemas/metric_registry.py — METRIC_REGISTRY exists
  → No IRegistryManager interface in contracts/interfaces.py
```

### Authority Trace
- **ACS §3.2 (Interface Contracts):** All modules must have interface contracts
- **FERA_AUTHORITY_AUDIT.md:** "Missing/Partially Implemented Interfaces" section flags M-12, M-13
- **Operating Plan Day 0-10:** M-12, M-13 listed as required modules

### Classification
**Documentation Gap** — Implementation exists, but formal interface contracts are missing.

### Fix Recommendation
Add `IConfigurationLoader` and `IRegistryManager` interfaces to `contracts/interfaces.py` with proper type hints and docstrings referencing the authority specs.

---

## 5. Internal Defect: D-1 — No Minimum Window Gate

### Symptom
System continues with 1 window, producing meaningless detector results. D-01, D-02, D-03 all skip when `metric_dataframe` has 1 window.

### Five Whys Analysis

| # | Question | Answer |
|---|----------|--------|
| 1 | Why do detectors produce meaningless results? | They need ≥2 windows to compare; 1 window = no comparison possible |
| 2 | Why is there only 1 window? | Time strategy with size=7 creates a single 7-day window ending at run date |
| 3 | Why doesn't the system abort? | No validation gate after segmentation |
| 4 | Why no validation gate? | The segmentation engine was built for "Day 7 foundation" without minimum window enforcement |
| 5 | Why wasn't this caught? | Tests use `MockSegmentationEngine` which always returns 2 windows |

### Root Cause
**Missing validation gate** after segmentation. AFD §Step 8 explicitly requires: "total windows ≥ 2 (required for drift detection). If <2 valid windows: abort." The `WindowSegmentationEngine.segment()` returns windows, but no caller validates `len(windows) >= 2`.

### Code Trace
```
src/miie/processing/segmentation.py:103-117
  Time strategy: creates 1 window (w00) — correct per strategy
  
  → No caller checks len(windows) < 2

src/miie/processing/segmentation.py:191-237
  MockSegmentationEngine: always returns 2 windows
  → Tests never exercise the 1-window path
```

### Authority Trace
- **AFD §Step 8:** "total windows ≥ 2 (required for drift detection). If <2 valid windows: abort."
- **TFS §5.2:** Window count requirements for detection validity

### Classification
**Missing Validation** — Authority explicitly requires this gate, but it's not implemented.

### Fix Recommendation
Add validation after segmentation in the pipeline:
```python
if len(windows) < 2:
    raise PipelineError(
        f"Insufficient windows: {len(windows)} (need ≥2). "
        "Adjust window_size or time range."
    )
```

---

## 6. Internal Defect: D-2 — Explanation Engine Factor Name Mismatch

### Symptom
Explanation engine generates incorrect narratives. Reports "Data quality factor is low (0.00)" and "Temporal coverage factor is low (0.00)" when actual values are 1.0.

### Five Whys Analysis

| # | Question | Answer |
|---|----------|--------|
| 1 | Why are narratives wrong? | Explanation engine reads `data_quality` and `temporal_coverage` keys that don't exist |
| 2 | Why wrong keys? | The explanation engine was written with different factor names than the scoring engine |
| 3 | Why different names? | The scoring engine (TFS §7.5) was implemented after the explanation engine |
| 4 | Why weren't they aligned? | No integration test validates factor name consistency between scoring and explanation |
| 5 | Why no integration test? | Tests use `MockExplanationEngine` which returns hardcoded narratives |

### Root Cause
**Dictionary key mismatch** between `ScoringEngine._compute_confidence_score_tfs7()` (produces `sample_size`, `missing_data`, `window_balance`) and `ExplanationEngine.generate()` (reads `sample_size`, `data_quality`, `temporal_coverage`).

### Code Trace
```
src/miie/processing/scoring/engine.py:353-361
  Returns: {"factors": {"sample_size": f1, "variance": f2, "missing_data": f3, "window_balance": f4, "detector_success": f5}}

src/miie/processing/explanation/engine.py:62-64
  Reads: confidence_factors.get("data_quality", 0.0)    ← WRONG KEY
  Reads: confidence_factors.get("temporal_coverage", 0.0) ← WRONG KEY
  → Falls back to default 0.0, generating false low-quality narratives
```

### Authority Trace
- **TFS §7.5:** Factors are `sample_size`, `variance`, `missing_data`, `window_balance`, `detector_success`
- **EXPLANATION_ENGINE_AUDIT.md:** Documented mismatch with exact line references

### Classification
**Bug** — Wrong dictionary keys cause false narratives.

### Fix Recommendation
Update `explanation/engine.py:62-64`:
```python
missing_data = confidence_factors.get("missing_data", 0.0)      # was "data_quality"
window_balance = confidence_factors.get("window_balance", 0.0)   # was "temporal_coverage"
```

---

## 7. Internal Defect: D-3 — Confidence f₁ Counts Data Points, Not Per-Window Data

### Symptom
Confidence sample_size factor `f₁` is always 0.02 regardless of window count. `f₁ = min(1.0, 1.0/50.0) = 0.02`.

### Five Whys Analysis

| # | Question | Answer |
|---|----------|--------|
| 1 | Why is f₁ always 0.02? | `mean_n` is always 1.0 because metric_dataframe has 1 data point per metric |
| 2 | Why 1 data point? | Extraction returns `{'w00': [total_value]}` — aggregated, not per-window |
| 3 | Why aggregated? | Extraction engine was built for "Day 7 foundation" without windowed extraction |
| 4 | Why wasn't windowed extraction built? | The operating plan deferred per-window extraction to "future versions" |
| 5 | Why does f₁ depend on per-window data? | TFS §7.5 defines `mean_n = mean(|Wₖ| for all k and all metrics with data)` |

### Root Cause
**Mathematical formula depends on per-window data that doesn't exist.** `_compute_sample_size_factor()` at `engine.py:364-396` counts data points in `metric_dataframe.metrics`, but metric_dataframe is created once before segmentation with aggregated values.

### Code Trace
```
src/miie/processing/scoring/engine.py:364-396
  for metric_id, metric_series in metric_dataframe.metrics.items():
      for value_list in metric_series.values():  # {'w00': [137.0]}
          for val in value_list:                  # [137.0] → 1 point
              total_points += 1
  mean_n = total_points / metric_count = 2/2 = 1.0
  f1 = min(1.0, 1.0/50.0) = 0.02

CONFIDENCE_FORENSIC_TRACE.md:
  Confirmed: f₁ is constant regardless of window count
```

### Authority Trace
- **TFS §7.5:** `mean_n = mean(|Wₖ| for all k and all metrics with data)` where `|Wₖ|` = count of data points in window k
- **CONFIDENCE_FORENSIC_TRACE.md:** Documents the mathematical proof of the miscalculation

### Classification
**Mathematical Error** — The formula is implemented incorrectly because the input data is wrong (see D-4).

### Fix Recommendation
Depends on D-4. Cannot fix without per-window data. Document as architectural debt.

---

## 8. Internal Defect: D-4 — Extraction Produces Aggregated, Not Per-Window Data

### Symptom
Extraction returns `{'w00': [total_value]}` for M-02 and M-06, not per-window values. All detectors see 1 window regardless of segmentation.

### Five Whys Analysis

| # | Question | Answer |
|---|----------|--------|
| 1 | Why is extraction aggregated? | `_extract_commit_frequency()` returns total commit count as single value |
| 2 | Why single value? | Comment says "For Day 7 foundation, we extract total commit count as a single value" |
| 3 | Why foundation-only? | The operating plan explicitly scoped Day 7 to "foundation" extraction |
| 4 | Why wasn't windowed extraction added later? | Subsequent days focused on detection/scoring, not extraction refactoring |
| 5 | Why is this a problem now? | Detection requires per-window data to compare across windows; aggregated data makes detection meaningless |

### Root Cause
**Architectural gap:** Extraction runs before segmentation and produces aggregated data. Segmentation creates WindowDefinitions, but these are NOT used to re-extract metrics per window. The `extract()` method accepts `windows` parameter but the pipeline doesn't pass segmented windows.

### Code Trace
```
src/miie/processing/extraction.py:100-108
  if windows:
      metrics[metric_id] = self._extract_commit_frequency_windowed(context, windows, exclude_bots)
  else:
      metrics[metric_id] = self._extract_commit_frequency(context, since, until, exclude_bots)
  
  → When windows=None (default), uses aggregated extraction

src/miie/processing/extraction.py:155-163
  def _extract_commit_frequency(...):
      commit_count = self._get_commit_count_since_until(...)
      return {"w00": [float(commit_count)]}  # Aggregated

src/miie/processing/extraction.py:169-225
  def _extract_commit_frequency_windowed(...):
      # Correct per-window extraction EXISTS
      # But pipeline doesn't call it with segmented windows
```

### Authority Trace
- **AFD §Step 7:** M-02: "Count per day", M-06: "mean per window" — per-window extraction required
- **SEGMENTATION_FORENSIC_TRACE.md:** "The metric_dataframe is created ONCE before segmentation"
- **AUTHORITY_COMPARISON.md:** Documents the gap between AFD spec and implementation

### Classification
**Implementation Gap** — The extraction engine was built for "Day 7 foundation" and returns aggregated values. Windowed extraction methods exist but aren't wired into the pipeline.

### Fix Recommendation
Refactor pipeline to pass segmented windows to extraction:
```python
# In pipeline.py:
windows = segmentation_engine.segment(metric_dataframe, strategy, size)
metric_dataframe = extraction_engine.extract(context, metric_list, windows=windows)
```

---

## 9. Additional Issue: Benchmark Simulation Not Real Execution

### Symptom
`BenchmarkEngine.execute()` at `processing/benchmark/engine.py:37-67` generates simulated predictions using `random.Random(seed)`, not actual detector execution on benchmark candidates.

### Five Whys Analysis

| # | Question | Answer |
|---|----------|--------|
| 1 | Why are benchmark results simulated? | `BenchmarkEngine` generates random accuracy/precision/recall values |
| 2 | Why simulated? | The engine was built as a "foundation" with deterministic simulation |
| 3 | Why not real execution? | Real execution requires cloning 120 candidate repos, which fails on Windows (see RC-01, RC-03) |
| 4 | Why does this matter? | Benchmark results (Precision/Recall) are used to certify detectors |
| 5 | Why certify with simulated data? | The TFS v1.0 benchmark targets were validated with mock data, not real repos |

### Root Cause
**Benchmark engine is a simulation, not a real execution engine.** The `BenchmarkEngine` at `processing/benchmark/engine.py` generates random metrics, while `BenchmarkRunner` at `benchmark/runner.py` delegates to `ProcessingBenchmarkEngine` which is also simulated.

### Code Trace
```
src/miie/processing/benchmark/engine.py:46-67
  accuracy = local_random.uniform(0.7, 0.95)  # Random, not real
  precision = local_random.uniform(0.65, 0.9)  # Random, not real

MIIE_V1_GOLD_RELEASE_PACKAGE.md:32-37
  Benchmark Results (TFS v1.0 Ground Truth):
  D-01: Precision=0.8889, Recall=0.9412
  → These are from simulated execution, not real repo analysis
```

### Classification
**Documentation Gap** — Benchmark results are presented as ground truth validation but are actually simulated. Should be documented as "simulated benchmark validation."

---

## 10. Additional Issue: Atomic Manifest Write Bug

### Symptom
`BenchmarkDatasetGenerator._write_manifest_atomic()` at `generator.py:416-442` has a logic error in the atomic replace path.

### Code Trace
```
src/miie/benchmark/generator.py:431-433
  if manifest_path.exists():
      manifest_path.replace(temp_file)  # Overwrites temp_file with manifest content!
      temp_file.replace(manifest_path)  # Puts temp content in manifest location
  else:
      temp_file.replace(manifest_path)
```

**Bug:** `manifest_path.replace(temp_file)` replaces the temp file WITH the existing manifest content, then `temp_file.replace(manifest_path)` puts the temp file's content back. The intended atomic write is inverted. Should be:
```python
temp_file.replace(manifest_path)  # Atomically replace manifest with temp content
```

### Classification
**Implementation Bug** — Atomic write logic is inverted.

---

## Root Cause Register Summary

| ID | Issue | Classification | Severity | Fix Complexity | Authority Ref |
|----|-------|---------------|----------|---------------|---------------|
| RC-01 | AutoGPT clone failure (WinError 5) | Environment Issue | HIGH | LOW | AFD §Step 5 |
| RC-02 | autogen clone failure (WinError 5) | Implementation Bug | HIGH | LOW | AFD §Step 5 |
| RC-03 | Large repo timeouts (180s) | Implementation Bug | HIGH | MEDIUM | TFS §4.1 |
| RC-04 | Authority partial compliance (M-12, M-13) | Documentation Gap | LOW | LOW | ACS §3.2 |
| D-1 | No minimum window gate | Missing Validation | HIGH | LOW | AFD §Step 8 |
| D-2 | Explanation engine factor name mismatch | Bug | MEDIUM | LOW | TFS §7.5 |
| D-3 | Confidence f₁ miscalculation | Mathematical Error | MEDIUM | MEDIUM | TFS §7.5 |
| D-4 | Extraction aggregated, not per-window | Implementation Gap | HIGH | HIGH | AFD §Step 7 |
| RC-05 | Benchmark simulation not real execution | Documentation Gap | MEDIUM | HIGH | TFS §10 |
| RC-06 | Atomic manifest write bug | Implementation Bug | LOW | LOW | — |

---

## Cross-Cutting Themes

### Theme 1: "Day 7 Foundation" Technical Debt
Defects D-3 and D-4 stem from the same architectural decision: extraction was built for "Day 7 foundation" with aggregated values, not per-window data. This was appropriate for initial development but became a blocker when detection and scoring required per-window comparison.

### Theme 2: Windows Platform Gaps
Issues RC-01 and RC-02 are Windows-specific file locking problems. The codebase was developed/tested on Windows but the clone logic doesn't account for Windows-specific file locking behavior.

### Theme 3: Mock-Driven Testing Blind Spots
D-1, D-2, and D-3 were not caught by tests because tests use `MockSegmentationEngine` (always returns 2 windows), `MockExplanationEngine` (hardcoded narratives), and `MockScoringEngine`. Integration tests with real engines would have caught these.

### Theme 4: Simulation vs. Real Execution
RC-05 reveals that benchmark validation was performed with simulated data, not real repository analysis. This is acceptable for development but should be clearly documented in certification artifacts.

---

## Remediation Priority

### P0 — Must Fix Before Release
1. **D-1:** Add minimum window gate (1 line fix, authority-mandated)
2. **D-2:** Fix explanation engine factor names (2 line fix, wrong narratives)

### P1 — Should Fix Before Release
3. **RC-01/RC-02:** Add retry logic to `GitCloner` (Windows compatibility)
4. **RC-03:** Add timeout to `GitCloner` (large repo handling)
5. **RC-06:** Fix atomic write logic (correctness)

### P2 — Document as Architectural Debt
6. **D-4:** Per-window extraction refactoring (significant architectural change)
7. **D-3:** Cannot fix without D-4 (dependent on per-window data)
8. **RC-05:** Document benchmark results as simulated validation

### P3 — Optional Enhancement
9. **RC-04:** Add interface contracts for M-12 and M-13
