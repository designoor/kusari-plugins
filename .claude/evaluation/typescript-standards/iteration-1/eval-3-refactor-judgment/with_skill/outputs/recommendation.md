```
░▀█▀░█▀▀░░░░░█▀▀░▀█▀░█▀█░█▀█░█▀▄░█▀█░█▀▄░█▀▄░█▀▀
░░█░░▀▀█░▄▄▄░▀▀█░░█░░█▀█░█░█░█░█░█▀█░█▀▄░█░█░▀▀█
░░▀░░▀▀▀░░░░░▀▀▀░░▀░░▀░▀░▀░▀░▀▀░░▀░▀░▀░▀░▀▀░░▀▀▀
```

# Refactor Recommendation: Dashboard.tsx

## Verdict

Yes, break it up. A 180-line function mixing data fetching, transformation, and rendering is a textbook case of mixed concerns. The skill standard flags this directly:

> "A file or function is accumulating mixed concerns (data fetching + transformation + rendering)" -- extract.

This is not a marginal call. Three distinct responsibilities in one function body means each one is harder to test, harder to read, and harder to change without risking the others.

## Confidence: High

The structural regression is directly visible from the description. No judgment ambiguity here.

## Recommended Decomposition

### 1. Extract data fetching into a custom hook

Replace the raw `useEffect` + `fetch` with a dedicated hook.

```ts
// src/hooks/useDashboardData.ts
import { useState, useEffect } from 'react';
import { z } from 'zod';
import type { DashboardData } from '../types/dashboard';

const DashboardResponseSchema = z.object({
  // define shape here -- single source of truth
});

export type DashboardData = z.infer<typeof DashboardResponseSchema>;

export function useDashboardData(): {
  data: DashboardData | null;
  error: Error | null;
  isLoading: boolean;
} {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();

    async function fetchData(): Promise<void> {
      try {
        const response = await fetch('/api/dashboard', {
          signal: controller.signal,
        });
        const raw: unknown = await response.json();
        const parsed = DashboardResponseSchema.parse(raw);
        setData(parsed);
      } catch (err) {
        if (err instanceof DOMException && err.name === 'AbortError') return;
        setError(err instanceof Error ? err : new Error(String(err)));
      } finally {
        setIsLoading(false);
      }
    }

    fetchData();
    return () => controller.abort();
  }, []);

  return { data, error, isLoading };
}
```

Why this matters beyond separation of concerns:

- **Boundary parsing.** The API response is untyped data entering the system. The skill standard requires parsing it into typed data once at the boundary via a schema (Zod or equivalent), then deriving the TypeScript type from that schema. A raw `fetch` dumping `any` or unvalidated JSON into component state violates this directly.
- **AbortController.** Manual `useEffect` + `fetch` without cleanup is a memory leak on unmount. The hook is the right place to own the lifecycle.
- **Named export.** `useDashboardData` is a named export. No default exports.

### 2. Extract transformation into a pure function

```ts
// src/utils/transformDashboardData.ts
import type { DashboardData } from '../types/dashboard';
import type { ChartConfig } from '../types/chart';

export function transformDashboardData(data: DashboardData): ChartConfig {
  // transformation logic here
  // explicit return type -- this is a public API surface
}
```

Why a separate function and not inline in the hook or component:

- Pure function, independently testable with no React dependency.
- The transformation logic likely has its own complexity (aggregation, formatting, derived calculations). Keeping it in the component means testing it requires rendering a component. Keeping it in the hook means testing it requires mocking fetch.
- If the chart format changes but the API does not (or vice versa), only one file changes.

### 3. Slim down the component

```ts
// src/components/Dashboard.tsx
import { useDashboardData } from '../hooks/useDashboardData';
import { transformDashboardData } from '../utils/transformDashboardData';
import { Chart } from './Chart';

export function Dashboard(): JSX.Element {
  const { data, error, isLoading } = useDashboardData();

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay error={error} />;
  if (!data) return null;

  const chartConfig = transformDashboardData(data);

  return <Chart config={chartConfig} />;
}
```

The component now does one thing: orchestrate loading states and delegate rendering. A reader understands what it does within five seconds.

## What NOT to do

- Do not extract further just because you can. If `Chart` is only used here and the rendering logic is straightforward, keep it as a single component. Extraction that adds a layer without reducing complexity is flagged by the standard as unnecessary.
- Do not create an abstraction layer over `fetch` (a `useApi` generic hook, an `HttpClient` class) unless there are multiple data-fetching hooks that share nontrivial logic (auth headers, retry, caching). One caller does not justify a wrapper.
- Do not add explicit return types to private helpers inside these files if TypeScript infers them correctly. Reserve explicit annotations for exported functions and public API surfaces.

## Standards Applied

| Standard | Finding |
|---|---|
| Structural Quality: When to extract | Mixed concerns (fetch + transform + render) -- extract. High confidence. |
| Boundary parsing | API response must be schema-parsed at the boundary, type derived from schema. |
| Type Safety | Manual fetch without validation likely passes `any` through the component. Fix by parsing with Zod at the hook level. |
| Code Clarity (five-second rule) | 180-line function with three responsibilities fails the test. Post-refactor, each unit passes it. |
| Named exports only | All extracted modules use named exports. |
| Over-typing exclusion | Do not add return types to private internals. Do add them to exported functions. |
