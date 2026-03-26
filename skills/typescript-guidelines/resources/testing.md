# Testing Patterns with Vitest

Modern TypeScript testing with Vitest - native TypeScript support, no configuration needed.

## Basic Test Structure

```typescript
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { UserService } from './user-service.js';
import type { User } from './types.js';

describe('UserService', () => {
  let service: UserService;

  beforeEach(() => {
    service = new UserService();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should create user with valid data', async () => {
    const user = await service.create({
      name: 'Alice',
      email: 'alice@example.com',
    });

    expect(user).toMatchObject({
      name: 'Alice',
      email: 'alice@example.com',
    });
    expect(user.id).toBeDefined();
  });

  it('should throw on invalid email', async () => {
    await expect(
      service.create({ name: 'Bob', email: 'invalid' }),
    ).rejects.toThrow('Invalid email');
  });
});
```

## Test Organization

### Group Related Tests

```typescript
describe('UserService', () => {
  describe('create', () => {
    it('should create user with valid data', () => { ... });
    it('should generate unique id', () => { ... });
    it('should throw on duplicate email', () => { ... });
  });

  describe('findById', () => {
    it('should return user when found', () => { ... });
    it('should return null when not found', () => { ... });
  });

  describe('update', () => {
    it('should update existing user', () => { ... });
    it('should throw when user not found', () => { ... });
  });
});
```

### Test Naming Conventions

```typescript
// Pattern: should [expected behavior] when [condition]
it('should return null when user not found', () => { ... });
it('should throw ValidationError when email is invalid', () => { ... });
it('should emit event when user is created', () => { ... });
```

## Mocking with `vi`

### Mock Functions

```typescript
import { vi, type Mock } from 'vitest';

// Create mock function
const mockFn = vi.fn();

// With implementation
const mockAdd = vi.fn((a: number, b: number) => a + b);

// With return value
const mockGetUser = vi.fn().mockReturnValue({ id: '1', name: 'Alice' });

// With resolved value (async)
const mockFetchUser = vi.fn().mockResolvedValue({ id: '1', name: 'Alice' });

// With rejected value
const mockFailingFetch = vi.fn().mockRejectedValue(new Error('Network error'));

// Assertions
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledTimes(2);
expect(mockFn).toHaveBeenCalledWith('arg1', 'arg2');
expect(mockFn).toHaveBeenLastCalledWith('final');
```

### Mock Modules

```typescript
// Mock entire module
vi.mock('./database.js', () => ({
  db: {
    query: vi.fn(),
    connect: vi.fn(),
  },
}));

// Mock with factory (hoisted)
vi.mock('./config.js', () => ({
  config: {
    apiUrl: 'http://test.api',
    timeout: 1000,
  },
}));

// Access mocked module
import { db } from './database.js';

it('should query database', async () => {
  vi.mocked(db.query).mockResolvedValue([{ id: '1' }]);

  const result = await service.findAll();

  expect(db.query).toHaveBeenCalledWith('SELECT * FROM users');
  expect(result).toHaveLength(1);
});
```

### Spy on Methods

```typescript
import { vi } from 'vitest';

const user = {
  name: 'Alice',
  greet() {
    return `Hello, ${this.name}`;
  },
};

// Spy on method (keeps original implementation)
const spy = vi.spyOn(user, 'greet');

user.greet();

expect(spy).toHaveBeenCalled();
expect(spy).toHaveReturnedWith('Hello, Alice');

// Spy and replace implementation
vi.spyOn(user, 'greet').mockReturnValue('Mocked greeting');
```

### Mock Globals

```typescript
// Mock fetch
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

// Mock Date
vi.useFakeTimers();
vi.setSystemTime(new Date('2024-01-01'));

// Clean up
afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
});
```

## Type-Safe Mocks

```typescript
import { vi, type Mock, type MockedFunction } from 'vitest';

// Type-safe mock interface
interface UserRepository {
  findById(id: string): Promise<User | null>;
  save(user: User): Promise<User>;
  delete(id: string): Promise<void>;
}

// Create typed mock
function createMockRepository(): {
  [K in keyof UserRepository]: MockedFunction<UserRepository[K]>;
} {
  return {
    findById: vi.fn(),
    save: vi.fn(),
    delete: vi.fn(),
  };
}

// Usage
describe('UserService', () => {
  let mockRepo: ReturnType<typeof createMockRepository>;
  let service: UserService;

  beforeEach(() => {
    mockRepo = createMockRepository();
    service = new UserService(mockRepo);
  });

  it('should find user by id', async () => {
    const mockUser: User = { id: '1', name: 'Alice', email: 'alice@test.com' };
    mockRepo.findById.mockResolvedValue(mockUser);

    const result = await service.getUser('1');

    expect(result).toEqual(mockUser);
    expect(mockRepo.findById).toHaveBeenCalledWith('1');
  });
});
```

## Async Testing

### Promises

```typescript
// Resolved promise
it('should resolve with data', async () => {
  const result = await fetchUser('1');
  expect(result).toMatchObject({ id: '1' });
});

// Alternative syntax
it('should resolve with data', () => {
  return expect(fetchUser('1')).resolves.toMatchObject({ id: '1' });
});

// Rejected promise
it('should reject on error', async () => {
  await expect(fetchUser('invalid')).rejects.toThrow('Not found');
});

// Alternative syntax
it('should reject on error', () => {
  return expect(fetchUser('invalid')).rejects.toThrow('Not found');
});
```

### Timers

```typescript
import { vi, beforeEach, afterEach } from 'vitest';

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
});

it('should debounce calls', async () => {
  const callback = vi.fn();
  const debounced = debounce(callback, 100);

  debounced();
  debounced();
  debounced();

  expect(callback).not.toHaveBeenCalled();

  await vi.advanceTimersByTimeAsync(100);

  expect(callback).toHaveBeenCalledTimes(1);
});

it('should retry with exponential backoff', async () => {
  const mockFetch = vi.fn()
    .mockRejectedValueOnce(new Error('Fail 1'))
    .mockRejectedValueOnce(new Error('Fail 2'))
    .mockResolvedValue({ data: 'success' });

  const promise = fetchWithRetry(mockFetch);

  // Advance through retries
  await vi.advanceTimersByTimeAsync(1000); // 1st retry
  await vi.advanceTimersByTimeAsync(2000); // 2nd retry

  const result = await promise;
  expect(result).toEqual({ data: 'success' });
  expect(mockFetch).toHaveBeenCalledTimes(3);
});
```

## Snapshot Testing

```typescript
// Object snapshots
it('should match snapshot', () => {
  const user = createUser({ name: 'Alice', email: 'alice@test.com' });
  expect(user).toMatchSnapshot();
});

// Inline snapshots (auto-updated)
it('should match inline snapshot', () => {
  const result = formatUser({ name: 'Alice', email: 'alice@test.com' });
  expect(result).toMatchInlineSnapshot(`
    {
      "displayName": "Alice",
      "email": "alice@test.com",
      "initials": "A",
    }
  `);
});

// Update snapshots: vitest -u
```

## Test Fixtures

### Setup and Teardown

```typescript
import { beforeAll, afterAll, beforeEach, afterEach } from 'vitest';

// Run once before all tests in file
beforeAll(async () => {
  await database.connect();
});

// Run once after all tests in file
afterAll(async () => {
  await database.disconnect();
});

// Run before each test
beforeEach(async () => {
  await database.clear();
  await database.seed();
});

// Run after each test
afterEach(() => {
  vi.restoreAllMocks();
});
```

### Factory Functions

```typescript
// User factory with defaults
function createUser(overrides: Partial<User> = {}): User {
  return {
    id: crypto.randomUUID(),
    name: 'Test User',
    email: 'test@example.com',
    createdAt: new Date(),
    ...overrides,
  };
}

// Usage in tests
it('should update user name', async () => {
  const user = createUser({ name: 'Original' });
  const updated = await service.updateName(user.id, 'Updated');
  expect(updated.name).toBe('Updated');
});
```

## Testing Error Handling

```typescript
// Test thrown errors
it('should throw ValidationError for invalid email', () => {
  expect(() => validateEmail('invalid')).toThrow(ValidationError);
  expect(() => validateEmail('invalid')).toThrow('Invalid email format');
});

// Test error properties
it('should include field in ValidationError', () => {
  try {
    validateEmail('invalid');
    expect.fail('Should have thrown');
  } catch (error) {
    expect(error).toBeInstanceOf(ValidationError);
    expect((error as ValidationError).field).toBe('email');
  }
});

// Async error testing
it('should reject with NotFoundError', async () => {
  await expect(service.getUser('nonexistent')).rejects.toThrow(NotFoundError);
});
```

## Coverage Configuration

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        '**/*.d.ts',
        '**/*.test.ts',
        '**/*.spec.ts',
        '**/index.ts',
        '**/types.ts',
        '**/mocks/**',
        'node_modules/**',
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
  },
});
```

Run with coverage:
```bash
vitest run --coverage
```

## Test Scripts

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "test:ui": "vitest --ui"
  }
}
```

## Best Practices

### 1. Test Behavior, Not Implementation

```typescript
// ❌ Testing implementation details
it('should call repository.save', async () => {
  await service.createUser(data);
  expect(mockRepo.save).toHaveBeenCalled();
});

// ✅ Testing behavior
it('should create user with generated id', async () => {
  const result = await service.createUser({ name: 'Alice' });
  expect(result.id).toBeDefined();
  expect(result.name).toBe('Alice');
});
```

### 2. One Assertion Concept Per Test

```typescript
// ❌ Multiple unrelated assertions
it('should create user', async () => {
  const user = await service.create(data);
  expect(user.id).toBeDefined();
  expect(user.createdAt).toBeInstanceOf(Date);
  expect(mockEmail.send).toHaveBeenCalled();
  expect(mockAnalytics.track).toHaveBeenCalled();
});

// ✅ Focused tests
it('should generate id for new user', async () => {
  const user = await service.create(data);
  expect(user.id).toBeDefined();
});

it('should send welcome email', async () => {
  await service.create(data);
  expect(mockEmail.send).toHaveBeenCalledWith(
    expect.objectContaining({ template: 'welcome' }),
  );
});
```

### 3. Use Descriptive Test Names

```typescript
// ❌ Vague names
it('works', () => { ... });
it('handles error', () => { ... });

// ✅ Descriptive names
it('should return user when found by valid id', () => { ... });
it('should throw NotFoundError when user does not exist', () => { ... });
```

### 4. Avoid Test Interdependence

```typescript
// ❌ Tests depend on order
let userId: string;

it('should create user', async () => {
  const user = await service.create(data);
  userId = user.id; // Shared state!
});

it('should find created user', async () => {
  const user = await service.findById(userId); // Depends on previous test!
});

// ✅ Independent tests
it('should find user by id', async () => {
  const created = await service.create(data);
  const found = await service.findById(created.id);
  expect(found).toEqual(created);
});
```
