# Packaging & Project Setup

Modern TypeScript project configuration with package.json, ESM modules, and tooling.

## Package.json Configuration

### Modern ESM Package

```json
{
  "name": "my-package",
  "version": "1.0.0",
  "description": "A modern TypeScript package",
  "type": "module",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js"
    },
    "./utils": {
      "types": "./dist/utils/index.d.ts",
      "import": "./dist/utils/index.js"
    }
  },
  "files": ["dist"],
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
    "verify": "npm run typecheck && npm run lint && npm run test",
    "prepublishOnly": "npm run verify && npm run build"
  },
  "engines": {
    "node": ">=20.0.0"
  },
  "packageManager": "pnpm@9.0.0"
}
```

### Development Dependencies

```json
{
  "devDependencies": {
    "@biomejs/biome": "^1.9.0",
    "@types/node": "^22.0.0",
    "typescript": "^5.7.0",
    "vitest": "^2.1.0",
    "@vitest/coverage-v8": "^2.1.0"
  }
}
```

### Common Dependencies

```json
{
  "dependencies": {
    "zod": "^3.23.0"
  }
}
```

## Project Structure

### Library/Package

```
my-library/
├── src/
│   ├── index.ts          # Main entry point
│   ├── types.ts          # Shared types
│   └── utils/
│       ├── index.ts
│       └── string.ts
├── tests/
│   ├── index.test.ts
│   └── utils/
│       └── string.test.ts
├── dist/                  # Build output (gitignored)
├── package.json
├── tsconfig.json
├── biome.json
├── vitest.config.ts
└── README.md
```

### Application

```
my-app/
├── src/
│   ├── index.ts          # Entry point
│   ├── config.ts         # Configuration
│   ├── types/
│   │   └── index.ts
│   ├── services/
│   │   ├── user.ts
│   │   └── auth.ts
│   ├── utils/
│   │   └── logger.ts
│   └── routes/           # API routes (if applicable)
│       └── users.ts
├── tests/
│   └── services/
│       └── user.test.ts
├── dist/
├── package.json
├── tsconfig.json
├── biome.json
├── vitest.config.ts
└── .env.example
```

### Monorepo

```
monorepo/
├── packages/
│   ├── shared/           # Shared types/utils
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── api/              # Backend service
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── web/              # Frontend app
│       ├── src/
│       ├── package.json
│       └── tsconfig.json
├── package.json          # Root package.json
├── pnpm-workspace.yaml
├── tsconfig.base.json    # Shared TS config
├── biome.json            # Shared Biome config
└── turbo.json            # Turborepo config (optional)
```

## TypeScript Configuration

### Base Config (tsconfig.base.json)

```json
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022"],
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitOverride": true,
    "forceConsistentCasingInFileNames": true,
    "verbatimModuleSyntax": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  }
}
```

### Project Config (extends base)

```json
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "extends": "./tsconfig.base.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### Monorepo Package Config

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src",
    "composite": true,
    "declarationDir": "dist"
  },
  "include": ["src/**/*"],
  "references": [{ "path": "../shared" }]
}
```

## pnpm Workspace

### pnpm-workspace.yaml

```yaml
packages:
  - 'packages/*'
```

### Root package.json

```json
{
  "name": "monorepo",
  "private": true,
  "type": "module",
  "scripts": {
    "build": "pnpm -r build",
    "test": "pnpm -r test",
    "lint": "biome check .",
    "typecheck": "pnpm -r typecheck"
  },
  "devDependencies": {
    "@biomejs/biome": "^1.9.0",
    "typescript": "^5.7.0"
  }
}
```

## Scripts Reference

### Essential Scripts

```json
{
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
    "verify": "npm run typecheck && npm run lint && npm run test",
    "clean": "rm -rf dist coverage"
  }
}
```

### With tsx for Development

```json
{
  "scripts": {
    "start": "node dist/index.js",
    "dev": "tsx watch src/index.ts",
    "build": "tsc"
  },
  "devDependencies": {
    "tsx": "^4.0.0"
  }
}
```

### With Nodemon Alternative

```json
{
  "scripts": {
    "dev": "tsx watch --clear-screen=false src/index.ts"
  }
}
```

## Makefile Integration

```makefile
.PHONY: build dev test lint typecheck verify clean

# Build
build:
	pnpm build

dev:
	pnpm dev

# Quality
lint:
	pnpm lint

lint-fix:
	pnpm lint:fix

format:
	pnpm format

typecheck:
	pnpm typecheck

# Testing
test:
	pnpm test

test-watch:
	pnpm test:watch

test-coverage:
	pnpm test:coverage

# Full verification
verify: typecheck lint test
	@echo "✅ All checks passed!"

# Clean
clean:
	rm -rf dist coverage node_modules/.cache

# Install
install:
	pnpm install

# CI
ci: install verify build
```

## Git Configuration

### .gitignore

```gitignore
# Dependencies
node_modules/

# Build output
dist/
build/
.next/

# Coverage
coverage/

# Environment
.env
.env.local
.env.*.local

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*
pnpm-debug.log*

# Cache
.cache/
*.tsbuildinfo
```

### .npmignore (for published packages)

```npmignore
# Source (types are in dist)
src/

# Tests
tests/
*.test.ts
*.spec.ts
vitest.config.ts
coverage/

# Config
tsconfig.json
biome.json
.github/

# Dev files
.env*
.gitignore
.npmignore
```

## Publishing Configuration

### For npm

```json
{
  "name": "@scope/package-name",
  "version": "1.0.0",
  "publishConfig": {
    "access": "public",
    "registry": "https://registry.npmjs.org"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/org/repo"
  },
  "keywords": ["typescript"],
  "author": "Your Name",
  "license": "MIT"
}
```

### Semantic Versioning

```bash
# Patch release (bug fixes)
npm version patch

# Minor release (new features, backwards compatible)
npm version minor

# Major release (breaking changes)
npm version major
```

## IDE Configuration

### .vscode/settings.json

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "biomejs.biome",
  "editor.codeActionsOnSave": {
    "quickfix.biome": "explicit",
    "source.organizeImports.biome": "explicit"
  },
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true
}
```

### .vscode/extensions.json

```json
{
  "recommendations": ["biomejs.biome", "vitest.explorer"]
}
```
