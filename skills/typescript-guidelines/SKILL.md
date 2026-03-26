---
name: typescript-guidelines
description: |
  Enforce modern TypeScript best practices with strict type safety, Biome linting, and Vitest testing.
  Uses Biome (replaces ESLint+Prettier), TypeScript strict mode, and Vitest.
  Use for: writing TypeScript code, reviewing code, ensuring type safety, configuring projects.
---

# TypeScript Development Guidelines

Automatically enforces modern TypeScript best practices when creating or modifying TypeScript code.

## Quick Start

**Natural language triggers:**
- "Create a TypeScript project with strict typing"
- "Review this TypeScript code for best practices"
- "Configure Biome and TypeScript for this project"
- "Add type safety to this JavaScript code"
- "Set up Vitest for testing"

## Requirements

| Dependency | Version | Purpose |
|------------|---------|---------|
| Node.js | 20+ | Runtime (LTS recommended) |
| TypeScript | 5.7+ | Type checking |
| Biome | 1.9+ | Linting + Formatting (replaces ESLint + Prettier) |
| Vitest | 2.1+ | Testing framework |
| pnpm/npm | Latest | Package management |

## Tool Stack (2025)

### Biome - All-in-One Linter & Formatter
Biome replaces: ESLint, Prettier, and 400+ lint rules in a single Rust-powered binary.

**Why Biome:**
- 10-25x faster than ESLint + Prettier (written in Rust)
- Single tool for lint + format + import sorting
- Zero configuration needed for sensible defaults
- Used by: Vercel, Discord, Shopify

**Biome does NOT replace TypeScript** - still need `tsc` for type checking.

### TypeScript - Static Type Checker
Use `strict: true` for ALL projects. This enables:
- `noImplicitAny` - No implicit any types
- `strictNullChecks` - null/undefined are distinct types
- `strictFunctionTypes` - Strict function parameter checking
- `strictPropertyInitialization` - Class properties must be initialized

**Additional recommended flags:**
- `noUncheckedIndexedAccess` - Adds undefined to index signatures (CRITICAL)
- `exactOptionalPropertyTypes` - Distinguishes missing vs undefined properties
- `verbatimModuleSyntax` - Prevents import ambiguity

### Vitest - Testing Framework
Modern testing with:
- Native TypeScript support (no ts-jest needed)
- Native ESM support (no Babel needed)
- 10-20x faster than Jest
- Hot module replacement in watch mode

## Guideline Domains

| Domain | Resource | When to Load | Status |
|--------|----------|--------------|--------|
| Universal | [universal.md](resources/universal.md) | All TypeScript code | Complete |
| Web/API | [web.md](resources/web.md) | React, Next.js, Node APIs | Complete |
| Testing | [testing.md](resources/testing.md) | Vitest patterns, mocking | Complete |
| Packaging | [packaging.md](resources/packaging.md) | package.json, npm/pnpm | Complete |

## Configuration Tiers

### Minimal (Quick Start)
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  }
}
```

```json
// biome.json
{
  "linter": { "enabled": true, "rules": { "recommended": true } },
  "formatter": { "enabled": true, "indentStyle": "space", "indentWidth": 2 }
}
```

### Standard (Legacy/Migration)
```json
// tsconfig.json additions
{
  "compilerOptions": {
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitOverride": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

```json
// biome.json additions
{
  "linter": {
    "rules": {
      "suspicious": { "noExplicitAny": "error" },
      "complexity": { "noBannedTypes": "error" }
    }
  }
}
```

### Strict (DEFAULT - Most Projects)
```json
// tsconfig.json additions
{
  "compilerOptions": {
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noPropertyAccessFromIndexSignature": true,
    "verbatimModuleSyntax": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  }
}
```

```json
// biome.json additions
{
  "linter": {
    "rules": {
      "suspicious": { "recommended": true },
      "complexity": { "recommended": true },
      "performance": { "recommended": true },
      "style": {
        "useConst": "error",
        "noVar": "error",
        "useTemplate": "error"
      }
    }
  }
}
```

### Enterprise (Full Compliance)
See [templates/tsconfig/enterprise.json](templates/tsconfig/enterprise.json) and [templates/biome/enterprise.json](templates/biome/enterprise.json).

## Key TypeScript Rules

| Rule | Purpose | Tier |
|------|---------|------|
| `strict: true` | Enable all strict checks | ALL |
| `noUncheckedIndexedAccess` | Index access returns T \| undefined | Strict |
| `exactOptionalPropertyTypes` | Missing !== undefined | Strict |
| `verbatimModuleSyntax` | Prevent import ambiguity | Strict |
| `noUnusedLocals` | No unused variables | Enterprise |
| `noUnusedParameters` | No unused parameters | Enterprise |

## Key Biome Rules

| Rule | Purpose | Tier |
|------|---------|------|
| `recommended` | All safe, widely-agreed rules | Minimal |
| `noExplicitAny` | Catch any usage at lint time | Standard |
| `noBannedTypes` | Prevent Object, Function, {} | Standard |
| `useConst` | Prefer const over let | Strict |
| `noVar` | No var declarations | Strict |
| `noConsoleLog` | No console in production | Enterprise |

## Modern Standards (MUST USE)

### ESM Modules Only
```typescript
// ✅ ESM - ALWAYS USE
import { readFile } from 'fs/promises';
export const config = { ... };

// ❌ CommonJS - NEVER USE
const fs = require('fs');
module.exports = { ... };
```

### Proper Type Safety
```typescript
// ✅ Use unknown + type guards
function parse(data: unknown): Config {
  if (!isConfig(data)) throw new Error('Invalid config');
  return data;
}

// ❌ Never use any
function parse(data: any): Config { ... }
```

### Runtime Validation at Boundaries
```typescript
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
});

// Validate external data
const user = UserSchema.parse(untrustedData);
```

## Enforcement Modes

### Strict Mode (New Code)
- All violations reported
- TypeScript strict + additional flags
- No `any` allowed (Biome catches at lint time)
- Load: All applicable domain resources

### Advisory Mode (Code Review)
- Violations reported with severity
- Non-blocking recommendations
- Load: Targeted domain resources

### Incremental Mode (Migration)
- Focus on modified code only
- Gradually enable strict rules
- Load: Relevant patterns only

## Verification

```bash
# Full verification (recommended)
pnpm verify  # or: tsc --noEmit && biome check . && vitest run

# Individual tools
tsc --noEmit           # Type check
biome check .          # Lint + format check
biome check --write .  # Auto-fix
vitest run             # Tests
vitest                 # Watch mode
```

## Integration

Works standalone or composed with domain-specific skills:
- `typescript-guidelines` + `react` → Type-safe React development
- `typescript-guidelines` + `nextjs` → Full-stack Next.js
- `typescript-guidelines` + `node` → Type-safe Node.js APIs

## Version

Based on: **TypeScript Best Practices 2025**
- TypeScript documentation: https://www.typescriptlang.org/
- Biome documentation: https://biomejs.dev/
- Vitest documentation: https://vitest.dev/
- Last updated: 2026-01-05
