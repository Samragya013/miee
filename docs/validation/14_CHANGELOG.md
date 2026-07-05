# MIIE v1.0.0 Changelog

**Release Date**: 2026-06-25
**Version**: 1.0.0

---

## [1.0.0] - 2026-06-25

### Added
- **CLI**: 10 commands (analyze, ingest, extract, segment, detect, score, explain, report, validate, version)
- **CLI Options**: --verbose, --forensic, --format json, --auth-token, --output
- **3-Tier Output**: Default (human-readable), Verbose (detector IDs + timing), Forensic (full evidence)
- **Privacy Filtering**: Automatic removal of sensitive fields (local_path, temp_path, user directories, Windows usernames, execution IDs, hashes)
- **D-01**: Distribution Drift Detector (KS test + PSI)
- **D-02**: Correlation Breakdown Detector (Pearson/Spearman/Fisher-z)
- **D-03**: Threshold Compression Detector (Excess Mass + Dip test)
- **Dispatcher Engine**: Orchestrate multiple detectors
- **Registry Engine**: Prevent duplicate detectors
- **Evidence Engine**: Deterministic evidence packages with provenance
- **Explanation Engine**: Human-readable factor explanations
- **Reporting Engine**: JSON-serializable reports
- **Scoring Engine**: ScorePackage computation with integrity, confidence, risk
- **Git URL Support**: Automatic cloning via GitCloner
- **Auth Token Support**: --auth-token option with .env fallback
- **Windows Encoding**: UTF-8 with error handling
- **7-Stage Progress**: Real-time progress display

### Fixed
- **Module Identity**: Changed from `from src.miie.` to `from miie.` in 59 files
- **window_id Pattern**: Updated from `^w[0-9]+$` to support 100+ windows
- **D-3/D-4 Confidence**: Fixed sample_size factor (was always 0.02, now correctly reflects window count)
- **ScorePackage Dict**: Added _serialize_for_json() for dataclass-aware JSON serialization
- **Windows Encoding**: Added encoding='utf-8', errors='replace' to prevent UnicodeDecodeError
- **Minimum Window Gate**: Added D-1 minimum window gate (exit code 3 when <2 windows)
- **Explanation Factor Names**: Aligned factor names between scoring and explanation engines
- **Commit Strategy**: Fixed days_per_window = size / commits_per_day

### Changed
- **Pipeline**: Added Step 4b re-extraction after segmentation
- **Extraction**: Added per-window extraction with batched git log
- **Config**: Made frozen=True dataclass
- **Evidence**: Added Provenance tracking
- **Explanation**: Improved human-readable output
- **Reporting**: Added JSON serialization

### Security
- **No Secrets**: Verified no secrets in codebase
- **.env Git-Ignored**: .env file excluded from version control
- **Auth Token**: Secure handling via environment variables

---

## Previous Changes

### [0.9.0] - 2026-06-20
- Initial implementation
- 3 detectors functional
- Basic CLI interface
- 271 unit tests

### [0.8.0] - 2026-06-15
- Pipeline architecture
- Schema definitions
- Contract tests

---

## Version History

| Version | Date | Milestone |
|---|---|---|
| 0.8.0 | 2026-06-15 | Pipeline architecture |
| 0.9.0 | 2026-06-20 | Initial implementation |
| 1.0.0 | 2026-06-25 | Release certification |

---

*This changelog follows Keep a Changelog format.*
