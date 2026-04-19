# Refactor Recommendation: Dashboard.tsx

## Verdict

Yes, break it up. A 180-line component that fetches, transforms, and renders violates separation of concerns and makes every piece harder to test, reuse, and reason about independently.

## Recommended Decomposition

### 1. Extract data fetching into a custom hook

Create `useDashboardData.ts`. Move the `useEffect` + `fetch` logic there. Return `{ data, isLoading, error }`.

```ts
function useDashboardData(params: DashboardParams) {
  const [data, setData] = useState<RawData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);

    fetch(buildUrl(params))
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((json) => {
        if (!cancelled) setData(json);
      })
      .catch((err) => {
        if (!cancelled) setError(err);
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => { cancelled = true; };
  }, [params]);

  return { data, isLoading, error };
}
```

Key details: the `cancelled` flag prevents state updates after unmount. Dependency array must include everything that should trigger a re-fetch.

Consider replacing the manual fetch with React Query (`@tanstack/react-query`) or SWR if the project already uses either. These libraries handle caching, deduplication, retry, and stale-while-revalidate out of the box, eliminating the need for manual loading/error state management entirely.

### 2. Extract data transformation into a pure function

Create `transformDashboardData.ts`. This function takes the raw API response and returns the shape the chart component expects. Pure function, no hooks, no React imports.

```ts
function transformDashboardData(raw: RawData): ChartData {
  // all mapping, filtering, aggregation logic lives here
}
```

This is the easiest piece to unit test. Do so.

### 3. Keep the component as a thin composition layer

```ts
function Dashboard({ params }: DashboardProps) {
  const { data, isLoading, error } = useDashboardData(params);

  if (isLoading) return <LoadingSkeleton />;
  if (error) return <ErrorDisplay error={error} />;

  const chartData = transformDashboardData(data);

  return <DashboardChart data={chartData} />;
}
```

The component becomes ~15 lines. It composes the hook, the transform, and the presentation. Nothing else.

### 4. Extract the chart rendering if it has significant JSX

If the chart markup is substantial (custom tooltips, legends, responsive wrappers), move it into its own `DashboardChart` component. If it is a single `<BarChart data={chartData} />` call, do not bother.

## Why This Split

| Concern | Location | Testability |
|---|---|---|
| Network I/O | Custom hook | Test with msw or mock fetch |
| Data shaping | Pure function | Direct unit tests, no React needed |
| Rendering | Component | Render tests with mock data, no network |

Each piece changes for exactly one reason. The fetch logic changes when the API changes. The transform changes when business rules change. The component changes when the UI changes.

## What Not To Do

- Do not reach for `useReducer` unless the loading/error/data state transitions are genuinely complex (they usually are not for a single fetch).
- Do not create a generic `useFetch` hook unless you have three or more components with the same pattern. Premature abstraction adds indirection without value.
- Do not split purely for line count. The split is justified here because there are three distinct responsibilities, not because 180 lines is "too many."
