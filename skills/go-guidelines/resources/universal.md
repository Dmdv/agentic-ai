# Universal Go Patterns

Core patterns that apply to ALL Go code regardless of domain.

## Error Handling

### Always Wrap Errors with Context

```go
// ALWAYS wrap errors with context
if err != nil {
    return fmt.Errorf("failed to process user %s: %w", userID, err)
}

// Use errors.Is for sentinel errors
if errors.Is(err, ErrNotFound) {
    return nil // Expected case
}

// Use errors.As for typed errors
var pathErr *os.PathError
if errors.As(err, &pathErr) {
    log.Printf("path error on %s: %v", pathErr.Path, pathErr.Err)
}
```

### Custom Error Types

```go
// Sentinel errors (simple cases)
var (
    ErrNotFound     = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
)

// Typed errors (with context)
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation error on %s: %s", e.Field, e.Message)
}

// Usage
return &ValidationError{Field: "email", Message: "invalid format"}
```

### Error Handling Patterns

```go
// Handle or return - never ignore
result, err := doSomething()
if err != nil {
    return fmt.Errorf("doing something: %w", err)
}

// Early return on error
if err := validate(input); err != nil {
    return fmt.Errorf("validation failed: %w", err)
}

// NEVER ignore errors
result, _ := doSomething() // WRONG - silent failure

// Defer with error handling
defer func() {
    if cerr := file.Close(); cerr != nil && err == nil {
        err = cerr
    }
}()
```

## Interface Design

### Accept Interfaces, Return Structs

```go
// Define interface where it's used (consumer side)
type UserStore interface {
    GetUser(ctx context.Context, id string) (*User, error)
    SaveUser(ctx context.Context, user *User) error
}

// Accept interface, return concrete struct
func NewService(store UserStore) *Service {
    return &Service{store: store}
}

// Implementation doesn't declare it implements interface
type PostgresUserStore struct {
    db *sql.DB
}

func (s *PostgresUserStore) GetUser(ctx context.Context, id string) (*User, error) {
    // Implementation
}
```

### Small, Focused Interfaces

```go
// Single-method interfaces (most powerful)
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

// Compose when needed
type ReadWriter interface {
    Reader
    Writer
}

// 1-3 methods is ideal
type UserGetter interface {
    GetUser(ctx context.Context, id string) (*User, error)
}

// Avoid kitchen-sink interfaces
type UserStore interface {
    GetUser(...)
    SaveUser(...)
    // Keep it small - split if growing
}
```

## Generics (Go 1.18+)

### Type Constraints

```go
// Built-in constraints
import "golang.org/x/exp/constraints"

func Min[T constraints.Ordered](a, b T) T {
    if a < b {
        return a
    }
    return b
}

// Custom constraint
type Number interface {
    ~int | ~int64 | ~float64
}

func Sum[T Number](values []T) T {
    var total T
    for _, v := range values {
        total += v
    }
    return total
}
```

### Generic Data Structures

```go
// Generic result type
type Result[T any] struct {
    Value T
    Error error
}

func NewResult[T any](value T, err error) Result[T] {
    return Result[T]{Value: value, Error: err}
}

// Generic slice operations
func Filter[T any](slice []T, predicate func(T) bool) []T {
    result := make([]T, 0, len(slice))
    for _, v := range slice {
        if predicate(v) {
            result = append(result, v)
        }
    }
    return result
}

func Map[T, U any](slice []T, mapper func(T) U) []U {
    result := make([]U, len(slice))
    for i, v := range slice {
        result[i] = mapper(v)
    }
    return result
}
```

### When to Use Generics

```go
// USE generics for:
// - Container types (slices, maps, sets)
// - Utility functions (min, max, filter, map)
// - Type-safe builders and factories

// AVOID generics for:
// - Everything else (interfaces are often better)
// - When interface{} with type assertions works fine
// - Business logic (usually not generic)
```

## Struct Design

### Constructor Functions

```go
// Use New* constructor pattern
func NewService(store UserStore, logger *slog.Logger) *Service {
    return &Service{
        store:  store,
        logger: logger,
    }
}

// With options pattern for complex initialization
type ServiceOption func(*Service)

func WithTimeout(d time.Duration) ServiceOption {
    return func(s *Service) {
        s.timeout = d
    }
}

func WithRetries(n int) ServiceOption {
    return func(s *Service) {
        s.retries = n
    }
}

func NewService(store UserStore, opts ...ServiceOption) *Service {
    s := &Service{
        store:   store,
        timeout: 30 * time.Second, // defaults
        retries: 3,
    }
    for _, opt := range opts {
        opt(s)
    }
    return s
}

// Usage
svc := NewService(store, WithTimeout(10*time.Second), WithRetries(5))
```

### Embedding for Composition

```go
// Embed for code reuse
type BaseHandler struct {
    logger *slog.Logger
}

func (h *BaseHandler) LogRequest(r *http.Request) {
    h.logger.Info("request", "method", r.Method, "path", r.URL.Path)
}

type UserHandler struct {
    BaseHandler // Embedded
    store UserStore
}

// UserHandler now has LogRequest method
```

### Zero Value Design

```go
// Design structs with useful zero values
type Counter struct {
    mu    sync.Mutex
    value int // zero value is 0, which is correct
}

func (c *Counter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.value++
}

// sync.Mutex zero value is unlocked mutex - ready to use
// bytes.Buffer zero value is empty buffer - ready to use

// When zero value isn't useful, require constructor
type Server struct {
    addr string // required
    // ...
}

func NewServer(addr string) *Server {
    return &Server{addr: addr}
}
```

## Naming Conventions

### Package Names

```go
// Short, lowercase, no underscores
package user     // Good
package userdb   // Good
package user_db  // Wrong
package userDB   // Wrong

// Avoid stutter
user.User      // Acceptable (package.Type)
user.UserStore // Avoid (user.Store is better)
```

### Variable Names

```go
// Short names for local variables
for i, v := range items { }
for k, v := range mapping { }

// Descriptive for exported fields
type Config struct {
    MaxConnections int      // Clear
    ConnTimeout    Duration // Abbreviated but clear
}

// Receivers are single letter or short
func (s *Service) Method() {}
func (uh *UserHandler) Handle() {} // Avoid - too long
func (h *UserHandler) Handle() {}  // Better
```

### Method Names

```go
// Getters don't use Get prefix
func (u *User) Name() string     // Good
func (u *User) GetName() string  // Wrong

// Conversion methods
func (t Time) String() string    // To string
func (t Time) MarshalJSON() ...  // To JSON

// Setters use Set prefix
func (u *User) SetName(name string)
```

## Constants and Enums

### Iota for Enums

```go
type Status int

const (
    StatusPending Status = iota
    StatusActive
    StatusClosed
)

// With explicit values
const (
    KB = 1 << (10 * iota)
    MB
    GB
    TB
)

// String method for debugging
func (s Status) String() string {
    switch s {
    case StatusPending:
        return "pending"
    case StatusActive:
        return "active"
    case StatusClosed:
        return "closed"
    default:
        return fmt.Sprintf("Status(%d)", s)
    }
}
```

### Constants Groups

```go
// Group related constants
const (
    DefaultTimeout = 30 * time.Second
    MaxRetries     = 3
    BufferSize     = 4096
)
```

## Memory and Performance

### Preallocate Slices

```go
// When size is known
items := make([]Item, 0, len(source))
for _, s := range source {
    items = append(items, transform(s))
}

// Maps too
m := make(map[string]int, expectedSize)
```

### String Building

```go
// Use strings.Builder for many concatenations
var b strings.Builder
b.Grow(expectedSize) // Optional: preallocate
for _, s := range parts {
    b.WriteString(s)
}
result := b.String()

// For simple cases, strings.Join
result := strings.Join(parts, ",")

// Avoid repeated concatenation
s := ""
for _, p := range parts {
    s += p // SLOW - creates new string each time
}
```

### Avoid Allocations

```go
// Reuse buffers with sync.Pool
var bufPool = sync.Pool{
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}

func process() {
    buf := bufPool.Get().(*bytes.Buffer)
    defer func() {
        buf.Reset()
        bufPool.Put(buf)
    }()
    // Use buf
}

// Use pointers for large structs in range
for i := range largeItems {
    item := &largeItems[i] // Pointer, no copy
    process(item)
}
```

## Documentation

### Package Comments

```go
// Package user provides user management functionality.
//
// It handles user creation, authentication, and profile management.
// See the Service type for the main entry point.
package user
```

### Function Comments

```go
// GetUser retrieves a user by ID.
// It returns ErrNotFound if the user doesn't exist.
func (s *Service) GetUser(ctx context.Context, id string) (*User, error) {
    // ...
}
```

### Example Functions

```go
func ExampleService_GetUser() {
    ctx := context.Background()
    svc := NewService(store)

    user, err := svc.GetUser(ctx, "user-123")
    if err != nil {
        log.Fatal(err)
    }

    fmt.Println(user.Name)
    // Output: John Doe
}
```
