# Final Repository Architecture Normalization — Directory Topology Audit

**Program**: MIIE v1.0 Final Repository Architecture Normalization
**Date**: 2026-06-26
**Mode**: READ-ONLY AUDIT

---

## Executive Summary

| Category | Count |
|---|---|
| Top-level directories | 12 |
| Source packages | 15 |
| Documentation categories | 11 |
| Archive directories | 49 |
| Benchmark categories | 8 |

---

## Complete Directory Tree

```
MIEE/
├── .claude/                    (Developer Workspace)
├── .github/                    (CI/CD)
├── .pytest_cache/              (Temporary Output)
├── archive/                    (Archive)
│   ├── cli_test_repo/          (Historical Validation)
│   ├── debug_test/             (Historical Validation)
│   ├── fastapi_test/           (Historical Validation)
│   ├── flask_audit/            (Experimental Work)
│   ├── flask_final/            (Experimental Work)
│   ├── flask_test/             (Historical Validation)
│   ├── markupsafe_test/        (Experimental Work)
│   ├── memory/                 (Temporary Storage)
│   ├── out/                    (Temporary Storage)
│   ├── output/                 (Temporary Storage)
│   ├── rc_cat_a_curl/          (Benchmark Fixture)
│   ├── rc_cat_a_curl_verbose/  (Benchmark Fixture)
│   ├── rc_cat_b_bun/           (Benchmark Fixture)
│   ├── rc_cat_b_langchain/     (Benchmark Fixture)
│   ├── rc_cat_b_llama_cpp/     (Benchmark Fixture)
│   ├── rc_cat_b_ruff/          (Benchmark Fixture)
│   ├── rc_cat_b_transformers/  (Benchmark Fixture)
│   ├── rc_cat_c_express/       (Benchmark Fixture)
│   ├── rc_cat_c_gym/           (Benchmark Fixture)
│   ├── rc_cat_c_moment/        (Benchmark Fixture)
│   ├── rc_cat_c_openoffice/    (Benchmark Fixture)
│   ├── rc_cat_c_requests/      (Experimental Work)
│   ├── rc_cat_d_mariadb/       (Experimental Work)
│   ├── rc_cat_d_opensearch/    (Experimental Work)
│   ├── rc_cat_d_opentofu/      (Experimental Work)
│   ├── rc_cat_d_valkey/        (Experimental Work)
│   ├── rc_cat_d_zed/           (Experimental Work)
│   ├── rc_cat_e_autogen/       (Experimental Work)
│   ├── rc_cat_e_autogen_retry/ (Experimental Work)
│   ├── rc_cat_e_AutoGPT/       (Experimental Work)
│   ├── rc_cat_e_AutoGPT_retry/ (Experimental Work)
│   ├── rc_cat_e_ComfyUI/       (Experimental Work)
│   ├── rc_cat_e_llama_index/   (Experimental Work)
│   ├── rc_cat_e_vllm/          (Experimental Work)
│   ├── rc_cat_f_airflow/       (Experimental Work)
│   ├── rc_cat_f_godot/         (Experimental Work)
│   ├── rc_cat_f_nanoGPT/       (Experimental Work)
│   ├── rc_cat_f_stable-diffusion-webui/ (Temporary Clone)
│   ├── rc_cat_f_the-algorithm/ (Temporary Clone)
│   ├── requests_test/          (Experimental Work)
│   ├── test_output/            (Temporary Storage)
│   ├── test_output_dryrun/     (Temporary Storage)
│   ├── test_output_multiple/   (Temporary Storage)
│   ├── test_output_single/     (Temporary Storage)
│   ├── tmp_output/             (Temporary Storage)
│   ├── tmp_output_ingestion/   (Temporary Storage)
│   └── tmp_output_ingestion2/  (Temporary Storage)
├── benchmarks/                 (Benchmarks)
│   ├── annotations/            (Benchmark Annotations)
│   ├── candidates/             (120 Official Candidates)
│   ├── datasets/               (Dataset Definitions)
│   ├── ground_truth/           (Ground Truth Data)
│   ├── metadata/               (Metadata)
│   ├── results/                (Benchmark Results)
│   ├── runners/                (Benchmark Runners)
│   └── tmp/                    (Temporary Outputs)
├── docs/                       (Documentation)
│   ├── adr/                    (Architecture Decisions)
│   ├── architecture/           (Architecture Docs)
│   ├── audits/                 (Audit Reports)
│   ├── authorities/            (Authority Documents)
│   ├── contracts/              (Contract Docs)
│   ├── execution/              (Execution Reports)
│   ├── governance/             (Release & FUC Reports)
│   ├── paper/                  (Research Paper)
│   ├── prompts/                (Agent Prompts)
│   ├── reports/                (Audit & Progress Reports)
│   └── research/               (Research Materials)
├── output/                     (Runtime Outputs)
├── scripts/                    (Utility Scripts)
├── src/                        (Production Source)
│   └── miie/                   (Main Package)
│       ├── api/                (FastAPI Server)
│       ├── benchmark/          (Benchmark Execution)
│       ├── cli.py              (CLI Entry Point)
│       ├── common/             (Common Utilities)
│       ├── config/             (Configuration)
│       ├── contracts/          (Data Contracts)
│       ├── detection/          (Detection Init)
│       ├── interface/          (Interface Init)
│       ├── orchestration/      (Pipeline Orchestration)
│       ├── processing/         (Core Processing)
│       ├── reporting/          (Reporting Templates)
│       ├── schemas/            (Data Models)
│       ├── storage/            (Storage Init)
│       ├── utils/              (Utilities)
│       └── validation/         (Validation Service)
├── tests/                      (Test Suite)
│   ├── api/                    (API Tests)
│   ├── architecture/           (Architecture Compliance)
│   ├── benchmark/              (Benchmark Validation)
│   ├── contract/               (Interface Contracts)
│   ├── fixtures/               (Test Fixtures)
│   ├── integration/            (Integration Tests)
│   ├── performance/            (Performance Tests)
│   ├── regression/             (Regression Tests)
│   ├── reproducibility/        (Reproducibility Tests)
│   ├── schema/                 (Schema Validation)
│   ├── unit/                   (Unit Tests)
│   └── workflow/               (End-to-End Workflows)
├── tmp_output/                 (Temporary Outputs)
├── tmp_output_ingestion/       (Temporary Outputs)
└── tmp_output_ingestion2/      (Temporary Outputs)
```

---

## Directory Classification

| Directory | Category | Owner |
|---|---|---|
| .claude/ | Developer Workspace | Developer |
| .github/ | CI/CD | DevOps |
| archive/ | Archive | Maintainer |
| benchmarks/ | Benchmarks | Benchmark Engineer |
| docs/ | Documentation | Documentation Engineer |
| output/ | Runtime Output | System |
| scripts/ | Utility | Developer |
| src/ | Production | Developer |
| tests/ | Test Suite | QA |
| tmp_output* | Temporary Output | System |

---

## Verdict

**DIRECTORY TOPOLOGY AUDIT: COMPLETE**

12 top-level directories, 15 source packages, 11 documentation categories.

---

*Directory topology audit completed 2026-06-26*
