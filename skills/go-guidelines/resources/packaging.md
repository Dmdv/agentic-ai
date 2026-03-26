# Go Packaging & Project Layout

Module management, project structure, and build patterns.

## Project Layout

### Standard Layout

```
myproject/
├── cmd/                    # Application entrypoints
│   ├── api/
│   │   └── main.go        # API server binary
│   └── worker/
│       └── main.go        # Background worker binary
├── internal/              # Private application code
│   ├── config/            # Configuration loading
│   ├── handler/           # HTTP handlers
│   ├── service/           # Business logic
│   ├── repository/        # Data access
│   └── model/             # Domain models
├── pkg/                   # Public library code (importable)
│   └── client/            # API client library
├── api/                   # API definitions (OpenAPI, proto)
├── web/                   # Web assets
├── scripts/               # Build/deploy scripts
├── deployments/           # Docker, K8s configs
├── .golangci.yml          # Linter configuration
├── Makefile               # Build automation
├── go.mod
├── go.sum
└── README.md
```

### Simple Layout (Small Projects)

```
myproject/
├── main.go                # Single entrypoint
├── handlers.go            # HTTP handlers
├── service.go             # Business logic
├── repository.go          # Data access
├── config.go              # Configuration
├── go.mod
├── go.sum
├── Makefile
└── README.md
```

### Library Layout

```
mylib/
├── mylib.go               # Main package API
├── types.go               # Public types
├── options.go             # Functional options
├── internal/              # Private implementation
│   └── parser/
├── examples/              # Example usage
│   └── basic/
│       └── main.go
├── go.mod
├── go.sum
└── README.md
```

## Module Management

### go.mod

```go
module github.com/yourorg/myproject

go 1.22

require (
    github.com/stretchr/testify v1.9.0
    golang.org/x/sync v0.6.0
)

// Optional: replace for local development
// replace github.com/yourorg/otherlib => ../otherlib
```

### Common Commands

```bash
# Initialize module
go mod init github.com/yourorg/myproject

# Add dependencies
go get github.com/stretchr/testify@latest
go get github.com/stretchr/testify@v1.9.0

# Update dependencies
go get -u ./...           # Update all
go get -u github.com/pkg  # Update specific

# Clean up
go mod tidy               # Remove unused, add missing
go mod verify             # Verify checksums

# Download for offline/CI
go mod download

# View dependency graph
go mod graph

# Explain why dependency is needed
go mod why github.com/some/dep
```

### Vendoring (Optional)

```bash
# Create vendor directory
go mod vendor

# Build using vendor
go build -mod=vendor ./...

# Verify vendor matches go.sum
go mod verify
```

## Package Design

### cmd/ Pattern

```go
// cmd/api/main.go
package main

import (
    "context"
    "log/slog"
    "os"
    "os/signal"

    "github.com/yourorg/myproject/internal/config"
    "github.com/yourorg/myproject/internal/server"
)

func main() {
    if err := run(); err != nil {
        slog.Error("fatal error", slog.Any("error", err))
        os.Exit(1)
    }
}

func run() error {
    ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt)
    defer cancel()

    cfg, err := config.Load()
    if err != nil {
        return fmt.Errorf("loading config: %w", err)
    }

    srv := server.New(cfg)
    return srv.Run(ctx)
}
```

### internal/ Packages

```go
// internal/service/user.go
package service

import (
    "context"

    "github.com/yourorg/myproject/internal/model"
    "github.com/yourorg/myproject/internal/repository"
)

type UserService struct {
    repo repository.UserRepository
}

func NewUserService(repo repository.UserRepository) *UserService {
    return &UserService{repo: repo}
}

func (s *UserService) GetUser(ctx context.Context, id string) (*model.User, error) {
    return s.repo.Find(ctx, id)
}
```

### pkg/ for Public Libraries

```go
// pkg/client/client.go
package client

import (
    "context"
    "net/http"
)

// Client is the public API client
type Client struct {
    baseURL    string
    httpClient *http.Client
}

// NewClient creates a new API client
func NewClient(baseURL string, opts ...Option) *Client {
    c := &Client{
        baseURL:    baseURL,
        httpClient: http.DefaultClient,
    }
    for _, opt := range opts {
        opt(c)
    }
    return c
}

// Option configures the client
type Option func(*Client)

// WithHTTPClient sets a custom HTTP client
func WithHTTPClient(hc *http.Client) Option {
    return func(c *Client) {
        c.httpClient = hc
    }
}
```

## Configuration

### Environment-Based Config

```go
// internal/config/config.go
package config

import (
    "fmt"
    "os"
    "strconv"
    "time"
)

type Config struct {
    Env         string
    Port        int
    DatabaseURL string
    LogLevel    string
    Timeout     time.Duration
}

func Load() (*Config, error) {
    cfg := &Config{
        Env:      getEnv("APP_ENV", "development"),
        Port:     getEnvInt("PORT", 8080),
        LogLevel: getEnv("LOG_LEVEL", "info"),
        Timeout:  getEnvDuration("TIMEOUT", 30*time.Second),
    }

    // Required values
    cfg.DatabaseURL = os.Getenv("DATABASE_URL")
    if cfg.DatabaseURL == "" {
        return nil, fmt.Errorf("DATABASE_URL is required")
    }

    return cfg, nil
}

func getEnv(key, fallback string) string {
    if value := os.Getenv(key); value != "" {
        return value
    }
    return fallback
}

func getEnvInt(key string, fallback int) int {
    if value := os.Getenv(key); value != "" {
        if i, err := strconv.Atoi(value); err == nil {
            return i
        }
    }
    return fallback
}

func getEnvDuration(key string, fallback time.Duration) time.Duration {
    if value := os.Getenv(key); value != "" {
        if d, err := time.ParseDuration(value); err == nil {
            return d
        }
    }
    return fallback
}
```

### Struct Tags Config

```go
import "github.com/kelseyhightower/envconfig"

type Config struct {
    Port        int           `envconfig:"PORT" default:"8080"`
    DatabaseURL string        `envconfig:"DATABASE_URL" required:"true"`
    LogLevel    string        `envconfig:"LOG_LEVEL" default:"info"`
    Timeout     time.Duration `envconfig:"TIMEOUT" default:"30s"`
}

func Load() (*Config, error) {
    var cfg Config
    if err := envconfig.Process("", &cfg); err != nil {
        return nil, err
    }
    return &cfg, nil
}
```

## Build Patterns

### Version Information

```go
// main.go
package main

import (
    "fmt"
    "runtime"
)

// Set by -ldflags
var (
    version   = "dev"
    buildTime = "unknown"
    gitCommit = "unknown"
)

func printVersion() {
    fmt.Printf("Version:    %s\n", version)
    fmt.Printf("Build Time: %s\n", buildTime)
    fmt.Printf("Git Commit: %s\n", gitCommit)
    fmt.Printf("Go Version: %s\n", runtime.Version())
}
```

```makefile
# Makefile
VERSION := $(shell git describe --tags --always --dirty)
BUILD_TIME := $(shell date -u '+%Y-%m-%d_%H:%M:%S')
GIT_COMMIT := $(shell git rev-parse --short HEAD)

LDFLAGS := -ldflags "-X main.version=$(VERSION) -X main.buildTime=$(BUILD_TIME) -X main.gitCommit=$(GIT_COMMIT)"

build:
	go build $(LDFLAGS) -o bin/app ./cmd/api
```

### Multi-Platform Build

```makefile
# Build for multiple platforms
.PHONY: build-all
build-all:
	GOOS=linux GOARCH=amd64 go build -o bin/app-linux-amd64 ./cmd/api
	GOOS=linux GOARCH=arm64 go build -o bin/app-linux-arm64 ./cmd/api
	GOOS=darwin GOARCH=amd64 go build -o bin/app-darwin-amd64 ./cmd/api
	GOOS=darwin GOARCH=arm64 go build -o bin/app-darwin-arm64 ./cmd/api
	GOOS=windows GOARCH=amd64 go build -o bin/app-windows-amd64.exe ./cmd/api
```

## Dockerfile

### Multi-Stage Build

```dockerfile
# Build stage
FROM golang:1.22-alpine AS builder

WORKDIR /app

# Cache dependencies
COPY go.mod go.sum ./
RUN go mod download

# Build
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /app/bin/api ./cmd/api

# Runtime stage
FROM alpine:3.19

RUN apk --no-cache add ca-certificates tzdata

WORKDIR /app
COPY --from=builder /app/bin/api .

# Non-root user
RUN adduser -D -g '' appuser
USER appuser

EXPOSE 8080
ENTRYPOINT ["./api"]
```

### Distroless (Minimal)

```dockerfile
FROM golang:1.22 AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /api ./cmd/api

FROM gcr.io/distroless/static-debian12
COPY --from=builder /api /api
ENTRYPOINT ["/api"]
```

## Dependency Injection

### Wire (Google)

```go
// wire.go
//go:build wireinject

package main

import (
    "github.com/google/wire"
    "github.com/yourorg/myproject/internal/config"
    "github.com/yourorg/myproject/internal/repository"
    "github.com/yourorg/myproject/internal/service"
    "github.com/yourorg/myproject/internal/server"
)

func InitializeServer(cfg *config.Config) (*server.Server, error) {
    wire.Build(
        repository.NewPostgresUserRepo,
        service.NewUserService,
        server.NewServer,
    )
    return nil, nil
}
```

### Manual DI (Preferred for Small/Medium)

```go
// main.go
func main() {
    cfg := config.Load()

    // Build dependency graph
    db := database.Connect(cfg.DatabaseURL)
    defer db.Close()

    userRepo := repository.NewPostgresUserRepo(db)
    userService := service.NewUserService(userRepo)
    userHandler := handler.NewUserHandler(userService)

    srv := server.New(cfg, userHandler)
    srv.Run()
}
```

## Release Patterns

### Git Tagging

```bash
# Create annotated tag
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3

# Semantic versioning
# v1.0.0 - Initial release
# v1.1.0 - New features (backward compatible)
# v1.1.1 - Bug fixes
# v2.0.0 - Breaking changes
```

### GoReleaser

```yaml
# .goreleaser.yaml
version: 2

builds:
  - main: ./cmd/api
    binary: api
    env:
      - CGO_ENABLED=0
    goos:
      - linux
      - darwin
      - windows
    goarch:
      - amd64
      - arm64
    ldflags:
      - -s -w
      - -X main.version={{.Version}}
      - -X main.commit={{.Commit}}

archives:
  - format: tar.gz
    name_template: "{{ .ProjectName }}_{{ .Version }}_{{ .Os }}_{{ .Arch }}"

checksum:
  name_template: 'checksums.txt'

changelog:
  sort: asc
  filters:
    exclude:
      - '^docs:'
      - '^test:'
```

```bash
# Release
goreleaser release --clean
```
