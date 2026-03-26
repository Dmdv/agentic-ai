# Performance Optimization Guidelines

Guidelines for performance-critical Rust code.

**Source**: Microsoft Pragmatic Rust Guidelines - Performance Section

---

## Allocation

### Rule PERF-001: Avoid Unnecessary Allocations
Reuse buffers, use `with_capacity()`, prefer `&str` over `String`.

### Rule PERF-002: Profile Before Optimizing
Use `cargo bench` and profilers like `perf` or `flamegraph`.

---

## Iteration

### Rule PERF-003: Use Iterator Combinators
Iterator chains optimize better than manual loops.

```rust
// GOOD
let sum: i32 = data.iter().filter(|&&x| x > 0).sum();

// LESS OPTIMAL
let mut sum = 0;
for &x in data {
    if x > 0 {
        sum += x;
    }
}
```

---

**Guideline Version**: Microsoft Pragmatic Rust Guidelines 2025-2026
