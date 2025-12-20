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

## [Unreleased]

### Planned
- Windows support (PowerShell/WSL)
- GitHub Actions integration
- VS Code extension
- Web UI for monitoring
- Cloud backup for checkpoints
- Custom persona builder
- Cost analytics dashboard
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
