# Go Concurrency Patterns

Safe and idiomatic concurrency with goroutines, channels, and context.

## Go Proverbs for Concurrency

> "Don't communicate by sharing memory, share memory by communicating."
> "Concurrency is not parallelism."
> "Channels orchestrate; mutexes serialize."

## Goroutines

### Basic Goroutine

```go
// Start a goroutine
go func() {
    // Do work
}()

// NEVER start goroutines without a way to stop them
// ALWAYS have a cancellation mechanism
```

### Goroutine Lifecycle Management

```go
// WITH cancellation via context
func worker(ctx context.Context) {
    for {
        select {
        case <-ctx.Done():
            return // Clean exit
        default:
            doWork()
        }
    }
}

// Usage
ctx, cancel := context.WithCancel(context.Background())
go worker(ctx)
// Later...
cancel() // Stop the worker
```

## Channels

### Channel Types

```go
// Unbuffered (synchronous)
ch := make(chan int)

// Buffered
ch := make(chan int, 100)

// Receive-only (use in function params)
func consume(ch <-chan int)

// Send-only (use in function params)
func produce(ch chan<- int)
```

### Channel Patterns

```go
// Generator pattern
func generate(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            out <- n
        }
    }()
    return out
}

// Pipeline pattern
func square(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            out <- n * n
        }
    }()
    return out
}

// Usage
nums := generate(1, 2, 3, 4)
squared := square(nums)
for n := range squared {
    fmt.Println(n)
}
```

### Fan-Out / Fan-In

```go
// Fan-out: start multiple goroutines reading from same channel
func fanOut(in <-chan int, workers int) []<-chan int {
    channels := make([]<-chan int, workers)
    for i := 0; i < workers; i++ {
        channels[i] = worker(in)
    }
    return channels
}

// Fan-in: merge multiple channels into one
func fanIn(channels ...<-chan int) <-chan int {
    out := make(chan int)
    var wg sync.WaitGroup

    for _, ch := range channels {
        wg.Add(1)
        go func(c <-chan int) {
            defer wg.Done()
            for v := range c {
                out <- v
            }
        }(ch)
    }

    go func() {
        wg.Wait()
        close(out)
    }()

    return out
}
```

### Select Statement

```go
// Non-blocking with default
select {
case msg := <-ch:
    process(msg)
default:
    // Channel empty, do something else
}

// Multiple channels with timeout
select {
case msg := <-ch1:
    handle(msg)
case msg := <-ch2:
    handle(msg)
case <-time.After(5 * time.Second):
    return errors.New("timeout")
case <-ctx.Done():
    return ctx.Err()
}

// Nil channel trick (disable case)
var ch1, ch2 <-chan int
if condition {
    ch1 = realChannel1
}
select {
case v := <-ch1: // Only active if ch1 != nil
    process(v)
case v := <-ch2:
    process(v)
}
```

## Context

### Context Propagation

```go
// ALWAYS pass context as first parameter
func DoWork(ctx context.Context, id string) error {
    // Check cancellation at the start
    if err := ctx.Err(); err != nil {
        return err
    }

    // Pass context to downstream calls
    result, err := s.store.Get(ctx, id)
    if err != nil {
        return err
    }

    return s.process(ctx, result)
}

// NEVER store context in structs
type Bad struct {
    ctx context.Context // WRONG
}

// NEVER use context.Background() in library code
// Always accept context from caller
```

### Context with Cancel

```go
// Create cancellable context
ctx, cancel := context.WithCancel(context.Background())
defer cancel() // Always call cancel to release resources

go func() {
    <-stopSignal
    cancel()
}()

// Check for cancellation in loops
for {
    select {
    case <-ctx.Done():
        return ctx.Err()
    default:
        doIteration()
    }
}
```

### Context with Timeout/Deadline

```go
// With timeout
ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
defer cancel()

result, err := slowOperation(ctx)
if errors.Is(err, context.DeadlineExceeded) {
    // Handle timeout
}

// With deadline
deadline := time.Now().Add(10 * time.Second)
ctx, cancel := context.WithDeadline(ctx, deadline)
defer cancel()
```

### Context Values (Use Sparingly)

```go
// Define typed keys to avoid collisions
type contextKey string

const (
    requestIDKey contextKey = "requestID"
    userIDKey    contextKey = "userID"
)

// Set value
ctx := context.WithValue(ctx, requestIDKey, "req-123")

// Get value
if reqID, ok := ctx.Value(requestIDKey).(string); ok {
    // Use reqID
}

// ONLY use for request-scoped data (trace IDs, auth tokens)
// NEVER use for optional parameters
```

## errgroup

### Coordinated Goroutines

```go
import "golang.org/x/sync/errgroup"

func processItems(ctx context.Context, items []Item) error {
    g, ctx := errgroup.WithContext(ctx)

    for _, item := range items {
        item := item // Not needed in Go 1.22+
        g.Go(func() error {
            return process(ctx, item)
        })
    }

    // Wait for all goroutines
    // Returns first error (and cancels others via ctx)
    return g.Wait()
}
```

### With Concurrency Limit

```go
func processItemsLimited(ctx context.Context, items []Item) error {
    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(10) // Max 10 concurrent goroutines

    for _, item := range items {
        item := item
        g.Go(func() error {
            return process(ctx, item)
        })
    }

    return g.Wait()
}
```

### Parallel Tasks

```go
func fetchAll(ctx context.Context) (*Result, error) {
    g, ctx := errgroup.WithContext(ctx)

    var users []User
    var orders []Order
    var products []Product

    g.Go(func() error {
        var err error
        users, err = fetchUsers(ctx)
        return err
    })

    g.Go(func() error {
        var err error
        orders, err = fetchOrders(ctx)
        return err
    })

    g.Go(func() error {
        var err error
        products, err = fetchProducts(ctx)
        return err
    })

    if err := g.Wait(); err != nil {
        return nil, err
    }

    return &Result{users, orders, products}, nil
}
```

## sync Package

### Mutex

```go
type Counter struct {
    mu    sync.Mutex
    value int
}

func (c *Counter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.value++
}

func (c *Counter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.value
}
```

### RWMutex

```go
type Cache struct {
    mu    sync.RWMutex
    items map[string]Item
}

func (c *Cache) Get(key string) (Item, bool) {
    c.mu.RLock() // Multiple readers allowed
    defer c.mu.RUnlock()
    item, ok := c.items[key]
    return item, ok
}

func (c *Cache) Set(key string, item Item) {
    c.mu.Lock() // Exclusive writer
    defer c.mu.Unlock()
    c.items[key] = item
}
```

### WaitGroup

```go
func processAll(items []Item) {
    var wg sync.WaitGroup

    for _, item := range items {
        wg.Add(1)
        go func(item Item) {
            defer wg.Done()
            process(item)
        }(item)
    }

    wg.Wait() // Block until all done
}
```

### Once

```go
var (
    instance *Singleton
    once     sync.Once
)

func GetInstance() *Singleton {
    once.Do(func() {
        instance = &Singleton{}
        instance.init()
    })
    return instance
}
```

### Atomic Types (Go 1.19+)

```go
import "sync/atomic"

// Typed atomic values - safer than atomic.AddInt64, etc.
var (
    counter atomic.Int64
    enabled atomic.Bool
    config  atomic.Pointer[Config]
)

func increment() {
    counter.Add(1)
}

func getValue() int64 {
    return counter.Load()
}

func toggle() {
    enabled.Store(!enabled.Load())
}

func updateConfig(c *Config) {
    config.Store(c)
}

func getConfig() *Config {
    return config.Load()
}

// Compare-and-swap
func trySetOnce(value int64) bool {
    return counter.CompareAndSwap(0, value)
}
```

### Pool

```go
var bufPool = sync.Pool{
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}

func process(data []byte) {
    buf := bufPool.Get().(*bytes.Buffer)
    defer func() {
        buf.Reset()
        bufPool.Put(buf)
    }()

    buf.Write(data)
    // Use buf...
}
```

## Worker Pool Pattern

```go
type Job struct {
    ID   int
    Data string
}

type Result struct {
    JobID  int
    Output string
    Error  error
}

func workerPool(ctx context.Context, jobs <-chan Job, results chan<- Result, workers int) {
    var wg sync.WaitGroup

    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for {
                select {
                case <-ctx.Done():
                    return
                case job, ok := <-jobs:
                    if !ok {
                        return
                    }
                    output, err := process(ctx, job)
                    results <- Result{
                        JobID:  job.ID,
                        Output: output,
                        Error:  err,
                    }
                }
            }
        }()
    }

    wg.Wait()
    close(results)
}
```

## Semaphore Pattern

```go
import "golang.org/x/sync/semaphore"

func processWithLimit(ctx context.Context, items []Item) error {
    sem := semaphore.NewWeighted(10) // Max 10 concurrent

    var wg sync.WaitGroup
    var firstErr error
    var errOnce sync.Once

    for _, item := range items {
        if err := sem.Acquire(ctx, 1); err != nil {
            return err
        }

        wg.Add(1)
        go func(item Item) {
            defer wg.Done()
            defer sem.Release(1)

            if err := process(ctx, item); err != nil {
                errOnce.Do(func() {
                    firstErr = err
                })
            }
        }(item)
    }

    wg.Wait()
    return firstErr
}
```

## Common Mistakes

### Goroutine Leaks

```go
// WRONG: goroutine leaks if timeout
func bad(ctx context.Context) error {
    ch := make(chan result)
    go func() {
        ch <- doExpensiveWork() // Blocks forever if no one reads
    }()

    select {
    case r := <-ch:
        return r.err
    case <-ctx.Done():
        return ctx.Err() // Goroutine leaks!
    }
}

// CORRECT: buffered channel or cleanup
func good(ctx context.Context) error {
    ch := make(chan result, 1) // Buffered - won't block
    go func() {
        ch <- doExpensiveWork()
    }()

    select {
    case r := <-ch:
        return r.err
    case <-ctx.Done():
        return ctx.Err()
    }
}
```

### Data Race

```go
// WRONG: data race
func bad() {
    var count int
    for i := 0; i < 1000; i++ {
        go func() {
            count++ // Race condition!
        }()
    }
}

// CORRECT: use atomic or mutex
func good() {
    var count atomic.Int64
    for i := 0; i < 1000; i++ {
        go func() {
            count.Add(1)
        }()
    }
}
```

### Loop Variable Capture (Pre-Go 1.22)

```go
// Before Go 1.22 - WRONG
for _, item := range items {
    go func() {
        process(item) // All goroutines see last item!
    }()
}

// Before Go 1.22 - CORRECT
for _, item := range items {
    item := item // Shadow variable
    go func() {
        process(item)
    }()
}

// Go 1.22+ - Fixed automatically
for _, item := range items {
    go func() {
        process(item) // Safe now
    }()
}
```

## Race Detection

```bash
# Always run tests with race detector
go test -race ./...

# Run binary with race detector
go run -race main.go
go build -race -o app ./cmd/app
```
