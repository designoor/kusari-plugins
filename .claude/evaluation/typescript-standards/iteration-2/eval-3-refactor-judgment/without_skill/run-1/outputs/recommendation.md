# Refactor Recommendation: Dashboard.tsx

## Should you break it up?

Yes. A 180-line component function that fetches data, transforms it, and renders a chart violates the single-responsibility principle and creates concrete maintenance problems: the fetch logic cannot be tested independently, the transformation logic cannot be reused, and the render output is entangled with async state management.

## How to break it up

### 1. Extract data fetching into a custom hook

Move the `useEffect` + `fetch` call into a dedicated hook. This isolates async lifecycle concerns from rendering.

```ts
// src/hooks/useDashboardData.ts
import { useState, useEffect } from "react";
import { RawDashboardData } from "../types";

interface UseDashboardDataResult {
  data: RawDashboardData | null;
  loading: boolean;
  error: Error | null;
}

export function useDashboardData(endpoint: string): UseDashboardDataResult {
  const [data, setData] = useState<RawDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;

    setLoading(true);
    fetch(endpoint)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json() as Promise<RawDashboardData>;
      })
      .then((json) => {
        if (!cancelled) {
          setData(json);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error(String(err)));
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [endpoint]);

  return { data, loading, error };
}
```

Note the `cancelled` flag -- the original monolith likely has a stale-closure bug where state is set after unmount. Extraction forces you to fix it.

### 2. Extract transformation into a pure function

Data transformation does not belong in a hook or component. Put it in a plain function that can be unit tested with no React dependency.

```ts
// src/utils/transformDashboardData.ts
import { RawDashboardData, ChartSeries } from "../types";

export function transformDashboardData(raw: RawDashboardData): ChartSeries[] {
  // transformation logic here
}
```

Call it with `useMemo` in the component or hook, depending on where the expense lives.

### 3. Extract the chart into a presentational component

```ts
// src/components/DashboardChart.tsx
import { ChartSeries } from "../types";

interface DashboardChartProps {
  series: ChartSeries[];
}

export function DashboardChart({ series }: DashboardChartProps) {
  // render-only logic, no fetch, no state
}
```

### 4. The resulting Dashboard component

```ts
// src/components/Dashboard.tsx
import { useMemo } from "react";
import { useDashboardData } from "../hooks/useDashboardData";
import { transformDashboardData } from "../utils/transformDashboardData";
import { DashboardChart } from "./DashboardChart";

export function Dashboard() {
  const { data, loading, error } = useDashboardData("/api/dashboard");

  const series = useMemo(
    () => (data ? transformDashboardData(data) : []),
    [data]
  );

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return <DashboardChart series={series} />;
}
```

The component is now under 20 lines.

## Decision criteria summary

| Concern | Where it goes |
|---|---|
| Async fetch + lifecycle | `useDashboardData` hook |
| Data shape transformation | `transformDashboardData` pure function |
| Chart rendering | `DashboardChart` presentational component |
| Orchestration | `Dashboard` (thin, composes the above) |

## What to prioritize first

If you can only do one thing, extract the custom hook. It eliminates the stale-closure risk, makes the fetch logic independently testable, and reduces the component enough to see the remaining structure clearly. The transformation extraction and presentational split follow naturally.

## Consider replacing manual fetch

If the project already uses React Query or SWR, replace the custom hook internals with one of those. They handle caching, deduplication, background refetching, and cancellation correctly. The interface of the hook (`{ data, loading, error }`) stays identical, so the component does not change.

If not already in the project, the custom hook pattern above is sufficient -- do not add a data-fetching library solely for this component.
