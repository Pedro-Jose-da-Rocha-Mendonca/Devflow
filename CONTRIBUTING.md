# Contributing to Claude Workflow Template

Thank you for your interest in contributing! This project aims to make AI-powered development workflows accessible to everyone.

## 🎯 How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/Pedro-Jose-da-Rocha-Mendonca/Devflow/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Claude Code version, project type)
   - Relevant log files from `tooling/.automation/logs/`

### Areas for Contribution

**High Priority**:
- [ ] Error handling edge cases
- [ ] Brownfield workflow improvements

**Medium Priority**:
- [ ] Better migration tooling

**Override System**:
- [ ] Cross-agent memory sharing

**Brownfield-Specific**:
- [ ] Safer refactoring patterns

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
   
## 📜 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn
- Follow open source etiquette

---

**Thank you for contributing!** 🎉
