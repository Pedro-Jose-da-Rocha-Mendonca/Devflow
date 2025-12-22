# Claude Code Workflow Template

> Automated development workflow powered by Claude Code CLI - A complete agent-based development system with smart model usage, context preservation, and multi-persona automation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude-Code-5A67D8)](https://claude.com/claude-code)

## 🚀 What is This?

A production-ready, portable workflow automation system that uses Claude Code CLI to implement user stories with minimal human intervention. Think "CI/CD for development" - but instead of deploying code, it writes code.

### Key Features

- **Multi-Persona Agent System** - 8 specialized AI agents (SM, DEV, BA, ARCHITECT, PM, WRITER, MAINTAINER, REVIEWER)
- **Smart Model Usage** - Opus for development, Sonnet for planning (40-60% cost savings)
- **Context Preservation** - Automatic checkpoints prevent work loss from context limits
- **Full Automation** - Context → Development → Testing → Review → Commit pipeline
- **Greenfield + Brownfield** - Supports both new features AND existing codebase maintenance
- **Agent Personalization** - Agent overrides and persistent agent memory
- **Claude Code Integration** - Native slash commands (`/story`, `/swarm`, `/pair`, `/route`, etc.)
- **Multi-Agent Collaboration** - Swarm mode, pair programming, and auto-routing
- **Project Agnostic** - Works with Flutter, Node.js, Python, Rust, Go, Ruby, etc.
- **Guided Setup** - Interactive wizard guides you through installation

## 📦 Quick Start

### Prerequisites

**macOS/Linux:**
- [Claude Code CLI](https://claude.com/claude-code) - `brew install claude-code`
- Python 3.8+
- Git
- zsh (default on macOS)

**Windows:**
- [Claude Code CLI](https://claude.com/claude-code) - `npm install -g @anthropic-ai/claude-code`
- Python 3.8+ (from python.org or Microsoft Store)
- Git for Windows
- PowerShell 5.1+ (included with Windows 10/11)

### Installation (macOS/Linux)

**Option 1: Clone and Setup (Recommended)**

```bash
# Clone this repository
git clone https://github.com/Pedro-Jose-da-Rocha-Mendonca/Devflow.git
cd Devflow

# Copy to your project
cp -r tooling /path/to/your/project/

# Run setup wizard
cd /path/to/your/project/tooling/scripts
./init-project-workflow.sh
```

**Option 2: Direct Copy**

```bash
# Download latest release
curl -L https://github.com/Pedro-Jose-da-Rocha-Mendonca/Devflow/archive/main.tar.gz | tar xz

# Move to your project
mv Devflow-main/tooling /path/to/your/project/

# Manual config
cd /path/to/your/project/tooling/.automation
cp config.sh.template config.sh
vim config.sh
```

### Installation (Windows)

**Option 1: Clone and Setup (Recommended)**

```powershell
# Clone this repository
git clone https://github.com/Pedro-Jose-da-Rocha-Mendonca/Devflow.git
cd Devflow

# Copy to your project
Copy-Item -Recurse tooling C:\path\to\your\project\

# Set execution policy (first time only, run as Admin)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run setup wizard
cd C:\path\to\your\project\tooling\scripts
.\init-project-workflow.ps1
```

**Option 2: Direct Copy**

```powershell
# Download latest release
Invoke-WebRequest -Uri "https://github.com/Pedro-Jose-da-Rocha-Mendonca/Devflow/archive/main.zip" -OutFile main.zip
Expand-Archive main.zip -DestinationPath .

# Move to your project
Move-Item Devflow-main\tooling C:\path\to\your\project\

# Manual config
cd C:\path\to\your\project\tooling\.automation
Copy-Item config.ps1.template config.ps1
notepad config.ps1
```

**Running Stories on Windows:**

```powershell
# Full pipeline with live monitoring
.\run-story.ps1 -StoryKey "3-5"

# Development only
.\run-story.ps1 -StoryKey "3-5" -Develop

# With specific model
.\run-story.ps1 -StoryKey "3-5" -Model opus

# Disable auto-commit
.\run-story.ps1 -StoryKey "3-5" -NoCommit
```

### Agent Personas

| Agent | Model | Cost | Use Case |
|-------|-------|------|----------|
| **SM** (Scrum Master) | Sonnet | Low | Context, planning, review |
| **DEV** (Developer) | Opus | High | Code implementation |
| **BA** (Business Analyst) | Sonnet | Low | Requirements |
| **ARCHITECT** | Sonnet | Low | Design specs |
| **PM** (Product Manager) | Sonnet | Low | Epic planning |
| **WRITER** | Sonnet | Low | Documentation |
| **MAINTAINER** | Opus/Sonnet | Varies | Bug fixes, refactoring, tech debt |
| **REVIEWER** (Adversarial) | Opus | High | Critical code review, finds problems |

## 💻 Claude Slash Commands

Devflow provides native slash commands for Claude Code:

### Core Commands

| Command | Description |
|---------|-------------|
| `/story <key>` | Run full story pipeline (context + dev + review) |
| `/develop <key>` | Run development phase only |
| `/review <key>` | Run code review phase |
| `/agent <name>` | Invoke a specific agent |
| `/adversarial <key>` | Critical review with Opus |

### Collaboration Commands (NEW!)

| Command | Description |
|---------|-------------|
| `/swarm <key>` | Multi-agent debate/consensus mode |
| `/pair <key>` | DEV + REVIEWER pair programming |
| `/route <task>` | Auto-route to best agents |
| `/collab <key>` | Unified collaboration CLI |

### Utility Commands

| Command | Description |
|---------|-------------|
| `/memory <key>` | View/query shared agent memory |
| `/handoff <key>` | View handoff summaries between agents |
| `/checkpoint` | Create/restore context checkpoints |
| `/costs` | View cost dashboard and analytics |
| `/personalize` | Agent personalization wizard |
| `/devflow <cmd>` | Run any Devflow command |

**Examples:**
```bash
/swarm 3-5                          # Run swarm with default agents
/swarm 3-5 --agents ARCHITECT,DEV   # Custom agents
/pair 3-5                           # Pair programming mode
/route "fix login bug"              # Auto-route to specialists
/memory 3-5 --query "auth decisions" # Query knowledge graph
```

## 🤖 Multi-Agent Collaboration

Devflow supports advanced multi-agent collaboration modes:

### Swarm Mode (Multi-Agent Debate)

Multiple agents work together, debating and iterating until consensus:

```bash
# Run swarm with default agents (ARCHITECT, DEV, REVIEWER)
./run-story.sh 3-5 --swarm

# Custom agent selection
./run-story.sh 3-5 --swarm --agents ARCHITECT,DEV,REVIEWER,SECURITY

# Control iterations
./run-story.sh 3-5 --swarm --max-iter 5
```

**How it works:**
1. All agents analyze the task
2. Agents provide feedback on each other's work
3. Issues are addressed iteratively
4. Continues until consensus or max iterations

### Pair Programming Mode

DEV and REVIEWER work together in real-time:

```bash
./run-story.sh 3-5 --pair
```

**How it works:**
1. DEV implements code in small chunks
2. REVIEWER provides immediate feedback
3. DEV addresses issues before continuing
4. Higher quality code with fewer late-stage revisions

### Auto-Route Mode (Intelligent Agent Selection)

Let Devflow automatically select the best agents:

```bash
# Auto-detect task type and select appropriate agents
./run-story.sh "fix authentication bug" --auto-route

# Works with any task description
./run-story.sh "add user profile feature" --auto-route
```

**How it works:**
- Analyzes task description for keywords
- Considers file types and complexity
- Routes to appropriate specialists (e.g., security → SECURITY agent)

### Shared Memory & Knowledge Graph

Agents now share context and learnings:

```bash
# View shared memory for a story
python tooling/scripts/run-collab.py 3-5 --memory

# Query the knowledge graph
python tooling/scripts/run-collab.py 3-5 --query "What did ARCHITECT decide about auth?"
```

**Features:**
- Cross-agent shared memory pool
- Decision tracking with knowledge graph
- Automatic handoff summaries between agents
- Queryable project knowledge base

### Budget Controls

Claude Code CLI provides built-in cost tracking. The workflow scripts add budget controls:

```bash
export MAX_BUDGET_CONTEXT=3.00   # Context creation: $3 max
export MAX_BUDGET_DEV=15.00      # Development: $15 max
export MAX_BUDGET_REVIEW=5.00    # Code review: $5 max
```

**Cost Optimization:**
- Opus for development and critical reviews (higher quality)
- Sonnet for planning, context, documentation (cost-effective)

## ⌨️ Shell Completion

Enable tab-completion for faster command entry.

### Zsh (macOS/Linux)

```bash
# Option 1: Add to fpath (recommended)
mkdir -p ~/.zsh/completions
cp tooling/completions/_run-story ~/.zsh/completions/

# Add to ~/.zshrc:
fpath=(~/.zsh/completions $fpath)
autoload -Uz compinit && compinit

# Reload shell
source ~/.zshrc
```

```bash
# Option 2: Direct source
# Add to ~/.zshrc:
source /path/to/devflow/tooling/completions/_run-story
```

### Bash (Linux)

```bash
# Option 1: System-wide (requires sudo)
sudo cp tooling/completions/run-story-completion.bash /etc/bash_completion.d/devflow

# Option 2: User only - add to ~/.bashrc:
source /path/to/devflow/tooling/completions/run-story-completion.bash
```

### PowerShell (Windows)

```powershell
# Add to your PowerShell profile ($PROFILE):
. C:\path\to\devflow\tooling\completions\DevflowCompletion.ps1

# Or import as module:
Import-Module C:\path\to\devflow\tooling\completions\DevflowCompletion.ps1

# View available commands
devflow-help
```

### What Gets Completed

- **Modes**: `--swarm`, `--pair`, `--auto-route`, `--sequential`
- **Agents**: `SM`, `DEV`, `BA`, `ARCHITECT`, `PM`, `WRITER`, `MAINTAINER`, `REVIEWER`
- **Models**: `opus`, `sonnet`, `haiku`
- **Options**: `--budget`, `--max-iterations`, `--quiet`, etc.

**Example usage:**

```bash
# Type and press Tab:
./run-story.sh 3-5 --sw<TAB>     # Completes to --swarm
./run-story.sh 3-5 --agents AR<TAB>  # Completes to ARCHITECT
```

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

Free to use in commercial and personal projects.

## 🙏 Acknowledgments

- Built for [Claude Code CLI](https://claude.com/claude-code)
- Agent override system inspired by [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)
- Agent-based architecture influenced by AutoGPT, CrewAI


<!-- VERSION_START - Auto-updated by update_version.py -->
**Version**: 1.7.0
**Status**: Production Ready
**Last Updated**: 2025-01-13
<!-- VERSION_END -->
