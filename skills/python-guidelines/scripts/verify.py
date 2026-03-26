#!/usr/bin/env python3
"""
Python Project Verification Script

Runs all code quality checks: ruff, mypy, pytest
Exit codes: 0 = all pass, 1 = failures found

Usage:
    python verify.py              # Run all checks
    python verify.py --quick      # Skip tests (lint + type check only)
    python verify.py --fix        # Auto-fix ruff issues
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CheckResult:
    """Result of a single check."""

    name: str
    passed: bool
    output: str
    skipped: bool = False


def run_command(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    """Run command and return (exit_code, combined_output)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )
        output = result.stdout + result.stderr
        return result.returncode, output.strip()
    except subprocess.TimeoutExpired:
        return 1, f"Command timed out: {' '.join(cmd)}"
    except FileNotFoundError:
        return -1, f"Command not found: {cmd[0]}"


def check_tool_available(tool: str) -> bool:
    """Check if a tool is available in PATH."""
    return shutil.which(tool) is not None


def run_ruff_check(fix: bool = False) -> CheckResult:
    """Run ruff linter."""
    if not check_tool_available("ruff"):
        return CheckResult("ruff check", False, "ruff not installed", skipped=True)

    cmd = ["ruff", "check", "."]
    if fix:
        cmd.append("--fix")

    code, output = run_command(cmd)
    passed = code == 0

    if passed and not output:
        output = "All checks passed!"

    return CheckResult("ruff check", passed, output)


def run_ruff_format(fix: bool = False) -> CheckResult:
    """Run ruff formatter check."""
    if not check_tool_available("ruff"):
        return CheckResult("ruff format", False, "ruff not installed", skipped=True)

    if fix:
        cmd = ["ruff", "format", "."]
    else:
        cmd = ["ruff", "format", "--check", "."]

    code, output = run_command(cmd)
    passed = code == 0

    if passed and not output:
        output = "All files formatted correctly!"

    return CheckResult("ruff format", passed, output)


def run_mypy() -> CheckResult:
    """Run mypy type checker."""
    if not check_tool_available("mypy"):
        return CheckResult("mypy", False, "mypy not installed", skipped=True)

    # Try to detect if pyproject.toml has mypy config
    pyproject = Path("pyproject.toml")
    if pyproject.exists():
        cmd = ["mypy", "."]
    else:
        # Fallback to reasonable defaults with strict mode
        cmd = ["mypy", "--strict", "--ignore-missing-imports", "."]

    code, output = run_command(cmd)
    passed = code == 0

    if passed and not output:
        output = "No type errors found!"

    return CheckResult("mypy", passed, output)


def run_pytest() -> CheckResult:
    """Run pytest test suite."""
    if not check_tool_available("pytest"):
        return CheckResult("pytest", False, "pytest not installed", skipped=True)

    # Check if tests directory exists
    tests_exist = any(Path(".").glob("test_*.py")) or Path("tests").exists()

    if not tests_exist:
        return CheckResult("pytest", True, "No tests found (skipped)", skipped=True)

    cmd = ["pytest", "-v", "--tb=short"]
    code, output = run_command(cmd)
    passed = code == 0

    return CheckResult("pytest", passed, output)


def print_result(result: CheckResult, verbose: bool = True) -> None:
    """Print a check result with formatting."""
    if result.skipped:
        status = "\033[33m⊘ SKIP\033[0m"  # Yellow
    elif result.passed:
        status = "\033[32m✓ PASS\033[0m"  # Green
    else:
        status = "\033[31m✗ FAIL\033[0m"  # Red

    print(f"\n{'='*60}")
    print(f"{status} {result.name}")
    print(f"{'='*60}")

    if verbose or not result.passed:
        if result.output:
            print(result.output)


def main() -> int:
    """Run all verification checks."""
    parser = argparse.ArgumentParser(description="Python project verification")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Skip tests (lint + type check only)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix ruff issues",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only show failures",
    )
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  Python Project Verification")
    print("=" * 60)

    results: list[CheckResult] = []

    # Run checks in order
    print("\nRunning ruff check...")
    results.append(run_ruff_check(fix=args.fix))
    print_result(results[-1], verbose=not args.quiet)

    print("\nRunning ruff format...")
    results.append(run_ruff_format(fix=args.fix))
    print_result(results[-1], verbose=not args.quiet)

    print("\nRunning mypy...")
    results.append(run_mypy())
    print_result(results[-1], verbose=not args.quiet)

    if not args.quick:
        print("\nRunning pytest...")
        results.append(run_pytest())
        print_result(results[-1], verbose=not args.quiet)

    # Summary
    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)

    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed and not r.skipped)
    skipped = sum(1 for r in results if r.skipped)
    total = len(results)

    for result in results:
        if result.skipped:
            symbol = "⊘"
        elif result.passed:
            symbol = "✓"
        else:
            symbol = "✗"
        print(f"  {symbol} {result.name}")

    print(f"\n  Passed: {passed}/{total}", end="")
    if skipped:
        print(f" (skipped: {skipped})", end="")
    print()

    if failed == 0:
        print("\n\033[32m✓ All checks passed!\033[0m\n")
        return 0
    else:
        print(f"\n\033[31m✗ {failed} check(s) failed!\033[0m\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
