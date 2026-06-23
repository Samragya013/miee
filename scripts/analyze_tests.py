#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Configuration
src_root = Path("src/miie")
test_root = Path("tests")

# Get all source files (excluding __pycache__)
source_files = []
for root, dirs, files in os.walk(src_root):
    # Skip __pycache__ directories
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for file in files:
        if file.endswith('.py'):
            source_files.append(Path(root) / file)

# Get all test files (excluding __pycache__)
test_files = []
for root, dirs, files in os.walk(test_root):
    # Skip __pycache__ directories
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for file in files:
        if file.endswith('.py') and not file.startswith('__'):
            test_files.append(Path(root) / file)

# Create a set of test file stems (without .py) for quick lookup
test_stems = {f.stem: f for f in test_files}
# Also create a mapping from relative path to test file for more specific lookup
test_rel_map = {}
for f in test_files:
    rel = f.relative_to(test_root)
    test_rel_map[rel.stem] = f  # This might overwrite if same stem in different dirs, but we'll handle

print("Source files without corresponding test files (by stem):")
print("=" * 60)
missing = []
for sf in source_files:
    # Get the relative path from src_root
    try:
        rel_to_src = sf.relative_to(src_root)
    except ValueError:
        # Should not happen
        continue

    # Remove the .py extension
    stem = sf.stem
    # Possible test locations:
    # 1. Same relative path under tests/unit, tests/integration, etc.
    found = False
    for test_type in ['unit', 'integration', 'schema', 'contract', 'benchmark', 'workflow', 'performance']:
        test_path = test_root / test_type / rel_to_src.parent / f"test_{stem}.py"
        if test_path.exists():
            found = True
            break
        # Also check without the 'test_' prefix? Some tests might not have test_ prefix?
        test_path2 = test_root / test_type / rel_to_src.parent / f"{stem}.py"
        if test_path2.exists():
            found = True
            break

    # Also check if the test file is directly in the test type directory (if the source is in a subdir)
    if not found:
        for test_type in ['unit', 'integration', 'schema', 'contract', 'benchmark', 'workflow', 'performance']:
            test_path = test_root / test_type / f"test_{stem}.py"
            if test_path.exists():
                found = True
                break
            test_path2 = test_root / test_type / f"{stem}.py"
            if test_path2.exists():
                found = True
                break

    # Also check in the root of tests (like conftest, but those are not testing a specific module)
    if not found:
        if (test_root / f"test_{stem}.py").exists():
            found = True
        if (test_root / f"{stem}.py").exists():
            found = True

    if not found:
        missing.append((sf, rel_to_src))

if missing:
    for sf, rel in missing:
        print(f"MISSING: {rel} (full: {sf})")
else:
    print("All source files have a corresponding test file (by stem and common test types).")

print("\n" + "=" * 60)
print("Source files and their corresponding test files (if found):")
print("=" * 60)
for sf in source_files:
    try:
        rel_to_src = sf.relative_to(src_root)
    except ValueError:
        continue
    stem = sf.stem
    found_at = None
    for test_type in ['unit', 'integration', 'schema', 'contract', 'benchmark', 'workflow', 'performance']:
        test_path = test_root / test_type / rel_to_src.parent / f"test_{stem}.py"
        if test_path.exists():
            found_at = test_path
            break
        test_path2 = test_root / test_type / rel_to_src.parent / f"{stem}.py"
        if test_path2.exists():
            found_at = test_path2
            break
    if not found_at:
        for test_type in ['unit', 'integration', 'schema', 'contract', 'benchmark', 'workflow', 'performance']:
            test_path = test_root / test_type / f"test_{stem}.py"
            if test_path.exists():
                found_at = test_path
                break
            test_path2 = test_root / test_type / f"{stem}.py"
            if test_path2.exists():
                found_at = test_path2
                break
    if not found_at:
        if (test_root / f"test_{stem}.py").exists():
            found_at = test_root / f"test_{stem}.py"
        elif (test_root / f"{stem}.py").exists():
            found_at = test_root / f"{stem}.py"

    if found_at:
        print(f"[FOUND] {rel_to_src} -> {found_at.relative_to(test_root)}")
    else:
        print(f"[MISSING] {rel_to_src}")

print("\n" + "=" * 60)
print("Test files that do not seem to correspond to any source file (possible orphan tests):")
print("=" * 60)
# For each test file, see if there is a source file that matches
orphan = []
for tf in test_files:
    # Skip conftest and __init__
    if tf.name in ['conftest.py', '__init__.py']:
        continue
    stem = tf.stem
    # Remove leading 'test_' if present
    if stem.startswith('test_'):
        stem = stem[5:]
    # Now look for a source file with this stem in src/miie
    found = False
    for sf in source_files:
        if sf.stem == stem:
            found = True
            break
    if not found:
        # Also check if the source file is in a subdirectory but same stem
        for sf in source_files:
            if sf.parent.name == stem and sf.name == '__init__.py':
                # This is a package, the test might be for the package
                found = True
                break
    if not found:
        orphan.append(tf)

if orphan:
    for tf in orphan:
        print(f"ORPHAN TEST: {tf.relative_to(test_root)}")
else:
    print("No orphan test files found.")

print("\n" + "=" * 60)
print("Summary:")
print("=" * 60)
print(f"Total source files: {len(source_files)}")
print(f"Total test files: {len(test_files)}")
print(f"Missing tests (source without test): {len(missing)}")
print(f"Orphan tests: {len(orphan)}")