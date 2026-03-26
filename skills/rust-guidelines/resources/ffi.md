# FFI (Foreign Function Interface) Guidelines

Safety-critical guidelines for interoperating with C/C++ code.

**Source**: Microsoft Pragmatic Rust Guidelines - FFI Section

---

## Core FFI Safety Rules

### Rule FFI-001: All FFI Boundaries are Unsafe
**Requirement**: Wrap all `extern "C"` functions in safe Rust APIs
**Rationale**: C code doesn't respect Rust's safety guarantees

```rust
// C function (unsafe)
extern "C" {
    fn c_process_data(data: *const u8, len: usize) -> i32;
}

// Safe Rust wrapper
pub fn process_data(data: &[u8]) -> Result<(), Error> {
    let result = unsafe {
        // SAFETY: data is valid slice, len matches
        c_process_data(data.as_ptr(), data.len())
    };
    if result == 0 {
        Ok(())
    } else {
        Err(Error::FFI(result))
    }
}
```

### Rule FFI-002: Validate All C Inputs
**Requirement**: Check null pointers, validate lengths, verify invariants
**Pattern**: Defensive programming at FFI boundary

```rust
#[no_mangle]
pub extern "C" fn rust_process(data: *const u8, len: usize) -> i32 {
    // Validate inputs
    if data.is_null() {
        return -1;  // Error code
    }

    let slice = unsafe {
        // SAFETY: Validated non-null above, len provided by caller
        std::slice::from_raw_parts(data, len)
    };

    match process_internal(slice) {
        Ok(()) => 0,
        Err(_) => -2,
    }
}
```

### Rule FFI-003: Use repr(C) for Shared Structs
**Requirement**: Structs crossing FFI boundary MUST have `#[repr(C)]`
**Rationale**: Rust's default layout is undefined

```rust
// WRONG - undefined layout
pub struct Point {
    x: f64,
    y: f64,
}

// CORRECT - C-compatible layout
#[repr(C)]
pub struct Point {
    x: f64,
    y: f64,
}
```

### Rule FFI-004: Never Pass Rust Types Directly
**Requirement**: Only pass C-compatible types across FFI
**Safe**: primitives, `#[repr(C)]` structs, raw pointers
**Unsafe**: `String`, `Vec`, `Box` (without conversion)

```rust
// WRONG - passing Rust String
extern "C" {
    fn c_print(s: String);  // INVALID!
}

// CORRECT - convert to C string
use std::ffi::CString;

pub fn print_message(msg: &str) -> Result<(), Error> {
    let c_msg = CString::new(msg)?;
    unsafe {
        c_print(c_msg.as_ptr());
    }
    Ok(())
}

extern "C" {
    fn c_print(s: *const std::os::raw::c_char);
}
```

### Rule FFI-005: Document Ownership
**Requirement**: Clearly document who owns allocated memory
**Pattern**: Comments stating ownership transfer

```rust
/// Allocates and returns a new Widget.
///
/// # Safety
///
/// Caller is responsible for calling `widget_free()` to deallocate.
/// Do not use after calling `widget_free()`.
#[no_mangle]
pub extern "C" fn widget_new() -> *mut Widget {
    Box::into_raw(Box::new(Widget::default()))
}

/// Frees a Widget previously allocated by `widget_new()`.
///
/// # Safety
///
/// - ptr must have been returned by `widget_new()`
/// - ptr must not have been freed previously
/// - ptr must not be used after this call
#[no_mangle]
pub unsafe extern "C" fn widget_free(ptr: *mut Widget) {
    if !ptr.is_null() {
        let _ = Box::from_raw(ptr);  // Drops and frees
    }
}
```

---

## String Handling

### Rule FFI-STR-001: Use CString for Rust→C
**Requirement**: Convert Rust strings to `CString` before passing to C

```rust
use std::ffi::CString;

pub fn call_c_with_string(msg: &str) -> Result<(), Error> {
    let c_msg = CString::new(msg)?;  // Adds null terminator
    unsafe {
        c_function(c_msg.as_ptr());
    }
    Ok(())
}
```

### Rule FFI-STR-002: Use CStr for C→Rust
**Requirement**: Convert C strings to Rust `&str` via `CStr`

```rust
use std::ffi::CStr;

pub fn convert_c_string(c_str: *const c_char) -> Option<String> {
    if c_str.is_null() {
        return None;
    }

    unsafe {
        CStr::from_ptr(c_str)
            .to_str()
            .ok()
            .map(|s| s.to_owned())
    }
}
```

---

## Error Handling Across FFI

### Rule FFI-ERR-001: Return Error Codes
**Requirement**: FFI functions SHOULD return integer error codes
**Pattern**: 0 = success, negative = error

```rust
#[no_mangle]
pub extern "C" fn process_data(
    data: *const u8,
    len: usize,
    out: *mut Result_t,
) -> i32 {
    if data.is_null() || out.is_null() {
        return -1;  // EINVAL
    }

    match process_internal_data(data, len) {
        Ok(result) => {
            unsafe { *out = result; }
            0  // Success
        }
        Err(Error::IO) => -2,
        Err(Error::Parse) => -3,
    }
}
```

### Rule FFI-ERR-002: Never Panic Across FFI
**Requirement**: Catch all panics before returning to C
**Pattern**: Use `catch_unwind`

```rust
use std::panic::catch_unwind;

#[no_mangle]
pub extern "C" fn safe_operation() -> i32 {
    match catch_unwind(|| {
        // Potentially panicking Rust code
        risky_operation()
    }) {
        Ok(result) => match result {
            Ok(()) => 0,
            Err(_) => -1,
        },
        Err(_) => -99,  // Panic occurred
    }
}
```

---

## Validation

```bash
# Check all extern functions have safety docs
grep -n 'extern "C"' src/ -A 5 | grep -E '(SAFETY|Safety)'

# Verify repr(C) on FFI structs
grep -n '#\[repr(C)\]' src/

# Run with Miri for UB detection
cargo +nightly miri test
```

---

**Guideline Version**: Microsoft Pragmatic Rust Guidelines 2025-2026
**Last Updated**: 2026-01-03
