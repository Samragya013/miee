# Known Defects Registry

| Defect ID | Title | Layer | Introduced | Discovered | Severity | Description | Impact | Fix Strategy | Status | Target Resolution |
|-----------|-------|-------|------------|------------|----------|-------------|--------|--------------|--------|-------------------|
| DEFECT-001 | EvidencePackage Validation Bypass | Schemas | Day 3 | Day 5 Completion Audit | Medium | EvidencePackage accepts invalid metric IDs and detector IDs when windows=[]. | Allows invalid data to pass validation when no windows are present, compromising data integrity. | Move metrics and detector validation outside the window validation loop in EvidencePackage.__post_init__() | Open | Day 6 Pre-Execution |