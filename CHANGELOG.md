# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2025-12-21

### Added
- **Agent Persona Templates** - Pre-built personality configurations for all 8 agents:
  - DEV agent: senior-fullstack, junior-mentored, security-focused, performance-engineer, rapid-prototyper
  - Reviewer agent: thorough-critic, mentoring-reviewer, quick-sanity
  - SM agent: agile-coach, technical-lead, startup-pm
  - Architect agent: enterprise-architect, cloud-native, pragmatic-minimalist
  - BA agent: requirements-engineer, agile-storyteller, domain-expert
  - PM agent: traditional-pm, agile-pm, hybrid-delivery
  - Writer agent: api-documentarian, user-guide-author, docs-as-code
  - Maintainer agent: oss-maintainer, legacy-steward, devops-maintainer
- **Personalization Wizard** (`personalize_agent.py`) - Interactive tool for customizing agent behavior
- **`/personalize` slash command** - Quick access to the personalization wizard from Claude Code
- **Memory Summarization Utility** (`memory_summarize.py`) - Consolidate and categorize agent memory files
- **Override Validation & Linting** - New tools to validate override YAML files
  - `validate-overrides.sh` - Shell script for validating YAML syntax, models, budgets
  - `validate-overrides.py` - Python version with JSON output support
  - Auto-fix capability for common issues (trailing whitespace, tabs)
  - Schema validation for override structure
- **Technical Debt Tracker** - Comprehensive debt metrics and reporting
  - `tech-debt-tracker.py` - Scans codebase for TODO, FIXME, HACK, etc.
  - Debt scoring system with severity weights
  - Dashboard view with visual progress bars
  - Trend tracking over time with history
  - Markdown report generation
  - JSON output for CI/CD integration
- **Enhanced Bug Root Cause Analysis** - Improved bug-report.md template
  - 5 Whys analysis framework
  - Fault tree visualization template
  - Root cause categorization (11 categories)
  - Hypothesis and evidence tracking
  - Investigation steps documentation
  - Impact analysis section
  - Prevention strategies
- **Migration Rollback Automation** - New rollback capabilities
  - `rollback-migration.sh` - Automated migration rollback tool
  - Rollback checkpoint creation and management
  - Git-based state preservation
  - Dependency file backup (package.json, pubspec.yaml, etc.)
  - Dry-run mode for preview
  - Enhanced migration-spec.md with comprehensive rollback plan
- **Custom Persona Builder** - Interactive agent persona creation
  - `create-persona.py` - Full-featured Python wizard
  - `create-persona.sh` - Shell script version
  - 7 pre-built templates (developer, reviewer, architect, tester, security, devops, documentation)
  - Automatic override file generation
  - Persona validation
- **Additional Project Types** - Java, Kotlin, Swift, and Android project detection
- **Project Override Templates** - Stack-specific configurations:
  - web-frontend.override.yaml
  - backend-api.override.yaml
  - data-science.override.yaml
  - devops.override.yaml
  - mobile-native.override.yaml

### Changed
- Expanded project type detection in initialization wizard
- Enhanced override system with template-based customization
- Enhanced `migration-spec.md` template with:
  - Detailed pre-migration checklist
  - Phase-based migration steps
  - Rollback triggers and automation commands
  - Communication plan template
  - Lessons learned section
- Improved `bug-report.md` template with structured root cause analysis

## [1.4.0] - 2025-12-21

### Added
- **Override Templates** - Pre-configured templates for common project types
  - `web-frontend.override.yaml` - React, Vue, Angular, Svelte
  - `backend-api.override.yaml` - Node.js, Python, Go, Rust APIs
  - `data-science.override.yaml` - ML, data analysis, Jupyter
  - `devops.override.yaml` - Infrastructure, CI/CD, Kubernetes
  - `mobile-native.override.yaml` - iOS (Swift), Android (Kotlin/Java)
- **Memory Summarization** - Utility to prevent unbounded memory growth
  - `memory_summarize.py` - Consolidates duplicate entries
  - Categorizes memories by type (errors, preferences, implementation, etc.)
  - Configurable max entries limit
- **Additional Project Types** - Java, Kotlin, Swift, Android support
  - Auto-detection for Maven, Gradle, Xcode projects
  - Updated config templates with all supported types

### Changed
- **Simplified CLI Integration** - Removed terminal-based CLI in favor of Claude Code native commands
  - Removed `tooling/scripts/gds` CLI wrapper
  - Removed `tooling/scripts/completions/` directory (zsh completions)
  - All workflows now accessed via Claude Code slash commands (`/story`, `/develop`, `/review`, etc.)
- **Simplified zsh autocomplete** - Replaced complex interactive menu with native zsh completion
  - Cleaner implementation (~130 lines vs ~450 lines)
- Renamed product from "GDS_Automation" to "Devflow" throughout codebase
- **CLAUDE.md** - Added project instructions file for Claude Code
  - Mandatory changelog update requirement before pushing
  - Project context and directory structure
  - Commit style guidelines
- **Claude Code Slash Commands** - Native slash commands for Devflow workflows
  - `/story` - Run full story pipeline
  - `/develop` - Run development phase
  - `/review` - Run code review
  - `/adversarial` - Run critical code review
  - `/agent` - Invoke a specific agent
  - `/bugfix` - Fix a bug
  - `/devflow` - Run any Devflow command
  - `/personalize` - Quick access to personalization wizard

### Removed
- `tooling/scripts/gds` - Terminal CLI wrapper
- `tooling/scripts/completions/_gds` - Zsh completion script
- `tooling/scripts/completions/_run-story` - Run-story completion script
- `tooling/scripts/completions/gds-interactive.zsh` - Interactive completion
- `tooling/scripts/completions/README.md` - Completion documentation

## [1.3.1] - 2025-12-20

### Added
- **Interactive Visual Autocomplete** - Claude-style `/` command experience
  - `Alt+.` triggers visual menu with arrow navigation
  - `devflow.` shell function for quick command menu
  - `devflow.story` and `devflow.agent` for context-specific menus
  - Fuzzy filtering by typing
  - fzf integration when available
  - Category-tagged commands (story, maint, agent)

### Changed
- `devflow setup` now installs interactive completion
- Updated completion documentation

### Fixed
- README: Removed references to non-existent Python scripts
- README: Fixed agent count (now 8 with REVIEWER)
- README: Updated version to 1.3.1
- README: Added Devflow CLI documentation
- README: Simplified cost management section
- CONTRIBUTING: Added override system contribution areas
- CONTRIBUTING: Updated release process documentation

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
  - `devflow` - Unified CLI wrapper with all commands
  - Story key completion from sprint-status.yaml
  - Mode and option completion
  - Agent and override completion
  - `devflow setup` command for easy installation
- **New CLI Commands**
  - `devflow profile` - Edit user profile
  - `devflow override <agent>` - Edit agent overrides
  - `devflow memory [show|add|clear] <agent>` - Manage agent memory
  - `devflow agents` - List available agents
  - `devflow logs [tail|list|view|clean]` - Log management

### Changed
- `claude-cli.sh` now loads overrides via `override-loader.sh`
- Agent prompts include user context and memories
- `run-story.sh` supports `--adversarial` mode

### New Files
- `tooling/.automation/overrides/` - Override configuration directory
- `tooling/.automation/memory/` - Persistent agent memory directory
- `tooling/.automation/agents/reviewer.md` - Adversarial reviewer agent
- `tooling/scripts/lib/override-loader.sh` - Override loading library
- `tooling/scripts/devflow` - Unified CLI wrapper
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

## [1.0.0] - 2025-12-20

### Added
- Initial release of Claude Workflow Template
- Multi-persona agent system (SM, DEV, BA, ARCHITECT, PM, WRITER)
- Smart model optimization (Opus for dev/review, Sonnet for planning)
- Automated story implementation pipeline
- Context checkpoint system with auto-save
- Interactive setup wizard (`init-project-workflow.sh`)
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

---

For more details, see the [GitHub releases](https://github.com/Pedro-Jose-da-Rocha-Mendonca/Devflow/releases).
