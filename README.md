# Claude Code Workflow Template

> Automated development workflow powered by Claude Code CLI - A complete agent-based development system with smart model usage, context preservation, and multi-persona automation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude-Code-5A67D8)](https://claude.com/claude-code)

## 🚀 What is This?

A production-ready, portable workflow automation system that uses Claude Code CLI to implement user stories with minimal human intervention. Think "CI/CD for development" - but instead of deploying code, it writes code.

### Key Features

- ✅ **Multi-Persona Agent System** - 6 specialized AI agents (SM, DEV, BA, ARCHITECT, PM, WRITER)
- ✅ **Smart Model Usage** - Opus for development, Sonnet for planning (40-60% cost savings)
- ✅ **Context Preservation** - Automatic checkpoints prevent work loss from context limits
- ✅ **Full Automation** - Context → Development → Testing → Review → Commit pipeline
- ✅ **Project Agnostic** - Works with Flutter, Node.js, Python, Rust, Go, Ruby, etc.
- ✅ **Guided Setup** - Interactive wizard guides you through installation
- ✅ **Documentation Standards** - Built-in templates and generators

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
git clone https://github.com/Pedro-Jose-da-Rocha-Mendonca/GDS_Automation.git
cd GDS_Automation

# Copy to your project
cp -r tooling /path/to/your/project/

# Run setup wizard
cd /path/to/your/project/tooling/scripts
./init-project-workflow.sh
```

**Option 2: Direct Copy**

```bash
# Download latest release
curl -L https://github.com/Pedro-Jose-da-Rocha-Mendonca/GDS_Automation/archive/main.tar.gz | tar xz

# Move to your project
mv GDS_Automation-main/tooling /path/to/your/project/

# Manual config
cd /path/to/your/project/tooling/.automation
cp config.sh.template config.sh
vim config.sh
```

### Installation (Windows)

**Option 1: Clone and Setup (Recommended)**

```powershell
# Clone this repository
git clone https://github.com/Pedro-Jose-da-Rocha-Mendonca/GDS_Automation.git
cd GDS_Automation

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
Invoke-WebRequest -Uri "https://github.com/Pedro-Jose-da-Rocha-Mendonca/GDS_Automation/archive/main.zip" -OutFile main.zip
Expand-Archive main.zip -DestinationPath .

# Move to your project
Move-Item GDS_Automation-main\tooling C:\path\to\your\project\

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

## 📖 Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup instructions
- **[User Guide](docs/USER-GUIDE.md)** - How to use the workflow
- **[Configuration](docs/CONFIGURATION.md)** - All configuration options
- **[Agent Personas](docs/AGENTS.md)** - How the multi-agent system works
- **[API Reference](docs/API.md)** - Script reference

## 🏗️ Architecture

### Directory Structure

```
your-project/
├── tooling/                        # Add this to any project
│   ├── .automation/
│   │   ├── agents/                # 6 AI agent personas
│   │   ├── checkpoints/           # Auto-created context saves
│   │   ├── logs/                  # Execution logs
│   │   └── config.sh              # Your configuration
│   ├── scripts/
│   │   ├── run-story.sh           # Main workflow runner
│   │   ├── checkpoint             # Context management
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

### Budget Controls

```bash
# In config.sh
export MAX_BUDGET_CONTEXT=3.00   # Auto-abort at $3
export MAX_BUDGET_DEV=15.00      # Auto-abort at $15
export MAX_BUDGET_REVIEW=5.00    # Auto-abort at $5
```

### Cost Analysis System

Real-time cost tracking with multi-currency display:

```bash
# Run with native cost tracking
python run-story.py 3-5 --native --show-costs

# View cost dashboard
python cost_dashboard.py --summary           # 30-day summary
python cost_dashboard.py --history 10        # Last 10 sessions
python cost_dashboard.py --story 3-5         # Costs for specific story
python cost_dashboard.py --export costs.csv  # Export to CSV
```

**Display Features:**
- Real-time token counts (input/output)
- Multi-currency display (USD, EUR, GBP, BRL)
- Per-agent and per-model cost breakdown
- Budget alerts (warning at 75%, critical at 90%)
- Auto-stop at budget limit

**Sample Output:**
```
╔══════════════════════════════════════════════════════════════════╗
║                    COST MONITOR - Story: 3-5                     ║
╠══════════════════════════════════════════════════════════════════╣
║  Agent: DEV          Model: opus       Elapsed: 04:32            ║
║  Tokens: 57,680      Cost: $1.77       Budget: 12% used          ║
║  USD: $1.77 │ EUR: €1.63 │ GBP: £1.40 │ BRL: R$10.80            ║
╚══════════════════════════════════════════════════════════════════╝
```

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

### Advanced Options

```bash
# Permission mode
export PERMISSION_MODE="dangerouslySkipPermissions"

# Checkpoint thresholds (%, warning/critical/emergency)
export CHECKPOINT_THRESHOLDS="75,85,95"

# Tool permissions per agent
# See docs/CONFIGURATION.md for full options
```

### Cost Tracking Options

```bash
# Cost display settings
export COST_DISPLAY_CURRENCY="USD"   # Primary currency
export COST_WARNING_PERCENT=75       # Warning threshold
export COST_CRITICAL_PERCENT=90      # Critical threshold
export COST_AUTO_STOP="true"         # Auto-stop at 100%

# Currency exchange rates (for multi-currency display)
export CURRENCY_RATE_EUR=0.92
export CURRENCY_RATE_GBP=0.79
export CURRENCY_RATE_BRL=6.10
```

## 🛠️ Available Commands

### Cross-Platform (Works on Windows, macOS, Linux)

```bash
# Main workflow - auto-detects your OS
python run-story.py <key>              # Full pipeline
python run-story.py <key> --develop    # Development only
python run-story.py <key> --review     # Review only
python run-story.py <key> --context    # Context only
python run-story.py <key> --native     # With cost tracking
python run-story.py <key> --budget 20  # Custom budget limit

# Cost dashboard
python cost_dashboard.py               # Show latest session
python cost_dashboard.py --summary     # 30-day summary
python cost_dashboard.py --history 10  # Last 10 sessions
python cost_dashboard.py --story 3-5   # Filter by story
python cost_dashboard.py --export costs.csv  # Export data

# Setup wizard
python init-project-workflow.py

# Checkpoint service
python setup-checkpoint-service.py install
python setup-checkpoint-service.py status

# Documentation generator
python new-doc.py --type guide --name "setup"
```

### Platform-Specific Commands

**macOS/Linux:**
```bash
./run-story.sh <key>
./checkpoint --list
./new-doc.sh --type guide --name "setup"
```

**Windows PowerShell:**
```powershell
.\run-story.ps1 -StoryKey "<key>"
python context_checkpoint.py --list
.\new-doc.ps1 -Type guide -Name "setup"
```

### Checkpoint Management

```bash
python context_checkpoint.py --list        # List all checkpoints
python context_checkpoint.py --checkpoint  # Create manual checkpoint
python context_checkpoint.py --resume <id> # Resume from checkpoint
```

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

### Development Setup

```bash
git clone https://github.com/Pedro-Jose-da-Rocha-Mendonca/GDS_Automation.git
cd GDS_Automation

# Make changes to tooling/scripts/*
vim tooling/scripts/run-story.sh

# Test locally
cp -r tooling /tmp/test-project/
cd /tmp/test-project/tooling/scripts
./run-story.sh test-story
```

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

Free to use in commercial and personal projects.

## 🙏 Acknowledgments

- Built for [Claude Code CLI](https://claude.com/claude-code)
- Inspired by BMAD method
- Agent-based architecture influenced by AutoGPT, CrewAI

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/Pedro-Jose-da-Rocha-Mendonca/GDS_Automation/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Pedro-Jose-da-Rocha-Mendonca/GDS_Automation/discussions)

## ⭐ Star History

If this project helps you, consider giving it a star!

---

**Made with ❤️ for developers who want AI to helps**

**Version**: 1.0.0
**Status**: Production Ready
**Last Updated**: 2025-12-20
