---
name: go-guidelines
description: |
  Enforce modern Go best practices with golangci-lint, table-driven tests, and idiomatic patterns.
  Uses golangci-lint (meta-linter), testify, and Go 1.22+ features.
  Use for: writing Go code, reviewing code, concurrency patterns, API development.
---

# Go Development Guidelines

Automatically enforces modern Go best practices when creating or modifying Go code.

## Quick Start

**Default: Use Strict tier** - Copy to your project root:
```bash
cp ~/.claude/skills/go-guidelines/templates/golangci/strict.yml .golangci.yml
cp ~/.claude/skills/go-guidelines/templates/Makefile Makefile
```

**Natural language triggers:**
- "Create a Go project with proper linting"
- "Review this Go code for best practices"
- "Configure golangci-lint for this project"
- "Add tests for this Go module"
- "Implement concurrent processing"

## Requirements

| Dependency | Version | Purpose |
|------------|---------|---------|
| Go | 1.22+ | Runtime and toolchain |
| golangci-lint | 1.62+ | Meta-linter (50+ linters) |
| testify | 1.9+ | Testing assertions and mocks |
| mockery | 2.x | Mock generation |

## Tool Stack (2025)

### golangci-lint - Meta-Linter
The de facto standard for Go linting, used by Kubernetes, Prometheus, and Terraform.

**Why golangci-lint:**
- Aggregates 50+ linters into one fast tool
- Parallel execution with intelligent caching
- Single `.golangci.yml` configuration
- Completes in seconds on large codebases

**Key linters included:**
- `staticcheck` - Gold standard static analysis (150+ checks)
- `revive` - Extensible linter (replaces golint)
- `gosec` - Security vulnerability scanner
- `errcheck` - Error return checking
- `govet` - Go vet checks

### go test - Built-in Testing
Go's testing is built into the toolchain:
- Native test runner with `-race` flag
- Benchmarking support
- Coverage reporting
- No external test runner needed

### testify - Enhanced Testing
Standard library for Go testing:
- `require` - Stops on failure (use 99% of the time)
- `assert` - Continues on failure
- `mock` - Interface mocking
- `suite` - Test suites with setup/teardown

## Guideline Domains

| Domain | Resource | When to Load | Status |
|--------|----------|--------------|--------|
| Universal | [universal.md](resources/universal.md) | All Go code | Complete |
| Testing | [testing.md](resources/testing.md) | Table-driven tests, mocking | Complete |
| Concurrency | [concurrency.md](resources/concurrency.md) | Goroutines, channels | Complete |
| Web/API | [web.md](resources/web.md) | HTTP servers, middleware | Complete |
| Packaging | [packaging.md](resources/packaging.md) | go.mod, project layout | Complete |

## Configuration Tiers

### Minimal (Quick Start)
```yaml
# .golangci.yml
linters:
  enable:
    - errcheck
    - govet
    - staticcheck
    - unused
```

### Standard (Production)
```yaml
linters:
  enable:
    - errcheck
    - govet
    - staticcheck
    - unused
    - gosimple
    - ineffassign
    - typecheck
    - gofmt
    - goimports
    - misspell
```

### Strict (DEFAULT - Most Projects)
```yaml
linters:
  enable:
    # Standard tier plus:
    - gosec          # Security checks
    - revive         # Extensible linting
    - gocritic       # Opinionated checks
    - prealloc       # Slice preallocation
    - noctx          # HTTP request context
    - exhaustive     # Exhaustive enum checks
    - errname        # Error naming conventions
```

### Enterprise (Full Compliance)
See [templates/golangci/enterprise.yml](templates/golangci/enterprise.yml).

## Key Go Idioms

### Error Handling
```go
// ✅ ALWAYS wrap errors with context
if err != nil {
    return fmt.Errorf("failed to process user %s: %w", userID, err)
}

// ✅ Use errors.Is and errors.As for comparison
if errors.Is(err, ErrNotFound) {
    return nil // Expected case
}

// ❌ NEVER ignore errors
result, _ := doSomething() // WRONG
```

### Interface Design
```go
// ✅ Accept interfaces, return structs
func NewService(store UserStore) *Service

// ✅ Define interfaces where used (not where implemented)
type UserStore interface {
    GetUser(ctx context.Context, id string) (*User, error)
}

// ✅ Small interfaces (1-3 methods)
type Reader interface {
    Read(p []byte) (n int, err error)
}
```

### Context Propagation
```go
// ✅ Context is ALWAYS first parameter
func DoWork(ctx context.Context, id string) error

// ✅ Check for cancellation
select {
case <-ctx.Done():
    return ctx.Err()
case result := <-workChan:
    return process(result)
}

// ❌ NEVER store context in structs
type Bad struct {
    ctx context.Context // WRONG
}
```

### Concurrency
```go
// ✅ Use errgroup for coordinated goroutines
g, ctx := errgroup.WithContext(ctx)
for _, item := range items {
    item := item // Not needed in Go 1.22+
    g.Go(func() error {
        return process(ctx, item)
    })
}
return g.Wait()

// ✅ Always provide exit path for goroutines
// ❌ NEVER start goroutines without way to stop them
```

## Key golangci-lint Rules

| Rule | Purpose | Tier |
|------|---------|------|
| `errcheck` | Check error returns | ALL |
| `staticcheck` | Static analysis (150+ checks) | ALL |
| `gosec` | Security vulnerabilities | Strict |
| `revive` | Extensible linting | Strict |
| `gocritic` | Opinionated checks | Strict |
| `gocyclo` | Cyclomatic complexity | Enterprise |
| `dupl` | Duplicate code detection | Enterprise |
| `wrapcheck` | Error wrapping | Enterprise |

## Modern Standards (Go 1.22+)

### Loop Variable Fix (Go 1.22)
```go
// Before Go 1.22 - needed explicit copy
for _, item := range items {
    item := item // Required to avoid capture bug
    go process(item)
}

// Go 1.22+ - fixed automatically
for _, item := range items {
    go process(item) // Safe now
}
```

### Enhanced HTTP Routing (Go 1.22)
```go
mux := http.NewServeMux()
mux.HandleFunc("GET /users/{id}", getUser)      // Method + path params
mux.HandleFunc("POST /users", createUser)
mux.HandleFunc("DELETE /users/{id}", deleteUser)
```

### Structured Logging (Go 1.21+)
```go
logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
logger.Info("request processed",
    slog.String("method", r.Method),
    slog.Duration("latency", time.Since(start)),
)
```

## Enforcement Modes

### Strict Mode (New Code)
- All linters enabled
- Race detection required
- No lint suppressions without justification

### Advisory Mode (Code Review)
- Violations reported with severity
- Non-blocking recommendations

### Incremental Mode (Migration)
- Focus on modified code
- Gradually enable stricter rules

## Verification

```bash
# Full verification (recommended)
make verify  # or: golangci-lint run && go test -race ./...

# Individual tools
golangci-lint run           # Lint check
golangci-lint run --fix     # Auto-fix where possible
go test -race -cover ./...  # Tests with race detection
go test -bench=. ./...      # Benchmarks
```

## Integration

Works standalone or composed with domain-specific skills:
- `go-guidelines` + `grpc` → gRPC service development
- `go-guidelines` + `kubernetes` → K8s controller/operator
- `go-guidelines` + `database` → Database access patterns

## References

Based on: **Go Best Practices 2025**
- Go Documentation: https://go.dev/doc/
- Effective Go: https://go.dev/doc/effective_go
- golangci-lint: https://golangci-lint.run/
- Go Proverbs: https://go-proverbs.github.io/
- Last updated: 2025-01-05
