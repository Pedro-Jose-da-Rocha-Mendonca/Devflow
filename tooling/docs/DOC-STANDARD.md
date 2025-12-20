# Documentation Standard - Stronger Project

**Version**: 1.0
**Last Updated**: 2025-12-20
**Applies To**: All documentation in `tooling/docs/`

---

## Purpose

This document defines the standard format, structure, and conventions for all documentation in the Stronger project's `tooling/docs/` directory.

---

## File Naming Conventions

### Format
```
[TYPE]-[descriptive-name].md
```

### Types
- `GUIDE` - User-facing guides and tutorials
- `SPEC` - Technical specifications
- `STATUS` - Status reports and tracking documents
- `STANDARD` - Standards and conventions (like this doc)
- `REFERENCE` - Quick reference sheets
- `EXAMPLE` - Code examples and patterns
- `STORY` - Story specifications (numbered: `3-6-story-name.md`)

### Examples
```
✅ Good:
- GUIDE-context-checkpoint.md
- SPEC-epic-3-goals.md
- STATUS-checkpoint-integration.md
- REFERENCE-automation-commands.md
- STANDARD-documentation.md
- EXAMPLE-checkpoint-integration.md

❌ Bad:
- context-checkpoint-guide.md
- epic3spec.md
- checkpoint_status.md
- automation.md
```

---

## Document Structure

### Required Sections (in order)

Every document MUST include these sections:

1. **Title** (H1)
2. **Metadata Block**
3. **Purpose/Overview**
4. **Table of Contents** (if >500 lines)
5. **Main Content**
6. **Footer**

### Optional Sections

Include as appropriate:
- Quick Start
- Examples
- Troubleshooting
- FAQ
- Related Documents
- Changelog

---

## Template

```markdown
# [Document Title]

**Type**: [Guide|Spec|Status|Reference|Example]
**Version**: X.Y
**Last Updated**: YYYY-MM-DD
**Author**: [Agent/Person]
**Status**: [Draft|Active|Deprecated]

---

## Purpose

[1-2 sentence description of what this document is for]

## Table of Contents

- [Section 1](#section-1)
- [Section 2](#section-2)
...

---

## [Main Content Sections]

...

---

## Related Documents

- [Link](path) - Description
- [Link](path) - Description

---

**Document Control**
- **Created**: YYYY-MM-DD
- **Last Reviewed**: YYYY-MM-DD
- **Next Review**: YYYY-MM-DD
- **Owner**: [Agent/Person]
```

---

## Formatting Standards

### Headers

```markdown
# H1 - Document Title Only (once per file)

## H2 - Major Sections

### H3 - Subsections

#### H4 - Sub-subsections (use sparingly)
```

### Code Blocks

Always specify language:

````markdown
```bash
# Shell commands
./run-story.sh 3-7
```

```python
# Python code
def example():
    pass
```

```yaml
# YAML
key: value
```
````

### Lists

**Bullet Lists**:
```markdown
- First level
  - Second level (2 spaces)
    - Third level (4 spaces)
```

**Numbered Lists**:
```markdown
1. First item
2. Second item
   - Sub-item (mixed lists OK)
3. Third item
```

### Emphasis

```markdown
**Bold** for emphasis
*Italic* for light emphasis
`code` for inline code/commands
```

### Links

```markdown
# External
[Link Text](https://example.com)

# Internal
[Section](#section-name)
[Other Doc](./other-doc.md)
```

### Tables

Always include header separator:

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data     | Data     | Data     |
```

### Alerts/Callouts

Use these emoji conventions:

```markdown
⚠️  **WARNING**: Important warning

💡 **TIP**: Helpful tip

📝 **NOTE**: Additional information

🚨 **CRITICAL**: Critical information

✅ **SUCCESS**: Successful outcome

❌ **ERROR**: Error or failure

🎯 **GOAL**: Objective or target

📊 **DATA**: Data or statistics

🔧 **TECHNICAL**: Technical details
```

---

## Content Guidelines

### Writing Style

1. **Active Voice**: "Run the script" not "The script should be run"
2. **Present Tense**: "The system creates" not "The system will create"
3. **Second Person**: "You can run" not "One can run" or "The user can run"
4. **Concise**: Remove unnecessary words
5. **Scannable**: Use headers, lists, and white space

### Examples

Always include:
- Input (what to type)
- Expected output
- Context (when/why to use)

```markdown
### Example: Creating a Checkpoint

**When to use**: Before risky operations

**Input**:
```bash
./tooling/scripts/checkpoint --checkpoint
```

**Expected Output**:
```
[09:04:45] 💾 Creating checkpoint: checkpoint_20251220_090445_1
[09:04:45] ✅ Checkpoint saved: checkpoint_20251220_090445_1.json
```
````

### Commands

Format commands consistently:

```markdown
# Single command
./run-story.sh 3-7

# Command with output
$ ./run-story.sh 3-7
Story: 3-7-build-strength-progression-graph
...

# Multi-line command
python3 tooling/scripts/context_checkpoint.py \
    --watch-log tooling/.automation/logs/3-7-develop.log \
    --session-id 3-7
```

---

## Document Types

### 1. GUIDE Documents

**Purpose**: Help users accomplish a task

**Required Sections**:
- Purpose
- Prerequisites
- Quick Start
- Step-by-Step Instructions
- Examples
- Troubleshooting
- Next Steps

**Example**: `GUIDE-context-checkpoint.md`

### 2. SPEC Documents

**Purpose**: Define technical specifications

**Required Sections**:
- Overview
- Objectives and Scope
- Architecture
- Implementation Details
- Dependencies
- Testing Requirements
- Acceptance Criteria

**Example**: `SPEC-epic-3-goals.md`

### 3. STATUS Documents

**Purpose**: Track progress and state

**Required Sections**:
- Current Status
- Integration Points
- What's Working
- What's Not Working
- Next Steps

**Example**: `STATUS-checkpoint-integration.md`

### 4. REFERENCE Documents

**Purpose**: Quick lookup information

**Required Sections**:
- Quick Reference Tables
- Command List
- Common Patterns
- Links to Full Guides

**Example**: `REFERENCE-automation-commands.md`

### 5. EXAMPLE Documents

**Purpose**: Show how to use features

**Required Sections**:
- Problem Statement
- Solution Overview
- Complete Example Code
- Explanation
- Variations

**Example**: `EXAMPLE-checkpoint-integration.md`

---

## Version Control

### Version Numbers

Format: `MAJOR.MINOR`

- **MAJOR**: Significant restructuring or breaking changes
- **MINOR**: Content updates, additions, clarifications

Example: `1.0` → `1.1` → `2.0`

### Changelog

Include at bottom of document:

```markdown
## Changelog

### 2.0 (2025-12-25)
- Major restructure of automation section
- Added new examples

### 1.1 (2025-12-20)
- Added troubleshooting section
- Fixed command examples

### 1.0 (2025-12-15)
- Initial version
```

---

## Directory Organization

```
tooling/docs/
├── standards/
│   └── DOC-STANDARD.md           # This file
│
├── guides/
│   ├── GUIDE-context-checkpoint.md
│   ├── GUIDE-automation-setup.md
│   └── GUIDE-story-workflow.md
│
├── specs/
│   ├── SPEC-epic-1.md
│   ├── SPEC-epic-2.md
│   └── SPEC-epic-3.md
│
├── status/
│   ├── STATUS-checkpoint-integration.md
│   ├── STATUS-sprint.md
│   └── sprint-status.yaml
│
├── references/
│   ├── REFERENCE-automation-commands.md
│   ├── REFERENCE-git-workflow.md
│   └── STORY-POINTS-EPIC-3.md
│
├── examples/
│   ├── EXAMPLE-checkpoint-integration.md
│   └── EXAMPLE-persona-switching.md
│
└── stories/
    ├── 3-6-build-workout-frequency-chart.md
    ├── 3-7-build-strength-progression-graph.md
    └── ...
```

---

## Review Process

### Required Reviews

1. **Self-Review**: Author checks against this standard
2. **Peer Review**: Another agent/person reviews
3. **Final Approval**: SM or Lead approves

### Review Checklist

- [ ] Follows naming convention
- [ ] Includes required metadata
- [ ] Has all required sections
- [ ] Code examples are tested
- [ ] Links are valid
- [ ] No spelling errors
- [ ] Scannable (headers, lists, whitespace)
- [ ] Examples include input/output
- [ ] Related docs are linked

---

## Migration Plan

### Phase 1: New Documents (Immediate)

All new documentation MUST follow this standard.

### Phase 2: High-Priority Updates (Week 1)

Update these documents first:
1. Main guides (checkpoint, automation)
2. Epic specs
3. Status documents

### Phase 3: Complete Migration (Week 2-3)

- Rename all documents to new convention
- Reorganize into subdirectories
- Add missing metadata blocks
- Fix formatting inconsistencies

---

## Tools

### Document Template

Use this template for new docs:

```bash
./tooling/scripts/new-doc.sh --type guide --name "my-new-guide"
# Creates: tooling/docs/guides/GUIDE-my-new-guide.md
# With full template populated
```

### Validation

Check document compliance:

```bash
./tooling/scripts/validate-docs.sh tooling/docs/GUIDE-checkpoint.md
# Checks naming, structure, required sections
```

---

## Examples

### Good Documentation

✅ Clear title and metadata:
```markdown
# Context Checkpoint User Guide

**Type**: Guide
**Version**: 1.0
**Last Updated**: 2025-12-20
**Author**: Dev Agent
**Status**: Active
```

✅ Scannable sections:
```markdown
## Quick Start

### Option 1: Interactive Mode
```bash
./tooling/scripts/checkpoint
```

### Option 2: Auto-Monitor
```bash
python3 tooling/scripts/context_checkpoint.py --watch-log <file>
```
```

✅ Complete examples:
```markdown
### Example: Resume from Checkpoint

**Problem**: Context was compacted mid-session

**Solution**:
```bash
# List checkpoints
./tooling/scripts/checkpoint --list

# Resume from latest
./tooling/scripts/checkpoint --resume checkpoint_20251220_090445_1
```

**Result**: Resume prompt is displayed to paste into Claude
```

### Bad Documentation

❌ Unclear title:
```markdown
# Checkpoint Stuff

Some information about checkpoints...
```

❌ Missing metadata:
```markdown
# My Guide

Here's how to do stuff...
```

❌ Incomplete examples:
```markdown
Just run this:
```bash
./script.sh
```
```

❌ Poor formatting:
```markdown
You can run script.sh or use the checkpoint command to create a checkpoint or list them using --list flag...
```

---

## Compliance

### Enforcement

- All PRs with documentation changes must pass validation
- SM agents will reject non-compliant documents
- Automated checks run on commit

### Exceptions

To request an exception:
1. Document reason in PR description
2. Get approval from SM or Lead
3. Add `<!-- EXCEPTION: reason -->` to document

---

## Updates to This Standard

### Proposing Changes

1. Create issue with proposed change
2. Discuss with team
3. Update this document
4. Increment version number
5. Add to changelog

### Notification

When this standard changes:
- Announce in team chat
- Update all templates
- Schedule review of existing docs

---

## Changelog

### 1.0 (2025-12-20)
- Initial standard created
- Defined naming conventions
- Established document structure
- Created templates
- Defined review process

---

**Document Control**
- **Created**: 2025-12-20
- **Last Reviewed**: 2025-12-20
- **Next Review**: 2026-01-20
- **Owner**: Dev Agent
