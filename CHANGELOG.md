# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-20

### Added
- Initial release of Claude Workflow Template
- Multi-persona agent system (SM, DEV, BA, ARCHITECT, PM, WRITER)
- Smart model optimization (Opus for dev/review, Sonnet for planning)
- Automated story implementation pipeline
- Context checkpoint system with auto-save
- BMAD-style interactive setup wizard (`init-project-workflow.sh`)
- Documentation standards and templates
- Sprint tracking system
- Export/import functionality for portability
- macOS LaunchAgent for background checkpoint monitoring
- Cost optimization with budget controls
- 6 pre-configured agent personas
- Complete documentation suite
- Git integration with auto-commit
- Code review automation

### Features
- `run-story.sh` - Main workflow runner
- `init-project-workflow.sh` - Interactive setup wizard
- `context_checkpoint.py` - Checkpoint management system
- `setup-checkpoint-service.sh` - Background service installer
- `new-doc.sh` - Documentation template generator
- `export-workflow-template.sh` - Template packager

### Documentation
- README.md - Main project documentation
- CONTRIBUTING.md - Contribution guidelines
- LICENSE - MIT License
- CHANGELOG.md - This file
- tooling/docs/DOC-STANDARD.md - Documentation standards

### Supported Project Types
- Flutter
- Node.js
- Python
- Rust
- Go
- Ruby
- Generic (any project)

### Model Strategy
- Opus ($15/$75 per M tokens) for development and code review
- Sonnet ($3/$15 per M tokens) for planning, context, documentation
- Average cost savings: 40-60% per story

### Budget Controls
- MAX_BUDGET_CONTEXT: Default $3.00
- MAX_BUDGET_DEV: Default $15.00
- MAX_BUDGET_REVIEW: Default $5.00

## [1.3.0] - 2025-12-20

### Added
- **Agent Override System** - BMAD-style personalization (inspired by [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD))
  - `user-profile.yaml` - Global user preferences (name, tech level, code style)
  - Per-agent override files (`dev.override.yaml`, `sm.override.yaml`, etc.)
  - Persistent agent memory system (`memory/{agent}.memory.md`)
  - Runtime merging: base agent + user profile + overrides + memory
  - Model and budget overrides per agent
  - Customizations survive updates to core agents
- **Adversarial Reviewer Agent** - Critical code reviewer that finds problems
  - Uses Opus for deeper analysis
  - Security, reliability, correctness, maintainability checks
  - Issue severity classification (Critical, High, Medium, Low)
  - `--adversarial` mode in run-story.sh
- **CLI Autocomplete System** - Zsh tab completion
  - `gds` - Unified CLI wrapper with all commands
  - Story key completion from sprint-status.yaml
  - Mode and option completion
  - Agent and override completion
  - `gds setup` command for easy installation
- **New CLI Commands**
  - `gds profile` - Edit user profile
  - `gds override <agent>` - Edit agent overrides
  - `gds memory [show|add|clear] <agent>` - Manage agent memory
  - `gds agents` - List available agents
  - `gds logs [tail|list|view|clean]` - Log management

### Changed
- `claude-cli.sh` now loads overrides via `override-loader.sh`
- Agent prompts include user context and memories
- `run-story.sh` supports `--adversarial` mode

### New Files
- `tooling/.automation/overrides/` - Override configuration directory
- `tooling/.automation/memory/` - Persistent agent memory directory
- `tooling/.automation/agents/reviewer.md` - Adversarial reviewer agent
- `tooling/scripts/lib/override-loader.sh` - Override loading library
- `tooling/scripts/gds` - Unified CLI wrapper
- `tooling/scripts/completions/` - Zsh completion scripts

## [1.2.0] - 2025-12-20

### Added
- **Brownfield Workflow Support** - Full support for existing codebase maintenance
  - `--bugfix` mode for bug investigation and fixing
  - `--refactor` mode for code refactoring
  - `--investigate` mode for codebase exploration (read-only)
  - `--quickfix` mode for small, targeted changes
  - `--migrate` mode for framework/dependency migrations
  - `--tech-debt` mode for technical debt resolution
- **MAINTAINER Agent Persona** - New agent specialized for brownfield work
- **Brownfield Directory Structure** - Organized folders for bugs, refactors, investigations, migrations, tech-debt
- **Task Templates** - Templates for bug reports, refactoring specs, migration plans, tech debt items
- **Workflow Mode Selection** - Init wizard now asks for greenfield, brownfield, or both

### Changed
- Agent count increased from 6 to 7 (added MAINTAINER)
- `run-story.sh` now supports brownfield modes alongside greenfield
- `init-project-workflow.sh` includes workflow mode selection step
- README updated with brownfield documentation
- CONTRIBUTING updated with brownfield contribution areas

## [1.1.0] - 2025-12-20

### Added
- **Windows Compatibility** - Full PowerShell support
  - `run-story.ps1` - Windows workflow runner
  - `init-project-workflow.ps1` - Windows setup wizard
  - `new-doc.ps1` - Windows documentation generator
  - Updated installation instructions for Windows
- **Cost Analysis System** - Real-time cost tracking
  - `cost_dashboard.py` - Cost monitoring dashboard
  - Multi-currency display (USD, EUR, GBP, BRL, CAD, AUD)
  - Per-agent and per-model cost breakdown
  - Budget alerts (warning at 75%, critical at 90%)
  - Auto-stop at budget limit
  - Session history and CSV export
- **Currency Selection** - Init wizard now prompts for preferred currency

### Changed
- Updated README with Windows installation instructions
- Added cost tracking configuration options to config.sh
- Improved cross-platform compatibility

## [Unreleased]

### Planned
- GitHub Actions integration
- VS Code extension
- Web UI for monitoring
- Cloud backup for checkpoints
- Custom persona builder
- Team collaboration features
- Multi-language support

---

## Version History

### Version 1.0.0 - Initial Release
**Date**: 2025-12-20

**Summary**: Complete automated development workflow system with multi-agent architecture, smart cost optimization, and context preservation.

**Key Metrics**:
- 15 core scripts
- 6 agent personas
- ~40KB package size
- $8-14 average cost per story
- 40-60% cost savings vs all-Opus approach

**Platform Support**:
- macOS (full support)
- Linux (partial - no LaunchAgent)
- Windows (planned)

---

For more details, see the [GitHub releases](https://github.com/Pedro-Jose-da-Rocha-Mendonca/GDS_Automation/releases).
