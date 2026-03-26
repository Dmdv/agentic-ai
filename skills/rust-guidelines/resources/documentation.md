# Documentation Standards

Comprehensive documentation guidelines for Rust projects.

**Source**: Microsoft Pragmatic Rust Guidelines - Documentation Section

---

## Doc Comments

### Rule DOC-001: All Public Items Have Docs
Every `pub` item must have `///` doc comments.

### Rule DOC-002: Include Examples
Use `# Examples` section with runnable code.

```rust
/// Parses a date string in YYYY-MM-DD format.
///
/// # Examples
///
/// ```
/// # use mylib::parse_date;
/// let date = parse_date("2026-01-03").unwrap();
/// ```
pub fn parse_date(s: &str) -> Result<Date, ParseError> {
    // implementation
}
```

---

## Module Documentation

### Rule DOC-MOD-001: Module-Level Docs
Use `//!` at the top of lib.rs and module files.

---

**Guideline Version**: Microsoft Pragmatic Rust Guidelines 2025-2026
