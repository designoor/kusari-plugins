**Issues found in `src/utils/dataProcessor.ts`:**

**1. Default export (line 12)** -- `processData` must be a named export. Default exports break symbol search, rename refactors, and tree-shaking.

**2. `any` throughout (lines 12, 13, 35, 39)** -- `data`, `result`, `getConfig()` return, and `user` parameter are all `any`. Every one needs a real type. `data` should be `unknown` with narrowing. `result` should be a typed interface. `getConfig` is a boundary parse and needs a schema.

**3. Unsafe cast without a type guard (line 16)** -- `data as UserData` does not validate shape at runtime. The surrounding `if (shouldValidate)` boolean does not narrow the type. Must use a schema parse or runtime shape check.

**4. Non-null assertion on a real nullable (line 23)** -- `config.settings!.timeout` will throw at runtime when `APP_CONFIG` is unset, because the fallback `'{}'` produces an object with no `settings` key. The `!` hides a real crash path.

**5. Unsafe cast from unvalidated input (line 40)** -- `user.role as 'admin' | 'member' | 'viewer'` on an `any`-typed object provides no runtime guarantee. An unexpected value silently passes through as a typed string.

**6. Boolean parameter pair (line 12)** -- `shouldValidate: boolean, includeMetadata: boolean` produces illegible call sites. Replace with a named options object.

**7. Missing return type on exported function (line 12)** -- Exported functions require explicit return type annotations. The current inferred type is `any` (because `result` is `any`), which propagates the hole to callers.

**8. Untyped boundary parse in `getConfig` (lines 35-37)** -- `process.env.APP_CONFIG` is external input and must be parsed through a schema at the boundary. The function must return a typed config object, not `any`.
