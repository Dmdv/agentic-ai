#!/bin/bash
# TypeScript Project Verification Script
# Runs all quality checks: TypeScript, Biome, Vitest

set -e  # Exit on first error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track results
ERRORS=0

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    ((ERRORS++))
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if command exists
check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "$1 is not installed"
        return 1
    fi
    return 0
}

# Parse arguments
SKIP_TESTS=false
FIX_MODE=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --fix)
            FIX_MODE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "Usage: verify.sh [options]"
            echo ""
            echo "Options:"
            echo "  --skip-tests  Skip running tests"
            echo "  --fix         Auto-fix linting and formatting issues"
            echo "  -v, --verbose Show detailed output"
            echo "  -h, --help    Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

print_header "TypeScript Project Verification"

# Step 1: Check required tools
echo "Checking required tools..."

if check_command "node"; then
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION"
else
    print_error "Node.js is required"
    exit 1
fi

# Check for package manager (prefer pnpm)
if check_command "pnpm"; then
    PKG_MGR="pnpm"
    print_success "pnpm found"
elif check_command "npm"; then
    PKG_MGR="npm"
    print_warning "Using npm (pnpm recommended)"
else
    print_error "No package manager found (pnpm or npm required)"
    exit 1
fi

# Step 2: Check package.json exists
if [[ ! -f "package.json" ]]; then
    print_error "package.json not found - are you in a TypeScript project?"
    exit 1
fi
print_success "package.json found"

# Step 3: Check if dependencies are installed
if [[ ! -d "node_modules" ]]; then
    print_warning "node_modules not found, installing dependencies..."
    $PKG_MGR install
fi

# Step 4: TypeScript type checking
print_header "TypeScript Type Checking"

if [[ -f "tsconfig.json" ]]; then
    echo "Running tsc --noEmit..."
    if $PKG_MGR exec tsc --noEmit; then
        print_success "TypeScript: No type errors"
    else
        print_error "TypeScript: Type errors found"
    fi
else
    print_warning "tsconfig.json not found, skipping type check"
fi

# Step 5: Biome linting and formatting
print_header "Biome Linting & Formatting"

if [[ -f "biome.json" ]] || [[ -f "biome.jsonc" ]]; then
    if $FIX_MODE; then
        echo "Running biome check --write..."
        if $PKG_MGR exec biome check --write .; then
            print_success "Biome: All issues fixed"
        else
            print_error "Biome: Some issues could not be auto-fixed"
        fi
    else
        echo "Running biome check..."
        if $PKG_MGR exec biome check .; then
            print_success "Biome: No issues found"
        else
            print_error "Biome: Issues found (run with --fix to auto-fix)"
        fi
    fi
else
    # Fallback to ESLint + Prettier if Biome not configured
    print_warning "biome.json not found, checking for ESLint..."

    if [[ -f ".eslintrc.json" ]] || [[ -f ".eslintrc.js" ]] || [[ -f "eslint.config.js" ]]; then
        echo "Running ESLint..."
        if $FIX_MODE; then
            $PKG_MGR exec eslint . --fix || print_error "ESLint: Issues found"
        else
            $PKG_MGR exec eslint . || print_error "ESLint: Issues found"
        fi
    else
        print_warning "No linter configuration found"
    fi
fi

# Step 6: Run tests
print_header "Running Tests"

if $SKIP_TESTS; then
    print_warning "Tests skipped (--skip-tests flag)"
else
    # Detect test runner
    if grep -q '"vitest"' package.json 2>/dev/null; then
        echo "Running Vitest..."
        if $PKG_MGR exec vitest run; then
            print_success "Vitest: All tests passed"
        else
            print_error "Vitest: Some tests failed"
        fi
    elif grep -q '"jest"' package.json 2>/dev/null; then
        echo "Running Jest..."
        if $PKG_MGR exec jest; then
            print_success "Jest: All tests passed"
        else
            print_error "Jest: Some tests failed"
        fi
    else
        print_warning "No test runner found (vitest or jest)"
    fi
fi

# Step 7: Check for common issues
print_header "Additional Checks"

# Check for any usage
if grep -rn ":\s*any" --include="*.ts" --include="*.tsx" src/ 2>/dev/null | head -5; then
    print_warning "Found 'any' type usage (consider using 'unknown')"
fi

# Check for console.log in src
if grep -rn "console\.log" --include="*.ts" --include="*.tsx" src/ 2>/dev/null | head -5; then
    print_warning "Found console.log statements in src/"
fi

# Check for TODO comments
TODO_COUNT=$(grep -rn "TODO\|FIXME\|HACK" --include="*.ts" --include="*.tsx" . 2>/dev/null | wc -l | tr -d ' ')
if [[ "$TODO_COUNT" -gt 0 ]]; then
    print_warning "Found $TODO_COUNT TODO/FIXME/HACK comments"
fi

# Final summary
print_header "Verification Summary"

if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✓ All checks passed!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    exit 0
else
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}  ✗ $ERRORS check(s) failed${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    exit 1
fi
