```
░▀█▀░█▀▀░░░░░█▀▀░▀█▀░█▀█░█▀█░█▀▄░█▀█░█▀▄░█▀▄░█▀▀
░░█░░▀▀█░▄▄▄░▀▀█░░█░░█▀█░█░█░█░█░█▀█░█▀▄░█░█░▀▀█
░░▀░░▀▀▀░░░░░▀▀▀░░▀░░▀░▀░▀░▀░▀▀░░▀░▀░▀░▀░▀▀░░▀▀▀
```

**Decision: Yes, break it up.**

A 180-line function combining data fetching, transformation, and rendering has mixed concerns. The structural quality standard is explicit: extraction is warranted when a function accumulates mixed concerns (data fetching + transformation + rendering). The secondary trigger also applies: logic that is hard to test because structure fights behavior. A fetch-transform-render monolith cannot be unit tested in any meaningful part without mounting the full component.

**What to extract:**

1. **`useDashboardData` hook** (`src/hooks/useDashboardData.ts`) -- owns the `useEffect`, `fetch`, and async state. Returns a discriminated union `{ status: 'loading' } | { status: 'error'; error: Error } | { status: 'success'; data: DashboardData }`. Includes a `cancelled` flag to prevent state updates after unmount (the manual fetch pattern requires this). Raw `res.json()` returns `any` by default -- it must route through a boundary parser immediately, not flow inward untyped.

2. **Boundary parser** (`src/lib/dashboardSchema.ts`) -- defines a Zod schema as the single source of truth, exports `DashboardData` as `z.infer<typeof Schema>`, exports `parseDashboardResponse(raw: unknown): DashboardData`. Called inside the hook before setting state. Everything downstream receives fully typed data with no scattered re-validation.

3. **Transformation function** (`src/lib/transformDashboardData.ts`) -- pure function, typed inputs and outputs, no React dependency. Testable without mounting anything.

4. **`Dashboard` component** (`src/components/Dashboard.tsx`) -- becomes a coordinator: call the hook, branch on status, call the transformer, render the chart. Readable in under five seconds.

**What not to extract:** Sub-components that are trivial JSX with no independent reuse. If `LoadingState` and `ErrorState` are one-liners, keep them inline. Extraction that adds a layer without reducing complexity is not an improvement.

**Type safety issues to address during extraction:**

- Any `any` on the fetch response -- route through the parser immediately
- Non-null assertions on data fields before fetch success is confirmed
- Unsafe casts on raw response shapes without runtime checks

These are violations, not style preferences. They must be resolved as part of the refactor, not deferred.

**Named exports only** on all extracted modules. No default exports.

| Concern | File |
|---|---|
| Async state + fetch | `src/hooks/useDashboardData.ts` |
| Boundary parsing + schema | `src/lib/dashboardSchema.ts` |
| Data transformation | `src/lib/transformDashboardData.ts` |
| Rendering + orchestration | `src/components/Dashboard.tsx` |
