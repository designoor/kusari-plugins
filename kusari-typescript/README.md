```
░█░█░█░█░█▀▀░█▀█░█▀▄░▀█▀░░░░░▀█▀░█░█░█▀█░█▀▀░█▀▀░█▀▀░█▀▄░▀█▀░█▀█░▀█▀
░█▀▄░█░█░▀▀█░█▀█░█▀▄░░█░░▄▄▄░░█░░░█░░█▀▀░█▀▀░▀▀█░█░░░█▀▄░░█░░█▀▀░░█░
░▀░▀░▀▀▀░▀▀▀░▀░▀░▀░▀░▀▀▀░░░░░░▀░░░▀░░▀░░░▀▀▀░▀▀▀░▀▀▀░▀░▀░▀▀▀░▀░░░░▀░
```

# kusari-typescript

TypeScript skills for writing, reviewing, and refactoring TypeScript code.

## Skills

### typescript-standards

Quality standards for type safety, code clarity, and maintainability in `.ts` / `.tsx` files. Covers writing new TypeScript, reviewing existing code, and refactoring for readability and correct typing.

Triggers: any task touching TypeScript source, type definitions, or TSX components.

### typescript-architecture

Structural maintainability: premature abstraction, unnecessary indirection, dead code, cross-module coupling, over-engineered types. Use when creating new modules, designing interfaces and module boundaries, refactoring across files, or performing a structural review.

Triggers: "check for dead code", "find unnecessary abstractions", "check coupling", "simplify types", architectural review requests.

### typescript-tests

Testing standards for tests that prove code works and catch real regressions. Covers new test authoring, test-suite refactoring, coverage evaluation, and flaky-test diagnosis.

Triggers: any task touching `.test.ts`, `.spec.ts`, test utilities, or test infrastructure.

## Components

| Type | Name | Purpose |
|------|------|---------|
| Skill | typescript-standards | Type safety, clarity, maintainability for TS/TSX |
| Skill | typescript-architecture | Structural review, coupling, abstraction, dead code |
| Skill | typescript-tests | Test design and quality standards |

## Separation of concerns

The three skills are deliberately disjoint. Each description includes explicit `Do NOT use` clauses so the model routes the right skill for the task instead of loading all three. If a task spans more than one, the model loads each at the phase where it applies.
