# Universal TypeScript Patterns

Core patterns and best practices for all TypeScript code.

## Type Safety Fundamentals

### Never Use `any` - Use `unknown`

```typescript
// ❌ NEVER - any bypasses all type checking
function bad(data: any) {
  return data.whatever; // No error, runtime crash
}

// ✅ ALWAYS - unknown requires type narrowing
function good(data: unknown) {
  if (isValidData(data)) {
    return data.value; // Type-safe after guard
  }
  throw new Error('Invalid data');
}
```

### Type Guards

```typescript
// Custom type guard
function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'email' in value &&
    typeof (value as User).id === 'string' &&
    typeof (value as User).email === 'string'
  );
}

// Usage
function processUser(data: unknown): User {
  if (!isUser(data)) {
    throw new Error('Invalid user data');
  }
  return data; // TypeScript knows this is User
}
```

### Assertion Functions

```typescript
function assertIsUser(value: unknown): asserts value is User {
  if (!isUser(value)) {
    throw new Error('Expected User');
  }
}

// Usage - narrows type after call
function handleUser(data: unknown) {
  assertIsUser(data);
  // data is now User type
  console.log(data.email);
}
```

## Discriminated Unions

The **most important pattern** for type-safe TypeScript.

### Result Type Pattern

```typescript
// Make illegal states unrepresentable
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

// Usage
function divide(a: number, b: number): Result<number, string> {
  if (b === 0) {
    return { success: false, error: 'Division by zero' };
  }
  return { success: true, data: a / b };
}

// Handling
const result = divide(10, 2);
if (result.success) {
  console.log(result.data); // TypeScript knows data exists
} else {
  console.error(result.error); // TypeScript knows error exists
}
```

### State Machine Pattern

```typescript
type LoadingState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };

function renderState<T>(state: LoadingState<T>) {
  switch (state.status) {
    case 'idle':
      return 'Ready to load';
    case 'loading':
      return 'Loading...';
    case 'success':
      return `Data: ${state.data}`; // data is available
    case 'error':
      return `Error: ${state.error.message}`; // error is available
  }
}
```

## Exhaustive Pattern Matching

Ensure all cases are handled at compile time.

```typescript
function assertNever(x: never): never {
  throw new Error(`Unexpected value: ${x}`);
}

type Status = 'pending' | 'approved' | 'rejected';

function handleStatus(status: Status): string {
  switch (status) {
    case 'pending':
      return 'Waiting...';
    case 'approved':
      return 'Done!';
    case 'rejected':
      return 'Failed';
    default:
      return assertNever(status); // Compile error if case missing
  }
}
```

## Branded Types

Prevent mixing up similar primitive types.

```typescript
// Brand types for type safety
type UserId = string & { readonly __brand: 'UserId' };
type OrderId = string & { readonly __brand: 'OrderId' };

// Constructor functions
function createUserId(id: string): UserId {
  return id as UserId;
}

function createOrderId(id: string): OrderId {
  return id as OrderId;
}

// Type-safe functions
function getUser(id: UserId): User { ... }
function getOrder(id: OrderId): Order { ... }

// Usage
const userId = createUserId('user-123');
const orderId = createOrderId('order-456');

getUser(userId);   // ✅ OK
getUser(orderId);  // ❌ Compile error - OrderId is not UserId
```

## Const Assertions

Narrow literal types and create readonly structures.

```typescript
// Without as const - types are widened
const config1 = {
  endpoint: '/api/users',
  method: 'GET',
};
// typeof config1.method = string

// With as const - types are narrowed
const config2 = {
  endpoint: '/api/users',
  method: 'GET',
} as const;
// typeof config2.method = 'GET'

// Array as const
const STATUSES = ['pending', 'approved', 'rejected'] as const;
type Status = (typeof STATUSES)[number]; // 'pending' | 'approved' | 'rejected'
```

## Runtime Validation with Zod

Validate external data at system boundaries.

```typescript
import { z } from 'zod';

// Define schema
const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  age: z.number().int().positive().optional(),
  role: z.enum(['admin', 'user', 'guest']),
  createdAt: z.coerce.date(),
});

// Infer TypeScript type from schema
type User = z.infer<typeof UserSchema>;

// Validate at API boundary
async function createUser(body: unknown): Promise<User> {
  // parse() throws on invalid data
  const validated = UserSchema.parse(body);
  return saveUser(validated);
}

// Safe parsing (doesn't throw)
function parseUser(data: unknown): Result<User, z.ZodError> {
  const result = UserSchema.safeParse(data);
  if (result.success) {
    return { success: true, data: result.data };
  }
  return { success: false, error: result.error };
}
```

## Utility Types

Use built-in utility types effectively.

```typescript
interface User {
  id: string;
  email: string;
  password: string;
  profile: {
    name: string;
    avatar: string;
  };
}

// Partial - all properties optional
type PartialUser = Partial<User>;

// Required - all properties required
type RequiredUser = Required<User>;

// Readonly - all properties readonly
type ReadonlyUser = Readonly<User>;

// Pick - select specific properties
type UserCredentials = Pick<User, 'email' | 'password'>;

// Omit - remove specific properties
type PublicUser = Omit<User, 'password'>;

// Record - key-value mapping
type UserMap = Record<string, User>;

// NonNullable - remove null/undefined
type NonNullEmail = NonNullable<string | null | undefined>; // string

// ReturnType - get function return type
type FetchResult = ReturnType<typeof fetchUser>;

// Parameters - get function parameter types
type FetchParams = Parameters<typeof fetchUser>;

// Awaited - unwrap Promise type
type UserData = Awaited<Promise<User>>; // User
```

## Error Handling

Type-safe error handling patterns.

```typescript
// Custom error classes with discrimination
class ValidationError extends Error {
  readonly _tag = 'ValidationError' as const;
  constructor(
    public readonly field: string,
    message: string,
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

class NetworkError extends Error {
  readonly _tag = 'NetworkError' as const;
  constructor(
    public readonly statusCode: number,
    message: string,
  ) {
    super(message);
    this.name = 'NetworkError';
  }
}

class NotFoundError extends Error {
  readonly _tag = 'NotFoundError' as const;
  constructor(
    public readonly resource: string,
    public readonly id: string,
  ) {
    super(`${resource} with id ${id} not found`);
    this.name = 'NotFoundError';
  }
}

// Union type for all app errors
type AppError = ValidationError | NetworkError | NotFoundError;

// Handle errors with exhaustive matching
function handleError(error: AppError): string {
  switch (error._tag) {
    case 'ValidationError':
      return `Validation failed for ${error.field}: ${error.message}`;
    case 'NetworkError':
      return `Network error (${error.statusCode}): ${error.message}`;
    case 'NotFoundError':
      return `${error.resource} not found: ${error.id}`;
    default:
      return assertNever(error);
  }
}
```

## Async Patterns

Type-safe async code.

```typescript
// Always return Result for fallible operations
async function fetchUser(id: string): Promise<Result<User, AppError>> {
  try {
    const response = await fetch(`/api/users/${id}`);

    if (response.status === 404) {
      return {
        success: false,
        error: new NotFoundError('User', id),
      };
    }

    if (!response.ok) {
      return {
        success: false,
        error: new NetworkError(response.status, response.statusText),
      };
    }

    const data = await response.json();
    const user = UserSchema.parse(data);

    return { success: true, data: user };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        success: false,
        error: new ValidationError('response', error.message),
      };
    }
    return {
      success: false,
      error: new NetworkError(0, error instanceof Error ? error.message : 'Unknown error'),
    };
  }
}

// Using the result
async function displayUser(id: string) {
  const result = await fetchUser(id);

  if (!result.success) {
    console.error(handleError(result.error));
    return;
  }

  console.log(`User: ${result.data.email}`);
}
```

## Generic Constraints

Write reusable, type-safe generic code.

```typescript
// Constrain to objects with id
function findById<T extends { id: string }>(items: T[], id: string): T | undefined {
  return items.find((item) => item.id === id);
}

// Constrain to specific keys
function pick<T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> {
  const result = {} as Pick<T, K>;
  for (const key of keys) {
    result[key] = obj[key];
  }
  return result;
}

// Multiple constraints
function merge<T extends object, U extends object>(a: T, b: U): T & U {
  return { ...a, ...b };
}
```

## Module Best Practices

### ESM Only - No CommonJS

```typescript
// ✅ ESM imports - ALWAYS USE
import { readFile } from 'node:fs/promises';
import { z } from 'zod';
import { type User } from './types.js';

// ✅ ESM exports
export const config = { ... };
export type { User };
export default class UserService { ... }

// ❌ CommonJS - NEVER USE
const fs = require('fs');
module.exports = { ... };
```

### Import Organization

```typescript
// 1. Node.js built-ins (with node: prefix)
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';

// 2. External packages
import { z } from 'zod';
import express from 'express';

// 3. Internal absolute imports
import { config } from '@/config';
import { logger } from '@/utils/logger';

// 4. Relative imports
import { UserService } from './services/user.js';
import type { User } from './types.js';
```

### Type-Only Imports

```typescript
// ✅ Use type-only imports for types
import type { User, Config } from './types.js';
import { type Request, type Response, Router } from 'express';

// Biome enforces this with useImportType and useExportType rules
```
