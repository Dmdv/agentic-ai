# Go Guidelines Skill

Comprehensive Go development guidelines enforcing modern best practices with golangci-lint, table-driven tests, and idiomatic patterns.

## Overview

This skill automatically applies Go best practices when working with Go code. It covers:

- **Linting**: golangci-lint meta-linter (50+ linters)
- **Testing**: Table-driven tests with testify
- **Concurrency**: Goroutines, channels, context, errgroup
- **Web/API**: HTTP handlers, middleware, JSON, slog
- **Packaging**: go.mod, project layout, Docker

## Quick Start

### Default Setup (Strict Tier)

```bash
# Copy strict configuration (DEFAULT for all projects)
cp ~/.claude/skills/go-guidelines/templates/golangci/strict.yml .golangci.yml
cp ~/.claude/skills/go-guidelines/templates/Makefile Makefile

# Edit Makefile variables
# BINARY_NAME ?= your-app
# MAIN_PACKAGE ?= ./cmd/your-app

# Run verification
make verify
```

### Alternative Tiers

```bash
# Minimal (prototypes only)
cp templates/golangci/minimal.yml .golangci.yml

# Standard (if strict is too aggressive)
cp templates/golangci/standard.yml .golangci.yml

# Enterprise (compliance requirements)
cp templates/golangci/enterprise.yml .golangci.yml
```

## Directory Structure

```
go-guidelines/
├── SKILL.md                    # Skill definition
├── README.md                   # This file
├── templates/
│   ├── Makefile               # Build automation template
│   └── golangci/              # Linter configurations
│       ├── minimal.yml        # Basic linting
│       ├── standard.yml       # Production defaults
│       ├── strict.yml         # Professional (DEFAULT)
│       └── enterprise.yml     # Full compliance
├── resources/
│   ├── universal.md           # Core Go patterns
│   ├── testing.md             # Testing patterns
│   ├── concurrency.md         # Concurrency patterns
│   ├── web.md                 # HTTP/API patterns
│   └── packaging.md           # Module/project layout
└── scripts/
    └── verify.sh              # Verification script
```

## Configuration Tiers

| Tier | Use Case | Key Linters |
|------|----------|-------------|
| **Minimal** | Prototypes, learning | errcheck, govet, staticcheck, unused |
| **Standard** | Production apps | + gosimple, gofmt, goimports, misspell |
| **Strict** (DEFAULT) | Professional projects | + gosec, revive, gocritic, exhaustive |
| **Enterprise** | Large codebases | + gocyclo, dupl, funlen, wrapcheck |

## Key Patterns

### Error Handling
```go
// Always wrap errors with context
if err != nil {
    return fmt.Errorf("failed to process user %s: %w", userID, err)
}

// Use errors.Is/As for comparison
if errors.Is(err, ErrNotFound) { ... }
```

### Interface Design
```go
// Accept interfaces, return structs
func NewService(store UserStore) *Service

// Define interfaces where used (consumer side)
type UserStore interface {
    GetUser(ctx context.Context, id string) (*User, error)
}
```

### Testing
```go
// Table-driven tests with testify
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive", 2, 3, 5},
        {"negative", -2, -3, -5},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            require.Equal(t, tt.expected, Add(tt.a, tt.b))
        })
    }
}
```

### Concurrency
```go
// Use errgroup for coordinated goroutines
g, ctx := errgroup.WithContext(ctx)
for _, item := range items {
    g.Go(func() error {
        return process(ctx, item) // Safe in Go 1.22+
    })
}
return g.Wait()
```

## Modern Go Features (1.22+)

### Loop Variable Fix
```go
// Go 1.22+ - no longer need to copy loop variable
for _, item := range items {
    go process(item) // Safe now
}
```

### Enhanced HTTP Routing
```go
mux.HandleFunc("GET /users/{id}", getUser)
mux.HandleFunc("POST /users", createUser)

// Access path value
id := r.PathValue("id")
```

### Structured Logging (slog)
```go
logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
logger.Info("request",
    slog.String("method", r.Method),
    slog.Duration("latency", time.Since(start)),
)
```

## Tool Installation

```bash
# golangci-lint (meta-linter)
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# testify (testing)
go get github.com/stretchr/testify

# mockery (mock generation)
go install github.com/vektra/mockery/v2@latest

# goimports (formatting)
go install golang.org/x/tools/cmd/goimports@latest
```

## Verification

```bash
# Full verification
./scripts/verify.sh

# With auto-fix
./scripts/verify.sh --fix

# Quick (skip race detection)
./scripts/verify.sh --quick

# Or using Makefile
make verify
make lint
make test-race
```

## Using with Claude Code

This skill is automatically applied when working with Go code. Example interactions:

### Setting Up a New Project

```
You: Create a new Go API project with proper structure

Claude: I'll set up a Go project following best practices:
- cmd/api/main.go for entrypoint
- internal/ for private packages
- .golangci.yml with strict tier
- Makefile with standard targets
```

### Code Review

```
You: Review this Go code for best practices

Claude: I'll check against go-guidelines:
- Error handling: wrapping with context ✓
- Interfaces: defined at consumer side ✓
- Context: passed as first parameter ✓
- Testing: table-driven pattern recommended
```

### Adding Tests

```
You: Add tests for the UserService

Claude: I'll create table-driven tests with testify:
- Test cases for success and error paths
- Using require for assertions
- Mocking dependencies with mockery
```

### Concurrency Patterns

```
You: Process these items concurrently with error handling

Claude: Using errgroup for coordinated goroutines:
- Context cancellation on first error
- Bounded concurrency with SetLimit()
- Proper cleanup with defer
```

### HTTP API Development

```
You: Create a REST endpoint for users

Claude: Using Go 1.22+ enhanced routing:
- Method + path patterns (GET /users/{id})
- Middleware chain (logging, recovery, auth)
- JSON helpers with proper error responses
- Structured logging with slog
```

### Fixing Linter Issues

```
You: golangci-lint is showing errors

Claude: Common fixes:
- errcheck: handle or explicitly ignore errors
- gosec: address security warnings
- gocritic: follow suggested improvements
- Run: golangci-lint run --fix for auto-fixes
```

## References

- [Go Documentation](https://go.dev/doc/)
- [Effective Go](https://go.dev/doc/effective_go)
- [golangci-lint](https://golangci-lint.run/)
- [Go Proverbs](https://go-proverbs.github.io/)
- [testify](https://github.com/stretchr/testify)

## Requirements

| Tool | Version | Purpose |
|------|---------|---------|
| Go | 1.22+ | Runtime and toolchain |
| golangci-lint | 1.62+ | Meta-linter |
| testify | 1.9+ | Testing assertions |
| mockery | 2.x | Mock generation |
