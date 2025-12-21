# Claude Code Project Instructions

## Mandatory Requirements

### Changelog Updates

**CRITICAL**: Before pushing ANY changes to GitHub, you MUST update `CHANGELOG.md`:

1. Add a new entry under the appropriate version section
2. Use the format: `- **Category**: Description of change`
3. Categories: `Added`, `Changed`, `Fixed`, `Removed`, `Security`, `Deprecated`
4. If no unreleased section exists, create one
5. **NEVER remove or modify existing changelog entries** - only add new ones

Example entry:
```markdown
## [Unreleased]

### Added
- New feature description

### Fixed
- Bug fix description
```

This applies to ALL commits being pushed, not just major releases.

### Changelog History Preservation

**IMPORTANT**: The changelog is a historical record. Previous version entries document what was released at that point in time. When making changes:
- Create a **new version entry** for current changes
- Do NOT modify past version entries to reflect current state
- Past entries should remain as they were when released

## Project Context

This is the Devflow (Goal-Driven Stories) Automation project - a workflow automation system for Claude Code that provides structured story-based development.

### Key Directories

- `tooling/.automation/agents/` - Agent persona definitions
- `tooling/.automation/overrides/` - User customizations
- `tooling/.automation/memory/` - Persistent agent learning
- `tooling/scripts/` - Automation scripts
- `tooling/docs/` - Documentation

### Commit Style

Use conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks
