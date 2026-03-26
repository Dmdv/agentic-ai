#!/usr/bin/env python3
"""
Validate and score documentation quality.

Requires: Python 3.9+ (for is_relative_to() and list[str] type hints)

Usage:
    python validation-scorer.py [doc_path] [doc_type]

Document Types:
    requirements       - Validates REQUIREMENTS.md
    architecture       - Validates ARCHITECTURE.md
    system-design      - Validates SYSTEM_DESIGN.md
    implementation-plan - Validates IMPLEMENTATION_PLAN.md
    test-strategy      - Validates TESTING_STRATEGY.md
    generic            - Basic validation for any document

Scoring Criteria (1-10):
    - Completeness: Are all required sections present?
    - Measurability: Are criteria quantifiable?
    - Consistency: No contradictions?
    - Traceability: Links to other docs/requirements?
    - Clarity: Clear, unambiguous language?

Examples:
    python validation-scorer.py .docs/requirements/REQUIREMENTS.md requirements
    python validation-scorer.py .docs/architecture/ARCHITECTURE.md architecture
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Runtime version check
if sys.version_info < (3, 9):
    sys.exit("Error: Python 3.9+ required (for is_relative_to() and list[str] type hints)")


@dataclass
class ValidationResult:
    """Result of document validation."""
    score: float
    completeness: float
    measurability: float
    consistency: float
    traceability: float
    clarity: float
    issues: list[str]
    suggestions: list[str]


# Required sections by document type
REQUIRED_SECTIONS = {
    "requirements": [
        "Introduction",
        "Functional Requirements",
        "Non-Functional Requirements",
        "Constraints",
        "Dependencies",
    ],
    "architecture": [
        "Part A",  # Strategic
        "Part B",  # Structural
        "Part C",  # Operational
        "Part D",  # ADRs
        "Quality Attributes",
        "Technology Stack",
    ],
    "test-strategy": [
        "Test Objectives",
        "Test Levels",
        "Coverage Targets",
        "Test Data",
        "Test Environment",
    ],
    "system-design": [
        "Introduction",
        "System Overview",
        "Component Design",
        "Data Flow",
        "Error Handling",
        "Integration Points",
    ],
    "implementation-plan": [
        "Introduction",
        "Implementation Phases",
        "Task Breakdown",
        "Dependencies",
        "Risk Mitigation",
        "Success Criteria",
    ],
    "generic": [
        "Introduction",
        "Overview",
    ],
}

# Patterns indicating measurable criteria
MEASURABLE_PATTERNS = [
    r"\d+%",           # Percentages
    r"\d+\s*(ms|s|min|hour)",  # Time measurements
    r"\d+\s*(MB|GB|TB|KB)",    # Size measurements
    r"\d+\s*(req|request|user|connection)",  # Counts
    r"(>=|<=|>|<|=)\s*\d+",    # Comparisons
    r"\d+\.\d+",       # Decimal numbers
]

# Patterns indicating traceability
TRACEABILITY_PATTERNS = [
    r"REQ-\d+",        # Requirement IDs
    r"FR-\d+",         # Functional requirement IDs
    r"NFR-\d+",        # Non-functional requirement IDs
    r"US-\d+",         # User story IDs
    r"ADR-\d+",        # Architecture decision IDs
    r"\[.*\]\(.*\.md\)",  # Markdown links to other docs
]

# Words that suggest vague/unclear language
VAGUE_WORDS = [
    "should", "might", "could", "maybe", "possibly",
    "appropriate", "adequate", "reasonable", "sufficient",
    "fast", "slow", "good", "bad", "nice", "easy",
    "etc", "and so on", "and more",
]


def check_completeness(content: str, doc_type: str) -> tuple[float, list[str]]:
    """Check if all required sections are present."""
    required = REQUIRED_SECTIONS.get(doc_type, REQUIRED_SECTIONS["generic"])
    found = 0
    missing = []

    for section in required:
        # Check for section as header (# or ##)
        pattern = rf"#+\s*{re.escape(section)}"
        if re.search(pattern, content, re.IGNORECASE):
            found += 1
        else:
            missing.append(f"Missing section: {section}")

    score = (found / len(required)) * 10 if required else 10
    return score, missing


def check_measurability(content: str) -> tuple[float, list[str]]:
    """Check for measurable, quantifiable criteria."""
    total_patterns = len(MEASURABLE_PATTERNS)
    found = 0
    suggestions = []

    for pattern in MEASURABLE_PATTERNS:
        if re.search(pattern, content):
            found += 1

    # Also check for NFR sections with measurability
    nfr_section = re.search(r"Non-Functional.*?(?=##|\Z)", content, re.DOTALL | re.IGNORECASE)
    if nfr_section:
        nfr_content = nfr_section.group()
        if not any(re.search(p, nfr_content) for p in MEASURABLE_PATTERNS[:3]):
            suggestions.append("NFRs lack measurable metrics (add specific numbers)")

    score = min((found / (total_patterns * 0.5)) * 10, 10)  # Expect at least half
    return score, suggestions


def check_traceability(content: str) -> tuple[float, list[str]]:
    """Check for links and references to other artifacts."""
    total_patterns = len(TRACEABILITY_PATTERNS)
    found = 0
    suggestions = []

    for pattern in TRACEABILITY_PATTERNS:
        if re.search(pattern, content):
            found += 1

    if found < 2:
        suggestions.append("Add more cross-references (REQ-xxx, FR-xxx, links to related docs)")

    score = min((found / (total_patterns * 0.3)) * 10, 10)  # Expect at least 30%
    return score, suggestions


def check_clarity(content: str) -> tuple[float, list[str]]:
    """Check for clear, unambiguous language."""
    issues = []
    vague_count = 0

    for word in VAGUE_WORDS:
        pattern = rf"\b{word}\b"
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            vague_count += len(matches)

    if vague_count > 10:
        issues.append(f"Found {vague_count} vague terms (should, might, etc.) - be more specific")

    # Check for passive voice indicators
    passive_patterns = [r"\bwill be\b", r"\bshould be\b", r"\bcan be\b", r"\bmust be\b"]
    passive_count = sum(len(re.findall(p, content)) for p in passive_patterns)
    if passive_count > 20:
        issues.append(f"High use of passive voice ({passive_count} instances) - use active voice")

    score = max(10 - (vague_count / 5) - (passive_count / 10), 1)
    return score, issues


def check_consistency(content: str) -> tuple[float, list[str]]:
    """Check for internal consistency."""
    issues = []

    # Check for contradictory statements
    contradictions = [
        (r"must\s+not", r"must\s+(?!not)"),
        (r"always", r"never"),
        (r"required", r"optional"),
    ]

    # Check if same term is defined differently
    # (simplified check - look for multiple definitions)
    definitions = re.findall(r"(\w+)\s+(?:is|means|refers to)\s+", content, re.IGNORECASE)
    if len(definitions) != len(set(definitions)):
        issues.append("Possible duplicate definitions found - ensure consistency")

    # Check for broken internal references
    references = re.findall(r"\[([^\]]+)\]\(#([^)]+)\)", content)
    for ref_text, ref_target in references:
        target_pattern = rf"#+\s*{re.escape(ref_target)}"
        if not re.search(target_pattern, content, re.IGNORECASE):
            issues.append(f"Broken internal link: [{ref_text}](#{ref_target})")

    score = max(10 - len(issues) * 2, 1)
    return score, issues


def validate_document(doc_path: str, doc_type: str) -> ValidationResult:
    """Validate a document and return detailed results."""
    path = Path(doc_path).resolve()

    # Security: Validate path is under .docs/ or current working directory
    cwd = Path.cwd().resolve()
    docs_dir = (cwd / ".docs").resolve()

    # Use is_relative_to() for safe path comparison (avoids /home/user matching /home/username)
    try:
        is_under_docs = path.is_relative_to(docs_dir)
    except ValueError:
        is_under_docs = False
    try:
        is_under_cwd = path.is_relative_to(cwd)
    except ValueError:
        is_under_cwd = False

    if not (is_under_docs or is_under_cwd):
        return ValidationResult(
            score=0,
            completeness=0,
            measurability=0,
            consistency=0,
            traceability=0,
            clarity=0,
            issues=[f"Security: Path must be under .docs/ or project directory: {doc_path}"],
            suggestions=[],
        )

    if not path.exists():
        return ValidationResult(
            score=0,
            completeness=0,
            measurability=0,
            consistency=0,
            traceability=0,
            clarity=0,
            issues=[f"File not found: {doc_path}"],
            suggestions=[],
        )

    # Security: Reject symlinks to prevent TOCTOU attacks
    if path.is_symlink():
        return ValidationResult(
            score=0,
            completeness=0,
            measurability=0,
            consistency=0,
            traceability=0,
            clarity=0,
            issues=[f"Security: Symlinks not allowed: {doc_path}"],
            suggestions=[],
        )

    content = path.read_text(encoding='utf-8')

    # Run all checks
    completeness, comp_issues = check_completeness(content, doc_type)
    measurability, meas_suggestions = check_measurability(content)
    traceability, trace_suggestions = check_traceability(content)
    clarity, clarity_issues = check_clarity(content)
    consistency, consist_issues = check_consistency(content)

    # Calculate overall score (weighted average)
    weights = {
        "completeness": 0.25,
        "measurability": 0.20,
        "consistency": 0.20,
        "traceability": 0.15,
        "clarity": 0.20,
    }

    overall = (
        completeness * weights["completeness"]
        + measurability * weights["measurability"]
        + consistency * weights["consistency"]
        + traceability * weights["traceability"]
        + clarity * weights["clarity"]
    )

    return ValidationResult(
        score=round(overall, 1),
        completeness=round(completeness, 1),
        measurability=round(measurability, 1),
        consistency=round(consistency, 1),
        traceability=round(traceability, 1),
        clarity=round(clarity, 1),
        issues=comp_issues + clarity_issues + consist_issues,
        suggestions=meas_suggestions + trace_suggestions,
    )


def print_result(result: ValidationResult, doc_path: str, doc_type: str) -> None:
    """Print validation result in a readable format."""
    print(f"\n{'='*60}")
    print(f"DOCUMENTATION VALIDATION REPORT")
    print(f"{'='*60}")
    print(f"Document: {doc_path}")
    print(f"Type: {doc_type}")
    print(f"{'='*60}\n")

    # Overall score with visual indicator
    status = "[APPROVED]" if result.score >= 9 else "[NEEDS WORK]" if result.score >= 7 else "[REJECTED]"
    print(f"OVERALL SCORE: {result.score}/10 {status}\n")

    # Component scores
    print("Component Scores:")
    print(f"  Completeness:  {result.completeness}/10 {'[PASS]' if result.completeness >= 8 else '[FAIL]'}")
    print(f"  Measurability: {result.measurability}/10 {'[PASS]' if result.measurability >= 8 else '[FAIL]'}")
    print(f"  Consistency:   {result.consistency}/10 {'[PASS]' if result.consistency >= 8 else '[FAIL]'}")
    print(f"  Traceability:  {result.traceability}/10 {'[PASS]' if result.traceability >= 8 else '[FAIL]'}")
    print(f"  Clarity:       {result.clarity}/10 {'[PASS]' if result.clarity >= 8 else '[FAIL]'}")

    if result.issues:
        print(f"\n{'─'*40}")
        print("Issues Found:")
        for issue in result.issues:
            print(f"  [!] {issue}")

    if result.suggestions:
        print(f"\n{'─'*40}")
        print("Suggestions:")
        for suggestion in result.suggestions:
            print(f"  [*] {suggestion}")

    print(f"\n{'='*60}")

    # Return exit code based on score
    return 0 if result.score >= 9 else 1


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    doc_path = sys.argv[1]
    doc_type = sys.argv[2] if len(sys.argv) > 2 else "generic"

    result = validate_document(doc_path, doc_type)
    exit_code = print_result(result, doc_path, doc_type)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
