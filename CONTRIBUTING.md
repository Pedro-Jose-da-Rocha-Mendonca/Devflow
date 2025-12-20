# Contributing to Claude Workflow Template

Thank you for your interest in contributing! This project aims to make AI-powered development workflows accessible to everyone.

## 🎯 How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/Pedro-Jose-da-Rocha-Mendonca/GDS_Automation/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Claude Code version, project type)
   - Relevant log files from `tooling/.automation/logs/`

### Suggesting Enhancements

1. Open a [Discussion](https://github.com/Pedro-Jose-da-Rocha-Mendonca/GDS_Automation/discussions) first
2. Describe:
   - The problem you're trying to solve
   - Your proposed solution
   - Alternative approaches considered
   - Impact on existing workflows

### Submitting Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/Pedro-Jose-da-Rocha-Mendonca/GDS_Automation.git
   cd GDS_Automation
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow existing code style
   - Update documentation
   - Add tests if applicable
   - Test in a real project

4. **Commit with clear messages**
   ```bash
   git commit -m "feat: Add support for project type X"
   git commit -m "fix: Checkpoint service crash on macOS"
   git commit -m "docs: Add troubleshooting for Windows"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub

## 📝 Development Guidelines

### Code Style

**Shell Scripts** (`.sh`):
- Use `#!/bin/zsh` shebang
- Set `-e` for error handling
- Add comments for complex logic
- Use descriptive variable names
- Follow existing formatting

**Python** (`.py`):
- Python 3.8+ compatible
- Use type hints
- Follow PEP 8
- Add docstrings

**Documentation** (`.md`):
- Follow `tooling/docs/DOC-STANDARD.md`
- Use clear, concise language
- Include examples
- Keep line length reasonable

### Testing

Before submitting:

```bash
# Test export
cd tooling/scripts
./export-workflow-template.sh /tmp

# Test import in clean project
mkdir -p /tmp/test-project
cd /tmp/test-project
tar -xzf /tmp/claude-workflow-template_*.tar.gz
mv claude-workflow-template/tooling .

# Test init wizard
cd tooling/scripts
./init-project-workflow.sh
# Cancel with 'n'

# Test story run (if you have test stories)
./run-story.sh test-story
```

### Areas for Contribution

**High Priority**:
- [ ] Additional project type support
- [ ] Error handling edge cases

**Medium Priority**:
- [ ] Additional agent personas
- [ ] Custom persona builder


## 🐛 Debugging

### Enable Verbose Logging

```bash
# In run-story.sh or any script
set -x  # Add at top of file
```

### Check Logs

```bash
# Development log
tail -f tooling/.automation/logs/*-develop.log

# Checkpoint service
tail -f tooling/.automation/logs/checkpoint-service.log

# Error logs
tail -f tooling/.automation/logs/checkpoint-service-error.log
```

### Common Issues

**Scripts not executable**:
```bash
chmod +x tooling/scripts/*.sh tooling/scripts/*.py
```

**Config not found**:
```bash
cp tooling/.automation/config.sh.template tooling/.automation/config.sh
```

**Python dependencies**:
```bash
python3 -m pip install --upgrade pip
# No external dependencies currently
```

## 📚 Documentation Structure

```
docs/
├── INSTALLATION.md       # Setup guide
├── USER-GUIDE.md        # How to use
├── CONFIGURATION.md     # Config options
├── AGENTS.md            # Agent system
├── COST-OPTIMIZATION.md # Cost strategy
├── API.md               # Script reference
└── TROUBLESHOOTING.md   # Common issues
```

## 🎨 Agent Persona Guidelines

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

## 🔄 Release Process

1. Update version in README.md
2. Update CHANGELOG.md
3. Create git tag: `v1.0.0`
4. Push tag: `git push origin v1.0.0`
5. Create GitHub release with notes

## 💬 Communication

- **Questions**: [Discussions](https://github.com/Pedro-Jose-da-Rocha-Mendonca/GDS_Automation/discussions)
- **Bug Reports**: [Issues](https://github.com/Pedro-Jose-da-Rocha-Mendonca/GDS_Automation/issues)
- **Security**: Open an issue with `[SECURITY]` prefix

## 🏆 Recognition

Contributors will be:
- Listed in README.md contributors section
- Mentioned in release notes
- Added to CONTRIBUTORS.md

## 📜 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn
- Follow open source etiquette

---

**Thank you for contributing!** 🎉
