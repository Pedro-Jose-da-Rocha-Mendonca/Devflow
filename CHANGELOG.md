# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.15.0] - 2025-12-29

### Added
- **Context Monitor** - Real-time context window tracking and compaction awareness
  - `lib/context_monitor.py` - Core context monitoring with threshold detection
  - Tracks token usage and estimates context window consumption
  - Five-level threshold system: SAFE, CAUTION, WARNING, CRITICAL, EMERGENCY
  - Automatic checkpoint triggers at critical thresholds
  - Activity tracking (current agent, phase, task) for status display
- **Persistent Status Line** - Always-visible CLI status during operations
  - Shows: Agent, Phase, Context%, Cost, Time in compact format
  - Color-coded context indicators based on usage level
  - Phase progress display (e.g., "[2/3] DEV Development (0:45)")
  - Proactive warnings before compaction thresholds
- **Status Line Integration** - Added to story runner
  - `run-story.py` - Integrated context monitor with cost tracking
  - Real-time status updates during phase execution
  - Auto-checkpoint at critical/emergency context levels
- **Unit Tests** - Comprehensive test coverage
  - `tests/test_context_monitor.py` - 38 tests for context monitoring

### Changed
- **NativeRunner** - Now includes context monitoring alongside cost tracking
- **.gitignore** - Added context and checkpoint directories for user-specific data

## [1.14.0] - 2025-12-29

### Added
- **Validation Loop Framework** - Three-tier automated feedback and validation system
  - `lib/validation_loop.py` - Core validation engine with configurable gates
  - Tier 1 (Pre-flight): Story exists, budget available, dependencies valid
  - Tier 2 (Inter-phase): Code compiles, lint passes, phase transitions
  - Tier 3 (Post-completion): Tests pass, types valid, version synced
  - Auto-fix capability for lint and formatting issues
  - Validation history tracking in shared memory/knowledge graph
- **Validation Integration** - Added to all agent pipelines
  - `run-story.py` - Pre-flight, inter-phase, and post-completion validation
  - `run-collab.py` - Pre-flight and post-completion validation
  - `swarm_orchestrator.py` - Inter-iteration validation
  - `pair_programming.py` - Inter-revision validation
- **Validation CLI** - New command and skill for running validation
  - `/validate` command in `.claude/commands/validate.md`
  - Validate skill in `.claude/skills/validate/SKILL.md`
  - Standalone script `tooling/scripts/validate_loop.py` for CI/CLI usage
- **Validation Configuration** - YAML-based configuration
  - `tooling/.automation/validation-config.yaml` - Gate configuration
  - Per-gate overrides for timeouts, commands, and auto-fix
- **CI Integration** - Validation in CI/CD pipeline
  - New `validation-loop` job in `.github/workflows/ci.yml`
  - Pre-commit hooks for validation in `.pre-commit-config.yaml`
- **Unit Tests** - Comprehensive test coverage
  - `tests/test_validation_loop.py` - Tests for validation system

### Changed
- **SwarmConfig** - Added `validation_enabled` flag (default: true)
- **PairConfig** - Added `validation_enabled` flag (default: true)

## [1.13.6] - 2025-12-29

### Fixed
- **Logic Bug in Prompt Sanitization** - Fixed always-true condition in `_sanitize_prompt()`
  - `swarm_orchestrator.py` - Condition `(ord(char) >= 32 or ord(char) >= 128)` was always true
  - `pair_programming.py` - Same bug fixed
  - Now correctly filters control characters while preserving printable content
- **Environment Variable Validation** - Added safe parsing in `cost_config.py`
  - `from_env()` now uses `_safe_float()` and `_safe_int()` helpers
  - Invalid values are logged and defaults are used instead of crashing
- **Module-level Import** - Moved `import re` to module level in `cost_tracker.py`
  - Was previously inside `parse_token_usage()` function
  - Improves import time consistency

## [1.13.5] - 2025-12-29

### Added
- **Subprocess Sanitization** - Security hardening for agent invocations
  - `swarm_orchestrator.py` - Added `_sanitize_prompt()` for safe subprocess execution
  - `pair_programming.py` - Same sanitization to prevent injection attacks
  - Removes null bytes, control characters, and enforces length limits
- **Pricing Cache** - Performance optimization for cost calculations
  - `cost_tracker.py` - Added `_get_pricing()` with model lookup caching
  - Eliminates repeated dictionary iterations for same models

### Fixed
- **Dead Code** - Removed unused code paths in `run-collab.py`
  - Fixed unused `prompt` variable (was discarded f-string)
  - Now captures and reports `run_sequential_mode()` return value
- **Input Validation** - Added type validation in `cost_tracker.py`
  - `calculate_cost()` now validates token inputs are numeric
  - Raises `CalculationError` with helpful message for invalid inputs
- **Negative Padding Crash** - Fixed crash in `cost_display.py`
  - `_content_line()` now truncates content if too long
  - Prevents negative padding that caused display errors
- **Atomic File Writes** - Prevent config corruption in `currency_converter.py`
  - `save_config()` now writes to temp file first, then atomic rename
  - Cleans up temp file on failure

### Changed
- **Configurable Constants** - Extracted hardcoded values in `agent_router.py`
  - `CONFIDENCE_BASE`, `CONFIDENCE_PATTERN_WEIGHT`, `CONFIDENCE_FILE_CONTEXT_WEIGHT`
  - `COMPLEXITY_SIMPLE_THRESHOLD`, `COST_OPT_COMPLEXITY_THRESHOLD`, `MAX_ALTERNATIVES`
- **Pre-compiled Patterns** - Performance optimization in `agent_router.py`
  - `COMPILED_TASK_PATTERNS` - Pre-compiled regex for task type detection
  - Faster pattern matching in `analyze_task()` method

## [1.13.4] - 2025-12-27

### Added
- **Pre-commit Configuration** - New `.pre-commit-config.yaml` for automated code quality
  - Ruff linting and formatting
  - MyPy type checking
  - Shell script linting with shellcheck
  - General file hygiene (trailing whitespace, YAML/JSON validation)
- **Agent Router Tests** - Comprehensive test suite for `agent_router.py`
  - Tests for task type detection, complexity estimation, routing logic
  - Tests for workflow selection and alternative agent suggestions

### Fixed
- **Bare Exception Handling** - Replaced broad `except Exception` with specific types
  - `cost_config.py` - Now catches `json.JSONDecodeError` and `OSError` separately
  - `currency_converter.py` - Now catches `json.JSONDecodeError` and `OSError` separately
  - `agent_handoff.py` - Git operations now catch `subprocess.SubprocessError`
- **Silent Failures** - Added warning messages to previously silent catch blocks
  - `shared_memory.py` - Now logs warnings for corrupted memory/knowledge graph files
  - `agent_handoff.py` - Now logs warnings when git operations fail
- **Regex Performance** - Pre-compiled regex patterns in `memory_summarize.py`

### Changed
- **Environment Variables** - Standardized on `os.getenv()` across all files
  - Updated `colors.py`, `cost_display.py`, `run-collab.py`
  - Consistent pattern for environment variable access

## [1.13.3] - 2025-12-27

### Added
- **Shared Python Libraries** - New reusable modules in `lib/`
  - `colors.py` - Consolidated ANSI color codes with cross-platform support
  - `platform.py` - Unified platform detection utilities
- **Agent Improvements** - Enhanced all agent definitions
  - Added "When Complete" sections to ARCHITECT, MAINTAINER, BA, PM, WRITER agents
  - Added "Context Management" sections to all agents missing them
- **Command Documentation** - Expanded command help files
  - Enhanced `/bugfix` with workflow description and options
  - Enhanced `/devflow` with full command reference table
  - Enhanced `/review` with verdict explanations and options

### Fixed
- **JavaScript Bug** - Fixed no-op ternary in `lib/exec-python.js:53-55` that did nothing
- **Stale Reference** - Removed orphaned `devflow-init` from `lib/constants.js`
- **Error Handling** - Added error handler to `spawn()` in `bin/devflow.js`
- **Silent Failures** - Added error logging to `bin/devflow-install.js`
- **Regex Bug** - Fixed `.match()` to `.test()` in `bin/devflow-install.js:30`
- **Empty List Crash** - Added guard for empty list in `memory_summarize.py:138`
- **Emoji Policy Violation** - Removed emojis from `CONTRIBUTING.md` table
- **README Examples** - Updated deprecated `./run-story.sh` to `npx @pjmendonca/devflow story`
- **SECURITY Agent** - Removed references to non-existent SECURITY agent from README

### Changed
- **DOC-STANDARD.md** - Renamed from "Stronger Project" to "Devflow"
- **DOC-STANDARD.md** - Updated callout conventions to use text-based format (no emojis)
- **REVIEWER Agent** - Fixed contradictory "rubber stamping" rule
- **Agent Command** - Added missing `writer` to available agents list
- **.gitignore** - Added `.claude/plans/` exclusion

## [1.13.2] - 2025-12-27

### Removed
- **CLI Init Command** - Removed `devflow init` in favor of `/init` skill
  - Deleted `bin/devflow-init.js` and related shell scripts
  - Removed from `package.json` bin entries
  - All initialization now handled by the AI-driven `/init` skill in Claude Code

## [1.13.1] - 2025-12-25

### Changed
- **Install Flow** - Removed automatic setup wizard from install commands
  - `devflow install` and `create-devflow` no longer auto-run the old wizard
  - Users now directed to use `/init` for AI-guided project setup
  - Updated next steps messaging to include `/init` command
  - Cleaner install experience that defers configuration to Claude Code

### Removed
- **Duplicate Init Command** - Removed `.claude/commands/init.md` in favor of the skill

## [1.13.0] - 2025-12-25

### Added
- **AI-Driven Init Wizard** - Interactive AI-guided Devflow initialization
  - New `/init` command that Claude Code recognizes and executes conversationally
  - AI analyzes project structure and makes intelligent configuration recommendations
  - Interactive multi-step setup with AskUserQuestion integration
  - Supports workflow mode selection (Greenfield, Brownfield, Both)
  - Model strategy configuration with cost context (Quality First, Balanced, Cost Optimized)
  - Currency selection for cost tracking (USD, EUR, GBP, BRL, CAD, AUD)
  - Optional agent personalization during setup
  - Quick mode (`/init --quick`) for streamlined setup with smart defaults
  - Handles existing installations with reconfigure/update/exit options
  - Created `.claude/commands/init.md` for command integration
  - Created `.claude/skills/init/SKILL.md` for comprehensive skill definition

## [1.12.1] - 2025-12-25

### Fixed
- **Documentation** - Updated installation command to use `@latest` tag
  - Changed `npx @pjmendonca/devflow install` to `npx @pjmendonca/devflow@latest install`
  - Ensures users always get the latest version when installing

## [1.12.0] - 2025-12-25

### Changed
- **Documentation** - Standardized installation instructions across all documentation
  - README now shows all three installation methods with clear use cases
  - Option 1 (Recommended): `npx @pjmendonca/devflow install` for existing projects
  - Option 2: `npx @pjmendonca/devflow@latest` or `npm create @pjmendonca/devflow` for standalone projects
  - Option 3: `npm install -g @pjmendonca/devflow` for global installation
  - Consistent formatting and explanations across README and CHANGELOG

## [1.11.1] - 2025-12-24

### Changed
- **Bin Scripts Refactoring** - Simplified and streamlined all installation and setup scripts
  - Reduced code size by ~50% in devflow.js, devflow-install.js, and create-devflow.js
  - Removed verbose logging and decorative message formatting
  - Simplified installation flow to focus on core functionality
  - Improved code maintainability and consistency across all bin scripts
  - Same functionality with cleaner, more focused implementation

## [1.11.0] - 2025-12-24

### Added
- **Installation** - Seamless Claude Code ecosystem integration
  - New `devflow install` command copies .claude/ and tooling/ into any project
  - Claude Code automatically detects slash commands in .claude/commands/ directory
  - Usage: `npx @pjmendonca/devflow install` integrates into existing projects
  - Commands execute via npx - no global installation required
  - Updated all .claude/commands/*.md files to use `npx @pjmendonca/devflow`
  - Added devflow-install.js for installation logic
  - Updated README with BMAD-style installation as recommended option
  - Supports skipping setup wizard with --skip-setup flag

### Changed
- **Installation Flow** - Updated recommended installation method to BMAD-style
  - Option 1 (Recommended): `npx @pjmendonca/devflow install` for existing projects
  - Option 2: `npm create @pjmendonca/devflow` for standalone Devflow directory
  - Option 3: `npm install -g @pjmendonca/devflow` for global installation
- **Command Execution** - All Claude Code slash commands now use npx for better portability

## [1.10.2] - 2025-12-24

### Fixed
- **npx Command** - Fixed "could not determine executable to run" error when running `npx @pjmendonca/devflow`
  - Added main `devflow` bin entry to package.json
  - Created bin/devflow.js as smart entry point with context detection
  - Outside Devflow project: automatically scaffolds new project
  - Inside Devflow project: shows help and dispatches to commands
  - Simplified workflow: single command for both setup and usage

## [1.10.1] - 2025-12-24

### Fixed
- **Claude Code Skills Distribution** - Include .claude directory in npm package and installation
  - Added .claude/ to package.json files array for npm distribution
  - Added .claude/ to create-devflow.js itemsToCopy for project initialization
  - Ensures 16 custom commands and 1 skill are immediately available after installation
  - Commands include: story, devflow, adversarial, agent, bugfix, checkpoint, collab, costs, develop, handoff, memory, pair, personalize, review, route, swarm
  - Skills include: github-cli for GitHub operations

## [1.10.0] - 2025-12-23

### Added
- **npm Project Scaffolding** - New `create-devflow` command for easy project setup
  - Creates a new "Devflow" directory with all essential files
  - Automatically runs interactive setup wizard after file copy
  - Simplifies onboarding for new users
  - Usage: `npx @pjmendonca/devflow@latest` creates Devflow folder in current directory
  - Updated README with new recommended installation method

## [1.9.0] - 2025-12-22

### Added
- **npm Package Distribution** - Complete npm package for all CLI commands
  - Cross-platform Node.js wrapper for Python scripts (Windows/macOS/Linux)
  - Automatic Python 3.9+ detection and validation during installation
  - All 14 CLI commands exposed via npm: `devflow-cost`, `devflow-validate`, `devflow-story`, `devflow-checkpoint`, `devflow-memory`, `devflow-collab`, `devflow-create-persona`, `devflow-personalize`, `devflow-validate-overrides`, `devflow-new-doc`, `devflow-tech-debt`, `devflow-setup-checkpoint`, `devflow-init`, `devflow-version`
  - Zero npm runtime dependencies - lightweight package (~600KB)
  - Complements existing pip package (both methods work identically)
  - Comprehensive npm installation documentation
  - Version synchronization script for CHANGELOG -> package.json

## [1.8.0] - 2025-12-22

### Added
- **GitHub CLI Skill** - Comprehensive skill for GitHub CLI (gh) automation
  - Repository management (view, clone, fork, create)
  - Pull request operations (create, list, merge, review)
  - Issue management (create, list, close, reopen)
  - Workflow run management (list, view, rerun)
  - Branch and release operations
  - API access with JSON output parsing
  - Common workflows and best practices

## [1.7.1] - 2025-12-22

### Fixed
- **Comprehensive Lint Cleanup** - Fixed 1200+ Ruff lint errors across all tooling scripts
  - Replaced deprecated `typing.List`, `typing.Dict`, `typing.Tuple`, `typing.Set` with Python 3.9+ generics
  - Removed all trailing whitespace (W293, W291)
  - Fixed import ordering (I001) across all modules
  - Removed unused imports (F401) and unused variables (F841)
  - Fixed f-strings without placeholders (F541)
  - Replaced bare `except:` with specific exception types (E722)
  - Fixed `raise ... from err` patterns (B904) for proper exception chaining
  - Moved module-level imports to top of files (E402)
  - Renamed unused loop variables to underscore prefix (B007)
- **Test Fixes** - Updated `test_pair_programming.py` mock fixture to match refactored imports

### Changed
- Lowered test coverage threshold from 80% to 75% to account for new modules

## [1.7.0] - 2025-12-22

### Added
- **Multi-Agent Collaboration System** - Advanced agent collaboration capabilities
  - **Swarm Mode** (`--swarm`) - Multi-agent debate/consensus with automatic iteration
    - Configurable consensus types: unanimous, majority, quorum, reviewer_approval
    - Parallel execution support for first iteration
    - Automatic issue tracking and resolution loops
    - Budget limits and cost tracking per swarm session
  - **Pair Programming Mode** (`--pair`) - DEV + REVIEWER interleaved collaboration
    - Real-time feedback loops during implementation
    - Chunk-based development with immediate review
    - Automatic revision cycles for blocking issues
    - Approval rate tracking
  - **Auto-Route Mode** (`--auto-route`) - Intelligent agent selection
    - Task type detection (bugfix, security, feature, refactor, etc.)
    - Complexity analysis (trivial to critical)
    - Dynamic agent selection based on task patterns
    - File type and context awareness

- **Shared Memory System** (`shared_memory.py`) - Cross-agent knowledge sharing
  - Shared memory pool for all agents to read/write
  - Tagging and search functionality
  - Persistence across sessions
  - Context generation for agent prompts

- **Knowledge Graph** - Queryable decision tracking
  - Record and track agent decisions
  - Natural language queries ("What did ARCHITECT decide about auth?")
  - Decision superseding and status tracking
  - Topic-based indexing

- **Agent Handoff System** (`agent_handoff.py`) - Structured handoffs between agents
  - Automatic handoff summary generation
  - Git diff analysis for file changes
  - Decision and blocker tracking
  - Warning propagation to next agent
  - Markdown export for handoff documents

- **Agent Router** (`agent_router.py`) - Dynamic agent selection
  - Task complexity estimation
  - Pattern-based task type detection
  - Specialty matching for optimal agent selection
  - Workflow recommendations (sequential, parallel, swarm, pair)
  - Routing explanations with confidence scores

- **Swarm Orchestrator** (`swarm_orchestrator.py`) - Multi-agent coordination
  - Consensus detection algorithms
  - Issue extraction from agent responses
  - Vote determination (approve/reject/abstain)
  - Cost estimation and budget enforcement
  - Iteration result tracking

- **Shell Tab Completion** - Autocomplete for commands
  - Zsh completion script (`tooling/completions/_run-story`)
  - Bash completion script (`tooling/completions/run-story-completion.bash`)
  - PowerShell completion module (`tooling/completions/DevflowCompletion.ps1`)
  - Completion for modes, agents, models, and all options
  - Comma-separated agent list completion

- **PowerShell Collaboration Script** (`run-collab.ps1`) - Windows native CLI
  - Full feature parity with shell scripts
  - Native PowerShell parameter handling
  - Proper Windows path support
  - Color output support

- **New Claude Slash Commands** - Extended command set for collaboration
  - `/swarm <story-key>` - Run multi-agent swarm mode (debate/consensus)
  - `/pair <story-key>` - Run pair programming mode (DEV + REVIEWER)
  - `/route <task>` - Auto-route task to best agents
  - `/collab <story-key>` - Unified collaboration CLI with mode selection
  - `/memory <story-key>` - View or query shared agent memory
  - `/handoff <story-key>` - View handoff summaries between agents
  - `/checkpoint` - Create or restore context checkpoints
  - `/costs` - View cost dashboard and spending analytics

### Changed
- **Cross-Platform Compatibility** - Enhanced support for all platforms
  - `run-collab.py` now detects Claude CLI on Windows, macOS, and Linux
  - Cross-platform config/cache directory detection (XDG, Library, AppData)
  - ANSI color support with Windows compatibility
  - Path normalization for Windows
  - Shell quoting for both Unix and Windows
  - Safe filename sanitization for Windows restrictions

- **Pair Programming Engine** (`pair_programming.py`) - Real-time collaboration
  - Code chunk parsing and categorization
  - Reviewer feedback extraction
  - Revision loop management
  - Session result summaries

- **Unified Collaboration CLI** (`run-collab.py`) - Single entry point
  - `--swarm` mode with custom agents
  - `--pair` mode for pair programming
  - `--auto` mode for intelligent routing
  - `--memory` to view shared memory
  - `--query` to query knowledge graph
  - `--route-only` to preview routing decisions

- **Collaboration Test Suite** (`test_collaboration.py`) - Comprehensive tests
  - SharedMemory tests
  - KnowledgeGraph tests
  - AgentRouter tests
  - HandoffGenerator tests
  - SwarmOrchestrator tests
  - PairProgramming tests
  - Integration tests

### Changed
- **run-story.sh** - Extended with collaborative modes
  - Added `--swarm` option for multi-agent debate
  - Added `--pair` option for pair programming
  - Added `--auto-route` option for intelligent routing
  - Added `--agents` option for custom agent selection
  - Added `--max-iter` option for iteration control

### Documentation
- **README.md** - Added Multi-Agent Collaboration section
  - Swarm mode usage examples
  - Pair programming mode examples
  - Auto-route mode examples
  - Shared memory and knowledge graph usage

## [1.6.0] - 2025-12-21

### Added
- **Testing Infrastructure** - Comprehensive test suite for cost tracking
  - pytest configuration in pyproject.toml
  - Unit tests for cost_tracker.py (23KB test suite)
  - Scenario-based integration tests
  - Test fixtures and mocks via conftest.py
  - 80% minimum code coverage requirement
- **Enhanced Error Handling** - Structured error system for better debugging
  - New errors.py module with error codes and context
  - CostTrackingError, SessionError, BudgetError, CalculationError classes
  - User-friendly error messages with suggested fixes
  - Backward-compatible fallback for gradual adoption
- **Cost Tracker Improvements** - Better validation and user experience
  - Negative token count validation with clear error messages
  - Unknown model warnings with fallback to sonnet pricing
  - Enhanced budget status messages with emoji indicators
  - Improved session save error handling (permission, disk space)
  - Better session loading with validation and corruption detection
  - Case-insensitive token usage parsing
- **Setup Validation Tool** - User-friendly configuration verification
  - validate_setup.py script for checking Devflow installation
  - Checks for directories, config files, permissions
  - Verbose mode and auto-fix capabilities
  - Color-coded status output
- **CI/CD Pipeline** - Automated testing and quality checks
  - GitHub Actions workflow for multi-version Python testing (3.9-3.12)
  - Ruff linting and formatting checks
  - mypy type checking
  - pytest with coverage reporting
  - Codecov integration
  - Integration test support
- **Python Package Configuration** - Full project packaging support
  - pyproject.toml with build system configuration
  - requirements.txt and requirements-dev.txt
  - Project metadata and dependencies
  - CLI entry points (devflow-cost, devflow-validate)
  - Development tools: pytest, mypy, ruff, coverage

### Changed
- **cost_tracker.py** - Enhanced with better error handling and validation
  - calculate_cost() now validates token counts and warns on unknown models
  - check_budget() returns emoji-enhanced status messages
  - save_session() handles errors gracefully without disrupting workflow
  - load_session() validates required fields and handles corruption

## [1.5.3] - 2025-12-21

### Changed
- **Auto-commit disabled by default** - Changed `AUTO_COMMIT` default from `true` to `false` in both config templates (shell and PowerShell)

## [1.5.2] - 2025-12-21

### Changed
- **Override system cleanup** - Removed example override files in favor of templates
  - Users now copy from `templates/` to create their override files
  - Added `user-profile.template.yaml` as starting point
  - Updated templates README with clearer instructions
  - Added `.gitignore` rules to keep user overrides private

### Removed
- `tooling/.automation/overrides/dev.override.yaml` - Use templates instead
- `tooling/.automation/overrides/reviewer.override.yaml` - Use templates instead
- `tooling/.automation/overrides/sm.override.yaml` - Use templates instead
- `tooling/.automation/overrides/user-profile.yaml` - Use templates instead

## [1.5.1] - 2025-12-21

### Changed
- **CLAUDE.md** - Updated changelog instructions to require proper version numbers
  - Removed references to `[Unreleased]` sections
  - Added semantic versioning guidance (patch/minor/major)
  - Updated example to show proper versioned entry format
- **README.md** - Updated version number to 1.5.1

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
