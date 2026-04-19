```
░▀█▀░█▀▀░░░░░█▀▀░▀█▀░█▀█░█▀█░█▀▄░█▀█░█▀▄░█▀▄░█▀▀
░░█░░▀▀█░▄▄▄░▀▀█░░█░░█▀█░█░█░█░█░█▀█░█▀▄░█░█░▀▀█
░░▀░░▀▀▀░░░░░▀▀▀░░▀░░▀░▀░▀░▀░▀▀░░▀░▀░▀░▀░▀▀░░▀▀▀
```

# Code Review: `src/utils/dataProcessor.ts`

## High Confidence (fix immediately)

### 1. Default export

**Line 12:** `export default function processData`

Default exports allow silent renames at import sites, breaking symbol search and rename refactors. Replace with a named export.

```ts
// Fix
export function processData(...)
```

### 2. `any` on the `data` parameter

**Line 12:** `data: any`

The primary input to the module is completely untyped. Every downstream usage inherits that hole. The `UserData` interface already exists -- use it, or use `unknown` with runtime narrowing at this boundary.

### 3. `any` on `result`

**Line 13:** `const result: any = {}`

The function's return value is `any`, which means every caller loses type safety. Define a return type that describes what this function actually produces (user, timeout, optional metadata). Annotate the return type on the function signature so callers and the compiler can verify correctness.

### 4. `any` return from `getConfig`

**Line 35:** `function getConfig(): any`

`getConfig` parses untyped JSON from an environment variable and returns `any`. This is a boundary -- it should parse into a typed structure. Define a schema or at minimum an interface for the config shape, parse/validate once here, and return typed data. Derive the type from the schema, not the reverse.

```ts
// Fix direction
interface AppConfig {
  settings: {
    timeout: number;
  };
}

function getConfig(): AppConfig {
  const raw: unknown = JSON.parse(process.env.APP_CONFIG || '{}');
  // validate shape here
  return raw as AppConfig; // acceptable only with actual validation preceding it
}
```

### 5. `any` on `formatUser` parameter

**Line 39:** `user: any`

`UserData` is already defined in this file. Use it. As written, `user.name` and `user.role` have no compiler backing.

### 6. Unsafe assertion without type guard

**Line 16:** `const validated = data as UserData`

Casting `any` to `UserData` is not validation. It tells the compiler to trust the shape without any runtime check. The `shouldValidate` flag name implies validation happens here, but nothing is actually verified. Replace with real narrowing -- a schema parse, or at minimum property checks that confirm the shape before assignment.

### 7. Unsafe assertion on `role`

**Line 40:** `const role = user.role as 'admin' | 'member' | 'viewer'`

This narrows `any` to a union with no runtime check. If `user.role` is `'superadmin'` or `undefined`, the cast silently lies. Either validate the value against the union at runtime, or type the parameter so the compiler already guarantees the shape.

### 8. Non-null assertion on a nullable path

**Line 23:** `config.settings!.timeout`

`getConfig` parses `'{}'` as the fallback, which means `settings` will be `undefined` in that case. The `!` assertion suppresses a real null risk. This will throw at runtime. Either guarantee the config shape through validation (see issue 4), or handle the missing case explicitly.

### 9. Parallel type definitions will drift

**Line 9:** `role: string` in `UserData` vs. **Line 40:** `'admin' | 'member' | 'viewer'` literal union in `formatUser`.

The `role` field is typed as `string` on the interface but narrowed to a specific union in a consumer. These two definitions will drift. Define the union once (`as const` array or a type alias) and use it in both places.

```ts
const roles = ['admin', 'member', 'viewer'] as const;
type Role = typeof roles[number];

interface UserData {
  name: string;
  email: string;
  role: Role;
}
```

## Moderate Confidence (flag with explanation)

### 10. Boolean parameters without named options

**Line 12:** `processData(data: any, shouldValidate: boolean, includeMetadata: boolean)`

Call sites will read as `processData(userData, true, false)` -- opaque without jumping to the signature. An options object makes intent visible at the call site.

```ts
interface ProcessOptions {
  shouldValidate: boolean;
  includeMetadata: boolean;
}

export function processData(data: UserData, options: ProcessOptions) { ... }
```

### 11. Vague names: `data`, `result`

`data` could be `userData` or `rawUser`. `result` could be `processedUser` or a named interface like `ProcessedUserResult`. Both fail the five-second rule because they carry no domain meaning.

### 12. No explicit return type on exported function

`processData` is exported but has no return type annotation. The inferred return type is `any` (because `result` is `any`), which means signature changes propagate silently to all callers. Once the `any` on `result` is fixed, add an explicit return type.

### 13. `import type` should be used for `ApiResponse`

**Line 4:** `import { ApiResponse } from '../types'`

`ApiResponse` is imported but never used as a runtime value anywhere in this file. If it were used, it should be `import type { ApiResponse }`. As it stands, the import is also dead code and should be removed entirely.

## Summary

The file has 9 high-confidence violations and 4 moderate-confidence items. The dominant pattern is untyped data flowing through the entire module via `any`, with unsafe assertions substituting for real validation. The fix path:

1. Remove all `any` types -- replace with `UserData`, a config interface, and a concrete return type.
2. Replace `as` casts with runtime narrowing (schema validation at the `getConfig` boundary, shape checks on user data).
3. Define the role union once and derive usage from it.
4. Switch to named export.
5. Remove or convert the unused `ApiResponse` import.
6. Replace boolean parameters with an options object.
