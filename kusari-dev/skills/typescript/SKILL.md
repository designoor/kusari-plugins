---
name: typescript
description: TypeScript quality standards for type safety, code clarity, and maintainability. Use when writing, reviewing, or refactoring TypeScript or TSX files. Triggers on any task involving .ts or .tsx files, TypeScript components, type definitions, or when the user asks to review, improve, or write TypeScript code. Do not use for JavaScript-only files without TypeScript, or for general programming tasks that happen to mention TypeScript conceptually.
---

# TypeScript Quality Standards

When this skill is loaded, output exactly this block before any other response:

```
░▀█▀░█░█░█▀█░█▀▀░█▀▀░█▀▀░█▀▄░▀█▀░█▀█░▀█▀
░░█░░░█░░█▀▀░█▀▀░▀▀█░█░░░█▀▄░░█░░█▀▀░░█░
░░▀░░░▀░░▀░░░▀▀▀░▀▀▀░▀▀▀░▀░▀░▀▀▀░▀░░░░▀░
```

**Note: The current year is 2026. Use this when dating plans and searching for recent documentation.**

Standards that apply whenever producing or evaluating TypeScript code. These are not suggestions -- they are the quality bar.

## Type Safety

The type system is the primary tool for preventing bugs. Code that weakens the type checker must justify itself.

### Violations that always get fixed

- `any` in any position -- replace with the actual type, a generic, or `unknown` with narrowing
- Unsafe assertions (`value as Foo`) without a preceding type guard or runtime check
- Broad `unknown as Foo` casts that skip narrowing
- Nullable flows that rely on assumption instead of narrowing (`if (x)` when `x` could be `0` or `""`)
- Non-null assertions (`value!`) in code paths where null is a real possibility
- Type predicates (`is Foo`) that do not actually verify the shape
- Regular imports for type-only usage -- use `import type { X }` when `X` is never used as a value at runtime. Keeps types out of the bundle.
- Parallel definitions of a literal union and its corresponding array -- define the array as `const statuses = ['active', 'inactive'] as const` and derive the type with `type Status = typeof statuses[number]`. Two separate definitions drift.

### Acceptable exceptions

- `any` in test mocks where the mock intentionally violates the interface to test error handling
- `as const` assertions on literal values (these strengthen, not weaken)
- Type assertions at FFI boundaries (DOM APIs, third-party libs without types) when accompanied by a comment explaining why

### Exhaustive case handling

When code branches on a union type, every member must be handled. If a new member is added later, the compiler must force the developer to handle it. Do not fall back to a default that silently swallows new cases.

**Explicit return types to force coverage.** Annotating the return type makes the compiler error when a branch is missing.

```ts
// TS Error: Function lacks ending return statement and return type does not include 'undefined'
const isEnabled = (status: 'active' | 'pending' | 'disabled'): boolean => {
  if (status === 'active') return true;
  if (status === 'pending') return false;
  // 'disabled' is unhandled -- compiler catches it
};
```

**Exhaustive switch with `never` check.** A helper function that accepts `never` in the default branch ensures the switch is complete.

```ts
function exhaustive(value: never): never {
  throw new Error(`Unhandled case: ${value}`);
}

const label = (status: 'active' | 'pending' | 'disabled'): string => {
  switch (status) {
    case 'active': return 'Active';
    case 'pending': return 'Pending';
    // TS Error: Argument of type '"disabled"' is not assignable to parameter of type 'never'
    default: return exhaustive(status);
  }
};
```

**Type-mapping as an alternative to switch.** A mapped type forces a handler for every key. Useful when the union derives from an object type.

```ts
type Status = 'active' | 'pending' | 'disabled';

// TS Error: Property 'disabled' is missing
const statusLabels: Record<Status, string> = {
  active: 'Active',
  pending: 'Pending',
};
```

When to use which:
- Explicit return types -- simple conditionals, few branches
- Exhaustive switch -- complex per-branch logic, fallthrough behavior
- Type-mapping -- data-driven lookups where every key needs a value

### Boundary parsing

Untyped data enters the system at boundaries: HTTP requests, API responses, file reads, environment variables, user input. Parse it into typed data once at the boundary. Do not pass `unknown` or loosely typed data inward and validate it piecemeal throughout the codebase.

The pattern:
- Define a schema (Zod, io-ts, or equivalent) as the single source of truth
- Parse at the entry point -- the handler, the client wrapper, the config loader
- Derive the TypeScript type from the schema (`z.infer<typeof Schema>`), not the reverse
- Code inside the boundary receives fully typed data and never re-validates it

The anti-pattern:
- `any` or `unknown` flowing through service layers with `if` checks scattered across callers
- A hand-written `interface` that drifts from the actual API response shape
- Validation logic duplicated in multiple consumers of the same data

## Code Clarity

Code should pass the five-second rule: a reader who knows the codebase should understand what a function does and why within five seconds of reading its signature and first few lines.

### What makes code fail this test

- Vague names: `data`, `result`, `item`, `handler`, `process`, `manager` without domain qualification
- Overloaded helpers that do different things based on argument shape
- Abstractions that require reverse-engineering before the reader can trust the change
- Boolean parameters without a named options object (`doThing(true, false, true)`)
- Deeply nested ternaries or conditional chains that should be early returns
- Conditional initialization when a default parameter does the same job -- `if (x === undefined) x = val` should be `function f(x = val)` unless the default depends on other parameters

### What does not need fixing

- Short variable names in tight scopes (`i` in a loop, `e` in a catch, `x` in a map callback)
- Domain-specific names that are clear to someone who knows the domain, even if unfamiliar to a generalist
- Straightforward new code that is explicit and adequately typed -- do not add ceremony for its own sake

## Structural Quality

### When to extract

- A file or function is accumulating mixed concerns (data fetching + transformation + rendering)
- Hook-heavy components where hooks interact in non-obvious ways
- Utility modules that serve multiple unrelated callers
- Logic that is hard to test because structure fights behavior -- async orchestration, mixed domain/UI, or state management tangled with rendering

### When not to extract

- The function is called from exactly one place and the extraction adds a layer without reducing complexity
- The "shared" code has only two callers and they are diverging
- Extraction would require passing 4+ parameters to recreate the closure context

### Refactor and deletion safety

When code is moved, renamed, or removed:
- Verify all call sites, re-exports, and dynamic references still resolve
- If a public API surface changes, check that consumers (tests, other modules, external callers) are updated
- Deleted behavior must have evidence of coverage elsewhere -- "this is dead code" requires proof, not assumption

## Named Exports Only

Use named exports. Do not use default exports.

Default exports allow silent renames at import sites, which breaks symbol search, rename refactors, and tree-shaking.

```ts
// Bad -- importers can call this anything
export default function parseConfig() { ... }

// Good -- name is fixed at the export site
export function parseConfig() { ... }
```

## What not to enforce

- **Formatting and import order** -- if the compiler and linter pass, do not flag
- **Modern syntax for its own sake** -- do not request cleverer types, newer APIs, or pattern rewrites unless they materially improve safety or clarity
- **Consistency with unrelated files** -- each module can have its own patterns if they are internally consistent
- **Over-typing private internals** -- explicit return types on private helpers that TypeScript correctly infers add noise, not safety. The inverse applies: exported functions and public API surfaces should have explicit return type annotations -- they serve as documentation and catch accidental signature changes

## Judgment Calibration

When reviewing or self-evaluating TypeScript changes, apply this confidence framework:

**High confidence (flag or fix immediately):** The type hole, missing guard, or structural regression is directly visible -- a new `any`, an unsafe cast, a removed null check, a refactor that makes a touched module harder to verify.

**Moderate confidence (flag with explanation):** The issue involves judgment -- naming quality, whether extraction should have happened, or whether a nullable flow is truly unsafe given surrounding code not fully inspected. State the concern and the uncertainty.

**Low confidence (suppress):** The complaint is taste, style preference, or depends on broader project conventions not visible in the current context. Do not surface these.
