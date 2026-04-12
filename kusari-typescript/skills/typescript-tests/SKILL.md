---
name: typescript-tests
description: TypeScript testing standards for writing tests that prove code works and catch real regressions. Use when writing new tests, reviewing test quality, refactoring test suites, or when the user asks to add tests, improve test coverage, fix flaky tests, or evaluate whether existing tests are sufficient. Triggers on any task involving .test.ts, .spec.ts, test utilities, or test infrastructure. Do NOT use for production code quality (use typescript-standards), structural review (use typescript-architecture), or test runner configuration issues unrelated to test design.
---

# TypeScript Tests

When this skill is loaded, output exactly this block before any other response:

```
░▀█▀░█▀▀░░░░░▀█▀░█▀▀░█▀▀░▀█▀░█▀▀
░░█░░▀▀█░▄▄▄░░█░░█▀▀░▀▀█░░█░░▀▀█
░░▀░░▀▀▀░░░░░░▀░░▀▀▀░▀▀▀░░▀░░▀▀▀
```

**Note: The current year is 2026. Use this when searching for recent documentation.**

Standards for writing tests that catch real regressions -- not tests that exist to satisfy a coverage metric. Every test must answer: "what breaks if this test is deleted?"

## Test Structure

### File placement and naming

Place test files adjacent to the module they test. Name them `<module>.test.ts` or `<module>.spec.ts` -- match whichever convention the project already uses.

```ts
// WRONG: tests in a distant __tests__ tree that mirrors src/
src/
  services/
    billing.ts
__tests__/
  services/
    billing.test.ts   // reader must mentally map the path

// CORRECT: co-located
src/
  services/
    billing.ts
    billing.test.ts   // one glance shows coverage exists
```

Exception: integration tests that span multiple modules belong in a top-level `tests/` or `test/` directory.

### Test naming

Each test name states three things: what is being tested, under what condition, and the expected outcome.

```ts
// WRONG: no condition, no expected outcome
it("processes order", () => { /* ... */ });

// CORRECT: what / condition / outcome
it("applies 15% discount when coupon is valid and order exceeds $50", () => { /* ... */ });
it("rejects order when inventory is insufficient", () => { /* ... */ });
```

### Describe/test organization

Group by behavior, not by method name. A `describe` block answers "when X happens" -- not "the processOrder function."

```ts
// WRONG: mirrors the implementation structure
describe("OrderService", () => {
  describe("processOrder", () => {
    it("should call validateOrder", () => { /* ... */ });
    it("should call calculateTotal", () => { /* ... */ });
  });
});

// CORRECT: describes behavioral scenarios
describe("order processing", () => {
  it("applies discount when coupon is valid", () => { /* ... */ });
  it("rejects order when inventory is insufficient", () => { /* ... */ });
  it("charges tax based on shipping address", () => { /* ... */ });
});
```

### Test body structure

Structure each test as Arrange (set up preconditions), Act (call the thing being tested), Assert (verify the outcome). When any phase bleeds into another, the test becomes harder to diagnose on failure.

### Setup/teardown boundaries

`beforeEach` sets up the minimum shared precondition. If a test needs additional setup beyond the shared baseline, that setup belongs inside the test body -- not in a broader `beforeAll` that makes individual tests harder to read in isolation.

```ts
// WRONG: beforeAll does too much, individual tests are unreadable without scrolling up
beforeAll(() => {
  db = createTestDb();
  user = createUser({ role: "admin", plan: "enterprise", region: "eu" });
  org = createOrg({ owner: user, tier: "premium" });
});

// CORRECT: beforeEach provides the minimal shared baseline
beforeEach(() => {
  db = createTestDb();
});

it("enterprise users see billing dashboard", () => {
  const user = createUser({ role: "admin", plan: "enterprise" });
  // test-specific setup is visible in the test
});
```

## Typed Test Data

Test data must be typed. When a production interface changes, untyped test fixtures silently drift -- the test passes against a shape that no longer matches reality.

```ts
// WRONG: untyped literal hides mismatches when Order changes
const order = {
  id: "1",
  total: 100,
  status: "active",
} as any;

// WRONG: partial literal without type annotation
const order = { id: "1", total: 100 };
// If Order gains a required field, this test still compiles

// CORRECT: typed against the production interface
const order: Order = {
  id: "1",
  total: 100,
  status: "active",
};
// Adding a required field to Order breaks this -- which is what you want
```

For complex types where constructing a full valid object is tedious, use a typed factory:

```ts
function createOrder(overrides: Partial<Order> = {}): Order {
  return {
    id: "default-id",
    total: 0,
    status: "pending",
    ...overrides,
  };
}

it("applies discount", () => {
  const order = createOrder({ total: 100 });
  expect(applyDiscount(order, 0.1)).toBe(90);
});
```

The factory centralizes defaults, so when `Order` gains a required field, you fix one function -- not every test file.

### Realistic values, not placeholders

Test data should resemble production data. Placeholder values like `"foo"`, `"test"`, and `123` obscure what the test exercises and hide boundary issues.

```ts
// WRONG: placeholders hide intent
const user = createUser({ name: "foo", email: "test", age: 1 });

// CORRECT: realistic data makes the scenario legible
const user = createUser({ name: "Alice Chen", email: "alice@example.com", age: 34 });
```

When a test targets a specific boundary (empty string, zero, max length), the placeholder-style value is fine -- it is the point of the test, not lazy fill.

## Assertions

### Assert behavior, not implementation

A test should break when behavior changes -- not when internal structure is refactored. If renaming a private method or reordering internal steps breaks the test, the test is coupled to implementation.

```ts
// WRONG: asserts internal call sequence
it("processes payment", () => {
  processPayment(order);
  expect(mockValidator.validate).toHaveBeenCalledBefore(mockCharger.charge);
  expect(mockCharger.charge).toHaveBeenCalledTimes(1);
  expect(mockReceipt.generate).toHaveBeenCalledWith(order.id);
});

// CORRECT: asserts observable outcome
it("processes payment", () => {
  const result = processPayment(order);
  expect(result.status).toBe("charged");
  expect(result.receiptId).toBeDefined();
  expect(result.amount).toBe(order.total);
});
```

### Specific values over truthiness

Truthiness assertions (`toBeTruthy`, `toBeDefined`, `not.toBeNull`) prove existence, not correctness. A function returning `"error"` passes `toBeTruthy`.

```ts
// WRONG: proves the function returns something, not the right thing
expect(calculateDiscount(order)).toBeTruthy();
expect(user.email).toBeDefined();

// CORRECT: proves the exact expected value
expect(calculateDiscount(order)).toBe(0.15);
expect(user.email).toBe("test@example.com");
```

When the exact value is non-deterministic (timestamps, UUIDs), assert the shape:

```ts
expect(result.id).toMatch(/^[0-9a-f]{8}-/); // UUID prefix
expect(result.createdAt).toBeInstanceOf(Date);
```

### Error path assertions

Test that errors fire correctly -- not just that the happy path works. Every `catch`, error return, or fallback branch introduced in new code should have a corresponding test that triggers it.

```ts
// WRONG: only tests the happy path
it("fetches user", async () => {
  const user = await getUser("valid-id");
  expect(user.name).toBe("Alice");
});

// CORRECT: also tests the failure mode
it("throws NotFoundError for missing user", async () => {
  await expect(getUser("nonexistent")).rejects.toThrow(NotFoundError);
});

it("throws ValidationError for malformed id", async () => {
  await expect(getUser("")).rejects.toThrow(ValidationError);
});
```

## Mocking Boundaries

### What to mock

Mock things that are **external to the unit's logic and non-deterministic or slow**:

- Network I/O (HTTP clients, database queries, message queues)
- Time (`Date.now`, timers)
- Randomness (`Math.random`, UUID generators)
- File system access in unit tests
- Third-party service SDKs

### What never to mock

- **The code under test.** If you mock half the function to test the other half, rewrite the function.
- **Pure transformations.** If a helper takes input and returns output with no side effects, call it directly.
- **Data structures.** Do not mock arrays, maps, or plain objects. Construct real ones.

```ts
// WRONG: mocking the thing being tested
it("formats currency", () => {
  vi.spyOn(formatter, "addSymbol").mockReturnValue("$10.00");
  expect(formatter.format(1000)).toBe("$10.00");
  // This tests that the mock works, not that format() works
});

// WRONG: mocking a pure utility
vi.mock("../utils/math", () => ({ sum: vi.fn(() => 10) }));
// Just call sum() -- it has no side effects
```

### Mock scoping and cleanup

Mocks must not leak between tests. Use `vi.restoreAllMocks()` in `afterEach` or use Vitest's `mockReset` configuration. Never rely on test execution order.

```ts
afterEach(() => {
  vi.restoreAllMocks();
});
```

When a mock is scoped to a single test, define it inside that test -- not in a shared `beforeEach` where unrelated tests might inherit it.

## Test Isolation

### No shared mutable state

Tests that share mutable state are order-dependent. They pass in isolation, fail in sequence (or vice versa), and produce flaky CI.

```ts
// WRONG: shared array mutated across tests
const items: string[] = [];

it("adds item", () => {
  items.push("a");
  expect(items).toHaveLength(1);
});

it("starts empty", () => {
  expect(items).toHaveLength(0); // FAILS -- previous test mutated it
});

// CORRECT: each test owns its state
it("adds item", () => {
  const items: string[] = [];
  items.push("a");
  expect(items).toHaveLength(1);
});
```

### Parallel-safe by default

Write tests assuming they run in parallel. No fixed ports, no global singletons, no reliance on file system paths that collide. If a test needs a unique resource, generate it:

```ts
const dbName = `test_${randomUUID().slice(0, 8)}`;
```

## Coverage That Matters

### Every behavioral branch gets a test

When new code introduces `if/else`, `switch`, `try/catch`, or conditional logic that changes observable behavior, each branch needs at least one test that exercises it. Trace each branch and confirm coverage.

Branches that only affect logging, telemetry, or debug output do not require dedicated tests.

### Error paths and edge cases over happy-path redundancy

Three tests for the happy path with slightly different valid inputs add less value than one happy-path test plus one test for each distinct failure mode. Prioritize:

1. Each error/rejection path
2. Boundary values (empty arrays, zero, max length, null where nullable)
3. State transitions (first call vs subsequent calls, empty vs populated)

### When NOT to test

- Trivial getters/setters with no logic
- Framework glue code (route declarations, module registrations) -- the framework tests itself
- Type-only code (interfaces, type aliases) -- the compiler verifies these
- One-line re-exports or delegation with no added behavior
- Configuration objects that are validated by the consuming library

## Anti-Patterns

### False confidence

Tests that pass but prove nothing. They exist to inflate coverage numbers.

Signals:
- Calls a function but only asserts it does not throw
- Asserts `toBeDefined` on a value that is always defined by construction
- Mocks so heavily that the test verifies the mock wiring, not the code
- Snapshot tests on internal data structures that change with every refactor

```ts
// FALSE CONFIDENCE: this "test" passes for any implementation
it("processes data", () => {
  expect(() => processData(input)).not.toThrow();
});

// FALSE CONFIDENCE: snapshot of internals
it("builds config", () => {
  expect(buildConfig()).toMatchSnapshot();
  // Any change triggers update -- reviewer rubber-stamps "update snapshots"
});
```

### Implementation coupling

Tests that break when you refactor without changing behavior. These are worse than no test because they punish improvement.

Signals:
- Asserting exact call counts on mocks when the count is an implementation detail
- Testing private methods directly (bypassing the public interface)
- Asserting execution order when order does not affect the outcome
- Snapshot tests on intermediate representations

```ts
// COUPLED: breaks if internals are reordered
expect(mockLogger.info).toHaveBeenCalledTimes(3);
expect(mockCache.set).toHaveBeenCalledBefore(mockDb.write);

// DECOUPLED: asserts the outcome, not the path
expect(result.saved).toBe(true);
expect(await db.find(id)).toEqual(expectedRecord);
```

### Snapshot abuse

Snapshots are appropriate for **stable, human-readable output** (rendered HTML, CLI output, serialized configs). They are inappropriate for:

- Internal object shapes that change frequently
- Large JSON blobs where the meaningful assertion is buried in noise
- Anything where "update snapshots" becomes a reflexive CI fix

If a snapshot test fails and the correct response is always "update it," the test is not protecting anything.

### Over-mocking

When more than 50% of a test's lines are mock setup, the test is testing its own scaffolding. This usually means the code under test has too many dependencies -- consider restructuring the production code so the unit can be tested with fewer mocks.

```ts
// OVER-MOCKED: 15 lines of setup, 2 lines of actual test
vi.mock("../auth");
vi.mock("../db");
vi.mock("../cache");
vi.mock("../logger");
vi.mock("../metrics");
vi.mock("../queue");
// ... more mocks ...

it("creates user", async () => {
  const user = await createUser(input);
  expect(user.id).toBeDefined();
});
// If this needs 6 mocks, createUser is doing too much
```

### Timers and sleeps in tests

Real timers (`setTimeout`, `sleep`, `new Promise(r => setTimeout(r, N))`) in tests cause flakiness. They pass on fast machines and fail on slow CI runners. Use fake timers or framework-provided async utilities.

```ts
// WRONG: real delay -- flaky, slow
it("debounces input", async () => {
  triggerInput("hello");
  await new Promise((r) => setTimeout(r, 500));
  expect(callback).toHaveBeenCalledOnce();
});

// CORRECT: fake timers -- deterministic, instant
it("debounces input", async () => {
  vi.useFakeTimers();
  triggerInput("hello");
  await vi.advanceTimersByTimeAsync(500);
  expect(callback).toHaveBeenCalledOnce();
  vi.useRealTimers();
});
```
