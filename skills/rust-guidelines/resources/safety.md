# Safety and Security Guidelines

Critical guidelines for unsafe code and security-sensitive applications.

**Source**: Microsoft Pragmatic Rust Guidelines - Safety Section

---

## Unsafe Code (S-UNSAFE)

### Rule S-UNSAFE-001: Minimize Unsafe
**Requirement**: Avoid `unsafe` unless absolutely necessary
**Justification Required**: Document why safe alternatives won't work

### Rule S-UNSAFE-002: Safety Invariants
**Requirement**: All `unsafe` blocks MUST have `// SAFETY:` comment
**Content**: Explain what invariants make this operation safe

```rust
// WRONG - no safety justification
unsafe {
    *ptr = value;
}

// CORRECT - documents safety invariant
// SAFETY: ptr was allocated with Box::new() and is valid, aligned,
// and will not be accessed elsewhere during this write
unsafe {
    *ptr = value;
}
```

### Rule S-UNSAFE-003: Encapsulate Unsafe
**Requirement**: Wrap unsafe code in safe APIs
**Pattern**: Unsafe in private functions, safe in public API

```rust
pub struct SafeVec<T> {
    ptr: *mut T,
    len: usize,
    capacity: usize,
}

impl<T> SafeVec<T> {
    // Public API is safe
    pub fn push(&mut self, value: T) {
        if self.len == self.capacity {
            self.grow();
        }
        self.push_unchecked(value);
    }

    // Unsafe helper - private
    unsafe fn push_unchecked(&mut self, value: T) {
        // SAFETY: Called only when capacity check passed
        ptr::write(self.ptr.add(self.len), value);
        self.len += 1;
    }
}
```

---

## Security (S-SEC)

### Rule S-SEC-001: No Hardcoded Secrets
**Requirement**: Never hardcode passwords, API keys, tokens
**Pattern**: Load from environment or config files

```rust
// WRONG
const API_KEY: &str = "sk-1234567890abcdef";

// CORRECT
fn get_api_key() -> Result<String, Error> {
    std::env::var("API_KEY")
        .map_err(|_| Error::MissingApiKey)
}
```

### Rule S-SEC-002: Validate All Inputs
**Requirement**: Validate external inputs before use
**Context**: User input, network data, file contents

```rust
pub fn process_user_input(input: &str) -> Result<Data, Error> {
    // Validate length
    if input.len() > MAX_INPUT_LEN {
        return Err(Error::InputTooLong);
    }

    // Validate characters
    if !input.chars().all(|c| c.is_alphanumeric() || c == '_') {
        return Err(Error::InvalidCharacters);
    }

    // Validate format
    let data = parse_format(input)?;

    Ok(data)
}
```

### Rule S-SEC-003: Use Constant-Time Comparison for Secrets
**Requirement**: Compare passwords/tokens with constant-time functions
**Rationale**: Prevent timing attacks

```rust
use subtle::ConstantTimeEq;

pub fn verify_token(provided: &[u8], expected: &[u8]) -> bool {
    provided.ct_eq(expected).into()
}

// WRONG - timing attack vulnerable
pub fn verify_token_wrong(provided: &[u8], expected: &[u8]) -> bool {
    provided == expected  // Short-circuits on first diff
}
```

### Rule S-SEC-004: Clear Sensitive Data
**Requirement**: Zeroize secrets after use
**Pattern**: Use `zeroize` crate

```rust
use zeroize::Zeroize;

pub struct Password {
    data: Vec<u8>,
}

impl Drop for Password {
    fn drop(&mut self) {
        self.data.zeroize();  // Clear memory
    }
}
```

---

## Dependency Security (S-DEP)

### Rule S-DEP-001: Audit Dependencies
**Requirement**: Run `cargo audit` regularly
**Frequency**: Before releases, in CI/CD

```bash
# Install cargo-audit
cargo install cargo-audit

# Check for known vulnerabilities
cargo audit

# Generate security advisory report
cargo audit --json > security-report.json
```

### Rule S-DEP-002: Minimal Dependencies
**Requirement**: Only include necessary dependencies
**Rationale**: Each dependency is potential attack surface

### Rule S-DEP-003: Pin Dependency Versions
**Requirement**: Lock Cargo.lock into version control
**Rationale**: Reproducible builds, prevent supply chain attacks

---

## Concurrency Safety (S-CONC)

### Rule S-CONC-001: Prefer Message Passing
**Requirement**: Use channels over shared state when possible
**Rationale**: Avoid data races, simpler reasoning

```rust
use std::sync::mpsc;

// PREFERRED - message passing
fn process_data(rx: mpsc::Receiver<Data>) {
    for data in rx {
        handle(data);
    }
}

// ACCEPTABLE - but requires synchronization
use std::sync::{Arc, Mutex};

fn process_data(shared: Arc<Mutex<Data>>) {
    let mut data = shared.lock().unwrap();
    // ...
}
```

### Rule S-CONC-002: Document Thread Safety
**Requirement**: Document thread safety in public API docs
**Markers**: Implement Send/Sync or document why not

```rust
/// Thread-safe cache with interior mutability.
///
/// This type is `Send + Sync` and can be safely shared across threads.
pub struct Cache {
    data: Arc<Mutex<HashMap<String, Value>>>,
}

// SAFETY: Cache is thread-safe due to Mutex
unsafe impl Send for Cache {}
unsafe impl Sync for Cache {}
```

---

## Testing Security (S-TEST)

### Rule S-TEST-001: Test Error Paths
**Requirement**: Test all error handling paths
**Rationale**: Error paths often contain security bugs

```rust
#[test]
fn test_invalid_input_rejected() {
    let result = process_input("../../../etc/passwd");
    assert!(matches!(result, Err(Error::InvalidPath)));
}

#[test]
fn test_buffer_overflow_prevented() {
    let huge_input = "x".repeat(1_000_000);
    let result = process_input(&huge_input);
    assert!(matches!(result, Err(Error::InputTooLarge)));
}
```

### Rule S-TEST-002: Fuzz Security-Critical Code
**Requirement**: Fuzz parsers, validators, crypto code
**Tool**: cargo-fuzz

```bash
# Install cargo-fuzz
cargo install cargo-fuzz

# Create fuzz target
cargo fuzz init

# Run fuzzer
cargo fuzz run fuzz_target_1
```

---

## Validation

```bash
# Security audit
cargo audit

# Check for unsafe blocks
grep -rn 'unsafe' src/ | wc -l

# Run with sanitizers
RUSTFLAGS="-Z sanitizer=address" cargo +nightly test

# Check for timing vulnerabilities
cargo bench  # Look for variance in secret comparisons
```

---

**Guideline Version**: Microsoft Pragmatic Rust Guidelines 2025-2026
**Last Updated**: 2026-01-03
