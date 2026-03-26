# Universal Rust Guidelines

Foundation principles that apply to ALL Rust code, regardless of context.

**Source**: Microsoft Pragmatic Rust Guidelines - Universal Section

---

## Core Principles

### 1. Embrace Ownership and Borrowing
- Let the type system prevent bugs at compile time
- Prefer owned types over references where ownership is clear
- Use borrowing to enable multiple readers or temporary mutations

### 2. Zero-Cost Abstractions
- Abstractions should compile to code as efficient as hand-written alternatives
- Prefer iterators over manual loops (compiler optimizes better)
- Use generics instead of dynamic dispatch when performance matters

### 3. Make Illegal States Unrepresentable
- Use type system to encode invariants
- Prefer enums over booleans for state
- Use newtypes to prevent mixing incompatible values

---

## Error Handling (U-ERR)

### Rule U-ERR-001: Public Functions Return Result
**Requirement**: All public functions that can fail MUST return `Result<T, E>`
**Exceptions**: None
**Validation**: Check all `pub fn` signatures

```rust
// WRONG
pub fn parse(input: &str) -> Data {
    input.parse().unwrap()  // Panic on invalid input
}

// CORRECT
pub fn parse(input: &str) -> Result<Data, ParseError> {
    input.parse().map_err(ParseError::InvalidFormat)
}
```

### Rule U-ERR-002: Use thiserror for Error Types
**Requirement**: Custom error types MUST implement `std::error::Error`
**Preferred**: Use `thiserror` crate for derive macro
**Validation**: Check error type implements trait

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ParseError {
    #[error("invalid format: {0}")]
    InvalidFormat(String),

    #[error("I/O error")]
    Io(#[from] std::io::Error),
}
```

### Rule U-ERR-003: Provide Context
**Requirement**: Errors MUST provide meaningful context
**Anti-pattern**: Generic error messages
**Validation**: Check error variants include context fields

```rust
// WRONG
#[error("operation failed")]
OperationFailed,

// CORRECT
#[error("failed to process {file}: {reason}")]
OperationFailed { file: String, reason: String },
```

### Rule U-ERR-004: Never unwrap() in Production
**Requirement**: Avoid `unwrap()`, `expect()`, `panic!()` in production paths
**Exceptions**: Test code, example code, genuinely unreachable code with proof
**Validation**: `grep -n 'unwrap\|expect\|panic!' src/`

```rust
// WRONG - panics on None
let value = map.get(&key).unwrap();

// CORRECT - propagates error
let value = map.get(&key).ok_or(Error::KeyNotFound)?;
```

---

## Type Safety (U-TYPE)

### Rule U-TYPE-001: Invalid States Unrepresentable
**Requirement**: Use type system to prevent invalid states
**Pattern**: Enums for exclusive states, newtypes for constraints

```rust
// WRONG - can be in invalid state
struct Connection {
    socket: Option<TcpStream>,
    is_connected: bool,  // Can be true with socket = None!
}

// CORRECT - impossible to be in invalid state
enum Connection {
    Disconnected,
    Connected(TcpStream),
}
```

### Rule U-TYPE-002: Newtype Pattern for Validation
**Requirement**: Wrap primitive types that have invariants
**Validation**: Check domain types aren't bare primitives

```rust
// WRONG - easy to mix up
fn transfer(from: u64, to: u64, amount: u64) { }

// CORRECT - type-safe, can't mix account ID with amount
#[derive(Debug, Clone, Copy)]
struct AccountId(u64);

#[derive(Debug, Clone, Copy)]
struct Amount(u64);

fn transfer(from: AccountId, to: AccountId, amount: Amount) { }
```

---

## Memory Safety (U-MEM)

### Rule U-MEM-001: Minimize Unsafe Code
**Requirement**: Avoid `unsafe` unless absolutely necessary
**Documentation**: All `unsafe` blocks MUST have safety comment
**Validation**: Check all `unsafe` has `// SAFETY:` comment

```rust
// WRONG - no safety justification
unsafe {
    *ptr = value;
}

// CORRECT - documents safety invariant
// SAFETY: ptr is valid and aligned because we just allocated it
// with Layout::new::<T>() and checked for null
unsafe {
    *ptr = value;
}
```

### Rule U-MEM-002: Prefer Safe Abstractions
**Requirement**: Use safe wrappers from std before writing unsafe
**Examples**: `Vec`, `Box`, `Arc`, `Mutex` instead of raw pointers

```rust
// WRONG - manual memory management
let ptr = libc::malloc(size);
// ... use ptr
libc::free(ptr);

// CORRECT - RAII with Box
let data = Box::new([0u8; SIZE]);
// automatically freed when dropped
```

---

## Ownership Patterns (U-OWN)

### Rule U-OWN-001: Clear Ownership Transfer
**Requirement**: Make ownership transfer explicit in function signatures
**Pattern**: Owned parameters when taking ownership, references when borrowing

```rust
// Takes ownership - caller can't use value after
pub fn consume(data: Vec<u8>) { }

// Borrows - caller retains ownership
pub fn inspect(data: &[u8]) { }

// Mutable borrow - temporary exclusive access
pub fn modify(data: &mut Vec<u8>) { }
```

### Rule U-OWN-002: Return Owned Data
**Requirement**: Public functions SHOULD return owned types, not references
**Exception**: Returning references into self (getter methods)
**Rationale**: Lifetime annotations complicate API

```rust
// WRONG - forces caller to deal with lifetimes
pub fn process<'a>(input: &'a str) -> &'a str { input }

// CORRECT - returns owned String
pub fn process(input: &str) -> String { input.to_owned() }

// EXCEPTION - getter methods can return references
impl Config {
    pub fn name(&self) -> &str { &self.name }
}
```

---

## Performance Fundamentals (U-PERF)

### Rule U-PERF-001: Preallocate Collections
**Requirement**: Use `with_capacity()` when final size is known
**Validation**: Check `Vec::new()` vs `Vec::with_capacity()`

```rust
// WRONG - multiple reallocations
let mut v = Vec::new();
for i in 0..1000 {
    v.push(i);  // May reallocate many times
}

// CORRECT - single allocation
let mut v = Vec::with_capacity(1000);
for i in 0..1000 {
    v.push(i);  // No reallocation
}
```

### Rule U-PERF-002: Use Iterators
**Requirement**: Prefer iterators over manual loops
**Rationale**: Compiler optimizes iterator chains better
**Validation**: Check for manual index-based loops

```rust
// ACCEPTABLE - but harder to optimize
let mut sum = 0;
for i in 0..data.len() {
    sum += data[i];
}

// BETTER - iterator fusion and optimizations
let sum: i32 = data.iter().sum();
```

---

## Trait Implementation (U-TRAIT)

### Rule U-TRAIT-001: Derive Common Traits
**Requirement**: Public types SHOULD derive Debug
**Recommended**: Also derive Clone, PartialEq, Eq when applicable
**Validation**: Check pub struct/enum has #[derive(Debug)]

```rust
// MINIMAL
#[derive(Debug)]
pub struct User {
    id: u64,
    name: String,
}

// COMPREHENSIVE - derive all applicable traits
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct UserId(u64);
```

### Rule U-TRAIT-002: Implement Display for Public Errors
**Requirement**: Error types MUST implement Display
**Preferred**: Use thiserror which implements automatically
**Validation**: Check error types implement Display

---

## Testing (U-TEST)

### Rule U-TEST-001: Unit Tests in Same File
**Requirement**: Unit tests SHOULD be in `#[cfg(test)] mod tests`
**Pattern**: Tests module at end of file

```rust
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
    }
}
```

### Rule U-TEST-002: Test Error Cases
**Requirement**: Test both success and error paths
**Pattern**: Use `#[should_panic]` or `Result` return for error tests

```rust
#[test]
fn test_parse_invalid_input() {
    let result = parse("invalid");
    assert!(result.is_err());
}

#[test]
#[should_panic(expected = "division by zero")]
fn test_divide_by_zero() {
    divide(10, 0);
}
```

---

## Documentation (U-DOC)

### Rule U-DOC-001: Document Public Items
**Requirement**: All pub items MUST have doc comments
**Format**: Triple-slash `///` for items, `//!` for modules
**Validation**: `cargo doc` warnings

```rust
/// Parses a configuration file and returns the Config struct.
///
/// # Errors
///
/// Returns `ParseError` if the file format is invalid.
///
/// # Examples
///
/// ```
/// let config = parse_config("config.toml")?;
/// ```
pub fn parse_config(path: &str) -> Result<Config, ParseError> {
    // implementation
}
```

### Rule U-DOC-002: Document Panics
**Requirement**: If function can panic, document when
**Format**: `# Panics` section in doc comment

```rust
/// Retrieves the value at the given index.
///
/// # Panics
///
/// Panics if index is out of bounds.
pub fn get(&self, index: usize) -> &T {
    &self.data[index]
}
```

---

## Validation Checklist

Run these checks before considering code guideline-compliant:

```bash
# Format check
cargo fmt --check

# Linting
cargo clippy -- -D warnings

# Tests
cargo test

# Documentation
cargo doc --no-deps

# Custom guideline checks
python ~/.claude/skills/rust-guidelines/scripts/guideline-checker.py src/
```

---

## Quick Reference

| Aspect | Guideline | Example |
|--------|-----------|---------|
| Errors | Return Result<T, E> | `pub fn parse() -> Result<Data, Error>` |
| Error types | Use thiserror | `#[derive(Error, Debug)]` |
| Panics | Never unwrap() in prod | `map.get(&key).ok_or(Error)?` |
| Types | Newtype for validation | `struct UserId(u64)` |
| Unsafe | Document safety | `// SAFETY: ptr is valid because...` |
| Ownership | Clear transfer | `fn consume(data: Vec<u8>)` |
| Performance | Preallocate collections | `Vec::with_capacity(n)` |
| Traits | Derive Debug | `#[derive(Debug)]` |
| Tests | Test error paths | `assert!(result.is_err())` |
| Docs | Document panics | `# Panics` section |

---

**Guideline Version**: Microsoft Pragmatic Rust Guidelines 2025-2026
**Last Updated**: 2026-01-03
