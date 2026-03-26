---
name: rust-guidelines
description: |
  Enforce Microsoft's Pragmatic Rust Guidelines automatically when working with Rust code.
  Provides progressive guideline enforcement, automated validation, and compliance tracking.
  Use for: writing Rust code, reviewing code, ensuring best practices, FFI safety, performance optimization.
---

# Rust Development Guidelines

Automatically enforces Microsoft's Pragmatic Rust Guidelines when creating or modifying Rust code.

## Quick Start

**Natural language triggers:**
- "Implement authentication in Rust"
- "Review this Rust code for guideline compliance"
- "Create a new Rust library following best practices"
- "Add FFI bindings with safety guarantees"

## Requirements

| Dependency | Version | Used By |
|------------|---------|---------|
| Rust | 1.70+ | All validation scripts |
| Python | 3.9+ | guideline-checker.py |
| Bash | 4.0+ | validation scripts |

## Guideline Domains

| Domain | Resource | When to Load | Status |
|--------|----------|--------------|--------|
| Universal | [universal.md](resources/universal.md) | All Rust code | Complete |
| Libraries | [libraries.md](resources/libraries.md) | Library crates | Complete |
| FFI | [ffi.md](resources/ffi.md) | Foreign function interfaces | Complete |
| Safety | [safety.md](resources/safety.md) | Unsafe code, security-critical | Complete |
| Applications | [applications.md](resources/applications.md) | Binary crates | Minimal |
| Performance | [performance.md](resources/performance.md) | Performance optimization | Minimal |
| Documentation | [documentation.md](resources/documentation.md) | Public APIs, doc comments | Minimal |
| AI Integration | [ai-integration.md](resources/ai-integration.md) | AI/ML features | Minimal |

**Note**: Domains marked "Minimal" contain core rules but will be expanded in future releases.

## Enforcement Modes

### Strict Mode (New Code)
- All violations reported
- Critical violations block completion
- Compliance comments added on request
- Load: All applicable domain resources

### Advisory Mode (Code Review)
- Violations reported with severity
- Non-blocking recommendations
- Prioritized by impact
- Load: Targeted domain resources

### Incremental Mode (Refactoring)
- Focus on modified code only
- Progressive adoption support
- Migration guidance provided
- Load: Relevant patterns only

## Bundled Scripts

### Validation
```bash
# Comprehensive guideline validation
python scripts/guideline-checker.py src/

# Strict mode (fails on errors/warnings)
python scripts/guideline-checker.py --strict src/

# Moderate mode (fails on critical only)
python scripts/guideline-checker.py --moderate src/

# Advisory mode (report only)
python scripts/guideline-checker.py --advisory src/
```

**Note**: Additional scripts (validate-rust.sh, code generators) are planned for future releases.

## Integration

Works standalone or composed with domain-specific skills:
- `rust-guidelines` + `web-development` → Web service with guideline compliance
- `rust-guidelines` + `embedded-systems` → Embedded firmware following safety guidelines
- `rust-guidelines` + `cli-tools` → CLI applications with proper error handling

## Compliance Tracking

Optional compliance comment format:
```rust
// Rust guideline compliant: 2026-01 (Microsoft Pragmatic Rust Guidelines)
```

Request with: "Add guideline compliance marker"

## Guidelines Version

Based on: **Microsoft Pragmatic Rust Guidelines (2025-2026)**
- Source: https://microsoft.github.io/rust-guidelines/
- AI-optimized format with condensed content
- Last synced: 2026-01-03
