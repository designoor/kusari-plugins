# kusari-plugins

Claude Code plugin collection.

## Installation

Register the marketplace:
```
/plugin marketplace add /Users/ryowa/Repos/kusari-plugins
```

Install a plugin:
```
/plugin install implementation-planner@kusari-plugins
/reload-plugins
```

## Plugins

- **kusari** -- PRD-to-code pipeline. Usage: `/plan <prd-file>` to create an implementation plan, `/execute <step-file>` to execute a step with test-first development, `/review [step-file]` to review uncommitted changes before commit.
