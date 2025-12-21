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
- **Claude Code Integration** - Native slash commands (`/story`, `/develop`, `/review`, etc.)
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

## 🏗️ Architecture

### Directory Structure

```
your-project/
├── tooling/                        # Add this to any project
│   ├── .automation/
│   │   ├── agents/                # 8 AI agent personas
│   │   ├── overrides/             # Agent personalization (survives updates)
│   │   ├── memory/                # Persistent agent learning
│   │   ├── checkpoints/           # Auto-created context saves
│   │   ├── logs/                  # Execution logs
│   │   └── config.sh              # Your configuration
│   ├── scripts/
│   │   ├── run-story.sh           # Main workflow runner
│   │   └── lib/                   # Core libraries
│   └── docs/
│       ├── sprint-status.yaml     # Sprint tracking
│       └── *.md                   # Story specifications
├── app/                           # Your actual project
└── ...
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

### Budget Controls

```bash
# In config.sh
export MAX_BUDGET_CONTEXT=3.00   # Auto-abort at $3
export MAX_BUDGET_DEV=15.00      # Auto-abort at $15
export MAX_BUDGET_REVIEW=5.00    # Auto-abort at $5
```

### Cost Management

Claude Code CLI provides built-in cost tracking. The workflow scripts add budget controls:

```bash
# Budget controls abort if exceeded
export MAX_BUDGET_CONTEXT=3.00   # Context creation: $3 max
export MAX_BUDGET_DEV=15.00      # Development: $15 max
export MAX_BUDGET_REVIEW=5.00    # Code review: $5 max
```

**Cost Optimization:**
- Opus for development and critical reviews (higher quality)
- Sonnet for planning, context, documentation (cost-effective)

## 🔧 Configuration

### Basic Setup

```bash
# tooling/.automation/config.sh
export PROJECT_NAME="my-app"
export PROJECT_TYPE="flutter"        # or: node, python, rust, etc.
export CLAUDE_MODEL_DEV="opus"       # Development model
export CLAUDE_MODEL_PLANNING="sonnet" # Planning model
export AUTO_COMMIT="true"            # Auto-commit after dev
export AUTO_PR="false"               # Auto-create PR (needs gh CLI)
```

## 🔧 Brownfield Workflows

For existing codebases, use brownfield modes to fix bugs, refactor code, and manage technical debt.

### Bug Fixes

```bash
# Fix a bug with a documented report
./run-story.sh login-crash --bugfix

# Fix a bug by description
./run-story.sh "users can't logout on mobile" --bugfix
```

### Refactoring

```bash
# Refactor a specific component
./run-story.sh auth-service --refactor

# Refactor with a spec file
# Create: tooling/docs/refactors/auth-service.md
./run-story.sh auth-service --refactor
```

### Investigation (Read-Only)

```bash
# Investigate how a feature works
./run-story.sh payment-flow --investigate

# Explore architecture
./run-story.sh database-layer --investigate
```

### Quick Fixes

```bash
# Make small, targeted changes
./run-story.sh "fix typo in header" --quickfix
./run-story.sh "update copyright year" --quickfix
```

### Migrations

```bash
# Run a planned migration
./run-story.sh react-18-upgrade --migrate

# Create: tooling/docs/migrations/react-18-upgrade.md
```

### Technical Debt

```bash
# Resolve technical debt
./run-story.sh legacy-api-cleanup --tech-debt
```

### Brownfield Directory Structure

```
tooling/docs/
├── bugs/              # Bug reports and fix summaries
├── refactors/         # Refactoring specs and summaries
├── investigations/    # Investigation reports
├── migrations/        # Migration plans and logs
└── tech-debt/         # Technical debt items
```

## 🛠️ Available Commands

### Claude Code Slash Commands

Use native Claude Code slash commands for all workflows:

| Command | Description |
|---------|-------------|
| `/story <key>` | Run full story pipeline (context + dev + review) |
| `/develop <key>` | Run development phase only |
| `/review <key>` | Run standard code review |
| `/adversarial <key>` | Run critical code review (Opus) |
| `/bugfix <id>` | Fix a bug |
| `/agent <name>` | Invoke a specific agent |
| `/devflow <cmd>` | Run any workflow command |

## 🔒 Security & Privacy

### Data Handling

- **No data collection** - All processing local or via Claude API
- **Git-friendly** - Sensitive files in `.gitignore`
- **API keys** - Use environment variables, never committed

### Recommended `.gitignore`

```gitignore
# Already included in tooling/.gitignore
tooling/.automation/logs/
tooling/.automation/checkpoints/
tooling/.automation/config.sh     # Keep your config local
```

### Budget Protection

```bash
# Hard limits prevent runaway costs
export MAX_BUDGET_DEV=15.00
# Script aborts if exceeded
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

Free to use in commercial and personal projects.

## 🙏 Acknowledgments

- Built for [Claude Code CLI](https://claude.com/claude-code)
- Agent override system inspired by [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)
- Agent-based architecture influenced by AutoGPT, CrewAI

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/Pedro-Jose-da-Rocha-Mendonca/Devflow/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Pedro-Jose-da-Rocha-Mendonca/Devflow/discussions)

---

**Version**: 1.4.0
**Status**: Production Ready
**Last Updated**: 2025-12-21
