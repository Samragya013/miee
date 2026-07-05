# Final Repository Architecture Normalization — Archive Governance Policy

**Program**: MIIE v1.0 Final Repository Architecture Normalization
**Date**: 2026-06-26
**Mode**: READ-ONLY AUDIT

---

## Executive Summary

| Action | Count |
|---|---|
| KEEP_IN_REPOSITORY | 15 |
| MOVE_TO_docs/examples | 0 |
| MOVE_TO_benchmarks | 0 |
| MOVE_TO_docs/research | 0 |
| IGNORE_VIA_.gitignore | 34 |
| DELETE_AFTER_VERIFICATION | 0 |
| MANUAL_REVIEW | 0 |

---

## Archive Policy Decisions

### KEEP_IN_REPOSITORY (15 items)

| Directory | Classification | Reason |
|---|---|---|
| rc_cat_a_curl | BENCHMARK_ASSET | Official benchmark fixture |
| rc_cat_a_curl_verbose | BENCHMARK_ASSET | Official benchmark fixture |
| rc_cat_b_bun | BENCHMARK_ASSET | Official benchmark fixture |
| rc_cat_b_langchain | BENCHMARK_ASSET | Official benchmark fixture |
| rc_cat_b_llama_cpp | BENCHMARK_ASSET | Official benchmark fixture |
| rc_cat_b_ruff | BENCHMARK_ASSET | Official benchmark fixture |
| rc_cat_b_transformers | BENCHMARK_ASSET | Official benchmark fixture |
| rc_cat_c_express | BENCHMARK_ASSET | Official benchmark fixture |
| rc_cat_c_gym | BENCHMARK_ASSET | Official benchmark fixture |
| rc_cat_c_moment | BENCHMARK_ASSET | Official benchmark fixture |
| rc_cat_c_openoffice | BENCHMARK_ASSET | Official benchmark fixture |
| cli_test_repo | HISTORICAL_VALIDATION | CLI testing history |
| debug_test | HISTORICAL_VALIDATION | Debug testing history |
| fastapi_test | HISTORICAL_VALIDATION | FastAPI testing history |
| flask_test | HISTORICAL_VALIDATION | Flask testing history |

### IGNORE_VIA_.gitignore (34 items)

| Directory | Classification | Reason |
|---|---|---|
| rc_cat_c_requests | SCRATCH_EXPERIMENT | Not official benchmark |
| rc_cat_d_mariadb | SCRATCH_EXPERIMENT | Not official benchmark |
| rc_cat_d_opensearch | SCRATCH_EXPERIMENT | Not official benchmark |
| rc_cat_d_opentofu | SCRATCH_EXPERIMENT | Not official benchmark |
| rc_cat_d_valkey | SCRATCH_EXPERIMENT | Not official benchmark |
| rc_cat_d_zed | SCRATCH_EXPERIMENT | Not official benchmark |
| rc_cat_e_autogen | SCRATCH_EXPERIMENT | Not official benchmark |
| rc_cat_e_autogen_retry | SCRATCH_EXPERIMENT | Not official benchmark |
| rc_cat_e_AutoGPT | SCRATCH_EXPERIMENT | Not official benchmark |
| rc_cat_e_AutoGPT_retry | SCRATCH_EXPERIMENT | Not official benchmark |
| rc_cat_e_ComfyUI | SCRATCH_EXPERIMENT | Not official benchmark |
| rc_cat_e_llama_index | SCRATCH_EXPERIMENT | Not official benchmark |
| rc_cat_e_vllm | SCRATCH_EXPERIMENT | Not official benchmark |
| rc_cat_f_airflow | SCRATCH_EXPERIMENT | Not official benchmark |
| rc_cat_f_godot | SCRATCH_EXPERIMENT | Not official benchmark |
| rc_cat_f_nanoGPT | SCRATCH_EXPERIMENT | Not official benchmark |
| rc_cat_f_stable-diffusion-webui | TEMPORARY_CLONE | Temporary clone |
| rc_cat_f_the-algorithm | TEMPORARY_CLONE | Temporary clone |
| memory | TEMPORARY_CLONE | Temporary storage |
| out | TEMPORARY_CLONE | Temporary storage |
| output | TEMPORARY_CLONE | Temporary storage |
| test_output | TEMPORARY_CLONE | Temporary storage |
| test_output_dryrun | TEMPORARY_CLONE | Temporary storage |
| test_output_multiple | TEMPORARY_CLONE | Temporary storage |
| test_output_single | TEMPORARY_CLONE | Temporary storage |
| tmp_output | TEMPORARY_CLONE | Temporary storage |
| tmp_output_ingestion | TEMPORARY_CLONE | Temporary storage |
| tmp_output_ingestion2 | TEMPORARY_CLONE | Temporary storage |
| flask_audit | LOCAL_DEBUG | Debug session |
| flask_final | LOCAL_DEBUG | Debug session |
| markupsafe_test | LOCAL_DEBUG | Debug session |
| requests_test | LOCAL_DEBUG | Debug session |
| dry_run_output | TEMPORARY_STORAGE | Dry run output |
| C?UsersSamragyaDownloadsMIEE.autoresearchmiievalidation | UNKNOWN | Corrupted directory name |

---

## Verdict

**ARCHIVE GOVERNANCE POLICY: COMPLETE**

15 items kept, 34 items to be ignored via .gitignore.

---

*Archive governance policy completed 2026-06-26*
