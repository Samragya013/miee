"""Tests for validating MIIE architectural layer dependencies."""

import ast
from pathlib import Path

import pytest

# Root directory of the project
ROOT_DIR = Path(__file__).parent.parent.parent
SRC_DIR = ROOT_DIR / "src" / "miie"

# Define layer dependencies based on dependency_rules.md
ALLOWED_DEPENDENCIES = {
    "interface": {"orchestration", "common"},
    "orchestration": {"processing", "storage", "common"},
    "processing": {"storage", "detection", "schemas", "contracts", "common"},
    "benchmark": {
        "processing",
        "storage",
        "detection",
        "schemas",
        "contracts",
        "common",
    },
    "storage": {"common"},
    "detection": {"schemas", "contracts", "common"},
    "contracts": {"schemas", "common"},
    "schemas": {"common"},
    "reporting": {"schemas", "contracts", "common"},
    "common": set(),  # Common should have no dependencies
}

FORBIDDEN_DEPENDENCIES = {
    "interface": {
        "interface",
        "processing",
        "benchmark",
        "storage",
        "detection",
        "contracts",
        "schemas",
        "reporting",
    },
    "orchestration": {"interface", "orchestration", "interface"},
    "processing": {"interface", "orchestration", "processing", "benchmark"},
    "benchmark": {"interface", "orchestration", "benchmark"},
    "storage": {
        "interface",
        "orchestration",
        "processing",
        "benchmark",
        "storage",
        "detection",
        "contracts",
        "schemas",
        "reporting",
    },
    "detection": {
        "interface",
        "orchestration",
        "processing",
        "benchmark",
        "storage",
        "detection",
    },
    "contracts": {
        "interface",
        "orchestration",
        "processing",
        "benchmark",
        "storage",
        "detection",
        "contracts",
        "reporting",
    },
    "schemas": {
        "interface",
        "orchestration",
        "processing",
        "benchmark",
        "storage",
        "detection",
        "contracts",
        "schemas",
        "reporting",
    },
    "reporting": {
        "interface",
        "orchestration",
        "processing",
        "benchmark",
        "storage",
        "detection",
        "reporting",
    },
    "common": {
        "interface",
        "orchestration",
        "processing",
        "benchmark",
        "storage",
        "detection",
        "contracts",
        "schemas",
        "reporting",
        "common",
    },
}


def get_imports_from_file(file_path):
    """Extract all module imports from a Python file."""
    try:
        tree = ast.parse(file_path.read_text())
    except (SyntaxError, UnicodeDecodeError):
        return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                # Get top-level package name
                top_level = alias.name.split(".")[0]
                imports.add(top_level)
        elif isinstance(node, ast.ImportFrom):
            if node.module:  # None for relative imports like `from . import x`
                # Get top-level package name
                top_level = node.module.split(".")[0]
                imports.add(top_level)
    return imports


def get_package_for_module(module_path):
    """Determine which package a module belongs to based on its path."""
    # Convert to Path object if it isn't already
    if isinstance(module_path, str):
        module_path = Path(module_path)

    # Get the path relative to src/miie
    try:
        relative_path = module_path.relative_to(SRC_DIR)
        # The first component is the package name
        return relative_path.parts[0] if relative_path.parts else None
    except ValueError:
        # Path is not under SRC_DIR
        return None


def test_layer_dependencies():
    """Test that modules only import from allowed layers."""
    violations = []

    # Iterate through all Python files in src/miie
    for py_file in SRC_DIR.rglob("*.py"):
        # Skip __pycache__ and similar directories
        if "__pycache__" in str(py_file):
            continue

        # Determine which package this file belongs to
        package = get_package_for_module(py_file)
        if package is None or package not in ALLOWED_DEPENDENCIES:
            # Skip files not in our expected packages (like root level files)
            continue

        # Get imports from this file
        imports = get_imports_from_file(py_file)

        # Check each import against allowed dependencies
        for imported_module in imports:
            # Skip standard library and external imports
            if imported_module in {
                "os",
                "sys",
                "json",
                "csv",
                "click",
                "yaml",
                "numpy",
                "pandas",
                "scipy",
                "jinja2",
                "pathlib",
                "typing",
                "dataclasses",
                "abc",
                "enum",
                "random",
                "math",
                "statistics",
                "datetime",
                "re",
                "collections",
                "itertools",
                "functools",
                "hashlib",
                "hmac",
                "subprocess",
                "textwrap",
                "uuid",
                "shutil",
                "tempfile",
                "glob",
                "fnmatch",
            }:
                continue

            # Check if it's one of our expected packages
            if imported_module in ALLOWED_DEPENDENCIES:
                if imported_module not in ALLOWED_DEPENDENCIES[package]:
                    violations.append(
                        f"{py_file.relative_to(ROOT_DIR)}: "
                        f"Forbidden import '{imported_module}' from package '{package}' "
                        f"(allowed: {ALLOWED_DEPENDENCIES[package]})"
                    )

    assert not violations, f"Dependency violations found:\n" + "\n".join(violations)


def test_no_circular_imports():
    """Test that there are no circular dependencies between packages."""
    # Build dependency graph
    graph = {package: set() for package in ALLOWED_DEPENDENCIES.keys()}

    # Populate graph with actual dependencies from code
    for py_file in SRC_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        package = get_package_for_module(py_file)
        if package is None or package not in ALLOWED_DEPENDENCIES:
            continue

        imports = get_imports_from_file(py_file)
        for imported_module in imports:
            if imported_module in ALLOWED_DEPENDENCIES:
                graph[package].add(imported_module)

    # Check for cycles using DFS
    def has_cycle(node, visited, rec_stack):
        visited.add(node)
        rec_stack.add(node)

        for neighbor in graph[node]:
            if neighbor not in visited:
                if has_cycle(neighbor, visited, rec_stack):
                    return True
            elif neighbor in rec_stack:
                return True

        rec_stack.remove(node)
        return False

    visited = set()
    rec_stack = set()
    cycles = []

    for node in graph:
        if node not in visited:
            if has_cycle(node, visited, rec_stack):
                # Find the actual cycle
                cycle_path = []
                temp_visited = set()
                temp_rec_stack = set()

                def find_cycle(n):
                    temp_visited.add(n)
                    temp_rec_stack.add(n)

                    for neighbor in graph[n]:
                        if neighbor not in temp_visited:
                            if find_cycle(neighbor):
                                cycle_path.append(f"{n} -> {neighbor}")
                                return True
                        elif neighbor in temp_rec_stack:
                            cycle_path.append(f"{n} -> {neighbor}")
                            return True

                    temp_rec_stack.remove(n)
                    return False

                find_cycle(node)
                cycles.append(" -> ".join(reversed(cycle_path)))

    assert not cycles, f"Circular dependencies found:\n" + "\n".join(cycles)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
