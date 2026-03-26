# AI Integration Guidelines

Guidelines for integrating AI/ML capabilities in Rust applications.

**Source**: Microsoft Pragmatic Rust Guidelines - AI Section

---

## Model Interfacing

### Rule AI-001: Type-Safe Model I/O
Wrap model inputs/outputs in strongly-typed Rust structures.

### Rule AI-002: Validate Model Outputs
Never trust ML model outputs without validation.

```rust
pub fn classify(image: &Image) -> Result<Classification, Error> {
    let raw_output = ml_model.predict(image)?;

    // Validate output is in expected range
    if raw_output.score < 0.0 || raw_output.score > 1.0 {
        return Err(Error::InvalidModelOutput);
    }

    Ok(Classification::from(raw_output))
}
```

---

**Guideline Version**: Microsoft Pragmatic Rust Guidelines 2025-2026
