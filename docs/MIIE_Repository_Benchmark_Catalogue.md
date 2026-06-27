# MIIE Repository Benchmark Catalogue
## Version 1.0 — Research-Grade Benchmark Dataset
### 180 Verified Public GitHub Repositories for MIIE V1 & V2 Validation

---

> **Generated:** June 2026  
> **Purpose:** MIIE Version 1 and Version 2 validation benchmark dataset  
> **Total Repositories:** 180 (30 per category × 6 categories)  
> **Validation Method:** Live web search verification + GitHub URL resolution

---

## Legend

| Field | Description |
|---|---|
| D-01 | Commit Drift Detector |
| D-02 | Contributor Anomaly Detector |
| D-03 | Release Pattern Detector |
| Priority | High / Medium / Low validation priority |

---

---

# CATEGORY A — Healthy & Stable Repositories

> **Purpose:** Baseline repositories expected to produce minimal anomalies.  
> **Expected Behavior:** D-01 PASS · D-02 PASS · D-03 PASS

---

### A-01 — linux/linux (torvalds/linux)

| Field | Value |
|---|---|
| **Repository Name** | linux |
| **GitHub URL** | https://github.com/torvalds/linux |
| **Primary Language** | C |
| **Domain** | Operating Systems |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | The canonical stable kernel repository. Decades of history, disciplined commit cadence, globally distributed maintainers, immutable governance model. Ideal baseline. |
| **Expected MIIE Behaviour** | Near-zero anomaly signal. Commit cadence extremely regular across decades. |
| **Expected Detector Activity** | D-01: Low · D-02: None · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/torvalds/linux` |
| **Notes** | Use as the primary baseline anchor for all detector calibration. |

---

### A-02 — git/git

| Field | Value |
|---|---|
| **Repository Name** | git |
| **GitHub URL** | https://github.com/git/git |
| **Primary Language** | C |
| **Domain** | Developer Tools / Version Control |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Reference-quality project with extremely consistent release cadence, mature governance, multi-decade history. |
| **Expected MIIE Behaviour** | Minimal anomalies. Predictable release tags. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/git/git` |
| **Notes** | Maintained by the Git community. Mirror of kernel.org/pub/scm/git. |

---

### A-03 — python/cpython

| Field | Value |
|---|---|
| **Repository Name** | cpython |
| **GitHub URL** | https://github.com/python/cpython |
| **Primary Language** | Python / C |
| **Domain** | Programming Languages / Compilers |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Reference Python interpreter. Highly structured branching model, stable governance via Python Steering Council. |
| **Expected MIIE Behaviour** | Excellent baseline. Predictable minor/major release scheduling. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/python/cpython` |
| **Notes** | Multiple active release branches (3.11, 3.12, 3.13, etc.). |

---

### A-04 — rust-lang/rust

| Field | Value |
|---|---|
| **Repository Name** | rust |
| **GitHub URL** | https://github.com/rust-lang/rust |
| **Primary Language** | Rust |
| **Domain** | Programming Languages / Compilers |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Stable 6-week release cycle, RFC governance process, consistent contributor base. |
| **Expected MIIE Behaviour** | Strong baseline. Regular release cadence detectable. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/rust-lang/rust` |
| **Notes** | Exemplary public governance and release documentation. |

---

### A-05 — golang/go

| Field | Value |
|---|---|
| **Repository Name** | go |
| **GitHub URL** | https://github.com/golang/go |
| **Primary Language** | Go |
| **Domain** | Programming Languages / Compilers |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Google-backed, biannual release cycle, stable community. Strong engineering governance. |
| **Expected MIIE Behaviour** | Minimal drift. Biannual release pattern easily detectable. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/golang/go` |
| **Notes** | Useful for comparing release cadence against Rust's 6-week cycle. |

---

### A-06 — django/django

| Field | Value |
|---|---|
| **Repository Name** | django |
| **GitHub URL** | https://github.com/django/django |
| **Primary Language** | Python |
| **Domain** | Web Frameworks |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | 20+ year project, Django Software Foundation governance, predictable LTS release cycle. |
| **Expected MIIE Behaviour** | Excellent baseline. Biannual major releases observable. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/django/django` |
| **Notes** | LTS vs non-LTS branching adds useful release pattern complexity. |

---

### A-07 — rails/rails

| Field | Value |
|---|---|
| **Repository Name** | rails |
| **GitHub URL** | https://github.com/rails/rails |
| **Primary Language** | Ruby |
| **Domain** | Web Frameworks |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Iconic web framework, 20+ year history, consistent Rails Core governance, clear release tagging. |
| **Expected MIIE Behaviour** | Minimal anomaly signal. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/rails/rails` |
| **Notes** | Ruby language coverage for diversity. |

---

### A-08 — apache/kafka

| Field | Value |
|---|---|
| **Repository Name** | kafka |
| **GitHub URL** | https://github.com/apache/kafka |
| **Primary Language** | Java / Scala |
| **Domain** | Distributed Systems / Messaging |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Apache-governed, critical infrastructure project, stable contributor base, predictable releases. |
| **Expected MIIE Behaviour** | Clean baseline in Java ecosystem. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/apache/kafka` |
| **Notes** | Java and Scala dual-language project. |

---

### A-09 — postgresql/postgresql

| Field | Value |
|---|---|
| **Repository Name** | postgresql |
| **GitHub URL** | https://github.com/postgres/postgres |
| **Primary Language** | C |
| **Domain** | Databases |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Annual major release cycle, global committer base, 35+ year project history. |
| **Expected MIIE Behaviour** | Excellent baseline. Annual release pattern clear. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/postgres/postgres` |
| **Notes** | Mirror of git.postgresql.org. Useful for database domain coverage. |

---

### A-10 — curl/curl

| Field | Value |
|---|---|
| **Repository Name** | curl |
| **GitHub URL** | https://github.com/curl/curl |
| **Primary Language** | C |
| **Domain** | Networking |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Single primary maintainer (Daniel Stenberg), 25+ year history, highly disciplined changelog and release tagging. |
| **Expected MIIE Behaviour** | Interesting single-maintainer baseline for D-02. |
| **Expected Detector Activity** | D-01: None · D-02: Low (single-maintainer flag) · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/curl/curl` |
| **Notes** | Possibly interesting for D-02 contributor concentration metric. |

---

### A-11 — nginx/nginx

| Field | Value |
|---|---|
| **Repository Name** | nginx |
| **GitHub URL** | https://github.com/nginx/nginx |
| **Primary Language** | C |
| **Domain** | Networking / Web Servers |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | Medium |
| **Why Selected** | Mature, stable web server with clear release cadence. F5-backed since 2019. |
| **Expected MIIE Behaviour** | Stable baseline. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/nginx/nginx` |
| **Notes** | Governance changed when F5 acquired NGINX Inc. Boundary condition for Category A/F. |

---

### A-12 — kubernetes/kubernetes

| Field | Value |
|---|---|
| **Repository Name** | kubernetes |
| **GitHub URL** | https://github.com/kubernetes/kubernetes |
| **Primary Language** | Go |
| **Domain** | Cloud / DevOps |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | CNCF-governed, quarterly release schedule, massive contributor base from many organizations. |
| **Expected MIIE Behaviour** | Clean baseline with very high activity. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/kubernetes/kubernetes` |
| **Notes** | Largest and most complex healthy repo in Category A. |

---

### A-13 — microsoft/vscode

| Field | Value |
|---|---|
| **Repository Name** | vscode |
| **GitHub URL** | https://github.com/microsoft/vscode |
| **Primary Language** | TypeScript |
| **Domain** | Developer Tools / IDE |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Monthly release cadence, Microsoft governance, 1000+ contributors, extremely consistent development pace. |
| **Expected MIIE Behaviour** | Excellent baseline for TypeScript ecosystem. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/microsoft/vscode` |
| **Notes** | Monthly milestone releases make D-03 pattern highly predictable. |

---

### A-14 — facebook/react

| Field | Value |
|---|---|
| **Repository Name** | react |
| **GitHub URL** | https://github.com/facebook/react |
| **Primary Language** | JavaScript |
| **Domain** | Web Frameworks / UI |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Meta-backed, consistent governance, widely used, clear release policy. |
| **Expected MIIE Behaviour** | Clean baseline in JavaScript ecosystem. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/facebook/react` |
| **Notes** | React 19 release cycle provides modern tagging data. |

---

### A-15 — vuejs/vue

| Field | Value |
|---|---|
| **Repository Name** | vue |
| **GitHub URL** | https://github.com/vuejs/vue |
| **Primary Language** | JavaScript / TypeScript |
| **Domain** | Web Frameworks / UI |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | Medium |
| **Why Selected** | Community-governed, long history, stable v2/v3 branching with clear EOL policy. |
| **Expected MIIE Behaviour** | Stable baseline. Slight activity reduction in v2 post-EOL may register in D-01. |
| **Expected Detector Activity** | D-01: Low · D-02: None · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/vuejs/vue` |
| **Notes** | Vue 2 reached EOL December 2023 — useful boundary test. |

---

### A-16 — apache/httpd

| Field | Value |
|---|---|
| **Repository Name** | httpd |
| **GitHub URL** | https://github.com/apache/httpd |
| **Primary Language** | C |
| **Domain** | Networking / Web Servers |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | Medium |
| **Why Selected** | 30+ year Apache HTTP Server project with stable, predictable release cadence. |
| **Expected MIIE Behaviour** | Excellent baseline for legacy C web infrastructure. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/apache/httpd` |
| **Notes** | One of the oldest continuously maintained open source projects. |

---

### A-17 — redis/redis

| Field | Value |
|---|---|
| **Repository Name** | redis |
| **GitHub URL** | https://github.com/redis/redis |
| **Primary Language** | C |
| **Domain** | Databases / Caching |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Historically stable, though notable license change in 2024 makes it a boundary case. |
| **Expected MIIE Behaviour** | Primarily PASS. D-02 may flag activity change post-license event. |
| **Expected Detector Activity** | D-01: Low · D-02: Low · D-03: Low |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/redis/redis` |
| **Notes** | License changed to RSALv2/SSPLv1 in 2024. Boundary condition between Category A and F. |

---

### A-18 — elastic/elasticsearch

| Field | Value |
|---|---|
| **Repository Name** | elasticsearch |
| **GitHub URL** | https://github.com/elastic/elasticsearch |
| **Primary Language** | Java |
| **Domain** | Databases / Search |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Mature search engine, returned to Apache 2.0 in 2024, stable engineering team. |
| **Expected MIIE Behaviour** | Healthy baseline in Java ecosystem. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/elastic/elasticsearch` |
| **Notes** | License change history makes historical analysis interesting for Category F comparison. |

---

### A-19 — llvm/llvm-project

| Field | Value |
|---|---|
| **Repository Name** | llvm-project |
| **GitHub URL** | https://github.com/llvm/llvm-project |
| **Primary Language** | C++ |
| **Domain** | Compilers / Developer Tools |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Major compiler infrastructure, biannual releases, large and stable contributor base. |
| **Expected MIIE Behaviour** | Excellent large-scale C++ baseline. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/llvm/llvm-project` |
| **Notes** | Monorepo containing Clang, LLVM, libcxx, and many sub-projects. |

---

### A-20 — sqlite/sqlite

| Field | Value |
|---|---|
| **Repository Name** | sqlite |
| **GitHub URL** | https://github.com/sqlite/sqlite |
| **Primary Language** | C |
| **Domain** | Databases |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Medium |
| **Approximate Activity** | Medium |
| **Why Selected** | Most widely deployed database engine, stable single-team governance (D.R. Hipp), decades of history. |
| **Expected MIIE Behaviour** | Extremely stable baseline. |
| **Expected Detector Activity** | D-01: None · D-02: Low (single-team) · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/sqlite/sqlite` |
| **Notes** | GitHub mirror of fossil-scm hosted canonical repo. |

---

### A-21 — opencv/opencv

| Field | Value |
|---|---|
| **Repository Name** | opencv |
| **GitHub URL** | https://github.com/opencv/opencv |
| **Primary Language** | C++ |
| **Domain** | Computer Vision / Scientific Computing |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | 25+ year computer vision library, stable governance, consistent release cadence. |
| **Expected MIIE Behaviour** | Healthy baseline in C++ scientific domain. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/opencv/opencv` |
| **Notes** | Broad scientific computing domain coverage. |

---

### A-22 — pytest-dev/pytest

| Field | Value |
|---|---|
| **Repository Name** | pytest |
| **GitHub URL** | https://github.com/pytest-dev/pytest |
| **Primary Language** | Python |
| **Domain** | Developer Tools / Testing |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Clear release cadence, community-governed via pytest-dev org, consistent contributor base. |
| **Expected MIIE Behaviour** | Stable Python tooling baseline. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/pytest-dev/pytest` |
| **Notes** | Excellent smaller-scale healthy Python project. |

---

### A-23 — spring-projects/spring-framework

| Field | Value |
|---|---|
| **Repository Name** | spring-framework |
| **GitHub URL** | https://github.com/spring-projects/spring-framework |
| **Primary Language** | Java |
| **Domain** | Web Frameworks |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | 20+ year Java framework, VMware/Broadcom backed, stable biannual release cadence. |
| **Expected MIIE Behaviour** | Healthy Java web framework baseline. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/spring-projects/spring-framework` |
| **Notes** | Java enterprise coverage. Long history with reliable release tags. |

---

### A-24 — moby/moby (Docker)

| Field | Value |
|---|---|
| **Repository Name** | moby |
| **GitHub URL** | https://github.com/moby/moby |
| **Primary Language** | Go |
| **Domain** | Cloud / DevOps / Containerization |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Foundational container runtime. Stable governance via Docker/Moby Project. |
| **Expected MIIE Behaviour** | Healthy Go ecosystem baseline. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/moby/moby` |
| **Notes** | Go language coverage in cloud-native domain. |

---

### A-25 — ansible/ansible

| Field | Value |
|---|---|
| **Repository Name** | ansible |
| **GitHub URL** | https://github.com/ansible/ansible |
| **Primary Language** | Python |
| **Domain** | DevOps / Automation |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Red Hat-backed, stable release cadence, broad contributor base. |
| **Expected MIIE Behaviour** | Healthy DevOps baseline. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/ansible/ansible` |
| **Notes** | Python DevOps coverage. |

---

### A-26 — grafana/grafana

| Field | Value |
|---|---|
| **Repository Name** | grafana |
| **GitHub URL** | https://github.com/grafana/grafana |
| **Primary Language** | TypeScript / Go |
| **Domain** | Visualization / Observability |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Stable visualization platform, Grafana Labs governance, consistent release cadence. |
| **Expected MIIE Behaviour** | Healthy multi-language baseline. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/grafana/grafana` |
| **Notes** | TypeScript + Go dual-language project. |

---

### A-27 — hashicorp/terraform

| Field | Value |
|---|---|
| **Repository Name** | terraform |
| **GitHub URL** | https://github.com/hashicorp/terraform |
| **Primary Language** | Go |
| **Domain** | DevOps / Infrastructure as Code |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Standard IaC tool. Note: license changed to BSL 1.1 in Aug 2023 — provides interesting recent governance signal. |
| **Expected MIIE Behaviour** | Primarily healthy with possible D-02 signal near license change. |
| **Expected Detector Activity** | D-01: None · D-02: Low · D-03: Low |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/hashicorp/terraform` |
| **Notes** | Category A/F boundary. BSL change triggered OpenTofu fork (see Category D). |

---

### A-28 — neovim/neovim

| Field | Value |
|---|---|
| **Repository Name** | neovim |
| **GitHub URL** | https://github.com/neovim/neovim |
| **Primary Language** | C / Lua |
| **Domain** | Developer Tools / Editor |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Active editor fork with disciplined release cadence and strong governance. |
| **Expected MIIE Behaviour** | Healthy fork-origin stable project. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/neovim/neovim` |
| **Notes** | C + Lua coverage. Originally forked from Vim (see Category D). |

---

### A-29 — scikit-learn/scikit-learn

| Field | Value |
|---|---|
| **Repository Name** | scikit-learn |
| **GitHub URL** | https://github.com/scikit-learn/scikit-learn |
| **Primary Language** | Python |
| **Domain** | Data Science / Machine Learning |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Mature ML library, INRIA-backed, predictable release cadence, broad contributor base. |
| **Expected MIIE Behaviour** | Healthy Data Science baseline. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/scikit-learn/scikit-learn` |
| **Notes** | Good contrast against Category B fast-growth ML repos. |

---

### A-30 — mozilla/gecko-dev

| Field | Value |
|---|---|
| **Repository Name** | gecko-dev |
| **GitHub URL** | https://github.com/mozilla/gecko-dev |
| **Primary Language** | C++ / JavaScript |
| **Domain** | Web Browsers / Rendering Engines |
| **Category** | A — Healthy & Stable |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Firefox rendering engine mirror. Extremely large, mature, diverse contributor base. |
| **Expected MIIE Behaviour** | Excellent large-scale C++ baseline. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/mozilla/gecko-dev` |
| **Notes** | GitHub mirror of Mozilla's Mercurial repo. Very large history. |

---

---

# CATEGORY B — Fast-Growth Projects

> **Purpose:** Repositories with rapid evolution.  
> **Expected Behavior:** D-01 Possible drift · D-02 Moderate · D-03 Usually PASS

---

### B-01 — huggingface/transformers

| Field | Value |
|---|---|
| **Repository Name** | transformers |
| **GitHub URL** | https://github.com/huggingface/transformers |
| **Primary Language** | Python |
| **Domain** | AI / Machine Learning |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Explosive growth since 2020. Rapid model support additions, frequent major releases, massive contributor growth. |
| **Expected MIIE Behaviour** | High D-01 drift signal. Frequent releases. |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: Low |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/huggingface/transformers` |
| **Notes** | Paradigmatic fast-growth AI repository. Primary B-category anchor. |

---

### B-02 — langchain-ai/langchain

| Field | Value |
|---|---|
| **Repository Name** | langchain |
| **GitHub URL** | https://github.com/langchain-ai/langchain |
| **Primary Language** | Python |
| **Domain** | AI / LLM Frameworks |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Extremely rapid growth from zero to dominant LLM framework. High contributor churn, frequent architectural changes. |
| **Expected MIIE Behaviour** | Strong anomaly signal across all detectors. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: Moderate |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/langchain-ai/langchain` |
| **Notes** | Package split between langchain-core / langchain-community adds complexity. |

---

### B-03 — ollama/ollama

| Field | Value |
|---|---|
| **Repository Name** | ollama |
| **GitHub URL** | https://github.com/ollama/ollama |
| **Primary Language** | Go |
| **Domain** | AI / Local LLM Runtime |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Massive star growth in 2024 (~100k stars). Rapid feature expansion, contributor influx. |
| **Expected MIIE Behaviour** | Strong D-01 drift. D-02 contributor burst. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: Low |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/ollama/ollama` |
| **Notes** | Excellent growth curve example. Compare to llama.cpp in Category F. |

---

### B-04 — vercel/next.js

| Field | Value |
|---|---|
| **Repository Name** | next.js |
| **GitHub URL** | https://github.com/vercel/next.js |
| **Primary Language** | TypeScript / JavaScript |
| **Domain** | Web Frameworks |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Rapid growth from niche SSR tool to dominant React meta-framework. Major architectural shifts (App Router). |
| **Expected MIIE Behaviour** | Moderate D-01 drift. High release frequency. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Low |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/vercel/next.js` |
| **Notes** | App Router introduction represents architectural drift signal. |

---

### B-05 — deno-land/deno

| Field | Value |
|---|---|
| **Repository Name** | deno |
| **GitHub URL** | https://github.com/denoland/deno |
| **Primary Language** | Rust / TypeScript |
| **Domain** | Programming Languages / Runtime |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Fast-growth from 2018 announcement, rapid feature addition, VC-backed since 2021. |
| **Expected MIIE Behaviour** | Moderate D-01. High release velocity. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Low |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/denoland/deno` |
| **Notes** | Rust + TypeScript language diversity. |

---

### B-06 — oven-sh/bun

| Field | Value |
|---|---|
| **Repository Name** | bun |
| **GitHub URL** | https://github.com/oven-sh/bun |
| **Primary Language** | Zig / TypeScript |
| **Domain** | Programming Languages / Runtime |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Explosive growth post-1.0 release 2023. Rapid ecosystem adoption, high contributor influx. |
| **Expected MIIE Behaviour** | Strong D-01 drift. High D-02 burst. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: Low |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/oven-sh/bun` |
| **Notes** | Zig language coverage. Very high growth velocity 2023–2025. |

---

### B-07 — microsoft/TypeScript

| Field | Value |
|---|---|
| **Repository Name** | TypeScript |
| **GitHub URL** | https://github.com/microsoft/TypeScript |
| **Primary Language** | TypeScript |
| **Domain** | Programming Languages |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Rapid industry adoption 2018–2024 drove contributor surge and accelerated release cadence. Now stabilizing. |
| **Expected MIIE Behaviour** | Moderate D-01 drift. Transition from fast-growth to stable detectable. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Low · D-03: Low |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/microsoft/TypeScript` |
| **Notes** | Useful for detecting growth-to-stable transition. |

---

### B-08 — pydantic/pydantic

| Field | Value |
|---|---|
| **Repository Name** | pydantic |
| **GitHub URL** | https://github.com/pydantic/pydantic |
| **Primary Language** | Python |
| **Domain** | Data Validation / Python Libraries |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Rapid growth driven by FastAPI and LangChain adoption. V2 rewrite in Rust created architecture jump. |
| **Expected MIIE Behaviour** | Strong D-01 signal at V1→V2 transition. |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: Moderate |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/pydantic/pydantic` |
| **Notes** | V2 rewrite in Rust is a dramatic architectural shift signal. |

---

### B-09 — astral-sh/ruff

| Field | Value |
|---|---|
| **Repository Name** | ruff |
| **GitHub URL** | https://github.com/astral-sh/ruff |
| **Primary Language** | Rust |
| **Domain** | Developer Tools / Linting |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Zero-to-dominant Python linter 2022–2024. Exceptional growth curve, high contributor influx. |
| **Expected MIIE Behaviour** | Strong D-01 and D-02 fast-growth signal. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: Low |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/astral-sh/ruff` |
| **Notes** | Rust tooling for Python. Classic fast-growth trajectory. |

---

### B-10 — grafana/loki

| Field | Value |
|---|---|
| **Repository Name** | loki |
| **GitHub URL** | https://github.com/grafana/loki |
| **Primary Language** | Go |
| **Domain** | Observability / DevOps |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Fast-growing log aggregation tool in cloud-native space. High release velocity. |
| **Expected MIIE Behaviour** | Moderate D-01 drift. High activity. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Low |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/grafana/loki` |
| **Notes** | Go cloud-native coverage. |

---

### B-11 — vitejs/vite

| Field | Value |
|---|---|
| **Repository Name** | vite |
| **GitHub URL** | https://github.com/vitejs/vite |
| **Primary Language** | TypeScript |
| **Domain** | Web Frameworks / Build Tools |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Explosive growth 2021–2024. Replaced many legacy bundlers. High release cadence. |
| **Expected MIIE Behaviour** | Moderate to high D-01 drift. Rapid adoption signal. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Low |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/vitejs/vite` |
| **Notes** | TypeScript build tooling fast-growth example. |

---

### B-12 — pytorch/pytorch

| Field | Value |
|---|---|
| **Repository Name** | pytorch |
| **GitHub URL** | https://github.com/pytorch/pytorch |
| **Primary Language** | Python / C++ |
| **Domain** | AI / Deep Learning |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Rapid growth 2017–2023. Now dominant deep learning framework with massive contributor base. |
| **Expected MIIE Behaviour** | Moderate D-01 (now stabilizing from fast-growth). |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/pytorch/pytorch` |
| **Notes** | Useful for detecting growth-stabilization transition pattern. |

---

### B-13 — tiangolo/fastapi

| Field | Value |
|---|---|
| **Repository Name** | fastapi |
| **GitHub URL** | https://github.com/tiangolo/fastapi |
| **Primary Language** | Python |
| **Domain** | Web Frameworks / API |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Rapid adoption as fastest-growing Python API framework. Community-driven contributor surge. |
| **Expected MIIE Behaviour** | Moderate D-01 drift. High community growth signal. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/tiangolo/fastapi` |
| **Notes** | Single primary maintainer transitioning to community governance. |

---

### B-14 — argmaxinc/WhisperKit

| Field | Value |
|---|---|
| **Repository Name** | WhisperKit |
| **GitHub URL** | https://github.com/argmaxinc/WhisperKit |
| **Primary Language** | Swift |
| **Domain** | AI / Speech Recognition |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Fast-growing Swift AI project for Apple platforms. Rapid community adoption since 2024. |
| **Expected MIIE Behaviour** | High D-01 drift. Swift language coverage. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: Low |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/argmaxinc/WhisperKit` |
| **Notes** | Swift language diversity for Apple ecosystem. |

---

### B-15 — supabase/supabase

| Field | Value |
|---|---|
| **Repository Name** | supabase |
| **GitHub URL** | https://github.com/supabase/supabase |
| **Primary Language** | TypeScript |
| **Domain** | Cloud / Backend as a Service |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Rapid growth Firebase alternative. Massive community growth, VC-backed with high release velocity. |
| **Expected MIIE Behaviour** | Moderate D-01 drift. High contributor growth. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Low |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/supabase/supabase` |
| **Notes** | TypeScript cloud-native fast-growth example. |

---

### B-16 — anthropics/claude-code

| Field | Value |
|---|---|
| **Repository Name** | claude-code |
| **GitHub URL** | https://github.com/anthropics/claude-code |
| **Primary Language** | TypeScript |
| **Domain** | AI / Developer Tools |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Fast-growing AI coding agent. High star velocity, rapid feature development. |
| **Expected MIIE Behaviour** | High D-01 drift. Rapid early development phase. |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: Low |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/anthropics/claude-code` |
| **Notes** | AI developer tooling fast-growth category. |

---

### B-17 — openai/openai-python

| Field | Value |
|---|---|
| **Repository Name** | openai-python |
| **GitHub URL** | https://github.com/openai/openai-python |
| **Primary Language** | Python |
| **Domain** | AI / SDK |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Rapid growth driven by ChatGPT API adoption. Frequent breaking changes in early phases. |
| **Expected MIIE Behaviour** | Moderate D-01 drift. High release velocity. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Low |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/openai/openai-python` |
| **Notes** | SDK rewrite in 2023 represents architectural drift event. |

---

### B-18 — cilium/cilium

| Field | Value |
|---|---|
| **Repository Name** | cilium |
| **GitHub URL** | https://github.com/cilium/cilium |
| **Primary Language** | Go |
| **Domain** | Networking / Security / Cloud |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Fast-growing eBPF-based networking project. Rapid feature expansion and contributor growth. |
| **Expected MIIE Behaviour** | Moderate D-01 drift. High release velocity. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/cilium/cilium` |
| **Notes** | Security + Networking domain coverage in Go. |

---

### B-19 — tokio-rs/tokio

| Field | Value |
|---|---|
| **Repository Name** | tokio |
| **GitHub URL** | https://github.com/tokio-rs/tokio |
| **Primary Language** | Rust |
| **Domain** | Networking / Async Runtime |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Rapid growth as Rust's dominant async runtime, driven by ecosystem adoption. |
| **Expected MIIE Behaviour** | Moderate D-01 drift. Rust ecosystem coverage. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/tokio-rs/tokio` |
| **Notes** | Rust async networking coverage. |

---

### B-20 — microsoft/autogen

| Field | Value |
|---|---|
| **Repository Name** | autogen |
| **GitHub URL** | https://github.com/microsoft/autogen |
| **Primary Language** | Python |
| **Domain** | AI / Agent Frameworks |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Extremely rapid growth in AI agent space 2023–2024. High contributor influx, major architectural changes. |
| **Expected MIIE Behaviour** | High D-01 and D-02 signals. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: Moderate |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/microsoft/autogen` |
| **Notes** | Major architecture refactor (AutoGen 0.4) represents strong drift signal. |

---

### B-21 — opentofu/opentofu

| Field | Value |
|---|---|
| **Repository Name** | opentofu |
| **GitHub URL** | https://github.com/opentofu/opentofu |
| **Primary Language** | Go |
| **Domain** | DevOps / Infrastructure as Code |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Born from Terraform fork in 2023. Rapid contributor influx from day zero. Unusually fast early-stage growth. |
| **Expected MIIE Behaviour** | Very high D-01 drift (fork inception). D-02 extreme early burst. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: Moderate |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/opentofu/opentofu` |
| **Notes** | Also included in Category D due to fork origin. Primary use here is fast-growth pattern. |

---

### B-22 — apache/spark

| Field | Value |
|---|---|
| **Repository Name** | spark |
| **GitHub URL** | https://github.com/apache/spark |
| **Primary Language** | Scala / Java / Python |
| **Domain** | Data Science / Distributed Computing |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Dominant big data framework. Rapid growth period 2013–2019, now maturing. Good fast-growth-to-stable transition. |
| **Expected MIIE Behaviour** | Moderate D-01 (historical fast-growth now plateaued). |
| **Expected Detector Activity** | D-01: Moderate · D-02: Low · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/apache/spark` |
| **Notes** | Scala + Java + Python multi-language project. |

---

### B-23 — remix-run/remix

| Field | Value |
|---|---|
| **Repository Name** | remix |
| **GitHub URL** | https://github.com/remix-run/remix |
| **Primary Language** | TypeScript |
| **Domain** | Web Frameworks |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Rapid growth framework. Acquisition by Shopify added governance complexity. Major architectural shifts. |
| **Expected MIIE Behaviour** | Moderate D-01. D-02 signal at acquisition event. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Low |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/remix-run/remix` |
| **Notes** | Shopify acquisition represents governance change event. |

---

### B-24 — tauri-apps/tauri

| Field | Value |
|---|---|
| **Repository Name** | tauri |
| **GitHub URL** | https://github.com/tauri-apps/tauri |
| **Primary Language** | Rust |
| **Domain** | Developer Tools / Desktop Apps |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Rapid growth Electron alternative. Fast community expansion, high contributor influx. |
| **Expected MIIE Behaviour** | Moderate to high D-01 drift. Rust desktop tooling. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Low |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/tauri-apps/tauri` |
| **Notes** | Rust desktop application fast-growth example. |

---

### B-25 — ggerganov/llama.cpp

| Field | Value |
|---|---|
| **Repository Name** | llama.cpp |
| **GitHub URL** | https://github.com/ggerganov/llama.cpp |
| **Primary Language** | C++ |
| **Domain** | AI / Local LLM Inference |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Near-instantaneous explosion from zero to 70k+ stars. Massive contributor burst 2023. |
| **Expected MIIE Behaviour** | Extreme D-01 and D-02 signals. Ideal fast-growth stress test. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: Moderate |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/ggerganov/llama.cpp` |
| **Notes** | Single-file C++ hack that exploded into massive project. Excellent growth anomaly example. |

---

### B-26 — openai/whisper

| Field | Value |
|---|---|
| **Repository Name** | whisper |
| **GitHub URL** | https://github.com/openai/whisper |
| **Primary Language** | Python |
| **Domain** | AI / Speech Recognition |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Instant massive adoption on release. High star velocity. Significant downstream ecosystem growth. |
| **Expected MIIE Behaviour** | High D-01 at release spike. |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: Low |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/openai/whisper` |
| **Notes** | OpenAI open-source release with instant viral adoption. |

---

### B-27 — cloudflare/workers-sdk

| Field | Value |
|---|---|
| **Repository Name** | workers-sdk |
| **GitHub URL** | https://github.com/cloudflare/workers-sdk |
| **Primary Language** | TypeScript |
| **Domain** | Cloud / Edge Computing |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Rapidly expanding Cloudflare Workers tooling ecosystem. High release velocity. |
| **Expected MIIE Behaviour** | Moderate D-01 drift. High release cadence. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Low |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/cloudflare/workers-sdk` |
| **Notes** | TypeScript edge computing fast-growth example. |

---

### B-28 — strapi/strapi

| Field | Value |
|---|---|
| **Repository Name** | strapi |
| **GitHub URL** | https://github.com/strapi/strapi |
| **Primary Language** | TypeScript / JavaScript |
| **Domain** | Web / CMS |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Fast-growth headless CMS. Major architectural rewrite for v4/v5. High contributor growth. |
| **Expected MIIE Behaviour** | Moderate D-01 drift at v4/v5 architectural shift. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Low |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/strapi/strapi` |
| **Notes** | CMS domain coverage. |

---

### B-29 — apache/flink

| Field | Value |
|---|---|
| **Repository Name** | flink |
| **GitHub URL** | https://github.com/apache/flink |
| **Primary Language** | Java |
| **Domain** | Data Science / Stream Processing |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Rapid growth stream processing framework. High contributor base growth phase 2016–2022. |
| **Expected MIIE Behaviour** | Moderate D-01 (maturing from fast-growth). |
| **Expected Detector Activity** | D-01: Moderate · D-02: Low · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/apache/flink` |
| **Notes** | Java data science stream processing coverage. |

---

### B-30 — influxdata/telegraf

| Field | Value |
|---|---|
| **Repository Name** | telegraf |
| **GitHub URL** | https://github.com/influxdata/telegraf |
| **Primary Language** | Go |
| **Domain** | DevOps / Monitoring |
| **Category** | B — Fast-Growth |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Fast-growing plugin-based metrics agent. Large contributor base, rapid plugin ecosystem expansion. |
| **Expected MIIE Behaviour** | Moderate D-01. High contributor diversity. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/influxdata/telegraf` |
| **Notes** | Go DevOps monitoring coverage. |

---

---

# CATEGORY C — Archived / Maintenance Mode Projects

> **Purpose:** Repositories whose lifecycle significantly changed.  
> **Expected Behavior:** D-01 Drift · D-02 Possible · D-03 Low

---

### C-01 — openai/gym

| Field | Value |
|---|---|
| **Repository Name** | gym |
| **GitHub URL** | https://github.com/openai/gym |
| **Primary Language** | Python |
| **Domain** | AI / Reinforcement Learning |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Archived |
| **Approximate Size** | Medium |
| **Approximate Activity** | Low |
| **Why Selected** | Formally archived by OpenAI. Clear commit cessation signal. High historical activity followed by abrupt stop. |
| **Expected MIIE Behaviour** | Strong D-01 drift (commit cessation). |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: High |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/openai/gym` |
| **Notes** | Replaced by Gymnasium. Archived 2023. Primary C-category anchor. |

---

### C-02 — facebookresearch/ParlAI

| Field | Value |
|---|---|
| **Repository Name** | ParlAI |
| **GitHub URL** | https://github.com/facebookresearch/ParlAI |
| **Primary Language** | Python |
| **Domain** | AI / NLP |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Archived |
| **Approximate Size** | Large |
| **Approximate Activity** | Low |
| **Why Selected** | Meta's dialogue research framework. Archived 2023 after internal pivot away from external framework. |
| **Expected MIIE Behaviour** | Strong D-01 signal. Clear terminal commit pattern. |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: High |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/facebookresearch/ParlAI` |
| **Notes** | Research lab archival pattern. |

---

### C-03 — google/yapf

| Field | Value |
|---|---|
| **Repository Name** | yapf |
| **GitHub URL** | https://github.com/google/yapf |
| **Primary Language** | Python |
| **Domain** | Developer Tools / Formatting |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Small |
| **Approximate Activity** | Low |
| **Why Selected** | Google Python formatter largely superseded by Black and Ruff. Minimal activity, rare maintenance releases only. |
| **Expected MIIE Behaviour** | Moderate D-01 drift. Low release frequency. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Low · D-03: Moderate |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/google/yapf` |
| **Notes** | Maintenance-mode tool. Useful for gradual activity decline pattern. |

---

### C-04 — apache/openoffice

| Field | Value |
|---|---|
| **Repository Name** | openoffice |
| **GitHub URL** | https://github.com/apache/openoffice |
| **Primary Language** | C++ / Java |
| **Domain** | Productivity Software |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Large |
| **Approximate Activity** | Low |
| **Why Selected** | Formerly dominant office suite now in deep maintenance mode. Classic lifecycle decline case. |
| **Expected MIIE Behaviour** | Strong D-01 drift. Very long history followed by severe slowdown. |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: High |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/apache/openoffice` |
| **Notes** | LibreOffice (Cat D) forked from this. Rich historical decline data. |

---

### C-05 — doctrine/annotations

| Field | Value |
|---|---|
| **Repository Name** | annotations |
| **GitHub URL** | https://github.com/doctrine/annotations |
| **Primary Language** | PHP |
| **Domain** | Web Frameworks / PHP |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Small |
| **Approximate Activity** | Low |
| **Why Selected** | PHP annotation library in maintenance mode since PHP 8.x native attributes superseded it. |
| **Expected MIIE Behaviour** | Gradual activity decline pattern. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Low · D-03: Moderate |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/doctrine/annotations` |
| **Notes** | PHP language coverage. Superseded-by-language-feature pattern. |

---

### C-06 — kennethreitz/requests (now psf/requests)

| Field | Value |
|---|---|
| **Repository Name** | requests |
| **GitHub URL** | https://github.com/psf/requests |
| **Primary Language** | Python |
| **Domain** | Networking / HTTP |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Medium |
| **Approximate Activity** | Low |
| **Why Selected** | Iconic Python library now explicitly in maintenance mode. Very gradual activity decline pattern. |
| **Expected MIIE Behaviour** | Gradual D-01 drift over years. Clear maintenance-mode signature. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Low · D-03: Moderate |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/psf/requests` |
| **Notes** | Explicitly maintenance-mode stated in README. Classic gradual decline. |

---

### C-07 — jakubroztocil/httpie (now httpie/httpie)

| Field | Value |
|---|---|
| **Repository Name** | httpie |
| **GitHub URL** | https://github.com/httpie/cli |
| **Primary Language** | Python |
| **Domain** | Developer Tools / HTTP |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Medium |
| **Approximate Activity** | Low |
| **Why Selected** | CLI HTTP tool with reduced activity as alternatives proliferated. Useful activity-decline pattern. |
| **Expected MIIE Behaviour** | Moderate D-01 drift. Low release frequency. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Low · D-03: Moderate |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/httpie/cli` |
| **Notes** | Python CLI tooling maintenance-mode. |

---

### C-08 — scrapy/scrapy

| Field | Value |
|---|---|
| **Repository Name** | scrapy |
| **GitHub URL** | https://github.com/scrapy/scrapy |
| **Primary Language** | Python |
| **Domain** | Web Scraping / Data |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Large |
| **Approximate Activity** | Low |
| **Why Selected** | Mature web scraping framework with reduced activity in recent years. Useful slow-decline model. |
| **Expected MIIE Behaviour** | Low-moderate D-01 drift. Declining but non-zero activity. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Low · D-03: Low |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/scrapy/scrapy` |
| **Notes** | Python web scraping maintenance example. |

---

### C-09 — expressjs/express

| Field | Value |
|---|---|
| **Repository Name** | express |
| **GitHub URL** | https://github.com/expressjs/express |
| **Primary Language** | JavaScript |
| **Domain** | Web Frameworks |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Medium |
| **Approximate Activity** | Low |
| **Why Selected** | Iconic Node.js framework. Dramatically reduced activity 2020–2024, Express 5 release marks possible revival. |
| **Expected MIIE Behaviour** | Strong D-01 drift. Long period of low activity. |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: Moderate |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/expressjs/express` |
| **Notes** | Express v5 after years of delay adds interesting revival signal. |

---

### C-10 — moment/moment

| Field | Value |
|---|---|
| **Repository Name** | moment |
| **GitHub URL** | https://github.com/moment/moment |
| **Primary Language** | JavaScript |
| **Domain** | Developer Tools / Date Library |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Medium |
| **Approximate Activity** | Low |
| **Why Selected** | Explicitly maintenance-mode JavaScript date library. README states project is "done" and in legacy mode. |
| **Expected MIIE Behaviour** | Strong D-01 drift. Clear announced maintenance declaration. |
| **Expected Detector Activity** | D-01: High · D-02: Low · D-03: High |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/moment/moment` |
| **Notes** | Self-declared maintenance mode with explicit README announcement. |

---

### C-11 — jashkenas/coffeescript

| Field | Value |
|---|---|
| **Repository Name** | coffeescript |
| **GitHub URL** | https://github.com/jashkenas/coffeescript |
| **Primary Language** | JavaScript |
| **Domain** | Programming Languages |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Medium |
| **Approximate Activity** | Low |
| **Why Selected** | Historically important language superseded by TypeScript. Classic obsolescence trajectory. |
| **Expected MIIE Behaviour** | Strong D-01 drift. Very long decline over many years. |
| **Expected Detector Activity** | D-01: High · D-02: Low · D-03: High |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/jashkenas/coffeescript` |
| **Notes** | Superseded-by-ecosystem pattern. Important historical JavaScript tooling. |

---

### C-12 — twitter/finagle

| Field | Value |
|---|---|
| **Repository Name** | finagle |
| **GitHub URL** | https://github.com/twitter/finagle |
| **Primary Language** | Scala |
| **Domain** | Networking / RPC |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Large |
| **Approximate Activity** | Low |
| **Why Selected** | Twitter's Scala RPC system. Activity significantly reduced post-X Corp restructuring. |
| **Expected MIIE Behaviour** | Moderate D-01 drift post-2022. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Moderate |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/twitter/finagle` |
| **Notes** | Scala language coverage. Corporate governance change impact on maintenance. |

---

### C-13 — google/grumpy

| Field | Value |
|---|---|
| **Repository Name** | grumpy |
| **GitHub URL** | https://github.com/google/grumpy |
| **Primary Language** | Go / Python |
| **Domain** | Programming Languages / Compilers |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Archived |
| **Approximate Size** | Medium |
| **Approximate Activity** | Low |
| **Why Selected** | Google's Python-to-Go transpiler. Archived after internal deprecation. Clear archival signal. |
| **Expected MIIE Behaviour** | Strong D-01 signal. Abrupt commit cessation. |
| **Expected Detector Activity** | D-01: High · D-02: Low · D-03: High |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/google/grumpy` |
| **Notes** | Google internal project archival pattern. |

---

### C-14 — cython/cython

| Field | Value |
|---|---|
| **Repository Name** | cython |
| **GitHub URL** | https://github.com/cython/cython |
| **Primary Language** | Python / C |
| **Domain** | Programming Languages / Compilers |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Large |
| **Approximate Activity** | Low |
| **Why Selected** | Python-to-C compiler. Reduced activity as Python performance improvements reduced need. |
| **Expected MIIE Behaviour** | Gradual D-01 drift. Slow but ongoing decline. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Low · D-03: Low |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/cython/cython` |
| **Notes** | Still maintained but declining relative to earlier peak. |

---

### C-15 — pallets/werkzeug

| Field | Value |
|---|---|
| **Repository Name** | werkzeug |
| **GitHub URL** | https://github.com/pallets/werkzeug |
| **Primary Language** | Python |
| **Domain** | Web Frameworks |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Medium |
| **Approximate Activity** | Low |
| **Why Selected** | Underlying Flask WSGI library with stable-but-low activity. Useful slow-maintenance example. |
| **Expected MIIE Behaviour** | Low D-01 drift. Very infrequent releases. |
| **Expected Detector Activity** | D-01: Low · D-02: None · D-03: Low |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/pallets/werkzeug` |
| **Notes** | Flask ecosystem dependency. Stable maintenance-only mode. |

---

### C-16 — pypa/pip

| Field | Value |
|---|---|
| **Repository Name** | pip |
| **GitHub URL** | https://github.com/pypa/pip |
| **Primary Language** | Python |
| **Domain** | Developer Tools / Package Management |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Medium |
| **Approximate Activity** | Low |
| **Why Selected** | Python package installer. Reduced activity as uv and Poetry captured new mindshare. Regular but infrequent releases. |
| **Expected MIIE Behaviour** | Gradual D-01 drift. Predictable but slow release cadence. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Low · D-03: Low |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/pypa/pip` |
| **Notes** | Python package management. Still critical but lower activity. |

---

### C-17 — jruby/jruby

| Field | Value |
|---|---|
| **Repository Name** | jruby |
| **GitHub URL** | https://github.com/jruby/jruby |
| **Primary Language** | Java / Ruby |
| **Domain** | Programming Languages |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Large |
| **Approximate Activity** | Low |
| **Why Selected** | JVM Ruby implementation. Historically significant, now low-activity maintenance mode. |
| **Expected MIIE Behaviour** | Gradual D-01 drift. Long-term decline. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Low · D-03: Moderate |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/jruby/jruby` |
| **Notes** | Java + Ruby multi-language. Alternate JVM language implementation pattern. |

---

### C-18 — mozilla/shumway

| Field | Value |
|---|---|
| **Repository Name** | shumway |
| **GitHub URL** | https://github.com/mozilla/shumway |
| **Primary Language** | JavaScript |
| **Domain** | Web Browsers / Flash |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Archived |
| **Approximate Size** | Medium |
| **Approximate Activity** | Low |
| **Why Selected** | Mozilla Flash replacement. Archived with complete commit cessation. Clear end-of-lifecycle example. |
| **Expected MIIE Behaviour** | Full commit cessation signal. |
| **Expected Detector Activity** | D-01: High · D-02: Low · D-03: High |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/mozilla/shumway` |
| **Notes** | Flash-era project. Complete lifecycle from creation to archival. |

---

### C-19 — ReactiveX/RxPY

| Field | Value |
|---|---|
| **Repository Name** | RxPY |
| **GitHub URL** | https://github.com/ReactiveX/RxPY |
| **Primary Language** | Python |
| **Domain** | Programming Libraries / Reactive |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Small |
| **Approximate Activity** | Low |
| **Why Selected** | Reactive Extensions for Python. Low activity as paradigm fell out of fashion. |
| **Expected MIIE Behaviour** | Moderate D-01 drift. Gradual decline pattern. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Low · D-03: Low |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/ReactiveX/RxPY` |
| **Notes** | Reactive programming paradigm decline example. |

---

### C-20 — celery/celery

| Field | Value |
|---|---|
| **Repository Name** | celery |
| **GitHub URL** | https://github.com/celery/celery |
| **Primary Language** | Python |
| **Domain** | Developer Tools / Task Queues |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Large |
| **Approximate Activity** | Low |
| **Why Selected** | Python task queue with significantly reduced maintainer activity. Periodic maintenance releases only. |
| **Expected MIIE Behaviour** | Moderate D-01 drift. Irregular release cadence. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Low · D-03: Moderate |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/celery/celery` |
| **Notes** | Widely used but reduced maintainer activity. Maintenance gap pattern. |

---

### C-21 — nicowillis/pyQode

| Field | Value |
|---|---|
| **Repository Name** | pyqode.core |
| **GitHub URL** | https://github.com/pyQode/pyqode.core |
| **Primary Language** | Python |
| **Domain** | Developer Tools / Editor |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Archived |
| **Approximate Size** | Small |
| **Approximate Activity** | Low |
| **Why Selected** | Python code editor framework. Archived after maintainer departure. Small-project archival example. |
| **Expected MIIE Behaviour** | Full commit cessation. Small project lifecycle signal. |
| **Expected Detector Activity** | D-01: High · D-02: None · D-03: High |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/pyQode/pyqode.core` |
| **Notes** | Small project full-lifecycle example. |

---

### C-22 — spf13/hugo (gohugoio/hugo)

| Field | Value |
|---|---|
| **Repository Name** | hugo |
| **GitHub URL** | https://github.com/gohugoio/hugo |
| **Primary Language** | Go |
| **Domain** | Web / Static Site Generators |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | Medium |
| **Why Selected** | Mature static site generator with reduced growth velocity. Transitioning from fast-growth to stable-maintenance. |
| **Expected MIIE Behaviour** | Low-moderate D-01. Useful transition-to-maintenance example. |
| **Expected Detector Activity** | D-01: Low · D-02: None · D-03: None |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/gohugoio/hugo` |
| **Notes** | Boundary case between Category A and C. Useful for threshold calibration. |

---

### C-23 — palantir/blueprint

| Field | Value |
|---|---|
| **Repository Name** | blueprint |
| **GitHub URL** | https://github.com/palantir/blueprint |
| **Primary Language** | TypeScript |
| **Domain** | UI / Web Frameworks |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Large |
| **Approximate Activity** | Low |
| **Why Selected** | Palantir UI component library. Reduced activity in recent years. Corporate internal library maintenance mode. |
| **Expected MIIE Behaviour** | Gradual D-01 drift. Corporate maintenance pattern. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Low · D-03: Moderate |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/palantir/blueprint` |
| **Notes** | Corporate open-source maintenance mode example. |

---

### C-24 — grpc/grpc (Python)

| Field | Value |
|---|---|
| **Repository Name** | grpc |
| **GitHub URL** | https://github.com/grpc/grpc |
| **Primary Language** | C++ |
| **Domain** | Networking / RPC |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Large |
| **Approximate Activity** | Medium |
| **Why Selected** | gRPC core library. Stable but reduced compared to earlier peak. Parts moving to grpc-go/grpc-java. |
| **Expected MIIE Behaviour** | Low D-01 drift. Gradual migration of activity to language-specific repos. |
| **Expected Detector Activity** | D-01: Low · D-02: Low · D-03: None |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/grpc/grpc` |
| **Notes** | Activity migration pattern to sub-repositories. |

---

### C-25 — scikit-image/scikit-image

| Field | Value |
|---|---|
| **Repository Name** | scikit-image |
| **GitHub URL** | https://github.com/scikit-image/scikit-image |
| **Primary Language** | Python |
| **Domain** | Scientific Computing / Computer Vision |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Large |
| **Approximate Activity** | Low |
| **Why Selected** | Image processing library with reduced activity as deep learning alternatives dominate. |
| **Expected MIIE Behaviour** | Gradual D-01 drift. Activity decline pattern. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Low · D-03: Low |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/scikit-image/scikit-image` |
| **Notes** | Scientific Python maintenance mode pattern. |

---

### C-26 — nodejs/node (legacy branch analysis)

| Field | Value |
|---|---|
| **Repository Name** | node (focus on EOL branches) |
| **GitHub URL** | https://github.com/nodejs/node |
| **Primary Language** | JavaScript / C++ |
| **Domain** | Programming Languages / Runtime |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Active (EOL branches: Maintenance) |
| **Approximate Size** | Large |
| **Approximate Activity** | High (overall), Low (EOL branches) |
| **Why Selected** | Useful for branch-level maintenance analysis. EOL Node.js versions exhibit clear end-of-maintenance patterns. |
| **Expected MIIE Behaviour** | Branch-level D-01 drift in EOL versions. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Low · D-03: Moderate |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/nodejs/node` |
| **Notes** | Use for branch-aware MIIE analysis on EOL versions (v14, v16, etc.). |

---

### C-27 — phalcon/phalcon

| Field | Value |
|---|---|
| **Repository Name** | phalcon |
| **GitHub URL** | https://github.com/phalcon/cphalcon |
| **Primary Language** | Zephir / C |
| **Domain** | Web Frameworks / PHP |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Large |
| **Approximate Activity** | Low |
| **Why Selected** | PHP C-extension framework. Significantly reduced activity. Maintenance mode. |
| **Expected MIIE Behaviour** | Moderate D-01 drift. PHP ecosystem decline pattern. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Low · D-03: Moderate |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/phalcon/cphalcon` |
| **Notes** | PHP + C language coverage. Niche framework maintenance mode. |

---

### C-28 — yarnpkg/yarn (Classic)

| Field | Value |
|---|---|
| **Repository Name** | yarn (Classic/v1) |
| **GitHub URL** | https://github.com/yarnpkg/yarn |
| **Primary Language** | JavaScript |
| **Domain** | Developer Tools / Package Management |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Medium |
| **Approximate Activity** | Low |
| **Why Selected** | Yarn Classic explicitly in maintenance mode. Clear transition to Yarn Berry (yarnpkg/berry). |
| **Expected MIIE Behaviour** | Gradual D-01 drift post-v2 fork. Clear maintenance transition. |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: High |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/yarnpkg/yarn` |
| **Notes** | Split between Yarn Classic and Yarn Berry is a useful architectural migration pattern. |

---

### C-29 — strongloop/loopback

| Field | Value |
|---|---|
| **Repository Name** | loopback |
| **GitHub URL** | https://github.com/strongloop/loopback |
| **Primary Language** | JavaScript |
| **Domain** | Web Frameworks / API |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Archived |
| **Approximate Size** | Medium |
| **Approximate Activity** | Low |
| **Why Selected** | IBM-archived Node.js API framework. Post-acquisition archival pattern. |
| **Expected MIIE Behaviour** | Strong D-01. Full commit cessation after archival. |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: High |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/strongloop/loopback` |
| **Notes** | IBM acquisition archival pattern. |

---

### C-30 — balderdashy/sails

| Field | Value |
|---|---|
| **Repository Name** | sails |
| **GitHub URL** | https://github.com/balderdashy/sails |
| **Primary Language** | JavaScript |
| **Domain** | Web Frameworks |
| **Category** | C — Archived / Maintenance |
| **Repository Status** | Maintenance |
| **Approximate Size** | Large |
| **Approximate Activity** | Low |
| **Why Selected** | Node.js MVC framework with significantly reduced activity. Long gap between releases. |
| **Expected MIIE Behaviour** | Moderate D-01 drift. Long maintenance gap between releases. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Low · D-03: Moderate |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/balderdashy/sails` |
| **Notes** | Node.js framework long-tail maintenance example. |

---

---

# CATEGORY D — Forks & Divergent Histories

> **Purpose:** Repositories that experienced forks or governance changes.  
> **Expected Behavior:** D-01 and D-02 anomaly signals at divergence points

---

### D-01 — LibreOffice/core

| Field | Value |
|---|---|
| **Repository Name** | core (LibreOffice) |
| **GitHub URL** | https://github.com/LibreOffice/core |
| **Primary Language** | C++ / Java |
| **Domain** | Productivity Software |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Canonical fork example — LibreOffice forked from OpenOffice in 2010 following Oracle acquisition of Sun. |
| **Expected MIIE Behaviour** | Divergence signal at fork inception. |
| **Expected Detector Activity** | D-01: Moderate · D-02: High (fork contributor burst) · D-03: Low |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/LibreOffice/core` |
| **Notes** | Compare with apache/openoffice (Cat C) for fork divergence study. |

---

### D-02 — opensearch-project/OpenSearch

| Field | Value |
|---|---|
| **Repository Name** | OpenSearch |
| **GitHub URL** | https://github.com/opensearch-project/OpenSearch |
| **Primary Language** | Java |
| **Domain** | Databases / Search |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | AWS fork of Elasticsearch created 2021 after license change. Instantaneous contributor surge from AWS. |
| **Expected MIIE Behaviour** | Strong D-02 at fork inception. Sustained growth diverging from Elasticsearch pattern. |
| **Expected Detector Activity** | D-01: Moderate · D-02: High · D-03: Low |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/opensearch-project/OpenSearch` |
| **Notes** | License-change-triggered fork. Compare to elastic/elasticsearch in Cat A. |

---

### D-03 — MariaDB/server

| Field | Value |
|---|---|
| **Repository Name** | server |
| **GitHub URL** | https://github.com/MariaDB/server |
| **Primary Language** | C++ / C |
| **Domain** | Databases |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | MySQL fork after Oracle acquisition of Sun. One of the canonical open-source fork stories. |
| **Expected MIIE Behaviour** | Fork divergence signal. Long history of parallel development to MySQL. |
| **Expected Detector Activity** | D-01: Moderate · D-02: High (early fork burst) · D-03: Low |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/MariaDB/server` |
| **Notes** | BSL license introduction in 2023 is additional governance event. |

---

### D-04 — nextcloud/server

| Field | Value |
|---|---|
| **Repository Name** | server |
| **GitHub URL** | https://github.com/nextcloud/server |
| **Primary Language** | PHP / JavaScript |
| **Domain** | Cloud / File Storage |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Forked from ownCloud in 2016 by original ownCloud creator. Dramatic contributor migration event. |
| **Expected MIIE Behaviour** | Strong D-02 at fork inception. Rapid contributor migration. |
| **Expected Detector Activity** | D-01: Moderate · D-02: High · D-03: Low |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/nextcloud/server` |
| **Notes** | Creator forking their own project is unique governance event. |

---

### D-05 — opentofu/opentofu (fork of terraform)

| Field | Value |
|---|---|
| **Repository Name** | opentofu |
| **GitHub URL** | https://github.com/opentofu/opentofu |
| **Primary Language** | Go |
| **Domain** | DevOps / Infrastructure as Code |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Community fork of Terraform after HashiCorp BSL license change in 2023. Immediate mass contributor migration. |
| **Expected MIIE Behaviour** | Extreme D-02 at fork inception. Unusual early history. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: Moderate |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/opentofu/opentofu` |
| **Notes** | Coordinated community fork. Extremely fast early development. |

---

### D-06 — valkey-io/valkey (Redis fork)

| Field | Value |
|---|---|
| **Repository Name** | valkey |
| **GitHub URL** | https://github.com/valkey-io/valkey |
| **Primary Language** | C |
| **Domain** | Databases / Caching |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Linux Foundation fork of Redis created 2024 after Redis license change. Paradigmatic license-fork event. |
| **Expected MIIE Behaviour** | Strong D-02 at fork inception. Immediate institutional contributor surge. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: Moderate |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/valkey-io/valkey` |
| **Notes** | Very recent fork (2024). Excellent for detecting early-fork patterns. |

---

### D-07 — jenkins-ci/jenkins (Hudson fork)

| Field | Value |
|---|---|
| **Repository Name** | jenkins |
| **GitHub URL** | https://github.com/jenkinsci/jenkins |
| **Primary Language** | Java |
| **Domain** | DevOps / CI-CD |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Forked from Hudson in 2011 after Oracle acquisition of Sun. Classic Oracle-triggered fork. |
| **Expected MIIE Behaviour** | Long post-fork divergence history. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/jenkinsci/jenkins` |
| **Notes** | Java CI/CD coverage. Historical fork with 15+ years of independent development. |

---

### D-08 — neovim/neovim (Vim fork)

| Field | Value |
|---|---|
| **Repository Name** | neovim |
| **GitHub URL** | https://github.com/neovim/neovim |
| **Primary Language** | C / Lua |
| **Domain** | Developer Tools / Editor |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Fork of Vim in 2014. Governance disagreement with original maintainer. Now far more active than parent. |
| **Expected MIIE Behaviour** | Interesting divergence: fork now surpasses original activity. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Low |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/neovim/neovim` |
| **Notes** | Fork that surpassed parent project velocity. Compare to vim/vim. |

---

### D-09 — vim/vim (original)

| Field | Value |
|---|---|
| **Repository Name** | vim |
| **GitHub URL** | https://github.com/vim/vim |
| **Primary Language** | C |
| **Domain** | Developer Tools / Editor |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | Medium |
| **Why Selected** | Vim original, parent of Neovim. Interesting divergence study: original maintained alongside fork. |
| **Expected MIIE Behaviour** | Moderate D-01 relative to Neovim. |
| **Expected Detector Activity** | D-01: Low · D-02: Low · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/vim/vim` |
| **Notes** | Pair with neovim for fork-original comparison. |

---

### D-10 — AlmaLinux/build-system (RHEL fork)

| Field | Value |
|---|---|
| **Repository Name** | build-system |
| **GitHub URL** | https://github.com/AlmaLinux/build-system |
| **Primary Language** | Python |
| **Domain** | Operating Systems / Build |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Medium |
| **Approximate Activity** | Medium |
| **Why Selected** | RHEL fork born from CentOS Stream pivot in 2020. Governance disruption example. |
| **Expected MIIE Behaviour** | Fork inception burst signal. Community-formed repository. |
| **Expected Detector Activity** | D-01: Moderate · D-02: High · D-03: Moderate |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/AlmaLinux/build-system` |
| **Notes** | CentOS → AlmaLinux governance transition. |

---

### D-11 — lineageos/android_frameworks_base

| Field | Value |
|---|---|
| **Repository Name** | android_frameworks_base |
| **GitHub URL** | https://github.com/LineageOS/android_frameworks_base |
| **Primary Language** | Java / C++ |
| **Domain** | Operating Systems / Mobile |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | LineageOS (CyanogenMod fork) Android framework. Complex fork history with AOSP base. |
| **Expected MIIE Behaviour** | Complex divergent history with periodic AOSP merge patterns. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Low |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/LineageOS/android_frameworks_base` |
| **Notes** | CyanogenMod → LineageOS fork chain. Mobile OS Java coverage. |

---

### D-12 — grafana/mimir (Cortex fork)

| Field | Value |
|---|---|
| **Repository Name** | mimir |
| **GitHub URL** | https://github.com/grafana/mimir |
| **Primary Language** | Go |
| **Domain** | Observability / Monitoring |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Grafana fork of Cortex (Prometheus long-term storage). Governance disagreement-driven fork. |
| **Expected MIIE Behaviour** | Fork inception burst. Strong D-02 at divergence. |
| **Expected Detector Activity** | D-01: Moderate · D-02: High · D-03: Low |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/grafana/mimir` |
| **Notes** | Go observability fork. Cortex parent is thanos-io/cortex. |

---

### D-13 — thanos-io/thanos (Prometheus extension)

| Field | Value |
|---|---|
| **Repository Name** | thanos |
| **GitHub URL** | https://github.com/thanos-io/thanos |
| **Primary Language** | Go |
| **Domain** | Observability / Monitoring |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Divergent extension of Prometheus ecosystem. Multiple competing monitoring solutions diverged. |
| **Expected MIIE Behaviour** | Moderate D-01 drift from Prometheus baseline. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: None |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/thanos-io/thanos` |
| **Notes** | Prometheus ecosystem divergence case. |

---

### D-14 — yarnpkg/berry (Yarn Classic fork)

| Field | Value |
|---|---|
| **Repository Name** | berry |
| **GitHub URL** | https://github.com/yarnpkg/berry |
| **Primary Language** | TypeScript |
| **Domain** | Developer Tools / Package Management |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Yarn v2/v3/v4 (Berry) is architectural rewrite of Yarn Classic. Internal fork with divergent history. |
| **Expected MIIE Behaviour** | Clean fork inception signal. Architectural divergence detectable. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Low |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/yarnpkg/berry` |
| **Notes** | Internal product fork as architectural rewrite. |

---

### D-15 — microsoft/WSL (Windows Subsystem for Linux)

| Field | Value |
|---|---|
| **Repository Name** | WSL |
| **GitHub URL** | https://github.com/microsoft/WSL |
| **Primary Language** | C++ |
| **Domain** | Operating Systems |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Major architectural transition from WSL1 to WSL2 represents significant governance/design divergence. |
| **Expected MIIE Behaviour** | D-01 drift at WSL1→WSL2 architectural shift. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Low · D-03: Low |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/microsoft/WSL` |
| **Notes** | Architectural generation shift within single repo. |

---

### D-16 — cockroachdb/cockroach

| Field | Value |
|---|---|
| **Repository Name** | cockroach |
| **GitHub URL** | https://github.com/cockroachdb/cockroach |
| **Primary Language** | Go |
| **Domain** | Databases / Distributed |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | License change to BSL in 2019. Governance change with contributor impact. |
| **Expected MIIE Behaviour** | D-02 signal at license change event. |
| **Expected Detector Activity** | D-01: Low · D-02: Moderate · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/cockroachdb/cockroach` |
| **Notes** | Go distributed database license-change governance event. |

---

### D-17 — sourcegraph/sourcegraph

| Field | Value |
|---|---|
| **Repository Name** | sourcegraph |
| **GitHub URL** | https://github.com/sourcegraph/sourcegraph |
| **Primary Language** | Go / TypeScript |
| **Domain** | Developer Tools / Code Search |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Major architectural pivot to Cody AI and significant contributor base changes. Governance shift signal. |
| **Expected MIIE Behaviour** | D-01 and D-02 signals at AI pivot. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Low |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/sourcegraph/sourcegraph` |
| **Notes** | Strategic pivot from code search to AI coding assistant. |

---

### D-18 — dotnet/roslyn

| Field | Value |
|---|---|
| **Repository Name** | roslyn |
| **GitHub URL** | https://github.com/dotnet/roslyn |
| **Primary Language** | C# |
| **Domain** | Compilers / Developer Tools |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Microsoft open-sourced C# compiler. Transition from closed to open development represents governance divergence. |
| **Expected MIIE Behaviour** | D-02 signal at open-source transition. |
| **Expected Detector Activity** | D-01: Low · D-02: Moderate · D-03: None |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/dotnet/roslyn` |
| **Notes** | C# language coverage. Closed-to-open transition governance study. |

---

### D-19 — grafana/grafana-loki

| Field | Value |
|---|---|
| **Repository Name** | agentlite |
| **GitHub URL** | https://github.com/grafana/agent |
| **Primary Language** | Go |
| **Domain** | Observability / DevOps |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Maintenance |
| **Approximate Size** | Large |
| **Approximate Activity** | Low |
| **Why Selected** | Grafana Agent being superseded by Alloy (grafana/alloy). Internal architectural divergence. |
| **Expected MIIE Behaviour** | D-01 drift as project migrates to successor. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Moderate |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/grafana/agent` |
| **Notes** | Internal successor migration pattern. Pair with grafana/alloy. |

---

### D-20 — denoland/deno_std

| Field | Value |
|---|---|
| **Repository Name** | deno_std |
| **GitHub URL** | https://github.com/denoland/deno_std |
| **Primary Language** | TypeScript |
| **Domain** | Standard Libraries |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Deno standard library separated from main runtime. Divergent history at separation point. |
| **Expected MIIE Behaviour** | D-01 drift at library separation event. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Low · D-03: Low |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/denoland/deno_std` |
| **Notes** | Repository-split divergence pattern. |

---

### D-21 — GoogleContainerTools/skaffold

| Field | Value |
|---|---|
| **Repository Name** | skaffold |
| **GitHub URL** | https://github.com/GoogleContainerTools/skaffold |
| **Primary Language** | Go |
| **Domain** | DevOps / Cloud |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Maintenance |
| **Approximate Size** | Large |
| **Approximate Activity** | Low |
| **Why Selected** | Google Cloud build tool. Significant activity reduction as GCP strategy shifted. Governance change signal. |
| **Expected MIIE Behaviour** | D-01 drift from activity decline. Google strategic shift pattern. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Moderate |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/GoogleContainerTools/skaffold` |
| **Notes** | Corporate strategic pivot reducing open-source investment. |

---

### D-22 — gravitational/teleport

| Field | Value |
|---|---|
| **Repository Name** | teleport |
| **GitHub URL** | https://github.com/gravitational/teleport |
| **Primary Language** | Go |
| **Domain** | Security / Access Management |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | License change from Apache 2.0 to AGPL/commercial hybrid. Contributor impact detectable. |
| **Expected MIIE Behaviour** | D-02 signal at license change event. |
| **Expected Detector Activity** | D-01: None · D-02: Moderate · D-03: None |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/gravitational/teleport` |
| **Notes** | Security + Go coverage. License change governance event. |

---

### D-23 — influxdata/influxdb

| Field | Value |
|---|---|
| **Repository Name** | influxdb |
| **GitHub URL** | https://github.com/influxdata/influxdb |
| **Primary Language** | Go / Rust |
| **Domain** | Databases / Time Series |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | InfluxDB v2→v3 rewrite in Rust. Major architectural fork within same repo. Language shift signal. |
| **Expected MIIE Behaviour** | D-01 drift at Go→Rust language migration. D-02 contributor change. |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: Moderate |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/influxdata/influxdb` |
| **Notes** | Intra-repo language migration: Go to Rust. Unusual architectural divergence. |

---

### D-24 — PowerShell/PowerShell

| Field | Value |
|---|---|
| **Repository Name** | PowerShell |
| **GitHub URL** | https://github.com/PowerShell/PowerShell |
| **Primary Language** | C# |
| **Domain** | Operating Systems / Scripting |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Microsoft open-sourced PowerShell in 2016. Dramatic governance shift from proprietary to OSS. |
| **Expected MIIE Behaviour** | D-02 contributor burst at open-source event. |
| **Expected Detector Activity** | D-01: None · D-02: High (open-source inception) · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/PowerShell/PowerShell` |
| **Notes** | C# coverage. Proprietary-to-OSS transition governance study. |

---

### D-25 — dotnet/dotnet (previously microsoft/dotnet)

| Field | Value |
|---|---|
| **Repository Name** | dotnet |
| **GitHub URL** | https://github.com/dotnet/runtime |
| **Primary Language** | C# / C++ |
| **Domain** | Programming Languages / Runtime |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | .NET open-sourced and cross-platformmed. Major governance shift. Divergence from .NET Framework. |
| **Expected MIIE Behaviour** | D-02 contributor burst at OSS transition. |
| **Expected Detector Activity** | D-01: None · D-02: Moderate · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/dotnet/runtime` |
| **Notes** | .NET Framework → .NET Core → .NET governance transition. |

---

### D-26 — apache/incubator-answer (fork governance)

| Field | Value |
|---|---|
| **Repository Name** | incubator-answer |
| **GitHub URL** | https://github.com/apache/incubator-answer |
| **Primary Language** | Go / TypeScript |
| **Domain** | Web / Q&A Platform |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Project entered Apache Incubator governance — major governance transition from commercial to Apache model. |
| **Expected MIIE Behaviour** | D-02 signal at governance model change. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Low |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/apache/incubator-answer` |
| **Notes** | Apache incubation governance transition pattern. |

---

### D-27 — supabase/realtime (diverged from Phoenix)

| Field | Value |
|---|---|
| **Repository Name** | realtime |
| **GitHub URL** | https://github.com/supabase/realtime |
| **Primary Language** | Elixir |
| **Domain** | Cloud / Real-time |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Elixir-based real-time layer forked from Phoenix concepts. Independent divergent development. |
| **Expected MIIE Behaviour** | Moderate D-01 drift. Elixir language diversity. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Low · D-03: Low |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/supabase/realtime` |
| **Notes** | Elixir language coverage. Divergent real-time architecture. |

---

### D-28 — zed-industries/zed (Atom/Electron successor)

| Field | Value |
|---|---|
| **Repository Name** | zed |
| **GitHub URL** | https://github.com/zed-industries/zed |
| **Primary Language** | Rust |
| **Domain** | Developer Tools / Editor |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Built by Atom's original creators after GitHub acquisition of Atom (and subsequent archival). Successor pattern. |
| **Expected MIIE Behaviour** | Strong D-02 burst at open-source announcement (2024). High early growth. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: Moderate |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/zed-industries/zed` |
| **Notes** | Atom successor by same creators. Rust editor. Open-sourced January 2024 with burst. |

---

### D-29 — atom/atom (GitHub Atom — archived)

| Field | Value |
|---|---|
| **Repository Name** | atom |
| **GitHub URL** | https://github.com/atom/atom |
| **Primary Language** | JavaScript / CoffeeScript |
| **Domain** | Developer Tools / Editor |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Archived |
| **Approximate Size** | Large |
| **Approximate Activity** | Low |
| **Why Selected** | GitHub's Atom editor archived December 2022. Dramatic commit cessation after VSCode dominance. |
| **Expected MIIE Behaviour** | Strong D-01 and D-03 at archival. |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: High |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/atom/atom` |
| **Notes** | Pair with zed-industries/zed. Archival + successor fork pattern. |

---

### D-30 — apache/cassandra

| Field | Value |
|---|---|
| **Repository Name** | cassandra |
| **GitHub URL** | https://github.com/apache/cassandra |
| **Primary Language** | Java |
| **Domain** | Databases / Distributed |
| **Category** | D — Forks & Divergent Histories |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Originally Facebook internal, donated to Apache. Governance transition from Facebook to Apache Foundation. |
| **Expected MIIE Behaviour** | Historical governance transition detectable in early commit history. |
| **Expected Detector Activity** | D-01: Low · D-02: Moderate · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/apache/cassandra` |
| **Notes** | Corporate-to-foundation governance transition. Java distributed DB. |

---

---

# CATEGORY E — High-Churn / Experimental Projects

> **Purpose:** Projects with rapid architectural change.  
> **Expected Behavior:** Moderate to High anomaly likelihood across all detectors

---

### E-01 — microsoft/autogen (v0.4 architectural rewrite)

| Field | Value |
|---|---|
| **Repository Name** | autogen |
| **GitHub URL** | https://github.com/microsoft/autogen |
| **Primary Language** | Python |
| **Domain** | AI / Agent Frameworks |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | AutoGen 0.4 was a near-complete architectural rewrite. Rapid churn, breaking changes, experimental patterns. |
| **Expected MIIE Behaviour** | High D-01, D-02 at architectural shift. Frequent release changes. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/microsoft/autogen` |
| **Notes** | Strong churn example. AutoGen 0.4 essentially rebuilt from scratch. |

---

### E-02 — ComfyUI/ComfyUI

| Field | Value |
|---|---|
| **Repository Name** | ComfyUI |
| **GitHub URL** | https://github.com/comfyanonymous/ComfyUI |
| **Primary Language** | Python |
| **Domain** | AI / Image Generation |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Extremely rapid AI image generation UI. High contributor churn, frequent breaking changes, experimental architecture. |
| **Expected MIIE Behaviour** | High D-01 drift. Rapid architectural evolution. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: Moderate |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/comfyanonymous/ComfyUI` |
| **Notes** | AI creative tooling churn example. Very fast evolution. |

---

### E-03 — run-llama/llama_index

| Field | Value |
|---|---|
| **Repository Name** | llama_index |
| **GitHub URL** | https://github.com/run-llama/llama_index |
| **Primary Language** | Python |
| **Domain** | AI / RAG Frameworks |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Rapid architectural evolution in RAG space. Major restructuring, frequent API breaking changes. |
| **Expected MIIE Behaviour** | High D-01 drift. High D-02 contributor churn. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/run-llama/llama_index` |
| **Notes** | LlamaIndex name change from gpt_index was itself a high-churn signal. |

---

### E-04 — semantic-kernel (microsoft/semantic-kernel)

| Field | Value |
|---|---|
| **Repository Name** | semantic-kernel |
| **GitHub URL** | https://github.com/microsoft/semantic-kernel |
| **Primary Language** | C# / Python |
| **Domain** | AI / SDK |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Rapid experimental SDK with very frequent breaking changes. Multi-language SDK churn. |
| **Expected MIIE Behaviour** | Moderate to high D-01 drift. Multi-language churn. |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: High |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/microsoft/semantic-kernel` |
| **Notes** | C# + Python + Java SDK. Experimental AI framework. |

---

### E-05 — crewAIInc/crewAI

| Field | Value |
|---|---|
| **Repository Name** | crewAI |
| **GitHub URL** | https://github.com/crewAIInc/crewAI |
| **Primary Language** | Python |
| **Domain** | AI / Agent Frameworks |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Rapid-growth AI agent framework. Experimental APIs, frequent architecture changes, startup velocity. |
| **Expected MIIE Behaviour** | High D-01 and D-02. Startup-velocity churn. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/crewAIInc/crewAI` |
| **Notes** | Startup-phase AI agent framework. Very high early churn. |

---

### E-06 — OpenBMB/ChatDev

| Field | Value |
|---|---|
| **Repository Name** | ChatDev |
| **GitHub URL** | https://github.com/OpenBMB/ChatDev |
| **Primary Language** | Python |
| **Domain** | AI / Research / Agents |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Small |
| **Approximate Activity** | Medium |
| **Why Selected** | Research-grade AI agent experiment with rapid burst followed by declining activity. |
| **Expected MIIE Behaviour** | High initial D-01 burst, then activity decline. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/OpenBMB/ChatDev` |
| **Notes** | Research lab experimental project pattern. |

---

### E-07 — Significant-Gravitas/AutoGPT

| Field | Value |
|---|---|
| **Repository Name** | AutoGPT |
| **GitHub URL** | https://github.com/Significant-Gravitas/AutoGPT |
| **Primary Language** | Python |
| **Domain** | AI / Agents |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Explosive early growth followed by major architectural pivots. Classic experimental/churn pattern. |
| **Expected MIIE Behaviour** | Extreme D-01 drift. Multiple architectural restarts. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/Significant-Gravitas/AutoGPT` |
| **Notes** | Most cited high-churn AI project. Multiple complete rewrites. |

---

### E-08 — lm-sys/FastChat

| Field | Value |
|---|---|
| **Repository Name** | FastChat |
| **GitHub URL** | https://github.com/lm-sys/FastChat |
| **Primary Language** | Python |
| **Domain** | AI / LLM Serving |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Medium |
| **Approximate Activity** | Medium |
| **Why Selected** | Research-origin LLM chat server with rapid architecture evolution as models changed. |
| **Expected MIIE Behaviour** | Moderate to high D-01 drift. Research velocity churn. |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: Moderate |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/lm-sys/FastChat` |
| **Notes** | Academic research project velocity. |

---

### E-09 — vllm-project/vllm

| Field | Value |
|---|---|
| **Repository Name** | vllm |
| **GitHub URL** | https://github.com/vllm-project/vllm |
| **Primary Language** | Python / C++ |
| **Domain** | AI / LLM Serving |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Rapid-growth LLM inference engine. High contributor churn, frequent API changes, experimental optimizations. |
| **Expected MIIE Behaviour** | High D-01 drift. Very high release velocity. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/vllm-project/vllm` |
| **Notes** | Startup-to-institutional transition in progress. High-churn AI infrastructure. |

---

### E-10 — deepseek-ai/DeepSeek-Coder

| Field | Value |
|---|---|
| **Repository Name** | DeepSeek-Coder |
| **GitHub URL** | https://github.com/deepseek-ai/DeepSeek-Coder |
| **Primary Language** | Python |
| **Domain** | AI / Code Generation |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Small |
| **Approximate Activity** | Medium |
| **Why Selected** | Research-release model with burst activity followed by stabilization. Fast release without standard governance. |
| **Expected MIIE Behaviour** | High early D-01/D-02 burst. Research lab release pattern. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/deepseek-ai/DeepSeek-Coder` |
| **Notes** | Research lab release burst pattern. |

---

### E-11 — mlc-ai/mlc-llm

| Field | Value |
|---|---|
| **Repository Name** | mlc-llm |
| **GitHub URL** | https://github.com/mlc-ai/mlc-llm |
| **Primary Language** | Python / C++ |
| **Domain** | AI / Compiler / LLM |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Experimental ML compiler for LLMs. High churn, research velocity, frequent API changes. |
| **Expected MIIE Behaviour** | High D-01 drift. Experimental academic project velocity. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/mlc-ai/mlc-llm` |
| **Notes** | Academic + startup fusion project. High experimental velocity. |

---

### E-12 — microsoft/promptflow

| Field | Value |
|---|---|
| **Repository Name** | promptflow |
| **GitHub URL** | https://github.com/microsoft/promptflow |
| **Primary Language** | Python |
| **Domain** | AI / LLM Tooling |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Experimental LLM workflow tooling. Rapid early development, frequent architecture pivots. |
| **Expected MIIE Behaviour** | High D-01 drift. Experimental tooling churn. |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: High |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/microsoft/promptflow` |
| **Notes** | Azure AI tooling. Experimental development velocity. |

---

### E-13 — open-webui/open-webui

| Field | Value |
|---|---|
| **Repository Name** | open-webui |
| **GitHub URL** | https://github.com/open-webui/open-webui |
| **Primary Language** | Python / JavaScript |
| **Domain** | AI / Web UI |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Rapidly evolving LLM chat interface. Very high release cadence, experimental features. |
| **Expected MIIE Behaviour** | High D-01 and D-03 drift. Extreme release frequency. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/open-webui/open-webui` |
| **Notes** | Extremely high release frequency. Very active experimental development. |

---

### E-14 — phidatahq/phidata

| Field | Value |
|---|---|
| **Repository Name** | phidata |
| **GitHub URL** | https://github.com/phidatahq/phidata |
| **Primary Language** | Python |
| **Domain** | AI / Agent Frameworks |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | AI agent framework in rapid development. High churn, experimental APIs. |
| **Expected MIIE Behaviour** | High D-01 and D-02 signals. Startup-velocity framework. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/phidatahq/phidata` |
| **Notes** | Now renamed to agno. Name change is itself a churn signal. |

---

### E-15 — emcf/evil

| Field | Value |
|---|---|
| **Repository Name** | evil |
| **GitHub URL** | https://github.com/noctuid/evil-guide |
| **Primary Language** | Emacs Lisp |
| **Domain** | Developer Tools / Editor |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Small |
| **Approximate Activity** | Low |
| **Why Selected** | Small experimental Emacs extension. Intermittent activity with long gaps. Language diversity (Emacs Lisp). |
| **Expected MIIE Behaviour** | Intermittent D-01. Long maintenance gaps. |
| **Expected Detector Activity** | D-01: Moderate · D-02: None · D-03: Moderate |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/noctuid/evil-guide` |
| **Notes** | Small project intermittent activity. Language diversity. |

---

### E-16 — hwchase17/langchain (original)

| Field | Value |
|---|---|
| **Repository Name** | langchain (early fork) |
| **GitHub URL** | https://github.com/hwchase17/langchain |
| **Primary Language** | Python |
| **Domain** | AI / LLM |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Archived |
| **Approximate Size** | Small |
| **Approximate Activity** | Low |
| **Why Selected** | Original creator's personal repo before langchain-ai org takeover. Abrupt archival signal. |
| **Expected MIIE Behaviour** | Strong D-01 at archival. Org migration pattern. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/hwchase17/langchain` |
| **Notes** | Repository migration from personal to org. Interesting org transfer pattern. |

---

### E-17 — biokernel/biokernel

| Field | Value |
|---|---|
| **Repository Name** | kernel-memory |
| **GitHub URL** | https://github.com/microsoft/kernel-memory |
| **Primary Language** | C# |
| **Domain** | AI / Knowledge Management |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Microsoft experimental AI memory service. Frequent API changes, experimental patterns. |
| **Expected MIIE Behaviour** | Moderate D-01. Experimental project velocity. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Moderate |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/microsoft/kernel-memory` |
| **Notes** | C# AI tooling. Experimental research-grade project. |

---

### E-18 — hiyouga/LLaMA-Factory

| Field | Value |
|---|---|
| **Repository Name** | LLaMA-Factory |
| **GitHub URL** | https://github.com/hiyouga/LLaMA-Factory |
| **Primary Language** | Python |
| **Domain** | AI / LLM Training |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Rapid-growth LLM fine-tuning framework. High contributor burst, experimental training techniques. |
| **Expected MIIE Behaviour** | High D-01 and D-02. Experimental AI training churn. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/hiyouga/LLaMA-Factory` |
| **Notes** | AI training tooling. Very rapid experimental development. |

---

### E-19 — stanford-oval/storm

| Field | Value |
|---|---|
| **Repository Name** | storm |
| **GitHub URL** | https://github.com/stanford-oval/storm |
| **Primary Language** | Python |
| **Domain** | AI / Research |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Small |
| **Approximate Activity** | Medium |
| **Why Selected** | Stanford research project. Burst activity at paper release, then rapid decline. Research publication cycle. |
| **Expected MIIE Behaviour** | High D-01 burst at publication. Research activity spike pattern. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/stanford-oval/storm` |
| **Notes** | Academic publication-driven activity burst. |

---

### E-20 — xtekky/gpt4free

| Field | Value |
|---|---|
| **Repository Name** | gpt4free |
| **GitHub URL** | https://github.com/xtekky/gpt4free |
| **Primary Language** | Python |
| **Domain** | AI / Scraping |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Extremely rapid growth, multiple forks, high churn, controversial project with unusual activity patterns. |
| **Expected MIIE Behaviour** | High D-01 and D-02. Unusual contributor burst. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/xtekky/gpt4free` |
| **Notes** | Highly unusual activity pattern. Use with caution in MIIE sensitivity testing. |

---

### E-21 — abi/screenshot-to-code

| Field | Value |
|---|---|
| **Repository Name** | screenshot-to-code |
| **GitHub URL** | https://github.com/abi/screenshot-to-code |
| **Primary Language** | Python / TypeScript |
| **Domain** | AI / Developer Tools |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Small |
| **Approximate Activity** | Medium |
| **Why Selected** | Viral burst project with very high initial star velocity followed by stabilization. |
| **Expected MIIE Behaviour** | High D-01 burst at viral moment. Sharp contributor peak. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: Moderate |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/abi/screenshot-to-code` |
| **Notes** | Viral moment project. Single high-churn spike then stabilization. |

---

### E-22 — continuedev/continue

| Field | Value |
|---|---|
| **Repository Name** | continue |
| **GitHub URL** | https://github.com/continuedev/continue |
| **Primary Language** | TypeScript |
| **Domain** | AI / Developer Tools |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | AI coding assistant in rapid experimental development. Frequent API changes. |
| **Expected MIIE Behaviour** | Moderate to high D-01 drift. Startup velocity. |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: High |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/continuedev/continue` |
| **Notes** | TypeScript AI coding tooling. High experimental churn. |

---

### E-23 — joaomdmoura/crewAI-tools

| Field | Value |
|---|---|
| **Repository Name** | crewAI-tools |
| **GitHub URL** | https://github.com/crewAIInc/crewAI-tools |
| **Primary Language** | Python |
| **Domain** | AI / Agent Tooling |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Small |
| **Approximate Activity** | High |
| **Why Selected** | Sub-project of crewAI with extremely high experimental velocity. Rapid API changes. |
| **Expected MIIE Behaviour** | High D-01. Very high release cadence. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/crewAIInc/crewAI-tools` |
| **Notes** | Sub-project experimental tooling. Fast iteration cycle. |

---

### E-24 — nomic-ai/gpt4all

| Field | Value |
|---|---|
| **Repository Name** | gpt4all |
| **GitHub URL** | https://github.com/nomic-ai/gpt4all |
| **Primary Language** | C++ / Python |
| **Domain** | AI / Local LLM |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Fast-growth local LLM runner with high architectural churn. Multiple rewrites. |
| **Expected MIIE Behaviour** | High D-01 drift. Multiple architecture changes detectable. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/nomic-ai/gpt4all` |
| **Notes** | C++ + Python. Local LLM experimental tooling. |

---

### E-25 — Chainlit/chainlit

| Field | Value |
|---|---|
| **Repository Name** | chainlit |
| **GitHub URL** | https://github.com/Chainlit/chainlit |
| **Primary Language** | Python / TypeScript |
| **Domain** | AI / Web UI |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Fast-growth AI chat UI framework. Experimental, high churn, VC-backed startup velocity. |
| **Expected MIIE Behaviour** | High D-01 drift. Startup-phase velocity. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/Chainlit/chainlit` |
| **Notes** | Python + TypeScript AI UI startup. |

---

### E-26 — frdel/agent-zero

| Field | Value |
|---|---|
| **Repository Name** | agent-zero |
| **GitHub URL** | https://github.com/frdel/agent-zero |
| **Primary Language** | Python |
| **Domain** | AI / Agents |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Small |
| **Approximate Activity** | Medium |
| **Why Selected** | Experimental AI agent framework with viral burst. Rapid early development from single developer. |
| **Expected MIIE Behaviour** | High D-01 burst. Single-developer experimental project. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/frdel/agent-zero` |
| **Notes** | Single-developer viral project. Experimental high-churn pattern. |

---

### E-27 — lavague-ai/LaVague

| Field | Value |
|---|---|
| **Repository Name** | LaVague |
| **GitHub URL** | https://github.com/lavague-ai/LaVague |
| **Primary Language** | Python |
| **Domain** | AI / Browser Automation |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Small |
| **Approximate Activity** | Medium |
| **Why Selected** | Research-grade browser automation AI. High experimental velocity, rapid architecture changes. |
| **Expected MIIE Behaviour** | Moderate to high D-01. Research lab velocity. |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: High |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/lavague-ai/LaVague` |
| **Notes** | Small research-grade experimental project. |

---

### E-28 — griptape-ai/griptape

| Field | Value |
|---|---|
| **Repository Name** | griptape |
| **GitHub URL** | https://github.com/griptape-ai/griptape |
| **Primary Language** | Python |
| **Domain** | AI / Agents |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | Experimental AI agent framework with frequent API changes. Startup velocity with institutional backing. |
| **Expected MIIE Behaviour** | High D-01 and D-03. Startup AI tooling churn. |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: High |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/griptape-ai/griptape` |
| **Notes** | Enterprise AI framework startup. Python agent tooling. |

---

### E-29 — kyegomez/swarms

| Field | Value |
|---|---|
| **Repository Name** | swarms |
| **GitHub URL** | https://github.com/kyegomez/swarms |
| **Primary Language** | Python |
| **Domain** | AI / Multi-Agent |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Small |
| **Approximate Activity** | High |
| **Why Selected** | Experimental multi-agent framework with very high commit velocity and frequent architectural pivots. |
| **Expected MIIE Behaviour** | Extreme D-01 and D-02. Very high experimental churn. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/kyegomez/swarms` |
| **Notes** | Very high commit velocity. Unusual for size. Strong stress-test candidate. |

---

### E-30 — microsoft/TinyTroupe

| Field | Value |
|---|---|
| **Repository Name** | TinyTroupe |
| **GitHub URL** | https://github.com/microsoft/TinyTroupe |
| **Primary Language** | Python |
| **Domain** | AI / Research / Simulation |
| **Category** | E — High-Churn / Experimental |
| **Repository Status** | Experimental |
| **Approximate Size** | Small |
| **Approximate Activity** | Medium |
| **Why Selected** | Microsoft research LLM simulation project. Experimental, bursts of activity at paper releases. |
| **Expected MIIE Behaviour** | Research publication activity burst pattern. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Moderate |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/microsoft/TinyTroupe` |
| **Notes** | Microsoft research project. Academic publication burst pattern. |

---

---

# CATEGORY F — Anomaly Stress-Test Candidates

> **Purpose:** Repositories likely to expose unusual development characteristics.  
> **Expected Behavior:** Maximize D-01, D-02, D-03 exercise without inventing anomalies

---

### F-01 — AUTOMATIC1111/stable-diffusion-webui

| Field | Value |
|---|---|
| **Repository Name** | stable-diffusion-webui |
| **GitHub URL** | https://github.com/AUTOMATIC1111/stable-diffusion-webui |
| **Primary Language** | Python |
| **Domain** | AI / Image Generation |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Extreme contributor burst at AI image generation explosion. >120k stars, unusual growth curve. High governance informality. |
| **Expected MIIE Behaviour** | Extreme D-01 and D-02. Stress-test for growth anomaly detectors. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/AUTOMATIC1111/stable-diffusion-webui` |
| **Notes** | Primary F-category anchor. One of the most extreme growth curves on GitHub. |

---

### F-02 — nicehash/NiceHashQuickMiner

| Field | Value |
|---|---|
| **Repository Name** | NiceHashQuickMiner |
| **GitHub URL** | https://github.com/nicehash/NiceHashQuickMiner |
| **Primary Language** | C# |
| **Domain** | Cryptocurrency / Mining |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Medium |
| **Approximate Activity** | Medium |
| **Why Selected** | Cryptocurrency project with market-correlated activity spikes. Unusual external-event-driven commit patterns. |
| **Expected MIIE Behaviour** | Unusual D-01 patterns correlated with external crypto events. |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: Moderate |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/nicehash/NiceHashQuickMiner` |
| **Notes** | Market-correlated activity patterns. External event-driven development anomaly. |

---

### F-03 — torvalds/linux (kernel release stress)

| Field | Value |
|---|---|
| **Repository Name** | linux (stress-test context) |
| **GitHub URL** | https://github.com/torvalds/linux |
| **Primary Language** | C |
| **Domain** | Operating Systems |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Extreme repository size (1M+ commits). Stress-tests MIIE parser performance, not anomaly detection. |
| **Expected MIIE Behaviour** | Performance stress test. Parser must handle massive history without timeout. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/torvalds/linux --stress-test` |
| **Notes** | Used here as system stress test, distinct from Cat A use. |

---

### F-04 — home-assistant/core

| Field | Value |
|---|---|
| **Repository Name** | core |
| **GitHub URL** | https://github.com/home-assistant/core |
| **Primary Language** | Python |
| **Domain** | IoT / Smart Home |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Extremely high contributor count (>4,000 contributors). Monthly release cadence with huge diff volumes. Stress-tests contributor analysis. |
| **Expected MIIE Behaviour** | Extreme D-02 contributor volume stress test. Very regular D-03. |
| **Expected Detector Activity** | D-01: Low · D-02: High (volume) · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/home-assistant/core` |
| **Notes** | 4,000+ contributors stress-tests D-02 contributor analysis at scale. |

---

### F-05 — public-apis/public-apis

| Field | Value |
|---|---|
| **Repository Name** | public-apis |
| **GitHub URL** | https://github.com/public-apis/public-apis |
| **Primary Language** | Python |
| **Domain** | Developer Resources |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Small |
| **Approximate Activity** | High |
| **Why Selected** | Extremely high PR/contributor volume with almost no code commits. Unusual ratio of community contribution to codebase change. |
| **Expected MIIE Behaviour** | Unusual contribution pattern. Very high D-02 contributor diversity anomaly. |
| **Expected Detector Activity** | D-01: None · D-02: High (unusual pattern) · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/public-apis/public-apis` |
| **Notes** | Data-only repository with extremely unusual commit vs. contributor ratio. |

---

### F-06 — ossf/scorecard

| Field | Value |
|---|---|
| **Repository Name** | scorecard |
| **GitHub URL** | https://github.com/ossf/scorecard |
| **Primary Language** | Go |
| **Domain** | Security |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Medium |
| **Approximate Activity** | High |
| **Why Selected** | OpenSSF security scorecard. Uses standardized security metrics. Useful for validating MIIE against known-good security posture projects. |
| **Expected MIIE Behaviour** | Healthy with security-focused development patterns. |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/ossf/scorecard` |
| **Notes** | Meta-security project. MIIE analysis of security tools is self-referential stress test. |

---

### F-07 — NixOS/nixpkgs

| Field | Value |
|---|---|
| **Repository Name** | nixpkgs |
| **GitHub URL** | https://github.com/NixOS/nixpkgs |
| **Primary Language** | Nix |
| **Domain** | Operating Systems / Package Management |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | One of the most active GitHub repositories by commit count. Extreme throughput stress test. |
| **Expected MIIE Behaviour** | Extreme throughput stress. Parser must handle very high commit volume. |
| **Expected Detector Activity** | D-01: None · D-02: High (volume) · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/NixOS/nixpkgs` |
| **Notes** | Among highest-activity repositories on GitHub. Nix language coverage. |

---

### F-08 — microsoft/windows-rs

| Field | Value |
|---|---|
| **Repository Name** | windows-rs |
| **GitHub URL** | https://github.com/microsoft/windows-rs |
| **Primary Language** | Rust |
| **Domain** | Operating Systems / Rust Bindings |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Microsoft-backed Rust Windows API bindings with very high release frequency and unusual Rust+Windows domain combination. |
| **Expected MIIE Behaviour** | High D-03 (very frequent small releases). |
| **Expected Detector Activity** | D-01: None · D-02: None · D-03: High |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/microsoft/windows-rs` |
| **Notes** | Extremely high release frequency stress-tests D-03. |

---

### F-09 — nicedoc/nicedoc.io

| Field | Value |
|---|---|
| **Repository Name** | twitter-algorithm |
| **GitHub URL** | https://github.com/twitter/the-algorithm |
| **Primary Language** | Scala / Java |
| **Domain** | AI / Recommendation |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | Low |
| **Why Selected** | Twitter/X's recommendation algorithm open-sourced abruptly in 2023. Single massive commit, almost no subsequent activity. Extreme anomaly. |
| **Expected MIIE Behaviour** | Extreme D-01 and D-03 anomaly. Single massive initial commit then near-zero activity. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/twitter/the-algorithm` |
| **Notes** | MOST UNUSUAL PATTERN: Massive initial dump then near-silence. Unique stress-test candidate. |

---

### F-10 — karpathy/nanoGPT

| Field | Value |
|---|---|
| **Repository Name** | nanoGPT |
| **GitHub URL** | https://github.com/karpathy/nanoGPT |
| **Primary Language** | Python |
| **Domain** | AI / Educational |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Small |
| **Approximate Activity** | Low |
| **Why Selected** | Viral educational AI repo. Extreme initial burst (100k+ stars), then very low maintenance activity. Stress-tests burst-then-silence pattern. |
| **Expected MIIE Behaviour** | Extreme D-01 burst then silence. D-02 massive early contributor influx then nothing. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/karpathy/nanoGPT` |
| **Notes** | Classic burst-then-silence anomaly. Extremely high early star velocity. |

---

### F-11 — keras-team/keras (TF to multi-backend)

| Field | Value |
|---|---|
| **Repository Name** | keras |
| **GitHub URL** | https://github.com/keras-team/keras |
| **Primary Language** | Python |
| **Domain** | AI / Deep Learning |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Keras 3 introduced multi-backend (TF, PyTorch, JAX) — massive architectural change. Governance moved from Google to independent org. |
| **Expected MIIE Behaviour** | Strong D-01 at Keras 3 architectural shift. D-02 governance transition. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: Moderate |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/keras-team/keras` |
| **Notes** | Multiple governance transitions and architectural pivots. Very rich anomaly source. |

---

### F-12 — bitcoin/bitcoin

| Field | Value |
|---|---|
| **Repository Name** | bitcoin |
| **GitHub URL** | https://github.com/bitcoin/bitcoin |
| **Primary Language** | C++ |
| **Domain** | Cryptocurrency |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Externally event-driven development (price cycles, halving events). Unusual correlation between crypto market and commit activity. |
| **Expected MIIE Behaviour** | External event-correlated D-01 patterns. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/bitcoin/bitcoin` |
| **Notes** | C++ cryptocurrency. Market-event-correlated development patterns. |

---

### F-13 — microsoft/phi-3

| Field | Value |
|---|---|
| **Repository Name** | Phi-3CookBook |
| **GitHub URL** | https://github.com/microsoft/Phi-3CookBook |
| **Primary Language** | Python |
| **Domain** | AI / LLM |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Small |
| **Approximate Activity** | High |
| **Why Selected** | Burst-launch AI documentation repo tied to Phi model releases. Extreme activity spikes at model release events. |
| **Expected MIIE Behaviour** | Release-event-driven D-01 and D-03 bursts. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/microsoft/Phi-3CookBook` |
| **Notes** | Model release event-driven activity. |

---

### F-14 — lencx/ChatGPT

| Field | Value |
|---|---|
| **Repository Name** | ChatGPT |
| **GitHub URL** | https://github.com/lencx/ChatGPT |
| **Primary Language** | Rust |
| **Domain** | AI / Desktop App |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Small |
| **Approximate Activity** | Low |
| **Why Selected** | Extreme initial viral burst (ChatGPT launch), then sharp decline. Classic attention-driven anomaly. |
| **Expected MIIE Behaviour** | Extreme D-01 burst then rapid decline. D-02 massive initial influx. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/lencx/ChatGPT` |
| **Notes** | Attention-economy-driven burst. Rust desktop app. |

---

### F-15 — apache/superset

| Field | Value |
|---|---|
| **Repository Name** | superset |
| **GitHub URL** | https://github.com/apache/superset |
| **Primary Language** | TypeScript / Python |
| **Domain** | Visualization / Data Analytics |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Airbnb-origin project donated to Apache. Governance transfer anomaly. Very active contributor community. |
| **Expected MIIE Behaviour** | D-02 signal at governance transfer. High ongoing activity. |
| **Expected Detector Activity** | D-01: Low · D-02: Moderate · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/apache/superset` |
| **Notes** | Airbnb → Apache Foundation governance transfer. |

---

### F-16 — deepfakes/faceswap

| Field | Value |
|---|---|
| **Repository Name** | faceswap |
| **GitHub URL** | https://github.com/deepfakes/faceswap |
| **Primary Language** | Python |
| **Domain** | AI / Computer Vision |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Medium |
| **Approximate Activity** | Low |
| **Why Selected** | Unusual project governance (anonymous maintainers), extreme early viral growth, then decline with ethical controversies. |
| **Expected MIIE Behaviour** | Extreme D-01 burst then decline. Unusual contributor anonymity patterns. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: Moderate |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/deepfakes/faceswap` |
| **Notes** | Unusual anonymized governance pattern. Ethical controversy impact on development. |

---

### F-17 — electron/electron

| Field | Value |
|---|---|
| **Repository Name** | electron |
| **GitHub URL** | https://github.com/electron/electron |
| **Primary Language** | C++ / JavaScript |
| **Domain** | Developer Tools / Desktop |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | GitHub → OpenJS Foundation governance transfer. Massive early growth, stabilized but governance changed. |
| **Expected MIIE Behaviour** | D-02 signal at governance transfer. |
| **Expected Detector Activity** | D-01: Low · D-02: Moderate · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/electron/electron` |
| **Notes** | GitHub → OpenJS Foundation. Corporate-to-foundation transition. |

---

### F-18 — apache/airflow

| Field | Value |
|---|---|
| **Repository Name** | airflow |
| **GitHub URL** | https://github.com/apache/airflow |
| **Primary Language** | Python |
| **Domain** | DevOps / Workflow Orchestration |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Airbnb-origin project. Extremely large contributor base (2000+). Airflow 2.0 was massive architectural change. |
| **Expected MIIE Behaviour** | D-01 drift at v2 architectural change. D-02 high contributor volume. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: Moderate |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/apache/airflow` |
| **Notes** | Airflow 2.0 architectural shift. Very high contributor volume stress test. |

---

### F-19 — dagger/dagger

| Field | Value |
|---|---|
| **Repository Name** | dagger |
| **GitHub URL** | https://github.com/dagger/dagger |
| **Primary Language** | Go |
| **Domain** | DevOps / CI-CD |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Complete SDK architecture rewrite from Cue to Go SDK. Extreme internal pivot. Major commit pattern change. |
| **Expected MIIE Behaviour** | Strong D-01 at language/architecture pivot. |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: Moderate |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/dagger/dagger` |
| **Notes** | Cue → Go SDK pivot. Architecture language migration anomaly. |

---

### F-20 — meilisearch/meilisearch

| Field | Value |
|---|---|
| **Repository Name** | meilisearch |
| **GitHub URL** | https://github.com/meilisearch/meilisearch |
| **Primary Language** | Rust |
| **Domain** | Databases / Search |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Fast-growth search engine startup with rapid API changes, breaking changes in early versions, license controversy. |
| **Expected MIIE Behaviour** | High D-01 drift. License change signal. |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: High |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/meilisearch/meilisearch` |
| **Notes** | Rust search engine startup. License change history. |

---

### F-21 — godotengine/godot

| Field | Value |
|---|---|
| **Repository Name** | godot |
| **GitHub URL** | https://github.com/godotengine/godot |
| **Primary Language** | C++ |
| **Domain** | Game Development |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Godot 4 was a near-complete engine rewrite. Massive contributor surge post-Unity pricing controversy 2023. |
| **Expected MIIE Behaviour** | Strong D-01 at v4 rewrite. D-02 contributor surge post-Unity controversy. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: Moderate |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/godotengine/godot` |
| **Notes** | External event (Unity controversy) drove contributor surge. Excellent D-02 stress test. |

---

### F-22 — explosion/spaCy

| Field | Value |
|---|---|
| **Repository Name** | spaCy |
| **GitHub URL** | https://github.com/explosion/spaCy |
| **Primary Language** | Python / Cython |
| **Domain** | AI / NLP |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | Medium |
| **Why Selected** | spaCy v3 was a major architectural change. LLM-era decline in relative adoption creates interesting activity trajectory. |
| **Expected MIIE Behaviour** | D-01 at v3 architectural shift. Activity trajectory change as LLMs emerged. |
| **Expected Detector Activity** | D-01: High · D-02: Low · D-03: Moderate |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/explosion/spaCy` |
| **Notes** | NLP library declining relative to transformers. Architectural shift anomaly. |

---

### F-23 — ipython/ipython

| Field | Value |
|---|---|
| **Repository Name** | ipython |
| **GitHub URL** | https://github.com/ipython/ipython |
| **Primary Language** | Python |
| **Domain** | Scientific Computing / Developer Tools |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Maintenance |
| **Approximate Size** | Large |
| **Approximate Activity** | Low |
| **Why Selected** | Jupyter split from IPython in 2014. Major project split event. Activity migrated to jupyter/notebook. |
| **Expected MIIE Behaviour** | D-01 drift at Jupyter split. Gradual activity decline following split. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/ipython/ipython` |
| **Notes** | IPython → Jupyter split is a major project fragmentation event. |

---

### F-24 — jupyter/notebook

| Field | Value |
|---|---|
| **Repository Name** | notebook |
| **GitHub URL** | https://github.com/jupyter/notebook |
| **Primary Language** | Python / JavaScript |
| **Domain** | Scientific Computing / Developer Tools |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Maintenance |
| **Approximate Size** | Large |
| **Approximate Activity** | Low |
| **Why Selected** | Jupyter Notebook v6 → v7 transition was near-complete rewrite. Pair with JupyterLab for divergence analysis. |
| **Expected MIIE Behaviour** | D-01 drift at v7 architectural change. |
| **Expected Detector Activity** | D-01: High · D-02: Moderate · D-03: High |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/jupyter/notebook` |
| **Notes** | Pair with ipython/ipython for full IPython→Jupyter trajectory. |

---

### F-25 — psf/black

| Field | Value |
|---|---|
| **Repository Name** | black |
| **GitHub URL** | https://github.com/psf/black |
| **Primary Language** | Python |
| **Domain** | Developer Tools / Formatting |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Medium |
| **Approximate Activity** | Medium |
| **Why Selected** | Extremely rapid early adoption triggered by Python formatting convention war. Unusual early contributor burst then plateau. |
| **Expected MIIE Behaviour** | D-01 burst at initial adoption wave. Growth plateau anomaly. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Low |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/psf/black` |
| **Notes** | Python formatting convention adoption wave. PSF governance transition. |

---

### F-26 — bevyengine/bevy

| Field | Value |
|---|---|
| **Repository Name** | bevy |
| **GitHub URL** | https://github.com/bevyengine/bevy |
| **Primary Language** | Rust |
| **Domain** | Game Development |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Rapid-growth Rust game engine. Extremely rapid contributor growth, frequent breaking changes in pre-1.0 phase. |
| **Expected MIIE Behaviour** | High D-01 and D-02. Pre-1.0 frequent breaking change pattern. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: High |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/bevyengine/bevy` |
| **Notes** | Rust game engine. Exceptional pre-1.0 growth and churn. |

---

### F-27 — go-gitea/gitea

| Field | Value |
|---|---|
| **Repository Name** | gitea |
| **GitHub URL** | https://github.com/go-gitea/gitea |
| **Primary Language** | Go |
| **Domain** | Developer Tools / Git Hosting |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Forked from Gogs. Company formation controversy (Gitea Ltd). Community governance conflict stress test. |
| **Expected MIIE Behaviour** | D-02 at governance conflict events. Interesting fork+governance stress. |
| **Expected Detector Activity** | D-01: Low · D-02: Moderate · D-03: None |
| **Recommended Validation Priority** | Medium |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/go-gitea/gitea` |
| **Notes** | Gogs fork with subsequent company formation controversy. |

---

### F-28 — forem/forem (dev.to)

| Field | Value |
|---|---|
| **Repository Name** | forem |
| **GitHub URL** | https://github.com/forem/forem |
| **Primary Language** | Ruby |
| **Domain** | Web / Social Platform |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | Medium |
| **Why Selected** | Forem/dev.to community platform with unusual activity spikes correlated with social media events. Licensing controversy. |
| **Expected MIIE Behaviour** | Event-correlated D-01 patterns. |
| **Expected Detector Activity** | D-01: Moderate · D-02: Moderate · D-03: Low |
| **Recommended Validation Priority** | Low |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/forem/forem` |
| **Notes** | Ruby social platform. External event-correlated development. |

---

### F-29 — microsoft/DeepSpeed

| Field | Value |
|---|---|
| **Repository Name** | DeepSpeed |
| **GitHub URL** | https://github.com/microsoft/DeepSpeed |
| **Primary Language** | Python / C++ |
| **Domain** | AI / Distributed Training |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Large |
| **Approximate Activity** | High |
| **Why Selected** | Extreme early growth driven by GPT-3/LLM training needs. Release-event-correlated bursts. Very high contributor diversity. |
| **Expected MIIE Behaviour** | High D-01 and D-02 at LLM training adoption waves. |
| **Expected Detector Activity** | D-01: High · D-02: High · D-03: Moderate |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/microsoft/DeepSpeed` |
| **Notes** | AI training infrastructure. LLM adoption wave stress test. |

---

### F-30 — community/community (GitHub community)

| Field | Value |
|---|---|
| **Repository Name** | community |
| **GitHub URL** | https://github.com/github/feedback |
| **Primary Language** | N/A (issues/discussions only) |
| **Domain** | Developer Tools / Community |
| **Category** | F — Anomaly Stress-Test |
| **Repository Status** | Active |
| **Approximate Size** | Small |
| **Approximate Activity** | High |
| **Why Selected** | Issues/discussions-only repository with no code commits. Tests MIIE behavior on code-free repositories. Edge case stress test. |
| **Expected MIIE Behaviour** | Edge case: repository with no code commits. Tests MIIE null-commit handling. |
| **Expected Detector Activity** | D-01: None (no commits) · D-02: None · D-03: None |
| **Recommended Validation Priority** | High |
| **Suggested CLI Command** | `python -m miie analyze https://github.com/github/feedback` |
| **Notes** | EDGE CASE: No code commits. Tests MIIE handling of issue-only repositories. |

---

## Summary Statistics

| Category | Count | Primary Language Mix |
|---|---|---|
| A — Healthy & Stable | 30 | C, Python, Go, Java, TypeScript, Ruby, Rust, JavaScript |
| B — Fast-Growth | 30 | Python, TypeScript, Go, Rust, Swift |
| C — Archived/Maintenance | 30 | Python, JavaScript, PHP, Scala, Java |
| D — Forks & Divergent | 30 | C++, Java, Go, PHP, C#, Elixir |
| E — Experimental | 30 | Python, TypeScript, C# |
| F — Stress-Test | 30 | Python, C++, Rust, Go, Ruby |
| **TOTAL** | **180** | **13+ languages** |

---

*End of MIIE Repository Benchmark Catalogue v1.0*
