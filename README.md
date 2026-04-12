░█░█░█░█░█▀▀░█▀█░█▀▄░▀█▀
░█▀▄░█░█░▀▀█░█▀█░█▀▄░░█░
░▀░▀░▀▀▀░▀▀▀░▀░▀░▀░▀░▀▀▀

# kusari-plugins

Claude Code plugin collection.

## Installation

Register the marketplace:
```
/plugin marketplace add /path/to/repository/kusari-plugins
```

Install a plugin:
```
/plugin install {plugin name}@kusari-plugins
/reload-plugins
```

## Plugins

### kusari-dev

PRD-to-code pipeline. Plan implementation from a PRD, execute steps test-first in an isolated worktree, review diffs, then merge.

- `/plan <prd-file>` analyze PRD and generate step files
- `/build <plan-folder-or-step>` execute steps in a worktree with per-step review
- `/execute <step-file>` run a single step
- `/review [step-file]` multi-agent review of uncommitted changes
- `/finish [step-title]` commit, merge, push, clean up worktree

### kusari-biz

Business evaluation via a panel of investor personas.

- `/evaluate <idea-or-file>` run seven investor personas in parallel and synthesize a consensus report

### kusari-typescript

TypeScript skills loaded on demand when editing TS/TSX.

- `typescript-standards` type safety, clarity, maintainability
- `typescript-architecture` structural review, coupling, abstractions
- `typescript-tests` test design and quality
