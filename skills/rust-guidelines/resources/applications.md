# Application Development Guidelines

Guidelines specific to Rust application/binary crates.

**Source**: Microsoft Pragmatic Rust Guidelines - Applications Section

---

## Error Handling

### Rule APP-001: User-Friendly Error Messages
Applications should provide helpful error messages for end users.

```rust
use anyhow::Context;

fn main() -> anyhow::Result<()> {
    let config = std::fs::read_to_string("config.toml")
        .context("Failed to read config.toml. Does the file exist?")?;
    Ok(())
}
```

---

## CLI Applications

### Rule APP-CLI-001: Use clap for Argument Parsing
Prefer `clap` for robust CLI argument handling.

### Rule APP-CLI-002: Handle Ctrl+C Gracefully
Set up signal handlers for clean shutdown.

---

**Guideline Version**: Microsoft Pragmatic Rust Guidelines 2025-2026
