# TypeScript Guidelines Skill

Modern TypeScript development guidelines with Biome, Vitest, and strict type safety. Zero-config templates for professional TypeScript projects.

## Quick Start

### 1. Choose Your Configuration Tier

| Tier | Use Case | Strictness |
|------|----------|------------|
| **Minimal** | Prototypes, learning | Basic type checking |
| **Standard** | Team projects, production | Balanced strictness |
| **Strict** (DEFAULT) | Professional projects | Maximum type safety |
| **Enterprise** | Large codebases | Strict + organizational rules |

### 2. Copy Configuration Files

```bash
# Copy tsconfig.json (choose your tier)
cp ~/.claude/skills/typescript-guidelines/templates/tsconfig/strict.json ./tsconfig.json

# Copy biome.json (match your tier)
cp ~/.claude/skills/typescript-guidelines/templates/biome/strict.json ./biome.json

# Copy vitest.config.ts
cp ~/.claude/skills/typescript-guidelines/templates/vitest.config.ts ./vitest.config.ts
```

### 3. Install Dependencies

```bash
# Using pnpm (recommended)
pnpm add -D typescript @biomejs/biome vitest @vitest/coverage-v8 @types/node

# Using npm
npm install -D typescript @biomejs/biome vitest @vitest/coverage-v8 @types/node
```

### 4. Add Scripts to package.json

```json
{
  "type": "module",
  "scripts": {
    "build": "tsc",
    "dev": "tsc --watch",
    "typecheck": "tsc --noEmit",
    "lint": "biome check .",
    "lint:fix": "biome check --write .",
    "format": "biome format --write .",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "verify": "npm run typecheck && npm run lint && npm run test"
  }
}
```

## Tool Stack

| Tool | Purpose | Why |
|------|---------|-----|
| **TypeScript 5.7+** | Type checking | Industry standard |
| **Biome** | Linting + Formatting | 10-25x faster than ESLint+Prettier |
| **Vitest** | Testing | Native TS, 10-20x faster than Jest |
| **Zod** | Runtime validation | Type-safe schema validation |
| **pnpm** | Package manager | Fast, disk efficient |

## Resources

### Core Patterns (`resources/universal.md`)

Essential TypeScript patterns for all code:

- **Never use `any`** - Always use `unknown` with type guards
- **Discriminated unions** - Make illegal states unrepresentable
- **Result pattern** - Type-safe error handling
- **Branded types** - Prevent mixing similar primitives
- **Zod validation** - Runtime validation at system boundaries

### Testing (`resources/testing.md`)

Vitest testing patterns:

- Mock functions with `vi.fn()` and `vi.mock()`
- Type-safe mock interfaces
- Async testing with proper timeout handling
- Fake timers for time-dependent code
- Coverage configuration

### Web Development (`resources/web.md`)

Framework-specific patterns:

- **React**: Typed components, hooks, context
- **Next.js**: App Router, Server Actions, API Routes
- **Node.js/Express**: Typed handlers, middleware, error handling
- **API Clients**: Type-safe fetch wrappers with Zod

### Project Setup (`resources/packaging.md`)

Configuration and structure:

- **package.json**: ESM configuration, scripts
- **Project structures**: Library, application, monorepo
- **pnpm workspaces**: Monorepo setup
- **Git configuration**: .gitignore, .npmignore

## Configuration Details

### TypeScript Strict Mode (Required)

The strict tier enables these critical options:

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noPropertyAccessFromIndexSignature": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitOverride": true,
    "verbatimModuleSyntax": true
  }
}
```

**Key setting**: `noUncheckedIndexedAccess` - The most impactful additional strict flag. Returns `T | undefined` for index access.

### Biome Rules

The strict tier enforces:

- **No `any`**: `noExplicitAny: error`
- **Const preference**: `useConst: error`
- **No var**: `noVar: error`
- **Type-only imports**: `useImportType: error`
- **Sorted imports**: `organizeImports: true`

### Vitest Coverage

Minimum thresholds (80%):

```typescript
coverage: {
  thresholds: {
    lines: 80,
    functions: 80,
    branches: 80,
    statements: 80,
  }
}
```

## Verification Script

Run all quality checks:

```bash
# Run verification
~/.claude/skills/typescript-guidelines/scripts/verify.sh

# Auto-fix issues
~/.claude/skills/typescript-guidelines/scripts/verify.sh --fix

# Skip tests
~/.claude/skills/typescript-guidelines/scripts/verify.sh --skip-tests

# Help
~/.claude/skills/typescript-guidelines/scripts/verify.sh --help
```

## Using with Claude Code

### Automatic Application

This skill triggers when Claude detects:
- TypeScript files (`.ts`, `.tsx`)
- `tsconfig.json` in project
- TypeScript-related questions

### Manual Reference

```
@typescript-guidelines Apply strict TypeScript patterns to my code
```

### Example Prompts

```
"Set up a new TypeScript project with strict mode"
"Review my TypeScript code for type safety issues"
"Help me configure Biome for my TypeScript project"
"Write tests for this TypeScript module using Vitest"
"Convert this JavaScript to type-safe TypeScript"
```

## Anti-Patterns to Avoid

### ❌ Never Do This

```typescript
// Using any
function process(data: any) { }  // ❌

// CommonJS
const fs = require('fs');  // ❌
module.exports = { };  // ❌

// Type assertions without validation
const user = data as User;  // ❌

// Ignoring null/undefined
items[0].name  // ❌ (without checking)
```

### ✅ Always Do This

```typescript
// Using unknown with type guards
function process(data: unknown) {
  if (isValidData(data)) { }
}  // ✅

// ESM imports
import { readFile } from 'node:fs/promises';  // ✅
export { };  // ✅

// Zod validation at boundaries
const user = UserSchema.parse(data);  // ✅

// Safe access with checks
if (items[0]) {
  console.log(items[0].name);
}  // ✅
```

## Directory Structure

```
typescript-guidelines/
├── SKILL.md              # Main skill definition
├── README.md             # This file
├── templates/
│   ├── tsconfig/
│   │   ├── minimal.json
│   │   ├── standard.json
│   │   ├── strict.json     # DEFAULT
│   │   └── enterprise.json
│   ├── biome/
│   │   ├── minimal.json
│   │   ├── standard.json
│   │   ├── strict.json     # DEFAULT
│   │   └── enterprise.json
│   └── vitest.config.ts
├── resources/
│   ├── universal.md       # Core TS patterns
│   ├── testing.md         # Vitest patterns
│   ├── web.md             # React/Next/Node patterns
│   └── packaging.md       # Project setup
└── scripts/
    └── verify.sh          # Verification script
```

## Minimum Requirements

- Node.js 20+
- TypeScript 5.7+
- Biome 1.9+
- Vitest 2.1+

## Migration Guide

### From ESLint + Prettier

1. Remove ESLint and Prettier dependencies
2. Delete `.eslintrc.*` and `.prettierrc.*`
3. Copy `biome.json` from templates
4. Run `biome check --write .` to format

### From Jest

1. Remove Jest dependencies
2. Delete `jest.config.*`
3. Copy `vitest.config.ts` from templates
4. Update imports: `jest` → `vitest`
5. Update test scripts in package.json

### From CommonJS

1. Add `"type": "module"` to package.json
2. Change `require()` → `import`
3. Change `module.exports` → `export`
4. Add `.js` extension to relative imports
5. Use `import type` for type-only imports

## References

- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [Biome Documentation](https://biomejs.dev/)
- [Vitest Documentation](https://vitest.dev/)
- [Zod Documentation](https://zod.dev/)
- [Total TypeScript](https://www.totaltypescript.com/)
