# Rust Development Guidelines Skill

Claude Code skill for enforcing Microsoft's Pragmatic Rust Guidelines automatically.

## Overview

This skill provides:
- **8 Guideline Domains**: Universal, Libraries, Applications, FFI, Safety, Performance, Documentation, AI Integration
- **Progressive Loading**: Load only relevant guidelines for your context
- **Automated Validation**: Python script checks code for compliance
- **3 Enforcement Modes**: Strict (new code), Moderate (review), Advisory (learning)

## Quick Start

Just describe what you're doing with Rust code:
```
"Implement user authentication in Rust"
"Review this FFI code for safety issues"
"Create a library following best practices"
```

Claude automatically loads relevant guidelines and applies them.

## Files

```
rust-guidelines/
├── SKILL.md                          # Main skill file (YAML frontmatter + docs)
├── README.md                         # This file
├── resources/                        # Guideline domains (loaded on-demand)
│   ├── universal.md                  # Foundation (all code)
│   ├── libraries.md                  # Library crates
│   ├── applications.md               # Binary crates
│   ├── ffi.md                       # FFI safety
│   ├── safety.md                    # Unsafe & security
│   ├── performance.md               # Optimization
│   ├── documentation.md             # Doc standards
│   └── ai-integration.md            # AI/ML patterns
├── scripts/                          # Validation tools
│   └── guideline-checker.py         # Main validation script
└── templates/                        # Code templates (future)
```

## Validation

Run automated checks:

```bash
# Quick check
python ~/.claude/skills/rust-guidelines/scripts/guideline-checker.py src/

# Strict mode (fails on errors/warnings)
python ~/.claude/skills/rust-guidelines/scripts/guideline-checker.py --strict src/

# Moderate mode (fails on critical only)
python ~/.claude/skills/rust-guidelines/scripts/guideline-checker.py --moderate src/

# Advisory mode (report only, never fails)
python ~/.claude/skills/rust-guidelines/scripts/guideline-checker.py --advisory src/
```

## Enforcement Modes

| Mode | Triggers | Loaded Resources | Validation |
|------|----------|------------------|------------|
| **Strict** | "implement", "create" new code | All applicable domains | Blocks on critical/error |
| **Moderate** | "review", "audit" existing code | Targeted domains | Blocks on critical only |
| **Advisory** | "learn", "understand" guidelines | Progressive disclosure | Reports, never blocks |

## Guideline Domains

### Universal (All Rust Code)
- Error handling (Result<T, E>, thiserror)
- Type safety (newtype pattern, invalid states)
- Memory safety (minimize unsafe, document SAFETY)
- Ownership patterns (clear transfer, return owned)
- Traits (derive Debug, implement Display)

### Libraries (Library Crates)
- API design (builder pattern, std naming)
- Semantic versioning (MAJOR.MINOR.PATCH)
- Documentation (crate-level, examples)
- Testing (integration tests, doc tests)
- Dependency management (minimal deps, features)

### FFI (Foreign Function Interface)
- Safety boundaries (wrap extern, validate inputs)
- String handling (CString, CStr)
- Memory ownership (document who frees)
- repr(C) for shared structs
- Error codes across boundaries

### Safety (Unsafe & Security)
- Unsafe code (minimize, document invariants)
- Security (no hardcoded secrets, validate inputs)
- Constant-time comparison for secrets
- Dependency auditing (cargo audit)
- Concurrency safety (prefer channels)

## Integration

### With V2 Pipeline
Automatically activates during Phase 4 (Implementation) for Rust projects.

### With Existing RUST_STANDARDS.md
Complements existing `/Users/dima/.claude/docs/RUST_STANDARDS.md`:
- RUST_STANDARDS.md: Lightweight reference (always loaded)
- rust-guidelines skill: Deep dive (on-demand, Microsoft-specific)

### With Domain Skills
Composes with domain-specific skills:
- `rust-guidelines` + `web-development` → Web service compliance
- `rust-guidelines` + `embedded-systems` → Embedded safety compliance
- `rust-guidelines` + `cli-tools` → CLI best practices

## Requirements

| Dependency | Version | Purpose |
|------------|---------|---------|
| Rust | 1.70+ | Validation scripts run clippy/fmt |
| Python | 3.9+ | guideline-checker.py |
| Bash | 4.0+ | Validation scripts |

## Guidelines Version

Based on: **Microsoft Pragmatic Rust Guidelines (2025-2026)**
- Source: https://microsoft.github.io/rust-guidelines/
- AI-optimized condensed format
- Last synced: 2026-01-03

## Future Enhancements

- [ ] Additional validation rules (more comprehensive checks)
- [ ] Code templates (error-handling.rs, async-service.rs, ffi-wrapper.rs)
- [ ] Cargo.toml validation
- [ ] Automated guideline sync script
- [ ] Integration with cargo-clippy custom lints
- [ ] Performance profiling integration

## Contributing

To update guidelines:
1. Update relevant resource files in `resources/`
2. Add validation logic to `scripts/guideline-checker.py`
3. Test with `python scripts/guideline-checker.py tests/`
4. Update SKILL.md if adding new domains

## License

Based on Microsoft's Pragmatic Rust Guidelines (MIT License)
