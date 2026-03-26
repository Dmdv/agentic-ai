# Library Development Guidelines

Guidelines specific to Rust library crates (code intended for reuse by other developers).

**Source**: Microsoft Pragmatic Rust Guidelines - Libraries Section

---

## API Design (L-API)

### Rule L-API-001: Follow std Library Naming
**Requirement**: Use std library naming conventions for similar concepts
**Pattern**:
- `into_*` - Consumes self, converts to target type
- `as_*` - Cheap reference conversion
- `to_*` - Expensive conversion, clones data
- `from_*` - Conversion from another type (From trait)

```rust
impl MyType {
    // Consumes self
    pub fn into_inner(self) -> InnerType { self.0 }

    // Cheap reference cast
    pub fn as_bytes(&self) -> &[u8] { &self.bytes }

    // Expensive conversion
    pub fn to_string(&self) -> String { format!("{:?}", self) }
}

// From trait for conversion
impl From<u64> for MyId {
    fn from(value: u64) -> Self { MyId(value) }
}
```

### Rule L-API-002: Builder Pattern for Complex Construction
**Requirement**: Types with >3 parameters SHOULD use builder pattern
**Rationale**: Improves API ergonomics, enables optional parameters

```rust
pub struct HttpClient {
    timeout: Duration,
    retries: u32,
    base_url: String,
}

// Builder pattern
pub struct HttpClientBuilder {
    timeout: Option<Duration>,
    retries: Option<u32>,
    base_url: Option<String>,
}

impl HttpClientBuilder {
    pub fn new() -> Self {
        Self { timeout: None, retries: None, base_url: None }
    }

    pub fn timeout(mut self, duration: Duration) -> Self {
        self.timeout = Some(duration);
        self
    }

    pub fn retries(mut self, count: u32) -> Self {
        self.retries = Some(count);
        self
    }

    pub fn base_url(mut self, url: String) -> Self {
        self.base_url = Some(url);
        self
    }

    pub fn build(self) -> Result<HttpClient, BuildError> {
        Ok(HttpClient {
            timeout: self.timeout.unwrap_or(Duration::from_secs(30)),
            retries: self.retries.unwrap_or(3),
            base_url: self.base_url.ok_or(BuildError::MissingBaseUrl)?,
        })
    }
}

// Usage
let client = HttpClientBuilder::new()
    .timeout(Duration::from_secs(10))
    .base_url("https://api.example.com".to_string())
    .build()?;
```

### Rule L-API-003: Make Hard to Misuse
**Requirement**: APIs SHOULD prevent misuse via type system
**Pattern**: Use type state pattern for stateful objects

```rust
// Type-state pattern - compile-time state tracking
struct Disconnected;
struct Connected;

struct Database<State = Disconnected> {
    connection: Option<Connection>,
    _state: PhantomData<State>,
}

impl Database<Disconnected> {
    pub fn new() -> Self {
        Database { connection: None, _state: PhantomData }
    }

    pub fn connect(self, url: &str) -> Result<Database<Connected>, Error> {
        let conn = Connection::establish(url)?;
        Ok(Database { connection: Some(conn), _state: PhantomData })
    }
}

impl Database<Connected> {
    // Only available when connected!
    pub fn query(&self, sql: &str) -> Result<QueryResult, Error> {
        self.connection.as_ref().unwrap().execute(sql)
    }

    pub fn disconnect(self) -> Database<Disconnected> {
        Database { connection: None, _state: PhantomData }
    }
}

// Usage - can't query before connecting (compile error)
let db = Database::new();
// db.query("SELECT * FROM users")?;  // ERROR: no method `query`
let db = db.connect("localhost:5432")?;
db.query("SELECT * FROM users")?;  // OK
```

---

## Semantic Versioning (L-VER)

### Rule L-VER-001: Follow SemVer Strictly
**Requirement**: Version number MUST follow semantic versioning
**Format**: MAJOR.MINOR.PATCH
- MAJOR: Breaking changes
- MINOR: New features, backwards compatible
- PATCH: Bug fixes

### Rule L-VER-002: Document Breaking Changes
**Requirement**: Breaking changes MUST be documented in CHANGELOG.md
**Pattern**: Keep a Changelog format

```markdown
# Changelog

## [2.0.0] - 2026-01-15
### Changed (BREAKING)
- `parse()` now returns `Result<T, ParseError>` instead of `Option<T>`
- Renamed `Client` to `HttpClient` for clarity

### Migration Guide
Replace:
```rust
let data = parse(input).unwrap();
```
With:
```rust
let data = parse(input)?;
```

## [1.1.0] - 2025-12-20
### Added
- New `timeout()` method on Client

## [1.0.0] - 2025-11-01
- Initial release
```

---

## Documentation (L-DOC)

### Rule L-DOC-001: Crate-Level Documentation
**Requirement**: Crates MUST have `//!` module-level docs in lib.rs
**Content**: What, why, basic usage example

```rust
//! # My HTTP Client
//!
//! A simple, type-safe HTTP client library.
//!
//! ## Features
//!
//! - Automatic retries with exponential backoff
//! - Type-safe request building
//! - Async/await support
//!
//! ## Example
//!
//! ```rust
//! use my_http_client::Client;
//!
//! let client = Client::new("https://api.example.com");
//! let response = client.get("/users").send().await?;
//! ```

pub struct Client { /* ... */ }
```

### Rule L-DOC-002: Examples in Doc Comments
**Requirement**: Public functions SHOULD have usage examples in doc comments
**Pattern**: Use `# Examples` section with tested code blocks

```rust
/// Sends a GET request to the specified path.
///
/// # Examples
///
/// ```
/// # use my_http_client::Client;
/// # async fn example() -> Result<(), Box<dyn std::error::Error>> {
/// let client = Client::new("https://api.example.com");
/// let response = client.get("/users").send().await?;
/// # Ok(())
/// # }
/// ```
///
/// # Errors
///
/// Returns an error if the network request fails or the response
/// status is not 2xx.
pub async fn get(&self, path: &str) -> Result<Response, Error> {
    // implementation
}
```

---

## Testing (L-TEST)

### Rule L-TEST-001: Integration Tests
**Requirement**: Libraries SHOULD have integration tests in `tests/` directory
**Pattern**: tests/ directory with one file per major feature

```
my-library/
├── src/
│   ├── lib.rs
│   └── client.rs
├── tests/
│   ├── http_client.rs
│   ├── retry_logic.rs
│   └── common/
│       └── mod.rs  # Shared test utilities
└── Cargo.toml
```

```rust
// tests/http_client.rs
use my_library::Client;

#[tokio::test]
async fn test_successful_request() {
    let client = Client::new("https://httpbin.org");
    let response = client.get("/get").send().await.unwrap();
    assert!(response.is_success());
}

#[tokio::test]
async fn test_404_error() {
    let client = Client::new("https://httpbin.org");
    let result = client.get("/status/404").send().await;
    assert!(result.is_err());
}
```

### Rule L-TEST-002: Doc Tests
**Requirement**: All public examples in doc comments MUST compile and pass
**Validation**: `cargo test --doc`

---

## Dependency Management (L-DEP)

### Rule L-DEP-001: Minimal Dependencies
**Requirement**: Only add dependencies when justified
**Rationale**: Each dependency increases compile time, attack surface, maintenance burden

### Rule L-DEP-002: Specify Feature Flags
**Requirement**: Large optional functionality SHOULD be behind feature flags

```toml
# Cargo.toml
[features]
default = []
tls = ["dep:rustls"]
compression = ["dep:flate2"]
full = ["tls", "compression"]

[dependencies]
rustls = { version = "0.21", optional = true }
flate2 = { version = "1.0", optional = true }
```

```rust
// lib.rs
#[cfg(feature = "tls")]
pub mod tls;

#[cfg(feature = "compression")]
pub fn compress(data: &[u8]) -> Vec<u8> {
    // implementation
}
```

---

## Error Handling (L-ERR)

### Rule L-ERR-001: Library-Specific Error Type
**Requirement**: Libraries MUST define custom error type
**Pattern**: Single error enum covering all library errors

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ClientError {
    #[error("network error: {0}")]
    Network(#[from] std::io::Error),

    #[error("invalid URL: {0}")]
    InvalidUrl(String),

    #[error("HTTP {status}: {message}")]
    Http { status: u16, message: String },

    #[error("timeout after {0:?}")]
    Timeout(Duration),
}

pub type Result<T> = std::result::Result<T, ClientError>;
```

### Rule L-ERR-002: Don't Expose Internal Errors
**Requirement**: Convert internal errors to library errors
**Anti-pattern**: Propagating dependency errors directly

```rust
// WRONG - exposes reqwest error
pub fn get(&self, url: &str) -> Result<Response, reqwest::Error> {
    reqwest::get(url)  // Leaks implementation detail
}

// CORRECT - wraps in library error
pub fn get(&self, url: &str) -> Result<Response, ClientError> {
    reqwest::get(url).map_err(|e| ClientError::Network(e.into()))
}
```

---

## Backwards Compatibility (L-COMPAT)

### Rule L-COMPAT-001: Avoid Breaking Changes
**Requirement**: Preserve backwards compatibility when possible
**Techniques**:
- Add new methods instead of modifying existing
- Use #[deprecated] for old APIs
- Provide migration period (one major version)

```rust
// v1.0.0
pub fn connect(url: &str) -> Result<Connection, Error> {
    // old implementation
}

// v1.5.0 - add new method, keep old
#[deprecated(since = "1.5.0", note = "use `connect_with_timeout` instead")]
pub fn connect(url: &str) -> Result<Connection, Error> {
    connect_with_timeout(url, Duration::from_secs(30))
}

pub fn connect_with_timeout(url: &str, timeout: Duration) -> Result<Connection, Error> {
    // new implementation
}

// v2.0.0 - remove deprecated
pub fn connect_with_timeout(url: &str, timeout: Duration) -> Result<Connection, Error> {
    // only new API remains
}
```

---

## Performance (L-PERF)

### Rule L-PERF-001: Provide Both Owned and Borrowed APIs
**Requirement**: Hot-path functions SHOULD accept borrowed types
**Pattern**: `AsRef<T>` for flexibility

```rust
// INFLEXIBLE - forces allocation
pub fn process(data: String) -> Result<(), Error> {
    // ...
}

// FLEXIBLE - accepts &str, String, Cow<str>
pub fn process(data: impl AsRef<str>) -> Result<(), Error> {
    let data = data.as_ref();
    // ...
}

// Usage
process("literal");          // No allocation
process(owned_string);        // No allocation (moves)
process(&borrowed_string);    // No allocation (borrows)
```

### Rule L-PERF-002: Lazy Initialization for Heavy Resources
**Requirement**: Expensive resources SHOULD be initialized on first use
**Pattern**: `Once` or `OnceLock` for thread-safe lazy init

```rust
use std::sync::OnceLock;

static EXPENSIVE_DATA: OnceLock<Vec<u8>> = OnceLock::new();

fn get_data() -> &'static Vec<u8> {
    EXPENSIVE_DATA.get_or_init(|| {
        // Heavy computation only runs once
        expensive_computation()
    })
}
```

---

## Validation Checklist

Library-specific checks:

```bash
# All public items documented
cargo doc --no-deps 2>&1 | grep warning

# Integration tests pass
cargo test --test '*'

# Doc tests pass
cargo test --doc

# No leaked dependencies in public API
cargo tree --edges normal --format "{p} {f}"

# Feature combinations work
cargo test --all-features
cargo test --no-default-features
```

---

**Guideline Version**: Microsoft Pragmatic Rust Guidelines 2025-2026
**Last Updated**: 2026-01-03
