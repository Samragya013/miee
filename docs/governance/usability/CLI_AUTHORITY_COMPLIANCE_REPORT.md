# CLI_AUTHORITY_COMPLIANCE_REPORT.md

## Phase 2 — Authority Review

### Change Set Under Review

1. `src/miie/utils/git.py` — GitURLParser + GitCloner
2. `src/miie/cli.py` — `--auth-token`, format fix, rich output
3. `src/miie/processing/ingestion.py` — auth_token passthrough, encoding
4. `src/miie/processing/extraction.py` — encoding fix

### Authority Compliance Matrix

| Authority | Change | Violation? | Notes |
|-----------|--------|------------|-------|
| **TFS** §17 Immutability | Config frozen dataclass unchanged | NO | ScorePackage still frozen |
| **TFS** §13.7 Exit Codes | Exit 0/1/2/3 preserved | NO | No new exit codes |
| **TRD** §8 Pipeline Stages | 8 stages unchanged | NO | URL→clone→existing pipeline |
| **TRD** §10 Detector Contracts | D-01/D-02/D-03 unchanged | NO | No detector modifications |
| **ACS** §5 Contract Interfaces | IIngestionEngine unchanged | NO | `ingest()` signature compatible |
| **ACS** §4 Schema Integrity | RepositoryContext unchanged | NO | Existing schema populated |
| **BSD** §3 API Surface | CLI commands unchanged | NO | Existing commands extended |
| **BSD** §6 Security | No secrets in code | NO | `.env` git-ignored |
| **AFD** §9.2 Crash Recovery | Partial results saved | NO | Preserved |
| **IMP** §4 Output Format | JSON + MD reports | NO | Reports still generated |

### Verdict

**NO AUTHORITY VIOLATIONS DETECTED**

All changes are additive (new module, extended CLI options) and do not modify existing contracts, schemas, detectors, or pipeline stages.

### Architecture Decision

URL handling implemented at the **ingestion layer** (not pipeline layer):

```
GitHub URL → GitCloner → temp dir → existing RepositoryIngestionEngine.ingest()
                                          ↓
                                   Existing RepositoryContext
                                          ↓
                                   Existing Pipeline (8 stages)
```

This preserves the "URL is transparent to pipeline" contract from TRD §8.
