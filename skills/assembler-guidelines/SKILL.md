---
name: assembler-guidelines
description: |
  Enforce strict architecture targeting, standard calling conventions, and explicit register management for Assembly language.
  Use for: x86, x86_64, or ARM64 (AArch64) low-level programming, reverse engineering, or performance micro-optimizations.
---

# Bare-Metal Assembly Guidelines

Automatically enforces safe register management, ABI compliance, and extreme performance optimization when writing raw Assembly.

## Quick Start
**Natural language triggers:**
- "Write an ARM64 assembly function to..."
- "Translate this C snippet into x86_64 Assembly"
- "Optimize this inline assembly"

## Core Architecture Rules

### 1. Architecture & Syntax Definition
- You MUST explicitly define the target architecture (e.g., `x86_64`, `ARM64/AArch64`) and the assembler dialect (e.g., `NASM`, `AT&T`, `Intel`, `GAS`) in your plan. 
- For Apple Silicon, strictly adhere to the standard `ARM64` instruction set and Apple's specific calling conventions (AArch64 ABI).

### 2. ABI Compliance (Application Binary Interface)
- **Calling Conventions:** You must strictly follow the ABI of the target OS. (e.g., System V AMD64 ABI for Linux/macOS x86_64, where arguments are passed in `rdi, rsi, rdx, rcx, r8, r9`).
- **Callee-Saved Registers:** If you use callee-saved registers (like `rbx, rbp, r12-r15` in x86_64), you MUST push them to the stack at the start of the function and pop them before returning to prevent corrupting the caller's state.

### 3. Stack Alignment
- Ensure the stack pointer is aligned to 16 bytes before making any `call` to an external C library function. Failure to align the stack will result in segmentation faults.

### 4. Readability & Maintenance
- Assembly is notoriously hard to read. You MUST add inline comments (`;` or `//`) to almost every line explaining *what* the operation is doing in the context of the higher-level algorithm, not just literally translating the mnemonic.
- Define data sections (`.data`, `.bss`, `.text`) clearly.