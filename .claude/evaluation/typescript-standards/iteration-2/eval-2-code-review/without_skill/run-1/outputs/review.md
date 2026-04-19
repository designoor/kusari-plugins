**File:** `src/utils/dataProcessor.ts`

**Issues**

**1. `any` types throughout (lines 12, 13, 35, 39)**
`data: any`, `result: any`, `getConfig(): any`, `user: any` all disable type checking. Replace with explicit interfaces. `data` should be `unknown` (forces a guard before use) or typed directly as `UserData`. `result` needs a named return interface. `getConfig()` needs a typed config interface. `formatUser`'s `user` param should be `UserData`.

**2. Unsafe type assertion on line 16**
`data as UserData` is not validation. It succeeds regardless of the actual runtime shape. Write a real type guard function (`isUserData(value: unknown): value is UserData`) and use it instead of the `as` cast.

**3. Non-null assertion on line 23**
`config.settings!.timeout` throws a runtime `TypeError` when `APP_CONFIG` is absent (which produces `{}`). Replace with optional chaining and a fallback: `config.settings?.timeout ?? DEFAULT_TIMEOUT`.

**4. `getConfig()` parses unvalidated env input**
`JSON.parse` on a malformed env var throws `SyntaxError`. Wrap in `try/catch` and return a typed default.

**5. Unsafe cast on line 40**
`user.role as 'admin' | 'member' | 'viewer'` does not constrain the runtime value. Validate with an explicit guard using an `as const` array and `includes`.

**6. Default export**
`processData` is a default export while `formatUser` is named. Default exports degrade searchability and refactor consistency. Use named exports throughout.

**7. Inconsistent return shape**
`result.metadata` exists only when `includeMetadata` is true. With `result: any`, this is invisible. Define a `ProcessResult` interface with `metadata?` as optional.

**8. Missing return type on `processData`**
No explicit return type. TypeScript infers `any` because `result` is `any`. Add a return type annotation once the other issues are resolved.

**Priority order:** fix `any` types first, then replace all `as` assertions with runtime guards, then fix the non-null assertion, wrap `getConfig` in try/catch, switch to named export, add return type.
