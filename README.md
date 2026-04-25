```
░█░█░█░█░█▀▀░█▀█░█▀▄░▀█▀░░░█▀█░█░░░█░█░█▀▀░▀█▀░█▀█░█▀▀
░█▀▄░█░█░▀▀█░█▀█░█▀▄░░█░░░░█▀▀░█░░░█░█░█░█░░█░░█░█░▀▀█
░▀░▀░▀▀▀░▀▀▀░▀░▀░▀░▀░▀▀▀░░░▀░░░▀▀▀░▀▀▀░▀▀▀░▀▀▀░▀░▀░▀▀▀
```

# kusari-plugins

Claude Code plugin collection.

## Installation

Register the marketplace:
```
/plugin marketplace add designoor/kusari-plugins
```

Install a plugin:
```
/plugin install {plugin name}@kusari-plugins
/reload-plugins
```

## Updating

Pull the latest marketplace index, then reinstall any plugins you use:
```
/plugin marketplace update kusari-plugins
/plugin install {plugin name}@kusari-plugins
/reload-plugins
```

## Plugins

### kusari-meta

Meta-tooling for authoring the rest of the plugin ecosystem: scaffolds new skills, agents, and MCP servers, and evaluates skills through iterative benchmarks.

- `create-skill` guide creation of well-structured plugin skills
- `create-agent` guide creation of plugin agents (subagents)
- `create-mcp` build MCP servers from use case through deployment
- `evaluate-skill` test, measure, and iteratively improve skills

## Working on this repo

`.claude/settings.json` registers the repo itself as a local marketplace and auto-enables `kusari-meta`, so the meta skills are available while authoring new plugins here. After cloning, trust the folder when Claude Code prompts, then invoke skills as `/kusari-meta:create-skill`, `/kusari-meta:create-agent`, `/kusari-meta:create-mcp`, `/kusari-meta:evaluate-skill`.

## License

MIT. See [LICENSE](LICENSE).
