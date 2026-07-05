# FRASC Phase 4 — Archive Audit

**Program**: MIIE v1.0 Final Release Assembly & Staging Certification
**Date**: 2026-06-26
**Mode**: READ-ONLY AUDIT

---

## Executive Summary

| Category | Count | Classification |
|---|---|---|
| Benchmark fixtures | 11 | KEEP_UNTRACKED |
| Historical validation | 4 | KEEP_UNTRACKED |
| Experimental work | 20 | KEEP_UNTRACKED |
| Temporary clones | 10 | KEEP_UNTRACKED |
| Scratch data | 4 | KEEP_UNTRACKED |
| Release assets | 0 | — |

---

## Archive Classification

### Benchmark Fixtures (11 directories)

| Directory | Classification | Reason |
|---|---|---|
| rc_cat_a_curl | BENCHMARK_FIXTURE | GitHub API testing |
| rc_cat_a_curl_verbose | BENCHMARK_FIXTURE | GitHub API testing |
| rc_cat_b_bun | BENCHMARK_FIXTURE | Runtime benchmark |
| rc_cat_b_langchain | BENCHMARK_FIXTURE | Runtime benchmark |
| rc_cat_b_llama_cpp | BENCHMARK_FIXTURE | Runtime benchmark |
| rc_cat_b_ruff | BENCHMARK_FIXTURE | Runtime benchmark |
| rc_cat_b_transformers | BENCHMARK_FIXTURE | Runtime benchmark |
| rc_cat_c_express | BENCHMARK_FIXTURE | Runtime benchmark |
| rc_cat_c_gym | BENCHMARK_FIXTURE | Runtime benchmark |
| rc_cat_c_moment | BENCHMARK_FIXTURE | Runtime benchmark |
| rc_cat_c_openoffice | BENCHMARK_FIXTURE | Runtime benchmark |

### Historical Validation (4 directories)

| Directory | Classification | Reason |
|---|---|---|
| cli_test_repo | HISTORICAL_VALIDATION | CLI testing |
| debug_test | HISTORICAL_VALIDATION | Debug testing |
| fastapi_test | HISTORICAL_VALIDATION | FastAPI testing |
| flask_test | HISTORICAL_VALIDATION | Flask testing |

### Experimental Work (20 directories)

| Directory | Classification | Reason |
|---|---|---|
| flask_audit | EXPERIMENTAL_WORK | Flask audit |
| flask_final | EXPERIMENTAL_WORK | Flask final |
| markupsafe_test | EXPERIMENTAL_WORK | MarkupSafe testing |
| requests_test | EXPERIMENTAL_WORK | Requests testing |
| rc_cat_c_requests | EXPERIMENTAL_WORK | Requests benchmark |
| rc_cat_d_mariadb | EXPERIMENTAL_WORK | MariaDB benchmark |
| rc_cat_d_opensearch | EXPERIMENTAL_WORK | OpenSearch benchmark |
| rc_cat_d_opentofu | EXPERIMENTAL_WORK | OpenTofu benchmark |
| rc_cat_d_valkey | EXPERIMENTAL_WORK | Valkey benchmark |
| rc_cat_d_zed | EXPERIMENTAL_WORK | Zed benchmark |
| rc_cat_e_autogen | EXPERIMENTAL_WORK | AutoGen benchmark |
| rc_cat_e_autogen_retry | EXPERIMENTAL_WORK | AutoGen retry |
| rc_cat_e_AutoGPT | EXPERIMENTAL_WORK | AutoGPT benchmark |
| rc_cat_e_AutoGPT_retry | EXPERIMENTAL_WORK | AutoGPT retry |
| rc_cat_e_ComfyUI | EXPERIMENTAL_WORK | ComfyUI benchmark |
| rc_cat_e_llama_index | EXPERIMENTAL_WORK | LlamaIndex benchmark |
| rc_cat_e_vllm | EXPERIMENTAL_WORK | vLLM benchmark |
| rc_cat_f_airflow | EXPERIMENTAL_WORK | Airflow benchmark |
| rc_cat_f_godot | EXPERIMENTAL_WORK | Godot benchmark |
| rc_cat_f_nanoGPT | EXPERIMENTAL_WORK | nanoGPT benchmark |

### Temporary Clones (10 directories)

| Directory | Classification | Reason |
|---|---|---|
| rc_cat_f_stable-diffusion-webui | TEMPORARY_CLONE | WebUI clone |
| rc_cat_f_the-algorithm | TEMPORARY_CLONE | Algorithm clone |
| memory | TEMPORARY_CLONE | Memory storage |
| out | TEMPORARY_CLONE | Output storage |
| output | TEMPORARY_CLONE | Output storage |
| test_output | TEMPORARY_CLONE | Test output |
| test_output_dryrun | TEMPORARY_CLONE | Dry run output |
| test_output_multiple | TEMPORARY_CLONE | Multiple output |
| test_output_single | TEMPORARY_CLONE | Single output |
| tmp_output | TEMPORARY_CLONE | Temp output |

### Scratch Data (4 files)

| File | Classification | Reason |
|---|---|---|
| .coverage | SCRATCH_DATA | Coverage report |
| day15_loop.json | SCRATCH_DATA | Loop state |
| extract_risk.py | SCRATCH_DATA | Extraction script |
| extract_summary.py | SCRATCH_DATA | Extraction script |
| FERA_LOOP_STATE.json | SCRATCH_DATA | Loop state |
| flask_debug.log | SCRATCH_DATA | Debug log |
| test2_output.txt | SCRATCH_DATA | Test output |
| test2b_output.txt | SCRATCH_DATA | Test output |
| test2c_output.txt | SCRATCH_DATA | Test output |
| test3_output.txt | SCRATCH_DATA | Test output |

---

## Verdict

**ARCHIVE AUDIT: COMPLETE**

49 directories classified. All internal, none required for release.

---

*Archive audit completed 2026-06-26*
