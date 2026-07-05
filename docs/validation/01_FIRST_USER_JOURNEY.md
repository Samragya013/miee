# FUSC Phase 1 — First User Journey

**Program**: MIIE v1.0 First User Security & Experience Certification
**Date**: 2026-06-26
**Evaluator**: First-time external user perspective

---

## Executive Summary

| Criterion | Status |
|---|---|
| Installation | PASS |
| CLI Discovery | PASS |
| Help | PASS |
| Error Recovery | PASS |
| Output Clarity | PASS |
| Professionalism | PASS |

---

## Journey Steps

### 1. Installation

```bash
pip install .
```

| Check | Result |
|---|---|
| Command succeeds | YES |
| Version installed | 1.0.0 |
| Dependencies resolved | YES |
| Errors | NONE |

### 2. First Execution

```bash
python -m miie --version
```

| Check | Result |
|---|---|
| Output | `python -m miie, version 1.0.0` |
| Clear | YES |
| Professional | YES |

### 3. Help Discovery

```bash
python -m miie --help
```

| Check | Result |
|---|---|
| Commands listed | 10 |
| Options clear | YES |
| Examples provided | YES |

### 4. First Analysis

```bash
python -m miie analyze . --window-strategy commit --window-size 100
```

| Check | Result |
|---|---|
| Progress displayed | YES |
| Stages shown | 7 |
| Output clear | YES |
| Verdict clear | YES |

### 5. Verbose Mode

```bash
python -m miie analyze . --window-strategy commit --window-size 100 --verbose
```

| Check | Result |
|---|---|
| Detector IDs shown | YES |
| Timing shown | YES |
| Additional info | YES |

### 6. Forensic Mode

```bash
python -m miie analyze . --window-strategy commit --window-size 100 --forensic
```

| Check | Result |
|---|---|
| Full evidence | YES |
| Window details | YES |
| Configuration | YES |

---

## Verdict

**FIRST USER JOURNEY: PASS**

Installation, discovery, help, analysis, and modes all work as expected.

---

*First user journey completed 2026-06-26*
