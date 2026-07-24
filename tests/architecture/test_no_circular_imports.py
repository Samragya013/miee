"""Tests specifically for detecting circular imports in MIIE architecture."""

import sys
from pathlib import Path

# Root directory of the project
ROOT_DIR = Path(__file__).parent.parent.parent
SRC_DIR = ROOT_DIR / "src" / "miie"


def test_import_graph_has_no_cycles():
    """Test that the import dependency graph has no circular dependencies."""
    # Add src to Python path so we can import modules
    sys.path.insert(0, str(ROOT_DIR / "src"))

    # Build adjacency list of package dependencies
    package_deps = {}

    # Scan all Python files to build dependency graph
    for py_file in SRC_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        # Determine package
        try:
            relative_path = py_file.relative_to(SRC_DIR)
            package = relative_path.parts[0] if relative_path.parts else None
        except ValueError:
            continue

        if package not in {
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
        }:
            continue

        if package not in package_deps:
            package_deps[package] = set()

        # Parse imports
        try:
            content = py_file.read_text(encoding="utf-8")
            # Simple approach: look for import patterns
            lines = content.split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("import ") or line.startswith("from "):
                    # Extract module name
                    if line.startswith("import "):
                        modules = line[7:].split(",")
                    else:  # from ...
                        if " import " in line:
                            module_part = line.split(" import ")[0]
                            modules = [module_part[5:]]  # Remove 'from '
                        else:
                            continue

                    for module in modules:
                        module = module.strip()
                        # Check if it's one of our packages
                        if module in package_deps:
                            package_deps[package].add(module)
        except (UnicodeDecodeError, OSError):
            # Skip files we can't read
            continue

    # Check for cycles using topological sort (Kahn's algorithm)
    # Calculate in-degrees
    in_degree = {package: 0 for package in package_deps}
    for package in package_deps:
        for dep in package_deps[package]:
            if dep in in_degree:
                in_degree[dep] += 1

    # Find nodes with no incoming edges
    queue = [package for package in in_degree if in_degree[package] == 0]
    topo_order = []
    visited_count = 0

    while queue:
        current = queue.pop(0)
        topo_order.append(current)
        visited_count += 1

        # Reduce in-degree of neighbors
        for neighbor in package_deps[current]:
            if neighbor in in_degree:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

    # If we couldn't visit all nodes, there's a cycle
    if visited_count != len(package_deps):
        # Find the nodes involved in cycles
        remaining_nodes = [package for package in in_degree if in_degree[package] > 0]
        assert False, f"Circular dependencies detected involving packages: {', '.join(remaining_nodes)}"


def test_layer_isolation():
    """Test that layers maintain proper isolation as defined in TRD."""
    # Define which packages should NOT import from which other packages
    forbidden_imports = {
        "interface": {
            "processing",
            "benchmark",
            "storage",
            "detection",
            "contracts",
            "schemas",
            "reporting",
        },
        "orchestration": {"interface"},  # Should not depend on interface (wrong direction)
        "processing": {
            "interface",
            "orchestration",
        },  # Should not depend on outer layers
        "benchmark": {
            "interface",
            "orchestration",
        },  # Should not depend on outer layers
        "storage": {
            "interface",
            "orchestration",
            "processing",
            "benchmark",
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
        },
        "contracts": {
            "interface",
            "orchestration",
            "processing",
            "benchmark",
            "storage",
            "detection",
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
            "reporting",
        },
        "reporting": {
            "interface",
            "orchestration",
            "processing",
            "benchmark",
            "storage",
            "detection",
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
        },
    }

    violations = []

    for py_file in SRC_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        try:
            relative_path = py_file.relative_to(SRC_DIR)
            package = relative_path.parts[0] if relative_path.parts else None
        except ValueError:
            continue

        if package not in forbidden_imports:
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith("import ") or stripped.startswith("from "):
                    # Extract imported modules
                    if stripped.startswith("import "):
                        imported = stripped[7:].split(",")
                    elif " import " in stripped:
                        imported = [stripped.split(" import ")[0][5:]]  # Remove 'from '
                    else:
                        continue

                    for imp in imported:
                        imp = imp.strip()
                        # Handle aliases like "import module as alias"
                        if " as " in imp:
                            imp = imp.split(" as ")[0].strip()
                        # Handle multiple imports like "import a, b"
                        if "," in imp:
                            # This is simplified - in reality we'd parse better
                            for sub_imp in imp.split(","):
                                sub_imp = sub_imp.strip()
                                if " as " in sub_imp:
                                    sub_imp = sub_imp.split(" as ")[0].strip()
                                if sub_imp in forbidden_imports[package]:
                                    violations.append(
                                        f"{py_file.relative_to(ROOT_DIR)}:{line_num}: "
                                        f"Forbidden import '{sub_imp}' from layer '{package}'"
                                    )
                        elif imp in forbidden_imports[package]:
                            violations.append(
                                f"{py_file.relative_to(ROOT_DIR)}:{line_num}: "
                                f"Forbidden import '{imp}' from layer '{package}'"
                            )
        except (UnicodeDecodeError, OSError):
            continue

    assert not violations, "Layer isolation violations:\n" + "\n".join(violations)


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
