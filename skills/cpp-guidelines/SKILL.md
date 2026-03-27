---
name: cpp-guidelines
description: |
  Enforce modern C++ (C++20/C++23) best practices, absolute memory safety, and modern build tooling.
  Uses CMake for out-of-source builds, clang-tidy for static analysis, and Google Test (gtest) for unit testing.
  Use for: writing C++ systems code, reviewing C++ architecture, ensuring memory safety.
---

# Modern C++ Development Guidelines

Automatically enforces strict enterprise standards when writing or modifying C++ code.

## Quick Start

**Natural language triggers:**
- "Create a new C++ project"
- "Refactor this C++ code to be memory safe"
- "Set up a CMakeLists.txt for this project"
- "Write unit tests using gtest"

## Requirements

| Dependency | Purpose |
|------------|---------|
| C++20+     | The required language standard. |
| CMake 3.20+| Build system generator. All builds MUST be out-of-source (`mkdir build && cd build`). |
| clang-tidy | Static analysis and linter. |
| gtest      | Google Test framework for all unit testing. |

## Core Architecture Rules

### 1. Absolute Memory Safety (No Raw Pointers for Ownership)
- **NEVER** use manual `new` or `delete`. 
- Always use `std::unique_ptr` for exclusive ownership (created via `std::make_unique`).
- Use `std::shared_ptr` ONLY when shared ownership is mathematically required (created via `std::make_shared`).
- Raw pointers (`T*`) are ONLY allowed for non-owning, temporary observations (e.g., passing a fast reference to a function where a C++ reference `T&` isn't viable).

### 2. Modern C++ Paradigms
- Use `constexpr` or `consteval` wherever calculations can be done at compile time.
- Prefer `std::array` or `std::vector` over C-style arrays (`T arr[]`).
- Use C++20 Concepts (`requires`) instead of complex `std::enable_if` SFINAE templates.
- Always use `auto` when the type is obvious from the right-hand side (Almost Always Auto).

### 3. Build & Environment Isolation
All new projects must generate a `CMakeLists.txt` file at the root.

**Standard Directory Structure:**
```text
project_root/
├── CMakeLists.txt
├── src/
│   └── main.cpp
├── include/
│   └── project/
├── tests/
│   └── test_main.cpp
```

### 4. Compilation & Testing
The agent must NEVER compile directly in the root directory (e.g., `g++ main.cpp`). 
When tasked with building or testing, the agent must execute:
```bash
mkdir -p build && cd build
cmake ..
make
ctest --output-on-failure
```