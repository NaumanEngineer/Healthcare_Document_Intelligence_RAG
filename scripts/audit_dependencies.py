"""Audit direct Python dependencies used by the repository.

Run from the repository root:

    python scripts/audit_dependencies.py

The script scans Python files in ``src`` and ``tests`` and separates:

- Python standard-library modules
- project-local modules
- third-party dependency candidates

Import names are mapped to their actual Python distribution names where those
names differ.

The script does not install packages or modify the environment.
"""

from __future__ import annotations

import ast
import importlib.metadata
import pathlib
import sys
from dataclasses import dataclass


REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[1]

SCAN_DIRECTORIES = (
    REPOSITORY_ROOT / "src",
    REPOSITORY_ROOT / "tests",
)

LOCAL_MODULES = {
    "src",
    "tests",
}

PACKAGE_NAME_MAP = {
    "fitz": "PyMuPDF",
    "rank_bm25": "rank-bm25",
    "sentence_transformers": "sentence-transformers",
    "sklearn": "scikit-learn",
}


@dataclass(frozen=True)
class DependencyRecord:
    """One discovered third-party dependency candidate."""

    import_name: str
    package_name: str
    installed_version: str | None


def _read_python_file(
    path: pathlib.Path,
) -> str:
    """Read Python source safely for AST inspection."""

    return path.read_text(
        encoding="utf-8-sig"
    )


def _extract_top_level_imports(
    path: pathlib.Path,
) -> set[str]:
    """Return top-level absolute imports from one Python file."""

    source = _read_python_file(
        path
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    imports: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                imports.add(
                    alias.name.split(".")[0]
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            if (
                node.level == 0
                and node.module
            ):
                imports.add(
                    node.module.split(".")[0]
                )

    return imports


def _collect_repository_imports(
) -> set[str]:
    """Collect imported top-level modules from src and tests."""

    imports: set[str] = set()

    for directory in SCAN_DIRECTORIES:
        if not directory.exists():
            continue

        for path in directory.rglob(
            "*.py"
        ):
            imports.update(
                _extract_top_level_imports(
                    path
                )
            )

    return imports


def _is_standard_library(
    module_name: str,
) -> bool:
    """Return whether module belongs to the Python standard library."""

    return (
        module_name
        in sys.stdlib_module_names
    )


def _package_name_for_import(
    import_name: str,
) -> str:
    """Translate import name to installed distribution name."""

    return PACKAGE_NAME_MAP.get(
        import_name,
        import_name,
    )


def _installed_version(
    package_name: str,
) -> str | None:
    """Return installed distribution version when available."""

    try:
        return (
            importlib.metadata.version(
                package_name
            )
        )

    except (
        importlib.metadata.PackageNotFoundError
    ):
        return None


def build_dependency_inventory(
) -> list[DependencyRecord]:
    """Build deterministic third-party dependency inventory."""

    imports = (
        _collect_repository_imports()
    )

    candidates = sorted(
        module_name
        for module_name in imports
        if module_name
        and module_name
        not in LOCAL_MODULES
        and not _is_standard_library(
            module_name
        )
    )

    records = []

    for import_name in candidates:
        package_name = (
            _package_name_for_import(
                import_name
            )
        )

        records.append(
            DependencyRecord(
                import_name=import_name,
                package_name=package_name,
                installed_version=(
                    _installed_version(
                        package_name
                    )
                ),
            )
        )

    return records


def main() -> int:
    """Print dependency inventory."""

    inventory = (
        build_dependency_inventory()
    )

    print(
        "Healthcare Document Intelligence RAG"
    )

    print(
        "Repository Dependency Audit"
    )

    print(
        "===================================="
    )

    print()

    print(
        f"Python: {sys.version.split()[0]}"
    )

    directories = ", ".join(
        str(
            path.relative_to(
                REPOSITORY_ROOT
            )
        )
        for path in SCAN_DIRECTORIES
    )

    print(
        f"Python files scanned from: "
        f"{directories}"
    )

    print()

    if not inventory:
        print(
            "No third-party dependency "
            "candidates found."
        )

        return 0

    print(
        "Direct third-party import candidates:"
    )

    print()

    missing = []

    for record in inventory:
        version = (
            record.installed_version
            if record.installed_version
            is not None
            else "NOT INSTALLED"
        )

        print(
            f"- import: {record.import_name}"
        )

        print(
            f"  package: {record.package_name}"
        )

        print(
            f"  installed: {version}"
        )

        if (
            record.installed_version
            is None
        ):
            missing.append(
                record.package_name
            )

    print()

    print(
        f"Candidate count: {len(inventory)}"
    )

    print(
        f"Missing locally: {len(missing)}"
    )

    if missing:
        print()

        print(
            "Missing package candidates:"
        )

        for package_name in missing:
            print(
                f"- {package_name}"
            )

        return 1

    print()

    print(
        "Dependency audit: PASS"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )