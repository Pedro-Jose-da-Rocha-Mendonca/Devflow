# Contributing to Devflow

Thank you for your interest in contributing! This project aims to make AI-powered development workflows accessible to everyone.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/Pedro-Jose-da-Rocha-Mendonca/Devflow/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version, Claude Code version, project type)
   - Relevant log files from `tooling/.automation/logs/`

### Submitting Pull Requests

> **Note**: Direct pushes to `main` are not allowed. All changes must go through a pull request and receive approval before merging.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following our coding standards
4. Add tests if applicable
5. Update documentation as needed
6. Run the test suite: `python -m pytest tests/`
7. Commit with conventional commit messages (e.g., `feat: add new feature`)
8. Push to your fork and open a Pull Request
9. Wait for review and approval (at least 1 approving review required)
10. Address any feedback from reviewers
11. Once approved, your PR will be merged

### Areas for Contribution

We welcome contributions in these areas:

**Core Functionality**:
- Improved error handling and recovery
- Better context preservation across sessions
- Performance optimizations

**Agent System**:
- New agent personas for specialized tasks
- Cross-agent memory and learning improvements
- Agent handoff enhancements

**Platform Support**:
- Linux shell compatibility improvements
- Windows PowerShell enhancements
- CI/CD pipeline integrations

**Documentation**:
- Usage examples and tutorials
- API documentation

**Testing**:
- Unit tests for uncovered modules
- Integration tests for shell scripts
- End-to-end workflow tests

## Agent Persona Guidelines

When adding/modifying agent personas:

1. **Clear role definition**
   ```markdown
   # Agent Name

   You are a [specific role] focused on [specific task].
   ```

2. **Responsibilities** (3-5 bullet points)
   - What they do
   - What they don't do

3. **Approach** (how they work)
   - Working style
   - Decision-making process
   - Quality standards

4. **Communication style**
   - Tone (technical, business, etc.)
   - Level of detail
   - Output format

5. **Model selection**
   ```bash
   # In invoke function
   local model="sonnet"  # or "opus" with justification
   ```

## Version Management

Version is managed from a single source of truth: `CHANGELOG.md`.

### Automatic Sync (Recommended)

Enable the pre-commit hook to auto-sync versions when you update the changelog:

```bash
git config core.hooksPath .githooks
```

Now when you commit changes to `CHANGELOG.md`, the version will automatically propagate to:
- `README.md`
- `pyproject.toml`
- `tooling/scripts/lib/__init__.py`

### Manual Sync

Run the version sync script manually:

```bash
# Sync all versions from CHANGELOG.md
python tooling/scripts/update_version.py

# Check if versions are in sync
python tooling/scripts/update_version.py --check

# Set a specific version everywhere
python tooling/scripts/update_version.py --version 1.8.0
```

### Adding a New Version

1. Add a new entry at the top of `CHANGELOG.md`:
   ```markdown
   ## [1.8.0] - 2025-12-25

   ### Added
   - New feature description
   ```
2. Commit with the pre-commit hook enabled, or run `update_version.py` manually
3. All version references will be updated automatically

## Branch Protection

The `main` branch is protected with the following rules:

- **No direct pushes** - All changes must go through pull requests
- **Required reviews** - At least 1 approving review before merging
- **Status checks** - Tests must pass before merging (when CI is configured)

This ensures code quality and prevents accidental breaking changes.

## Style Guidelines

### No Emojis Policy

This project does NOT use emojis anywhere in the codebase. This applies to:

- Source code (comments, strings, output messages)
- Documentation (README, CONTRIBUTING, etc.)
- Agent personas and templates
- Commit messages and changelog entries
- Test files and fixtures

**Use text alternatives instead:**
| Instead of | Use |
|------------|-----|
| ✅ | `[OK]`, `[PASS]` |
| ❌ | `[ERROR]`, `[FAIL]` |
| ⚠️ | `[WARNING]` |
| ℹ️ | `[INFO]` |
| 🔴 | `[CRITICAL]`, `[MUST FIX]` |
| 🟡 | `[SHOULD FIX]` |
| 💡 | `[SUGGESTION]`, `[TIP]` |

This ensures consistent display across all terminals and environments.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn
- Follow open source etiquette

---

**Thank you for contributing!** 
