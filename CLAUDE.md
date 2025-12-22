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

### Version Synchronization

**CRITICAL**: After updating `CHANGELOG.md` with a new version, you MUST sync versions across all files:

```bash
# Sync README.md and pyproject.toml from CHANGELOG version
python3 tooling/scripts/update_version.py --sync-pyproject
```

This updates:
- `README.md` - Version number and last updated date
- `pyproject.toml` - Package version

You can verify versions are in sync with:
```bash
python3 tooling/scripts/update_version.py --check
```

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

### No Emojis Policy

**CRITICAL**: This project does NOT use emojis in any code, documentation, or output messages.

- **Do NOT use emojis** in code comments, docstrings, or string literals
- **Do NOT use emojis** in documentation (README, CONTRIBUTING, etc.)
- **Do NOT use emojis** in commit messages or changelog entries
- **Do NOT use emojis** in agent personas or output templates
- Use text alternatives instead: `[OK]`, `[WARNING]`, `[ERROR]`, `[INFO]`, etc.

Examples of text alternatives:
- Instead of ✅ use `[OK]` or `[PASS]`
- Instead of ❌ use `[ERROR]` or `[FAIL]`
- Instead of ⚠️ use `[WARNING]`
- Instead of ℹ️ use `[INFO]`
- Instead of 🔴 use `[CRITICAL]` or `[MUST FIX]`
- Instead of 🟡 use `[SHOULD FIX]`
- Instead of 💡 use `[SUGGESTION]` or `[TIP]`
