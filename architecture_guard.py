"""
Lightweight architecture guard for the progressive migration.

Checks only the target tree (`src/app`) to avoid breaking legacy runtime code.
Rules are defined in ARCHITECTURE_RULES.md.
"""

import argparse
from pathlib import Path
from typing import Iterable, List, Tuple

MAX_BYTES = 4000
FORBIDDEN_FILENAMES = {"client.py", "core.py", "utils.py"}


def _iter_python_files(base_path: Path) -> Iterable[Path]:
    """Yield all .py files under the given base path."""
    return base_path.rglob("*.py")


def check_architecture(base_path: Path = Path("src/app")) -> Tuple[bool, List[str]]:
    """
    Validate the target tree against size and filename rules.

    Args:
        base_path: Directory to scan. Defaults to "src/app".

    Returns:
        (ok, violations) where ok is True when no violations are found.
    """
    base = Path(base_path)
    if not base.exists():
        return False, [f"Base path {base} does not exist"]

    violations: List[str] = []

    for py_file in _iter_python_files(base):
        if py_file.name in FORBIDDEN_FILENAMES:
            violations.append(f"Forbidden filename: {py_file.relative_to(base)}")

        size_bytes = py_file.stat().st_size
        if size_bytes > MAX_BYTES:
            violations.append(
                f"File exceeds {MAX_BYTES} bytes: {py_file.relative_to(base)} ({size_bytes} bytes)"
            )

    return not violations, violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check src/app for architecture guardrail violations."
    )
    parser.add_argument(
        "--base",
        default="src/app",
        help="Base directory to scan (default: src/app)",
    )
    args = parser.parse_args()

    base = Path(args.base)
    ok, violations = check_architecture(base)
    if ok:
        print(f"[OK] No architecture violations under {args.base}")
        return 0

    print(f"[FAIL] Architecture violations under {args.base}:")
    for issue in violations:
        print(f" - {issue}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
