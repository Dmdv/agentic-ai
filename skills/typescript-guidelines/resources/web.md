# Web Development Patterns

TypeScript patterns for React, Next.js, Node.js APIs, and web development.

## React with TypeScript

### Component Props

```typescript
// Interface for props (preferred)
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick: () => void;
  children: React.ReactNode;
}

// Function declaration (PREFERRED - better type inference)
function Button({
  variant,
  size = 'md',
  disabled = false,
  onClick,
  children,
}: ButtonProps) {
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

// Arrow function alternative (also valid)
const ButtonAlt = ({ variant, size = 'md', ...props }: ButtonProps) => {
  return <button {...props} />;
};
```

### Extending HTML Elements

```typescript
// Extend native button props
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant: 'primary' | 'secondary';
  isLoading?: boolean;
}

function Button({
  variant,
  isLoading,
  children,
  disabled,
  ...rest
}: ButtonProps) {
  return (
    <button
      className={`btn btn-${variant}`}
      disabled={disabled || isLoading}
      {...rest}
    >
      {isLoading ? <Spinner /> : children}
    </button>
  );
}
```

### Generic Components

```typescript
// Generic list component
interface ListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor: (item: T) => string;
}

function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return (
    <ul>
      {items.map((item, index) => (
        <li key={keyExtractor(item)}>{renderItem(item, index)}</li>
      ))}
    </ul>
  );
}

// Usage
<List
  items={users}
  renderItem={(user) => <UserCard user={user} />}
  keyExtractor={(user) => user.id}
/>
```

### Typed Hooks

```typescript
// Custom hook with proper types
interface UseAsyncState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

function useAsync<T>(
  asyncFn: () => Promise<T>,
  deps: React.DependencyList = [],
): UseAsyncState<T> {
  const [state, setState] = useState<UseAsyncState<T>>({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    let mounted = true;

    asyncFn()
      .then((data) => {
        if (mounted) setState({ data, loading: false, error: null });
      })
      .catch((error) => {
        if (mounted) setState({ data: null, loading: false, error });
      });

    return () => {
      mounted = false;
    };
  }, deps);

  return state;
}

// Usage
const { data: user, loading, error } = useAsync(() => fetchUser(id), [id]);
```

### Context with TypeScript

```typescript
// Define context type
interface AuthContextType {
  user: User | null;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

// Create context with undefined default
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider component
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = async (credentials: Credentials) => {
    const user = await authService.login(credentials);
    setUser(user);
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        isAuthenticated: user !== null,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// Type-safe hook
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

### Event Handlers

```typescript
// Form events
const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  // Handle form submission
};

// Input events
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  setValue(e.target.value);
};

// Click events
const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
  console.log('Clicked at:', e.clientX, e.clientY);
};

// Keyboard events
const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
  if (e.key === 'Enter') {
    handleSubmit();
  }
};
```

## Next.js App Router

### Page Components

```typescript
// app/users/[id]/page.tsx
interface PageProps {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export default async function UserPage({ params }: PageProps) {
  const { id } = await params;
  const user = await fetchUser(id);

  if (!user) {
    notFound();
  }

  return <UserProfile user={user} />;
}

// Generate metadata
export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { id } = await params;
  const user = await fetchUser(id);

  return {
    title: user?.name ?? 'User Not Found',
    description: user?.bio,
  };
}
```

### Server Actions

```typescript
// app/actions.ts
'use server';

import { z } from 'zod';
import { revalidatePath } from 'next/cache';

const CreateUserSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
});

export async function createUser(formData: FormData) {
  const rawData = {
    name: formData.get('name'),
    email: formData.get('email'),
  };

  const validated = CreateUserSchema.parse(rawData);
  const user = await db.user.create({ data: validated });

  revalidatePath('/users');
  return user;
}
```

### API Routes

```typescript
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

const CreateUserSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const data = CreateUserSchema.parse(body);
    const user = await db.user.create({ data });

    return NextResponse.json(user, { status: 201 });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation failed', details: error.errors },
        { status: 400 },
      );
    }
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const page = parseInt(searchParams.get('page') ?? '1', 10);
  const limit = parseInt(searchParams.get('limit') ?? '10', 10);

  const users = await db.user.findMany({
    skip: (page - 1) * limit,
    take: limit,
  });

  return NextResponse.json(users);
}
```

### Route Handlers with Params

```typescript
// app/api/users/[id]/route.ts
interface RouteContext {
  params: Promise<{ id: string }>;
}

export async function GET(request: NextRequest, { params }: RouteContext) {
  const { id } = await params;
  const user = await db.user.findUnique({ where: { id } });

  if (!user) {
    return NextResponse.json({ error: 'User not found' }, { status: 404 });
  }

  return NextResponse.json(user);
}
```

## Node.js/Express APIs

### Typed Express

```typescript
import express, {
  type Request,
  type Response,
  type NextFunction,
  type RequestHandler,
} from 'express';
import { z } from 'zod';

const app = express();
app.use(express.json());

// Request body type
interface CreateUserBody {
  name: string;
  email: string;
}

// Response type
interface UserResponse {
  id: string;
  name: string;
  email: string;
  createdAt: string;
}

// Typed handler
const createUser: RequestHandler<{}, UserResponse, CreateUserBody> = async (
  req,
  res,
  next,
) => {
  try {
    const user = await userService.create(req.body);
    res.status(201).json(user);
  } catch (error) {
    next(error);
  }
};

app.post('/users', createUser);
```

### Validation Middleware

```typescript
import { z, type ZodSchema } from 'zod';
import type { RequestHandler } from 'express';

function validate<T>(schema: ZodSchema<T>): RequestHandler {
  return (req, res, next) => {
    try {
      req.body = schema.parse(req.body);
      next();
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({
          error: 'Validation failed',
          details: error.errors,
        });
        return;
      }
      next(error);
    }
  };
}

// Usage
const CreateUserSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
});

app.post('/users', validate(CreateUserSchema), createUser);
```

### Error Handling Middleware

```typescript
// Custom error classes
class AppError extends Error {
  constructor(
    public statusCode: number,
    message: string,
    public isOperational = true,
  ) {
    super(message);
    this.name = 'AppError';
  }
}

class NotFoundError extends AppError {
  constructor(resource: string) {
    super(404, `${resource} not found`);
    this.name = 'NotFoundError';
  }
}

class ValidationError extends AppError {
  constructor(message: string) {
    super(400, message);
    this.name = 'ValidationError';
  }
}

// Error handler middleware
const errorHandler: ErrorRequestHandler = (err, req, res, _next) => {
  if (err instanceof AppError) {
    res.status(err.statusCode).json({
      error: err.name,
      message: err.message,
    });
    return;
  }

  // Log unexpected errors
  console.error('Unexpected error:', err);

  res.status(500).json({
    error: 'InternalServerError',
    message: 'Something went wrong',
  });
};

app.use(errorHandler);
```

### Async Handler Wrapper

```typescript
type AsyncHandler = (
  req: Request,
  res: Response,
  next: NextFunction,
) => Promise<void>;

function asyncHandler(fn: AsyncHandler): RequestHandler {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}

// Usage - no try/catch needed
app.get(
  '/users/:id',
  asyncHandler(async (req, res) => {
    const user = await userService.findById(req.params.id);
    if (!user) {
      throw new NotFoundError('User');
    }
    res.json(user);
  }),
);
```

## Type-Safe API Clients

### Fetch Wrapper

```typescript
import { z, type ZodSchema } from 'zod';

interface FetchOptions extends RequestInit {
  params?: Record<string, string>;
}

async function typedFetch<T>(
  url: string,
  schema: ZodSchema<T>,
  options: FetchOptions = {},
): Promise<T> {
  const { params, ...fetchOptions } = options;

  // Add query params
  const fullUrl = params
    ? `${url}?${new URLSearchParams(params).toString()}`
    : url;

  const response = await fetch(fullUrl, {
    ...fetchOptions,
    headers: {
      'Content-Type': 'application/json',
      ...fetchOptions.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  const data = await response.json();
  return schema.parse(data);
}

// Usage
const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
});

const user = await typedFetch('/api/users/1', UserSchema);
// user is typed as { id: string; name: string; email: string }
```

### API Client Class

```typescript
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
});

const UsersSchema = z.array(UserSchema);

type User = z.infer<typeof UserSchema>;

class ApiClient {
  constructor(private baseUrl: string) {}

  private async request<T>(
    path: string,
    schema: z.ZodSchema<T>,
    options?: RequestInit,
  ): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return schema.parse(await response.json());
  }

  async getUsers(): Promise<User[]> {
    return this.request('/users', UsersSchema);
  }

  async getUser(id: string): Promise<User> {
    return this.request(`/users/${id}`, UserSchema);
  }

  async createUser(data: Omit<User, 'id'>): Promise<User> {
    return this.request('/users', UserSchema, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

// Usage
const api = new ApiClient('https://api.example.com');
const users = await api.getUsers();
```

## Environment Variables

```typescript
import { z } from 'zod';

// Define schema for environment variables
const EnvSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  API_KEY: z.string().min(1),
  REDIS_URL: z.string().url().optional(),
});

// Parse and validate
const env = EnvSchema.parse(process.env);

// Export typed env
export const config = {
  isDev: env.NODE_ENV === 'development',
  isProd: env.NODE_ENV === 'production',
  port: env.PORT,
  databaseUrl: env.DATABASE_URL,
  apiKey: env.API_KEY,
  redisUrl: env.REDIS_URL,
} as const;

// Type for the config
export type Config = typeof config;
```
