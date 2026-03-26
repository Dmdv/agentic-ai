#!/bin/bash
# Go Project Verification Script
# Runs all quality checks for Go projects
# Usage: ./verify.sh [--fix] [--quick]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Flags
FIX=false
QUICK=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --fix) FIX=true ;;
        --quick) QUICK=true ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

echo "=========================================="
echo "Go Project Verification"
echo "=========================================="
echo ""

# Check for go.mod
if [[ ! -f "go.mod" ]]; then
    echo -e "${RED}ERROR: go.mod not found. Run from project root.${NC}"
    exit 1
fi

# Check Go version
GO_VERSION=$(go version | grep -oE 'go[0-9]+\.[0-9]+')
echo -e "Go version: ${GREEN}${GO_VERSION}${NC}"
echo ""

ERRORS=0

# 1. Format check
echo ">> Checking formatting..."
if [[ "$FIX" == true ]]; then
    gofmt -s -w .
    goimports -w . 2>/dev/null || true
    echo -e "${GREEN}   Formatting applied${NC}"
else
    UNFORMATTED=$(gofmt -l . 2>/dev/null)
    if [[ -n "$UNFORMATTED" ]]; then
        echo -e "${RED}   Unformatted files:${NC}"
        echo "$UNFORMATTED"
        ((ERRORS++))
    else
        echo -e "${GREEN}   All files formatted${NC}"
    fi
fi

# 2. Go vet
echo ""
echo ">> Running go vet..."
if go vet ./... 2>&1; then
    echo -e "${GREEN}   go vet passed${NC}"
else
    echo -e "${RED}   go vet found issues${NC}"
    ((ERRORS++))
fi

# 3. golangci-lint
echo ""
echo ">> Running golangci-lint..."
if command -v golangci-lint &> /dev/null; then
    if [[ "$FIX" == true ]]; then
        golangci-lint run --fix || ((ERRORS++))
    else
        if golangci-lint run; then
            echo -e "${GREEN}   golangci-lint passed${NC}"
        else
            echo -e "${RED}   golangci-lint found issues${NC}"
            ((ERRORS++))
        fi
    fi
else
    echo -e "${YELLOW}   golangci-lint not installed (skipping)${NC}"
    echo "   Install: go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest"
fi

# 4. Tests
echo ""
if [[ "$QUICK" == true ]]; then
    echo ">> Running quick tests..."
    if go test -short ./... 2>&1; then
        echo -e "${GREEN}   Tests passed${NC}"
    else
        echo -e "${RED}   Tests failed${NC}"
        ((ERRORS++))
    fi
else
    echo ">> Running tests with race detection..."
    if go test -race -cover ./... 2>&1; then
        echo -e "${GREEN}   Tests passed${NC}"
    else
        echo -e "${RED}   Tests failed${NC}"
        ((ERRORS++))
    fi
fi

# 5. Build check
echo ""
echo ">> Checking build..."
if go build ./... 2>&1; then
    echo -e "${GREEN}   Build successful${NC}"
else
    echo -e "${RED}   Build failed${NC}"
    ((ERRORS++))
fi

# 6. Module tidiness
echo ""
echo ">> Checking module tidiness..."
cp go.mod go.mod.bak
cp go.sum go.sum.bak 2>/dev/null || true
go mod tidy
if diff -q go.mod go.mod.bak > /dev/null 2>&1; then
    echo -e "${GREEN}   go.mod is tidy${NC}"
else
    if [[ "$FIX" == true ]]; then
        echo -e "${YELLOW}   go.mod tidied${NC}"
    else
        echo -e "${RED}   go.mod needs tidying (run 'go mod tidy')${NC}"
        mv go.mod.bak go.mod
        mv go.sum.bak go.sum 2>/dev/null || true
        ((ERRORS++))
    fi
fi
rm -f go.mod.bak go.sum.bak

# Summary
echo ""
echo "=========================================="
if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}All verification checks passed!${NC}"
    exit 0
else
    echo -e "${RED}Verification failed with $ERRORS error(s)${NC}"
    exit 1
fi
