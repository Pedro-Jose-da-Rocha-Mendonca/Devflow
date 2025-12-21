# Claude Code Project Instructions

## Mandatory Requirements

### Changelog Updates

**CRITICAL**: Before pushing ANY changes to GitHub, you MUST update `CHANGELOG.md`:

1. Add entries to the **current version section** at the top of the changelog
2. Use the format: `- **Category**: Description of change`
3. Categories: `Added`, `Changed`, `Fixed`, `Removed`, `Security`, `Deprecated`
4. **ALWAYS use a proper version number** (e.g., `[1.5.0]`) - NEVER use `[Unreleased]`
5. Check the latest version in the changelog and increment appropriately:
   - Patch (1.5.1): Bug fixes, minor corrections
   - Minor (1.6.0): New features, enhancements
   - Major (2.0.0): Breaking changes
6. **NEVER remove or modify existing changelog entries** - only add new ones

Example entry:
```markdown
## [1.6.0] - 2025-12-21

### Added
- **New Feature** - Description of the new feature

### Fixed
- **Bug Fix** - Description of what was fixed
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
