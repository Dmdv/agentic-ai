# Go Testing Patterns

Comprehensive testing patterns using table-driven tests, testify, and mocking.

## Table-Driven Tests

### Basic Pattern

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive numbers", 2, 3, 5},
        {"negative numbers", -2, -3, -5},
        {"zero", 0, 0, 0},
        {"mixed signs", -2, 5, 3},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := Add(tt.a, tt.b)
            if result != tt.expected {
                t.Errorf("Add(%d, %d) = %d; want %d", tt.a, tt.b, result, tt.expected)
            }
        })
    }
}
```

### With Error Cases

```go
func TestDivide(t *testing.T) {
    tests := []struct {
        name      string
        dividend  int
        divisor   int
        expected  int
        wantErr   bool
        errType   error
    }{
        {"valid division", 10, 2, 5, false, nil},
        {"division by zero", 10, 0, 0, true, ErrDivisionByZero},
        {"negative result", -10, 2, -5, false, nil},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result, err := Divide(tt.dividend, tt.divisor)

            if tt.wantErr {
                if err == nil {
                    t.Errorf("expected error, got nil")
                    return
                }
                if tt.errType != nil && !errors.Is(err, tt.errType) {
                    t.Errorf("expected error %v, got %v", tt.errType, err)
                }
                return
            }

            if err != nil {
                t.Errorf("unexpected error: %v", err)
                return
            }

            if result != tt.expected {
                t.Errorf("got %d; want %d", result, tt.expected)
            }
        })
    }
}
```

## Testify Library

### require vs assert

```go
import (
    "testing"
    "github.com/stretchr/testify/require"
    "github.com/stretchr/testify/assert"
)

func TestUserService(t *testing.T) {
    // Use require for setup/preconditions - stops on failure
    svc, err := NewService(config)
    require.NoError(t, err, "service creation must succeed")
    require.NotNil(t, svc)

    // Use assert for actual test assertions - continues on failure
    user, err := svc.GetUser(ctx, "user-123")
    assert.NoError(t, err)
    assert.Equal(t, "John", user.Name)
    assert.Equal(t, "john@example.com", user.Email)
}

// Rule: Use require 99% of the time
// Only use assert when you want to see ALL failures at once
```

### Common Assertions

```go
func TestAssertions(t *testing.T) {
    // Equality
    require.Equal(t, expected, actual)
    require.NotEqual(t, unexpected, actual)

    // Nil checks
    require.Nil(t, val)
    require.NotNil(t, val)

    // Boolean
    require.True(t, condition)
    require.False(t, condition)

    // Errors
    require.NoError(t, err)
    require.Error(t, err)
    require.ErrorIs(t, err, ErrNotFound)
    require.ErrorContains(t, err, "not found")

    // Collections
    require.Len(t, slice, 3)
    require.Empty(t, slice)
    require.Contains(t, slice, element)
    require.ElementsMatch(t, expected, actual) // Order independent

    // Strings
    require.Contains(t, str, substring)
    require.Regexp(t, pattern, str)

    // Types
    require.IsType(t, &User{}, val)

    // Panics
    require.Panics(t, func() { panicFunc() })
    require.NotPanics(t, func() { safeFunc() })

    // Eventually (for async)
    require.Eventually(t, func() bool {
        return checkCondition()
    }, 5*time.Second, 100*time.Millisecond)
}
```

## Mocking

### Interface-Based Mocking

```go
// Define interface at point of use
type UserStore interface {
    GetUser(ctx context.Context, id string) (*User, error)
    SaveUser(ctx context.Context, user *User) error
}

// Manual mock
type MockUserStore struct {
    GetUserFunc func(ctx context.Context, id string) (*User, error)
    SaveUserFunc func(ctx context.Context, user *User) error
}

func (m *MockUserStore) GetUser(ctx context.Context, id string) (*User, error) {
    return m.GetUserFunc(ctx, id)
}

func (m *MockUserStore) SaveUser(ctx context.Context, user *User) error {
    return m.SaveUserFunc(ctx, user)
}

// Usage in tests
func TestService_GetUser(t *testing.T) {
    expectedUser := &User{ID: "123", Name: "John"}

    store := &MockUserStore{
        GetUserFunc: func(ctx context.Context, id string) (*User, error) {
            require.Equal(t, "123", id)
            return expectedUser, nil
        },
    }

    svc := NewService(store)
    user, err := svc.GetUser(context.Background(), "123")

    require.NoError(t, err)
    require.Equal(t, expectedUser, user)
}
```

### Using Mockery

```go
// Generate mocks: mockery --all --dir=internal --output=internal/mocks

//go:generate mockery --name=UserStore --output=./mocks --outpkg=mocks

// In tests
func TestService_CreateUser(t *testing.T) {
    mockStore := mocks.NewUserStore(t)

    // Set expectations
    mockStore.EXPECT().
        SaveUser(mock.Anything, mock.MatchedBy(func(u *User) bool {
            return u.Name == "John"
        })).
        Return(nil).
        Once()

    svc := NewService(mockStore)
    err := svc.CreateUser(context.Background(), "John", "john@example.com")

    require.NoError(t, err)
    mockStore.AssertExpectations(t)
}
```

### testify/mock

```go
import "github.com/stretchr/testify/mock"

type MockUserStore struct {
    mock.Mock
}

func (m *MockUserStore) GetUser(ctx context.Context, id string) (*User, error) {
    args := m.Called(ctx, id)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*User), args.Error(1)
}

func TestWithMock(t *testing.T) {
    mockStore := new(MockUserStore)

    // Setup expectations
    mockStore.On("GetUser", mock.Anything, "123").
        Return(&User{ID: "123", Name: "John"}, nil)

    svc := NewService(mockStore)
    user, err := svc.GetUser(context.Background(), "123")

    require.NoError(t, err)
    require.Equal(t, "John", user.Name)

    mockStore.AssertExpectations(t)
    mockStore.AssertCalled(t, "GetUser", mock.Anything, "123")
}
```

## Test Fixtures

### Setup and Teardown

```go
func TestMain(m *testing.M) {
    // Global setup
    setup()

    code := m.Run()

    // Global teardown
    teardown()

    os.Exit(code)
}

// Per-test setup with t.Cleanup
func TestWithCleanup(t *testing.T) {
    // Setup
    tmpDir := t.TempDir() // Automatically cleaned up
    file := createTempFile(t, tmpDir)

    t.Cleanup(func() {
        // Any additional cleanup
        os.Remove(file)
    })

    // Test
    // ...
}
```

### Test Suites (testify/suite)

```go
import "github.com/stretchr/testify/suite"

type UserServiceSuite struct {
    suite.Suite
    store   *MockUserStore
    service *UserService
}

func (s *UserServiceSuite) SetupTest() {
    s.store = new(MockUserStore)
    s.service = NewUserService(s.store)
}

func (s *UserServiceSuite) TearDownTest() {
    // Cleanup after each test
}

func (s *UserServiceSuite) TestGetUser() {
    s.store.On("GetUser", mock.Anything, "123").
        Return(&User{ID: "123"}, nil)

    user, err := s.service.GetUser(context.Background(), "123")

    s.Require().NoError(err)
    s.Equal("123", user.ID)
}

func TestUserServiceSuite(t *testing.T) {
    suite.Run(t, new(UserServiceSuite))
}
```

## Benchmarking

### Basic Benchmarks

```go
func BenchmarkProcess(b *testing.B) {
    // Setup (not timed)
    data := generateTestData()

    b.ResetTimer() // Reset timer after setup

    for i := 0; i < b.N; i++ {
        Process(data)
    }
}

// With allocations reporting
func BenchmarkProcessAllocs(b *testing.B) {
    data := generateTestData()
    b.ResetTimer()
    b.ReportAllocs()

    for i := 0; i < b.N; i++ {
        Process(data)
    }
}
```

### Parallel Benchmarks

```go
func BenchmarkParallel(b *testing.B) {
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            Process()
        }
    })
}
```

### Sub-Benchmarks

```go
func BenchmarkSizes(b *testing.B) {
    sizes := []int{100, 1000, 10000}

    for _, size := range sizes {
        b.Run(fmt.Sprintf("size-%d", size), func(b *testing.B) {
            data := make([]int, size)
            b.ResetTimer()

            for i := 0; i < b.N; i++ {
                Process(data)
            }
        })
    }
}
```

## Testing Best Practices

### Test File Organization

```
package/
├── user.go
├── user_test.go          # Unit tests
├── user_integration_test.go  # Integration tests (use build tag)
└── testdata/             # Test fixtures
    ├── valid_user.json
    └── invalid_user.json
```

### Build Tags for Test Types

```go
//go:build integration
// +build integration

package user_test

func TestIntegration_Database(t *testing.T) {
    // Run with: go test -tags=integration ./...
}
```

### Test Helpers

```go
// Helper function
func setupTestDB(t *testing.T) *sql.DB {
    t.Helper() // Marks this as a helper

    db, err := sql.Open("postgres", testDSN)
    require.NoError(t, err)

    t.Cleanup(func() {
        db.Close()
    })

    return db
}

// Custom assertion
func assertUserEqual(t *testing.T, expected, actual *User) {
    t.Helper()

    require.Equal(t, expected.ID, actual.ID, "ID mismatch")
    require.Equal(t, expected.Name, actual.Name, "Name mismatch")
    require.Equal(t, expected.Email, actual.Email, "Email mismatch")
}
```

### Golden Files

```go
func TestRender(t *testing.T) {
    result := Render(input)

    golden := filepath.Join("testdata", t.Name()+".golden")

    if *update {
        os.WriteFile(golden, []byte(result), 0644)
    }

    expected, err := os.ReadFile(golden)
    require.NoError(t, err)
    require.Equal(t, string(expected), result)
}

// Run with: go test -update to update golden files
var update = flag.Bool("update", false, "update golden files")
```

### HTTP Handler Testing

```go
func TestHandler(t *testing.T) {
    handler := NewUserHandler(mockStore)

    req := httptest.NewRequest("GET", "/users/123", nil)
    rec := httptest.NewRecorder()

    handler.ServeHTTP(rec, req)

    require.Equal(t, http.StatusOK, rec.Code)

    var user User
    err := json.NewDecoder(rec.Body).Decode(&user)
    require.NoError(t, err)
    require.Equal(t, "123", user.ID)
}
```

## Fuzz Testing (Go 1.18+)

### Basic Fuzz Test

```go
func FuzzParseJSON(f *testing.F) {
    // Add seed corpus
    f.Add([]byte(`{"name": "test"}`))
    f.Add([]byte(`{}`))
    f.Add([]byte(`[]`))

    f.Fuzz(func(t *testing.T, data []byte) {
        var result map[string]any
        err := json.Unmarshal(data, &result)
        if err != nil {
            return // Invalid JSON is expected
        }

        // Re-marshal and verify round-trip
        _, err = json.Marshal(result)
        if err != nil {
            t.Errorf("failed to re-marshal: %v", err)
        }
    })
}
```

### Running Fuzz Tests

```bash
# Run for 30 seconds
go test -fuzz=FuzzParseJSON -fuzztime=30s ./...

# Run until failure or interrupt
go test -fuzz=FuzzParseJSON ./...

# Run with specific corpus
go test -fuzz=FuzzParseJSON -fuzzdir=testdata/fuzz ./...
```

### Fuzz Test Best Practices

```go
// Use seed corpus from real-world data
f.Add(realWorldInput1)
f.Add(realWorldInput2)

// Test for crashes, not specific behavior
f.Fuzz(func(t *testing.T, input string) {
    _ = Parse(input) // Just don't panic
})

// Test invariants
f.Fuzz(func(t *testing.T, data []byte) {
    encoded := Encode(data)
    decoded := Decode(encoded)
    if !bytes.Equal(data, decoded) {
        t.Errorf("round-trip failed")
    }
})
```

## Running Tests

```bash
# Basic
go test ./...

# Verbose
go test -v ./...

# With race detection (ALWAYS use in CI)
go test -race ./...

# With coverage
go test -cover ./...
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out

# Specific test
go test -run TestUserService ./...
go test -run TestUserService/TestGetUser ./...

# Benchmarks
go test -bench=. ./...
go test -bench=BenchmarkProcess -benchmem ./...

# Short tests only
go test -short ./...

# With timeout
go test -timeout 30s ./...

# Integration tests
go test -tags=integration ./...
```
