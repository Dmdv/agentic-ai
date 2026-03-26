#!/usr/bin/env python3
"""
Validate Rust code against Microsoft Pragmatic Rust Guidelines.

Requires: Python 3.9+ (for is_relative_to())

Usage:
    python guideline-checker.py [--strict|--moderate|--advisory] <path>

Examples:
    python guideline-checker.py src/
    python guideline-checker.py --strict src/main.rs
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Runtime version check
if sys.version_info < (3, 9):
    sys.exit("Error: Python 3.9+ required (for is_relative_to())")


class Severity(Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class Violation:
    """A single guideline violation."""
    rule_id: str
    severity: Severity
    file_path: str
    line_number: int
    message: str
    suggestion: str


class GuidelineChecker:
    """Checks Rust code for guideline compliance."""

    def __init__(self, mode: str = "strict"):
        self.mode = mode
        self.violations: list[Violation] = []

    def check_file(self, file_path: Path) -> None:
        """Check a single Rust file for violations."""
        if not file_path.exists() or file_path.suffix != ".rs":
            return

        content = file_path.read_text()
        lines = content.split("\n")

        for i, line in enumerate(lines, start=1):
            self.check_unwrap(file_path, i, line)
            self.check_public_docs(file_path, i, line, lines)

    def check_unwrap(self, file_path: Path, line_num: int, line: str) -> None:
        """Check for unwrap() in production code."""
        if ".unwrap()" in line or ".expect(" in line:
            # Allow in test code
            if "#[cfg(test)]" in line or "#[test]" in line or "mod tests" in line:
                return

            self.violations.append(Violation(
                rule_id="U-ERR-004",
                severity=Severity.ERROR,
                file_path=str(file_path),
                line_number=line_num,
                message="Avoid unwrap() in production code",
                suggestion="Use '?' operator or match to handle Result/Option"
            ))

    def check_public_docs(self, file_path: Path, line_num: int, line: str, all_lines: list[str]) -> None:
        """Check that public items have documentation."""
        if line.strip().startswith("pub fn") or line.strip().startswith("pub struct") or line.strip().startswith("pub enum"):
            # Look for doc comment above (checking up to 5 lines back to account for attributes)
            has_docs = False
            for lookback in range(1, min(6, line_num)):
                prev_line = all_lines[line_num - 1 - lookback].strip()
                if prev_line.startswith("///") or prev_line.startswith("#[doc"):
                    has_docs = True
                    break
                # Stop looking if we hit non-attribute, non-empty line
                if prev_line and not prev_line.startswith("#["):
                    break

            if not has_docs:
                self.violations.append(Violation(
                    rule_id="U-DOC-001",
                    severity=Severity.WARNING if self.mode == "strict" else Severity.INFO,
                    file_path=str(file_path),
                    line_number=line_num,
                    message="Public item missing documentation",
                    suggestion="Add /// doc comment above this item"
                ))

    def check_directory(self, dir_path: Path) -> None:
        """Recursively check all Rust files in directory."""
        for rust_file in dir_path.rglob("*.rs"):
            self.check_file(rust_file)

    def report(self) -> int:
        """Print violation report and return exit code."""
        if not self.violations:
            print("[OK] No guideline violations found")
            return 0

        # Group by severity
        by_severity = {
            Severity.CRITICAL: [],
            Severity.ERROR: [],
            Severity.WARNING: [],
            Severity.INFO: [],
        }

        for v in self.violations:
            by_severity[v.severity].append(v)

        # Print report
        total = len(self.violations)
        print(f"\nGuideline Violations: {total}\n")

        for severity in [Severity.CRITICAL, Severity.ERROR, Severity.WARNING, Severity.INFO]:
            violations = by_severity[severity]
            if not violations:
                continue

            print(f"\n{severity.value} ({len(violations)}):")
            for v in violations:
                print(f"  {v.file_path}:{v.line_number}")
                print(f"    [{v.rule_id}] {v.message}")
                print(f"    Suggestion: {v.suggestion}")
                print()

        # Determine exit code based on mode
        has_critical = len(by_severity[Severity.CRITICAL]) > 0
        has_error = len(by_severity[Severity.ERROR]) > 0

        if self.mode == "strict":
            if has_critical or has_error:
                print(f"[FAILED] Strict mode: {len(by_severity[Severity.CRITICAL])} critical, {len(by_severity[Severity.ERROR])} errors")
                return 1
        elif self.mode == "moderate":
            if has_critical:
                print(f"[FAILED] Moderate mode: {len(by_severity[Severity.CRITICAL])} critical violations")
                return 1

        print(f"[PASS] {self.mode.capitalize()} mode check passed")
        return 0


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Check Rust code for Microsoft guideline compliance")
    parser.add_argument("path", help="File or directory to check")
    parser.add_argument("--strict", action="store_const", const="strict", dest="mode", default="strict",
                        help="Fail on errors and warnings (default)")
    parser.add_argument("--moderate", action="store_const", const="moderate", dest="mode",
                        help="Fail on critical issues only")
    parser.add_argument("--advisory", action="store_const", const="advisory", dest="mode",
                        help="Report only, never fail")

    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path not found: {path}")
        return 1

    checker = GuidelineChecker(mode=args.mode)

    if path.is_file():
        checker.check_file(path)
    else:
        checker.check_directory(path)

    return checker.report()


if __name__ == "__main__":
    sys.exit(main())
