# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Development Commands

```bash
# Validate setup and Python environment
python3 tooling/scripts/validate_setup.py

# Run a story pipeline
python3 tooling/scripts/run-story.py <story-key> [--develop|--review|--context]

# Cost dashboard
python3 tooling/scripts/cost_dashboard.py [--history 10] [--story <key>]

# Version sync (after updating CHANGELOG.md)
python3 tooling/scripts/update_version.py        # Sync all files
python3 tooling/scripts/update_version.py --check  # Verify sync

# Agent personalization
python3 tooling/scripts/personalize_agent.py [agent-name]

# Validate overrides
python3 tooling/scripts/validate-overrides.py
```

## Architecture Overview

### Dual-Layer CLI System

The project has two entry points that work together:

1. **Node.js CLI** (`bin/`) - npm package entry points
   - `devflow.js` - Main dispatcher, routes commands to `devflow-*.js` scripts
   - Each `devflow-*.js` uses `lib/exec-python.js` to call Python scripts
   - Cross-platform Python detection (python3/python/py)

2. **Python Scripts** (`tooling/scripts/`) - Core automation logic
   - `run-story.py` - Story pipeline with cost tracking
   - `run-collab.py` - Multi-agent collaboration modes
   - `lib/` - Shared modules (cost_tracker, agent_router, shared_memory, etc.)

### Agent System

Agents are AI personas defined in `tooling/.automation/agents/*.md`:
- **SM** (Scrum Master) - Planning, context creation, review
- **DEV** - Code implementation
- **REVIEWER** - Code quality review
- **ARCHITECT** - System design
- **MAINTAINER** - Brownfield work (bugs, refactoring)
- **BA**, **PM**, **WRITER** - Supporting roles

Agent behavior can be customized via YAML overrides in `tooling/.automation/overrides/` using templates from `templates/`.

### Claude Code Integration

Commands in `.claude/commands/*.md` expose slash commands (`/story`, `/develop`, `/init`, etc.) that Claude Code auto-detects. Skills in `.claude/skills/*/SKILL.md` provide richer AI-driven interactions.

### Cost and Memory Systems

- `lib/cost_tracker.py` - Token usage tracking with budget limits
- `lib/shared_memory.py` - Cross-agent knowledge graph and memory pool
- `lib/agent_handoff.py` - Structured context preservation between agents
- Session data stored in `tooling/.automation/costs/sessions/`

## Mandatory Requirements

### Changelog Updates

**CRITICAL**: Before pushing ANY changes, update `CHANGELOG.md`:

1. Add entries to a **new version section** at the top
2. Format: `- **Category** - Description`
3. Categories: `Added`, `Changed`, `Fixed`, `Removed`, `Security`, `Deprecated`
4. **Use proper version numbers** (never `[Unreleased]`):
   - Patch (1.5.1): Bug fixes
   - Minor (1.6.0): New features
   - Major (2.0.0): Breaking changes
5. **Never modify existing entries** - only add new ones

Then sync versions:
```bash
python3 tooling/scripts/update_version.py
```

### No Emojis Policy

**CRITICAL**: This project does NOT use emojis anywhere.

Use text alternatives:
- `[OK]` / `[PASS]` instead of checkmarks
- `[ERROR]` / `[FAIL]` instead of X marks
- `[WARNING]`, `[INFO]`, `[CRITICAL]`, `[SUGGESTION]`

### Commit Style

Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`
