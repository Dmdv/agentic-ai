---
name: c-guidelines
description: |
  Enforce strict, secure, and highly optimized C programming practices.
  Uses Makefiles, strict compiler flags, and memory safety checks.
  Use for: embedded systems, kernel modules, drivers, and high-performance libraries.
---

# Secure C Programming Guidelines

Automatically enforces enterprise standards for low-level C development, prioritizing memory safety and POSIX compliance.

## Quick Start
**Natural language triggers:**
- "Write a C program to..."
- "Create a Makefile for this C project"
- "Review this C code for buffer overflows"

## Requirements
| Tool | Purpose |
|------|---------|
| gcc / clang | Compilation. |
| make | Build automation. |
| valgrind | Memory leak detection (run via bash tool if available). |

## Core Architecture Rules

### 1. Memory Safety (Absolute Priority)
- **NEVER** use `gets()`, `strcpy()`, `sprintf()`, or `strcat()`. ALWAYS use their safe `n` bounds-checked equivalents (`fgets()`, `strncpy()`, `snprintf()`, `strncat()`).
- Always check the return value of `malloc()`, `calloc()`, and `realloc()` for `NULL` before dereferencing.
- Every `malloc()` MUST have a well-documented and architected corresponding `free()`. Set pointers to `NULL` immediately after freeing to prevent double-free/use-after-free bugs.

### 2. Compilation Standards
- **Strict Flags:** Always compile with `-Wall -Wextra -Werror -pedantic -std=c11` (or newer). Do not allow warnings to pass silently.
- **Environment Isolation:** Never compile raw files in the root directory. You MUST create a `Makefile` that directs compiled objects (`.o`) to a `build/` directory and final executables to a `bin/` directory.

### 3. Data Types & Typesafety
- Use `<stdint.h>` for explicitly sized integers (e.g., `uint32_t`, `int8_t`) rather than ambiguous types like `int` or `long` when doing bitwise operations or interacting with hardware/network protocols.
- Avoid "magic numbers." Define constants using `#define` or `const` variables.