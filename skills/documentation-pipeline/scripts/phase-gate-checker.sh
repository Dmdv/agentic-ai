#!/usr/bin/env bash
#
# Phase Gate Checker
# Requires: Bash 4.0+ (for associative arrays)
# Validates prerequisites before proceeding to the next documentation phase.
#
# Usage:
#   bash phase-gate-checker.sh [phase_number]
#
# Examples:
#   bash phase-gate-checker.sh 2    # Check if ready for Phase 2 (Architecture)
#   bash phase-gate-checker.sh 3    # Check if ready for Phase 3 (Build)
#   bash phase-gate-checker.sh all  # Check all phases
#

set -euo pipefail

# Runtime version check
if [[ ${BASH_VERSINFO[0]} -lt 4 ]]; then
    echo "Error: Bash 4.0+ required (for associative arrays)"
    exit 1
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

DOCS_DIR=".docs"

# Required documents by phase
declare -A PHASE_PREREQS=(
    [0]=""  # Phase 0 (Conception) has no prerequisites
    [1]=""  # Phase 1 has no prerequisites
    [2]="requirements/REQUIREMENTS.md"
    [3]="requirements/REQUIREMENTS.md architecture/ARCHITECTURE.md architecture/SYSTEM_DESIGN.md"
    [4]="requirements/REQUIREMENTS.md architecture/ARCHITECTURE.md planning/IMPLEMENTATION_PLAN.md"
    [5]="testing/TESTING_STRATEGY.md testing/TEST_PLAN.md reviews/CODE_REVIEW.md"
    [6]="release/DEPLOYMENT.md release/ROLLBACK_PLAN.md"
    [7]="operations/MONITORING_GUIDE.md operations/ALERT_PLAYBOOK.md"
    [8]="support/INCIDENT_RESPONSE.md"
    [9]="maintenance/TECHNICAL_DEBT.md"
)

# Approval markers to check
APPROVAL_MARKER="<!-- IMMUTABLE: SOURCE OF TRUTH -->"
DRAFT_MARKER="<!-- DRAFT:"

check_file_exists() {
    local file="$1"
    if [[ -f "$DOCS_DIR/$file" ]]; then
        echo -e "  ${GREEN}[PASS]${NC} $file exists"
        return 0
    else
        echo -e "  ${RED}[FAIL]${NC} $file missing"
        return 1
    fi
}

check_approval_status() {
    local file="$1"
    local full_path="$DOCS_DIR/$file"

    if [[ ! -f "$full_path" ]]; then
        return 1
    fi

    if grep -q "$APPROVAL_MARKER" "$full_path" 2>/dev/null; then
        echo -e "  ${GREEN}[PASS]${NC} $file is APPROVED (immutable)"
        return 0
    elif grep -q "$DRAFT_MARKER" "$full_path" 2>/dev/null; then
        echo -e "  ${YELLOW}[WARN]${NC} $file is still in DRAFT state"
        return 1
    else
        echo -e "  ${YELLOW}[WARN]${NC} $file has no approval marker (assumed draft)"
        return 1
    fi
}

check_minimum_content() {
    local file="$1"
    local full_path="$DOCS_DIR/$file"
    local min_lines=50

    if [[ ! -f "$full_path" ]]; then
        return 1
    fi

    local line_count
    line_count=$(wc -l < "$full_path" | tr -d ' ')

    if [[ $line_count -ge $min_lines ]]; then
        echo -e "  ${GREEN}[PASS]${NC} $file has sufficient content ($line_count lines)"
        return 0
    else
        echo -e "  ${YELLOW}[WARN]${NC} $file may be incomplete ($line_count lines, expected >$min_lines)"
        return 1
    fi
}

check_phase() {
    local phase="$1"
    local prereqs="${PHASE_PREREQS[$phase]:-}"
    local passed=0
    local failed=0
    local warnings=0

    echo ""
    echo "========================================"
    echo "Phase $phase Gate Check"
    echo "========================================"

    if [[ -z "$prereqs" ]]; then
        echo -e "${GREEN}No prerequisites for Phase $phase${NC}"
        return 0
    fi

    echo ""
    echo "Checking prerequisites..."
    echo ""

    for prereq in $prereqs; do
        echo "Document: $prereq"

        # Check existence
        if check_file_exists "$prereq"; then
            ((passed++))
        else
            ((failed++))
            continue
        fi

        # Check approval status (warning only, not blocking)
        if ! check_approval_status "$prereq"; then
            ((warnings++))
        fi

        # Check minimum content
        if check_minimum_content "$prereq"; then
            ((passed++))
        else
            ((warnings++))
        fi

        echo ""
    done

    echo "========================================"
    echo "Summary:"
    echo -e "  Passed: ${GREEN}$passed${NC}"
    echo -e "  Failed: ${RED}$failed${NC}"
    echo -e "  Warnings: ${YELLOW}$warnings${NC}"
    echo "========================================"

    if [[ $failed -gt 0 ]]; then
        echo -e "${RED}[FAILED] GATE FAILED: Cannot proceed to Phase $phase${NC}"
        echo ""
        echo "Required actions:"
        echo "  1. Create missing documents"
        echo "  2. Run validation on existing documents"
        echo "  3. Get approval before proceeding"
        return 1
    elif [[ $warnings -gt 0 ]]; then
        echo -e "${YELLOW}[WARN] GATE PASSED WITH WARNINGS${NC}"
        echo ""
        echo "Recommended actions:"
        echo "  1. Complete draft documents"
        echo "  2. Run validation and get approval"
        return 0
    else
        echo -e "${GREEN}[OK] GATE PASSED: Ready for Phase $phase${NC}"
        return 0
    fi
}

check_all_phases() {
    local total_passed=0
    local total_failed=0

    echo ""
    echo "========================================"
    echo "Checking All Phase Gates"
    echo "========================================"

    for phase in {0..9}; do
        if check_phase "$phase" 2>/dev/null; then
            ((total_passed++))
        else
            ((total_failed++))
        fi
    done

    echo ""
    echo "========================================"
    echo "Overall Status:"
    echo -e "  Phases Ready: ${GREEN}$total_passed${NC}"
    echo -e "  Phases Blocked: ${RED}$total_failed${NC}"
    echo "========================================"
}

# Main
main() {
    if [[ ! -d "$DOCS_DIR" ]]; then
        echo -e "${RED}Error: .docs/ directory not found${NC}"
        echo "Run: python scripts/init-docs-structure.py [tier] [project_name]"
        exit 1
    fi

    local phase="${1:-}"

    # Input sanitization: only allow expected values
    if [[ -n "$phase" && "$phase" != "all" && ! "$phase" =~ ^[0-9]$ ]]; then
        echo -e "${RED}Error: Invalid input '$phase'${NC}"
        echo "Valid inputs: 0-9 or 'all'"
        exit 1
    fi

    case "$phase" in
        "")
            echo "Usage: bash phase-gate-checker.sh [phase_number|all]"
            echo ""
            echo "Examples:"
            echo "  bash phase-gate-checker.sh 0    # Check Phase 0 prerequisites"
            echo "  bash phase-gate-checker.sh 2    # Check Phase 2 prerequisites"
            echo "  bash phase-gate-checker.sh all  # Check all phases"
            exit 0
            ;;
        "all")
            check_all_phases
            ;;
        [0-9])
            check_phase "$phase"
            ;;
        *)
            echo -e "${RED}Error: Invalid phase number '$phase'${NC}"
            echo "Valid phases: 0-9 or 'all'"
            exit 1
            ;;
    esac
}

main "$@"
