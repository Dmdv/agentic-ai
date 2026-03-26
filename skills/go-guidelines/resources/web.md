# Go Web & API Patterns

HTTP servers, middleware, JSON handling, and structured logging.

## HTTP Server (Go 1.22+)

### Enhanced Routing (Go 1.22)

```go
mux := http.NewServeMux()

// Method + path pattern
mux.HandleFunc("GET /users", listUsers)
mux.HandleFunc("POST /users", createUser)
mux.HandleFunc("GET /users/{id}", getUser)
mux.HandleFunc("PUT /users/{id}", updateUser)
mux.HandleFunc("DELETE /users/{id}", deleteUser)

// Path parameters
func getUser(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id") // Go 1.22+ built-in
    // ...
}

// Wildcards
mux.HandleFunc("GET /files/{path...}", serveFile) // Matches rest of path
```

### Server Configuration

```go
func NewServer(cfg Config) *http.Server {
    mux := http.NewServeMux()
    registerRoutes(mux)

    return &http.Server{
        Addr:         cfg.Addr,
        Handler:      mux,
        ReadTimeout:  15 * time.Second,
        WriteTimeout: 15 * time.Second,
        IdleTimeout:  60 * time.Second,
    }
}

func main() {
    srv := NewServer(cfg)

    // Graceful shutdown
    go func() {
        sigCh := make(chan os.Signal, 1)
        signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
        <-sigCh

        ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
        defer cancel()

        srv.Shutdown(ctx)
    }()

    if err := srv.ListenAndServe(); err != http.ErrServerClosed {
        log.Fatal(err)
    }
}
```

## Middleware

### Middleware Pattern

```go
type Middleware func(http.Handler) http.Handler

func Chain(h http.Handler, middlewares ...Middleware) http.Handler {
    for i := len(middlewares) - 1; i >= 0; i-- {
        h = middlewares[i](h)
    }
    return h
}

// Usage
handler := Chain(
    mux,
    LoggingMiddleware(logger),
    RecoveryMiddleware,
    RequestIDMiddleware,
    AuthMiddleware(authService),
)
```

### Logging Middleware

```go
func LoggingMiddleware(logger *slog.Logger) Middleware {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            start := time.Now()

            // Wrap response writer to capture status
            wrapped := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}

            defer func() {
                logger.Info("request",
                    slog.String("method", r.Method),
                    slog.String("path", r.URL.Path),
                    slog.Int("status", wrapped.statusCode),
                    slog.Duration("duration", time.Since(start)),
                    slog.String("remote_addr", r.RemoteAddr),
                )
            }()

            next.ServeHTTP(wrapped, r)
        })
    }
}

type responseWriter struct {
    http.ResponseWriter
    statusCode int
}

func (rw *responseWriter) WriteHeader(code int) {
    rw.statusCode = code
    rw.ResponseWriter.WriteHeader(code)
}
```

### Recovery Middleware

```go
func RecoveryMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if err := recover(); err != nil {
                // Log the stack trace
                slog.Error("panic recovered",
                    slog.Any("error", err),
                    slog.String("stack", string(debug.Stack())),
                )

                http.Error(w, "Internal Server Error", http.StatusInternalServerError)
            }
        }()

        next.ServeHTTP(w, r)
    })
}
```

### Request ID Middleware

```go
type contextKey string

const RequestIDKey contextKey = "requestID"

func RequestIDMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        requestID := r.Header.Get("X-Request-ID")
        if requestID == "" {
            requestID = uuid.New().String()
        }

        ctx := context.WithValue(r.Context(), RequestIDKey, requestID)
        w.Header().Set("X-Request-ID", requestID)

        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

// Helper to get request ID
func GetRequestID(ctx context.Context) string {
    if id, ok := ctx.Value(RequestIDKey).(string); ok {
        return id
    }
    return ""
}
```

### Auth Middleware

```go
func AuthMiddleware(authService AuthService) Middleware {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            token := r.Header.Get("Authorization")
            if token == "" {
                http.Error(w, "Unauthorized", http.StatusUnauthorized)
                return
            }

            // Remove "Bearer " prefix
            token = strings.TrimPrefix(token, "Bearer ")

            user, err := authService.ValidateToken(r.Context(), token)
            if err != nil {
                http.Error(w, "Unauthorized", http.StatusUnauthorized)
                return
            }

            ctx := context.WithValue(r.Context(), UserKey, user)
            next.ServeHTTP(w, r.WithContext(ctx))
        })
    }
}
```

## JSON Handling

### Request/Response Types

```go
type CreateUserRequest struct {
    Name  string `json:"name" validate:"required,min=2"`
    Email string `json:"email" validate:"required,email"`
}

type UserResponse struct {
    ID        string    `json:"id"`
    Name      string    `json:"name"`
    Email     string    `json:"email"`
    CreatedAt time.Time `json:"created_at"`
}

type ErrorResponse struct {
    Error   string `json:"error"`
    Code    string `json:"code,omitempty"`
    Details any    `json:"details,omitempty"`
}
```

### JSON Helpers

```go
func WriteJSON(w http.ResponseWriter, status int, data any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    if err := json.NewEncoder(w).Encode(data); err != nil {
        slog.Error("failed to encode JSON response", slog.Any("error", err))
    }
}

func WriteError(w http.ResponseWriter, status int, message string) {
    WriteJSON(w, status, ErrorResponse{Error: message})
}

func ReadJSON[T any](r *http.Request) (T, error) {
    var v T

    // Limit body size
    r.Body = http.MaxBytesReader(nil, r.Body, 1<<20) // 1MB

    decoder := json.NewDecoder(r.Body)
    decoder.DisallowUnknownFields() // Strict parsing

    if err := decoder.Decode(&v); err != nil {
        return v, fmt.Errorf("invalid JSON: %w", err)
    }

    return v, nil
}
```

### Handler Example

```go
func (h *UserHandler) CreateUser(w http.ResponseWriter, r *http.Request) {
    req, err := ReadJSON[CreateUserRequest](r)
    if err != nil {
        WriteError(w, http.StatusBadRequest, err.Error())
        return
    }

    // Validate
    if err := h.validator.Struct(req); err != nil {
        WriteError(w, http.StatusBadRequest, "validation failed")
        return
    }

    user, err := h.service.CreateUser(r.Context(), req.Name, req.Email)
    if err != nil {
        if errors.Is(err, ErrEmailExists) {
            WriteError(w, http.StatusConflict, "email already exists")
            return
        }
        WriteError(w, http.StatusInternalServerError, "failed to create user")
        return
    }

    WriteJSON(w, http.StatusCreated, UserResponse{
        ID:        user.ID,
        Name:      user.Name,
        Email:     user.Email,
        CreatedAt: user.CreatedAt,
    })
}
```

## Structured Logging (slog - Go 1.21+)

### Setup

```go
func NewLogger(env string) *slog.Logger {
    var handler slog.Handler

    switch env {
    case "production":
        handler = slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
            Level: slog.LevelInfo,
        })
    default:
        handler = slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
            Level: slog.LevelDebug,
        })
    }

    return slog.New(handler)
}

// Set as default
slog.SetDefault(NewLogger(env))
```

### Logging Patterns

```go
// Basic logging
slog.Info("server started", slog.String("addr", addr))
slog.Error("failed to connect", slog.Any("error", err))

// With groups
slog.Info("request processed",
    slog.Group("request",
        slog.String("method", r.Method),
        slog.String("path", r.URL.Path),
    ),
    slog.Group("response",
        slog.Int("status", status),
        slog.Duration("latency", latency),
    ),
)

// Create child logger with default attributes
logger := slog.With(
    slog.String("service", "user-api"),
    slog.String("version", version),
)

// Request-scoped logger
reqLogger := logger.With(
    slog.String("request_id", requestID),
    slog.String("user_id", userID),
)
```

### Logger in Context

```go
type contextKey string

const LoggerKey contextKey = "logger"

func LoggerMiddleware(logger *slog.Logger) Middleware {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            requestID := GetRequestID(r.Context())

            reqLogger := logger.With(
                slog.String("request_id", requestID),
                slog.String("method", r.Method),
                slog.String("path", r.URL.Path),
            )

            ctx := context.WithValue(r.Context(), LoggerKey, reqLogger)
            next.ServeHTTP(w, r.WithContext(ctx))
        })
    }
}

func LoggerFromContext(ctx context.Context) *slog.Logger {
    if logger, ok := ctx.Value(LoggerKey).(*slog.Logger); ok {
        return logger
    }
    return slog.Default()
}
```

## HTTP Client

### Configured Client

```go
func NewHTTPClient() *http.Client {
    return &http.Client{
        Timeout: 30 * time.Second,
        Transport: &http.Transport{
            MaxIdleConns:        100,
            MaxIdleConnsPerHost: 10,
            IdleConnTimeout:     90 * time.Second,
        },
    }
}

// Always use context
func (c *APIClient) GetUser(ctx context.Context, id string) (*User, error) {
    req, err := http.NewRequestWithContext(ctx, "GET", c.baseURL+"/users/"+id, nil)
    if err != nil {
        return nil, fmt.Errorf("creating request: %w", err)
    }

    req.Header.Set("Authorization", "Bearer "+c.token)

    resp, err := c.client.Do(req)
    if err != nil {
        return nil, fmt.Errorf("executing request: %w", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("unexpected status: %d", resp.StatusCode)
    }

    var user User
    if err := json.NewDecoder(resp.Body).Decode(&user); err != nil {
        return nil, fmt.Errorf("decoding response: %w", err)
    }

    return &user, nil
}
```

### Retries with Backoff

```go
func WithRetry(client *http.Client, maxRetries int) *http.Client {
    return &http.Client{
        Transport: &retryTransport{
            base:       client.Transport,
            maxRetries: maxRetries,
        },
        Timeout: client.Timeout,
    }
}

type retryTransport struct {
    base       http.RoundTripper
    maxRetries int
}

func (t *retryTransport) RoundTrip(req *http.Request) (*http.Response, error) {
    var resp *http.Response
    var err error

    for i := 0; i <= t.maxRetries; i++ {
        resp, err = t.base.RoundTrip(req)
        if err != nil || resp.StatusCode >= 500 {
            if i < t.maxRetries {
                time.Sleep(time.Duration(i+1) * 100 * time.Millisecond)
                continue
            }
        }
        break
    }

    return resp, err
}
```

## Validation

### Using go-playground/validator

```go
import "github.com/go-playground/validator/v10"

var validate = validator.New()

type CreateUserRequest struct {
    Name     string `json:"name" validate:"required,min=2,max=100"`
    Email    string `json:"email" validate:"required,email"`
    Age      int    `json:"age" validate:"gte=18,lte=150"`
    Password string `json:"password" validate:"required,min=8"`
}

func (h *Handler) CreateUser(w http.ResponseWriter, r *http.Request) {
    var req CreateUserRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        WriteError(w, http.StatusBadRequest, "invalid JSON")
        return
    }

    if err := validate.Struct(req); err != nil {
        errs := err.(validator.ValidationErrors)
        WriteJSON(w, http.StatusBadRequest, ErrorResponse{
            Error:   "validation failed",
            Details: formatValidationErrors(errs),
        })
        return
    }

    // Process request...
}

func formatValidationErrors(errs validator.ValidationErrors) map[string]string {
    result := make(map[string]string)
    for _, e := range errs {
        result[e.Field()] = e.Tag()
    }
    return result
}
```

## Health Checks

```go
type HealthChecker interface {
    Check(ctx context.Context) error
}

func HealthHandler(checkers map[string]HealthChecker) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
        defer cancel()

        status := make(map[string]string)
        healthy := true

        for name, checker := range checkers {
            if err := checker.Check(ctx); err != nil {
                status[name] = fmt.Sprintf("unhealthy: %v", err)
                healthy = false
            } else {
                status[name] = "healthy"
            }
        }

        code := http.StatusOK
        if !healthy {
            code = http.StatusServiceUnavailable
        }

        WriteJSON(w, code, map[string]any{
            "status": status,
            "time":   time.Now().UTC(),
        })
    }
}
```
