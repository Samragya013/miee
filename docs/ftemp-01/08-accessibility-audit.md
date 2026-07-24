# FTEMP-01 Phase 8: Accessibility Audit

## Problem
Terminal TUIs often rely solely on color to convey meaning, making them unusable for color-blind users.

## Evidence
- WCAG 2.1 Level AA: 1.4.1 - Color not sole indicator of information
- WCAG 2.1 Level AA: 1.4.3 - Minimum contrast ratio 4.5:1
- 8% of males, 0.5% of females have color vision deficiency (Wong, 2011)
- Deuteranopia (red-green) affects 6% of males - most common

## Design Decisions

### 8.1 Color-Blind Safe Palettes
Four palettes based on Wong (2011) Nature Methods:
- **Normal**: Standard traffic light (green/cyan/yellow/red)
- **Deuteranopia**: Blue/yellow/magenta (no red-green confusion)
- **Protanopia**: Same as deuteranopia (red-green replacement)
- **Tritanopia**: Red/cyan/green (no blue-yellow confusion)
- **Monochrome**: Bold/dim only (no color)

### 8.2 Dual Coding Principle
Every color-coded element has a text-only marker:
- Colors: green/red/yellow
- Icons: V/X/! (ASCII only, cp1252 safe)
- Text labels: CLEAR/DETECTED/WARNING
- Meaning: excellent/poor/fair

### 8.3 Environment Variables
| Variable | Values | Effect |
|----------|--------|--------|
| NO_COLOR | (any) | Disable all colors |
| TERM=dumb | dumb | Disable colors + Unicode |
| MIIE_COLOR_MODE | deuteranopia/protanopia/tritanopia/monochrome | Color-blind palette |
| MIIE_HIGH_CONTRAST | 1/true/yes | High contrast mode |

### 8.4 Score Display
```
Integrity: 1.000 [excellent]  # includes text meaning
Confidence: 0.950 [good]      # not just color
```

## Implementation
- `src/miie/cli/accessibility.py` - AccessibilityConfig, color-blind palettes, dual-coded status markers
- accessible_score() - Score with text meaning
- accessible_verdict() - Verdict with text explanation
- Terminal detection (NO_COLOR, TERM=dumb)
- Unicode support detection (Windows Terminal vs legacy cmd)
