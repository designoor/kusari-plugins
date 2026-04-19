# Code Review: `dataProcessor.ts`

## Critical Issues

### 1. Pervasive `any` usage destroys type safety

Four separate `any` types appear in this file: the `data` parameter (line 12), the `result` variable (line 13), the `getConfig` return type (line 35), and the `user` parameter in `formatUser` (line 39). Every one of these should be replaced with a concrete type or a generic.

**Fix for `processData`:**
- `data` should be typed as `UserData` (or a generic `T`).
- `result` should be a defined return interface, not `any`.

**Fix for `getConfig`:**
- Define a `Config` interface with the expected shape and use it as the return type.

**Fix for `formatUser`:**
- Type the parameter as `UserData`.

### 2. Unsafe type assertions used as substitutes for validation

Line 16: `data as UserData` does not validate anything at runtime. If `data` lacks the required fields, the cast silently passes and downstream code breaks. Line 40: `user.role as 'admin' | 'member' | 'viewer'` is equally hollow.

**Fix:** Replace `as` casts with actual runtime validation (e.g., type guards, schema validation with zod/io-ts, or manual property checks). If you need a type narrowing function:

```typescript
function isUserData(value: unknown): value is UserData {
  return (
    typeof value === 'object' &&
    value !== null &&
    'name' in value &&
    'email' in value &&
    'role' in value
  );
}
```

### 3. Non-null assertion on `config.settings!.timeout` (line 23)

The `!` operator suppresses TypeScript's null check. Given that `getConfig` parses `process.env.APP_CONFIG || '{}'`, the parsed object will frequently lack a `settings` property entirely. This line will throw a runtime `TypeError`.

**Fix:** Use optional chaining with a fallback, or validate the config shape before accessing nested properties:

```typescript
const timeout = config.settings?.timeout ?? DEFAULT_TIMEOUT;
```

### 4. `getConfig` parses environment variable JSON without error handling

`JSON.parse` throws on malformed input. If `APP_CONFIG` contains invalid JSON, the process crashes with an unhandled exception.

**Fix:** Wrap in try/catch, validate the parsed result, and return a typed default on failure.

## Moderate Issues

### 5. `role` on `UserData` is typed as `string` instead of a union

The `UserData` interface declares `role: string`, but `formatUser` casts it to `'admin' | 'member' | 'viewer'`. These two declarations are inconsistent. The interface should use the union type directly:

```typescript
type UserRole = 'admin' | 'member' | 'viewer';

interface UserData {
  name: string;
  email: string;
  role: UserRole;
}
```

### 6. `processData` has a boolean parameter problem

Two boolean parameters (`shouldValidate`, `includeMetadata`) create four behavioral permutations from a single function. This is a code smell. Callers cannot understand the function's behavior without reading its implementation.

**Fix:** Use an options object:

```typescript
interface ProcessOptions {
  validate: boolean;
  includeMetadata: boolean;
}

export function processData(data: UserData, options: ProcessOptions): ProcessedResult {
  // ...
}
```

### 7. Default export on a named function

`export default function processData` is a default export of a named function. Default exports make auto-imports less predictable and refactoring harder. Use a named export instead:

```typescript
export function processData(...)
```

### 8. `processedAt` stores a `Date` object, not a serializable value

Line 27: `processedAt: new Date()` stores a `Date` instance. If this result is serialized to JSON, `Date` becomes a string, but the type does not reflect that. Use `new Date().toISOString()` for explicit serialization, and type the field as `string`.

## Minor Issues

### 9. Unused import

`ApiResponse` (line 4) is imported but never used. Remove it.

### 10. No explicit return type on `processData`

The function returns `any` implicitly because `result` is typed as `any`. Adding an explicit return type forces the implementation to conform to a contract and catches mistakes at compile time.

## Summary

The dominant problem is the complete absence of type safety in a TypeScript file. The `any` types, unsafe casts, and non-null assertion collectively mean TypeScript provides zero guarantees here. Fix the types first; the rest follows.

| Severity | Count |
|----------|-------|
| Critical | 4 |
| Moderate | 4 |
| Minor | 2 |
