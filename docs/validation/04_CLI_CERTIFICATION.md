# First User Certification — Phase 4: CLI Certification

**Program**: MIIE v1.0 First User Certification
**Date**: 2026-06-26

---

## Executive Summary

| Dimension | Status |
|---|---|
| Entry points | WORKING |
| Help | WORKING |
| Version | WORKING |
| Commands | 10 |
| Error handling | GRACEFUL |
| Privacy filtering | ACTIVE |

---

## CLI Entry Points

| Method | Command | Status |
|---|---|---|
| Module | python -m miie | WORKING |
| Script | miie | WORKING |

---

## Command Inventory

| Command | Description | Status |
|---|---|---|
| analyze | Full pipeline analysis | WORKING |
| ingest | Ingest commits | WORKING |
| detect | Run detection | WORKING |
| explain | Generate explanations | WORKING |
| export | Export results | WORKING |
| evaluate | Evaluate benchmarks | WORKING |
| generate | Generate candidates | WORKING |
| benchmark | Execute benchmarks | WORKING |
| validate | Validate config | WORKING |
| status | Show status | WORKING |

---

## Help System

| Test | Result |
|---|---|
| --help (global) | WORKING |
| analyze --help | WORKING |
| detect --help | WORKING |
| explain --help | WORKING |

---

## Version Output

```
$ python -m miie --version
python -m miie, version 1.0.0
```

| Check | Status |
|---|---|
| Version displayed | PASS |
| Version correct | PASS (1.0.0) |

---

## Error Handling

| Scenario | Result |
|---|---|
| Invalid command | Graceful error |
| Missing arguments | Usage message |
| Invalid options | Helpful error |
| Network failure | Graceful error |

---

## Privacy Filtering

| Field | Filtered |
|---|---|
| local_path | YES |
| temp_path | YES |
| user directories | YES |
| Windows usernames | YES |
| execution IDs | YES |
| hashes | YES |

---

## Terminal Output

| Feature | Status |
|---|---|
| Header banner | WORKING |
| Progress stages | WORKING (7 stages) |
| Section headers | WORKING |
| Status indicators | WORKING ([OK], [DONE]) |
| Summary section | WORKING |
| Report paths | WORKING |

---

## Exit Codes

| Code | Meaning | Trigger |
|---|---|---|
| 0 | Success | Analysis complete |
| 1 | Integrity issue | Integrity < 1.0 |
| 2 | System error | Internal failure |
| 3 | Validation error | Insufficient windows |

---

## Verdict

**CLI: PASS**

All commands work. Help system functional. Error handling graceful. Privacy filtering active.

---

*CLI certification completed 2026-06-26*
