# Module Responsibility Matrix

## Package: interface
**Purpose:** Handle external interactions with the system (CLI, API, configuration, registry)
**Allowed Dependencies:** 
- orchestrtion (for dispatching requests)
- common (for shared utilities)
**Forbidden Dependencies:** 
- processing (direct access to core logic violates layer separation)
- benchmark (direct access violates layer separation)
- storage (direct file access should go through appropriate layers)
- detection (direct access to detector logic)
- schemas (direct access to data models)
- reporting (direct access to report generation)
**Future Owner:** Engineer A (based on TRD Section 27)
**Authority Source:** TRD §2.1, §18-19

## Package: orchestration
**Purpose:** Manage workflow execution, job state, and pipeline coordination
**Allowed Dependencies:** 
- interface (for receiving requests)
- processing (for executing pipeline stages)
- storage (for persisting job state)
- common (for shared utilities)
**Forbidden Dependencies:** 
- benchmark (direct access should be through workflow engine)
- detection (direct access should be through pipeline)
- schemas (direct access to data models)
- reporting (direct access to report generation)
**Future Owner:** Engineer A (based on TRD Section 27)
**Authority Source:** TRD §2.1, §6.3

## Package: processing
**Purpose:** Execute the core analysis pipeline: ingestion → extraction → segmentation → detection → scoring → evidence → explanation → export
**Allowed Dependencies:** 
- storage (for reading/writing cached data)
- detection (for detector engine)
- schemas (for data validation)
- contracts (for DTO validation)
- common (for shared utilities)
**Forbidden Dependencies:** 
- interface (violates layer separation - core should not know about external interfaces)
- benchmark (should be separate subsystem)
- reporting (should be final stage, not called directly from middle stages)
**Future Owner:** Engineer B and Engineer C (based on TRD Section 27)
**Authority Source:** TRD §2.1, §5.2-5.9, §6.1

## Package: benchmark
**Purpose:** Manage benchmark dataset generation, ground truth management, benchmark execution, and evaluation
**Allowed Dependencies:** 
- processing (for using detector engine during benchmark runs)
- storage (for reading/writing benchmark data)
- detection (for accessing detector definitions)
- schemas (for validating benchmark data formats)
- contracts (for DTO validation)
- common (for shared utilities)
**Forbidden Dependencies:** 
- interface (violates layer separation)
- orchestration (should be independent subsystem)
- reporting (benchmark has its own reporting)
**Future Owner:** Engineer C (based on TRD Section 27)
**Authority Source:** TRD §2.1, §5.6-5.8, §6.2

## Package: storage
**Purpose:** Provide filesystem abstraction for persistent storage of inputs, intermediate results, and outputs
**Allowed Dependencies:** 
- common (for shared utilities)
**Forbidden Dependencies:** 
- ALL OTHER PACKAGES (storage layer should be dependency-free, only depended upon)
**Future Owner:** Engineer A (based on TRD Section 27 - storage is cross-cutting)
**Authority Source:** TRD §2.1, §16

## Package: detection
**Purpose:** Implement statistical tests for drift, correlation breakdown, and threshold compression (D-01, D-02, D-03)
**Allowed Dependencies:** 
- schemas (for validating detector inputs/outputs)
- contracts (for DTO validation)
- common (for shared utilities, statistical libraries)
**Forbidden Dependencies:** 
- interface (violates layer separation)
- orchestration (should be called through pipeline)
- processing (should not depend on core pipeline logic)
- benchmark (should be independent)
- storage (direct file access should go through storage layer)
- reporting (should not generate reports)
**Future Owner:** Engineer B (based on TRD Section 27)
**Authority Source:** TRD §2.1, §5.5, §10, §12

## Package: contracts
**Purpose:** Define data transfer objects (DTOs), interfaces, protocols, and validation rules for layer communication
**Allowed Dependencies:** 
- schemas (for referencing data models)
- common (for shared utilities)
**Forbidden Dependencies:** 
- interface (should not depend on external interfaces)
- orchestration (should not depend on workflow logic)
- processing (should not depend on core pipeline logic)
- benchmark (should not depend on benchmark logic)
- storage (should not depend on storage implementation)
- detection (should not depend on detector implementations)
- reporting (should not depend on report generation)
**Future Owner:** Engineer A (based on TRD Section 27)
**Authority Source:** ACS_MIIE_v1.0.md, TRD §2.1, §18

## Package: schemas
**Purpose:** Define JSON schemas and dataclasses for data validation and serialization
**Allowed Dependencies:** 
- common (for shared utilities)
**Forbidden Dependencies:** 
- ALL OTHER PACKAGES (schemas should be dependency-free, only depended upon)
**Future Owner:** Engineer C (based on TRD Section 27)
**Authority Source:** BSD-Engineering_MIIE_v1.0.md, TRD §2.1, §17

## Package: reporting
**Purpose:** Generate analysis and benchmark reports in JSON, Markdown, and CSV formats
**Allowed Dependencies:** 
- schemas (for validating report data)
- contracts (for using DTOs)
- common (for shared utilities, template engines)
**Forbidden Dependencies:** 
- interface (should not know about external interfaces)
- orchestration (should be called as final step)
- processing (should receive processed data, not access pipeline directly)
- benchmark (should have separate reporting if needed)
- storage (should receive data, not access files directly)
- detection (should not access detector logic directly)
**Future Owner:** Engineer A (based on TRD Section 27)
**Authority Source:** TRD §2.1, §5.9, §20

## Package: common
**Purpose:** Provide shared utilities, constants, helpers, and cross-cutting concerns
**Allowed Dependencies:** 
- NONE (should be independent)
**Forbidden Dependencies:** 
- NONE (by definition, common utilities should not create circular dependencies)
**Future Owner:** All engineers (shared responsibility)
**Authority Source:** TRD §2.1 (implied by layered architecture)