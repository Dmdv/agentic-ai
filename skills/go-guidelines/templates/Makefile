# Go Project Makefile Template
# Provides standardized targets for all Go projects
# Copy to: project root as Makefile

# Configuration
BINARY_NAME ?= app
MAIN_PACKAGE ?= ./cmd/$(BINARY_NAME)
GO_VERSION ?= 1.22

# Build flags
BUILD_TIME := $(shell date -u '+%Y-%m-%d_%H:%M:%S')
GIT_COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
LDFLAGS := -ldflags "-X main.version=$(VERSION) -X main.buildTime=$(BUILD_TIME) -X main.gitCommit=$(GIT_COMMIT)"

# Tools
GOLANGCI_LINT := $(shell which golangci-lint 2>/dev/null)
MOCKERY := $(shell which mockery 2>/dev/null)

.PHONY: all build run test test-race test-cover lint fmt vet clean deps tools help
.PHONY: verify docker docker-build docker-run bench profile

# Default target
all: verify build

##@ Development

build: ## Build the binary
	@echo "Building $(BINARY_NAME)..."
	go build $(LDFLAGS) -o bin/$(BINARY_NAME) $(MAIN_PACKAGE)

run: ## Run the application
	go run $(MAIN_PACKAGE)

run-dev: ## Run with live reload (requires air)
	@command -v air >/dev/null 2>&1 || { echo "Installing air..."; go install github.com/air-verse/air@latest; }
	air

clean: ## Clean build artifacts
	rm -rf bin/
	rm -rf coverage/
	go clean -testcache

##@ Testing

test: ## Run tests
	go test -v ./...

test-race: ## Run tests with race detection
	go test -race -v ./...

test-cover: ## Run tests with coverage
	@mkdir -p coverage
	go test -race -coverprofile=coverage/coverage.out -covermode=atomic ./...
	go tool cover -html=coverage/coverage.out -o coverage/coverage.html
	@echo "Coverage report: coverage/coverage.html"
	@go tool cover -func=coverage/coverage.out | tail -1

test-short: ## Run short tests only
	go test -short -v ./...

test-integration: ## Run integration tests
	go test -v -tags=integration ./...

bench: ## Run benchmarks
	go test -bench=. -benchmem ./...

##@ Code Quality

lint: ## Run golangci-lint
ifndef GOLANGCI_LINT
	@echo "Installing golangci-lint..."
	@go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
endif
	golangci-lint run

lint-fix: ## Run golangci-lint with auto-fix
	golangci-lint run --fix

fmt: ## Format code
	gofmt -s -w .
	goimports -w .

vet: ## Run go vet
	go vet ./...

verify: lint test-race ## Run all verification (lint + tests with race detection)
	@echo "All verification checks passed!"

##@ Dependencies

deps: ## Download dependencies
	go mod download

deps-upgrade: ## Upgrade dependencies
	go get -u ./...
	go mod tidy

deps-tidy: ## Tidy dependencies
	go mod tidy

deps-verify: ## Verify dependencies
	go mod verify

##@ Code Generation

generate: ## Run go generate
	go generate ./...

mocks: ## Generate mocks with mockery
ifndef MOCKERY
	@echo "Installing mockery..."
	@go install github.com/vektra/mockery/v2@latest
endif
	@mkdir -p internal/mocks
	mockery --all --dir=internal --output=internal/mocks --outpkg=mocks

##@ Tools

tools: ## Install development tools
	@echo "Installing development tools..."
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
	go install github.com/vektra/mockery/v2@latest
	go install golang.org/x/tools/cmd/goimports@latest
	go install github.com/air-verse/air@latest
	@echo "Tools installed!"

##@ Docker

docker-build: ## Build Docker image
	docker build -t $(BINARY_NAME):$(VERSION) .

docker-run: ## Run Docker container
	docker run --rm -p 8080:8080 $(BINARY_NAME):$(VERSION)

##@ Profiling

profile-cpu: ## Run CPU profiling
	go test -cpuprofile=cpu.prof -bench=. ./...
	go tool pprof -http=:8080 cpu.prof

profile-mem: ## Run memory profiling
	go test -memprofile=mem.prof -bench=. ./...
	go tool pprof -http=:8080 mem.prof

##@ Release

release-check: ## Check release readiness
	@echo "Checking release readiness..."
	@test -z "$$(git status --porcelain)" || (echo "Working directory not clean" && exit 1)
	@golangci-lint run
	@go test -race ./...
	@echo "Ready for release!"

##@ Help

help: ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
