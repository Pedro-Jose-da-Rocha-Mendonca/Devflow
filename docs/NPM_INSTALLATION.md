# Devflow npm Installation Guide

Complete guide for installing and using Devflow via npm.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Available Commands](#available-commands)
- [Troubleshooting](#troubleshooting)
- [npm vs pip Comparison](#npm-vs-pip-comparison)
- [Uninstallation](#uninstallation)

## Prerequisites

### Required

- **Python 3.9 or higher** - Devflow's core scripts are written in Python
  - Check version: `python3 --version` or `python --version`
  - Install from [python.org](https://www.python.org/downloads/)

- **Node.js 14.0.0 or higher** - For npm package management
  - Check version: `node --version`
  - Install from [nodejs.org](https://nodejs.org/)

- **npm 6.0.0 or higher** - Comes with Node.js
  - Check version: `npm --version`

### Platform-Specific

#### macOS
```bash
# Using Homebrew
brew install python@3.11 node

# Verify
python3 --version
node --version
```

#### Linux (Ubuntu/Debian)
```bash
# Install Python and Node.js
sudo apt update
sudo apt install python3 python3-pip nodejs npm

# Verify
python3 --version
node --version
```

#### Windows
1. Install Python from [python.org](https://www.python.org/downloads/windows/)
   - Check "Add Python to PATH" during installation
2. Install Node.js from [nodejs.org](https://nodejs.org/)
3. Verify in Command Prompt:
   ```cmd
   python --version
   node --version
   ```

## Installation

### Global Installation (Recommended)

Install Devflow globally to use from any directory:

```bash
npm install -g @pjmendonca/devflow
```

After installation, verify it works:

```bash
devflow-validate
```

You should see:
```
✓ Python 3.x.x found (python3)
✓ Devflow is ready to use!

Try: devflow-validate
```

### Local Project Installation

Install in a specific project:

```bash
cd /path/to/your/project
npm install devflow
```

Run commands using npx:

```bash
npx devflow-validate
npx devflow-cost
```

## Available Commands

All 14 CLI commands are available after installation:

### Core Commands

#### `devflow-validate`
Validate your Devflow setup and environment.

```bash
devflow-validate
```

#### `devflow-init`
Initialize Devflow in your project with interactive wizard.

```bash
devflow-init
```

#### `devflow-cost`
View cost tracking dashboard for Claude API usage.

```bash
devflow-cost                    # Interactive dashboard
devflow-cost --summary          # Show summary
devflow-cost --list-sessions    # List all sessions
devflow-cost --export csv       # Export to CSV
```

### Story & Workflow Commands

#### `devflow-story`
Run development stories with agent automation.

```bash
devflow-story 3-5              # Run stories 3 through 5
devflow-story 3-5 --phase dev  # Run only development phase
devflow-story 3-5 --pair       # Use pair programming mode
devflow-story 3-5 --swarm      # Use swarm mode
```

#### `devflow-collab`
Run collaborative multi-agent workflows.

```bash
devflow-collab --swarm         # Multi-agent debate/consensus
devflow-collab --pair          # DEV + REVIEWER collaboration
devflow-collab --auto-route    # Intelligent agent selection
```

### Checkpoint & Memory Commands

#### `devflow-checkpoint`
Manage context checkpoints for long-running tasks.

```bash
devflow-checkpoint create      # Create checkpoint
devflow-checkpoint restore     # Restore from checkpoint
devflow-checkpoint list        # List checkpoints
```

#### `devflow-memory`
Manage agent memory and knowledge base.

```bash
devflow-memory summarize       # Summarize memory
devflow-memory query "search"  # Query memory
devflow-memory stats           # Show memory statistics
```

#### `devflow-setup-checkpoint`
Initialize checkpoint service.

```bash
devflow-setup-checkpoint
```

### Personalization Commands

#### `devflow-personalize`
Personalize agent behavior with guided wizard.

```bash
devflow-personalize
```

#### `devflow-create-persona`
Create custom agent personas.

```bash
devflow-create-persona
```

#### `devflow-validate-overrides`
Validate agent override configurations.

```bash
devflow-validate-overrides
```

### Documentation & Tracking

#### `devflow-new-doc`
Generate new documentation files.

```bash
devflow-new-doc
```

#### `devflow-tech-debt`
Track and manage technical debt.

```bash
devflow-tech-debt list         # List tech debt items
devflow-tech-debt add          # Add new item
```

### Utility Commands

#### `devflow-version`
Manage and sync version numbers across project files.

```bash
devflow-version --check        # Check version sync
devflow-version --version 1.9.0 # Set specific version
```

## Troubleshooting

### Python Not Found

**Error:**
```
✗ Python not found
```

**Solution:**

**macOS/Linux:**
```bash
# Check if Python is installed
which python3

# If not found, install
brew install python@3.11  # macOS
sudo apt install python3   # Ubuntu/Debian
```

**Windows:**
1. Download Python from [python.org](https://www.python.org/downloads/windows/)
2. Run installer and check "Add Python to PATH"
3. Restart Command Prompt
4. Verify: `python --version`

### Wrong Python Version

**Error:**
```
✗ Python 3.8.x found, but 3.9.0+ required
```

**Solution:**

Upgrade Python to 3.9 or higher:

**macOS:**
```bash
brew upgrade python@3.11
```

**Linux:**
```bash
sudo apt update
sudo apt install python3.11
```

**Windows:**

Download and install Python 3.11+ from [python.org](https://www.python.org/downloads/windows/)

### Permission Errors

**Error:**
```
EACCES: permission denied
```

**Solution:**

**Option 1: Use npm without sudo (Recommended)**

```bash
# Configure npm to use a different directory
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH=~/.npm-global/bin:$PATH

# Reload shell
source ~/.bashrc  # or source ~/.zshrc

# Install again
npm install -g devflow
```

**Option 2: Use sudo (Not recommended)**

```bash
sudo npm install -g devflow
```

### Windows: Scripts Disabled

**Error:**
```
cannot be loaded because running scripts is disabled
```

**Solution:**

Run PowerShell as Administrator:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try installation again.

### Command Not Found

**Error:**
```
devflow-validate: command not found
```

**Solution:**

1. Ensure global installation succeeded:
   ```bash
   npm list -g devflow
   ```

2. Check npm global bin directory is in PATH:
   ```bash
   npm config get prefix
   ```

3. Add to PATH if needed:

   **macOS/Linux (add to ~/.bashrc or ~/.zshrc):**
   ```bash
   export PATH="$(npm config get prefix)/bin:$PATH"
   ```

   **Windows:**
   - Add `C:\Users\<YourName>\AppData\Roaming\npm` to PATH
   - Restart Command Prompt

## npm vs pip Comparison

Both installation methods work identically. Choose based on your ecosystem preference:

| Feature | npm | pip |
|---------|-----|-----|
| **Installation** | `npm install -g @pjmendonca/devflow` | `pip install devflow` |
| **Commands** | Same 14 commands | Same 14 commands |
| **Updates** | `npm update -g @pjmendonca/devflow` | `pip install --upgrade devflow` |
| **Uninstall** | `npm uninstall -g @pjmendonca/devflow` | `pip uninstall devflow` |
| **Requirements** | Python 3.9+ + Node.js 14+ | Python 3.9+ |
| **Package Size** | ~600KB | ~500KB |
| **Ecosystem** | Node.js/JavaScript | Python |
| **Published** | npm registry | PyPI (planned) |

### When to Use npm

- You work primarily in Node.js/JavaScript projects
- You prefer npm for dependency management
- You want the latest published version
- Your team uses npm for tooling

### When to Use pip

- You work primarily in Python projects
- You prefer Python's package management
- You want to install from source
- You're already using pip for other tools

## Uninstallation

### Global Uninstall

```bash
npm uninstall -g @pjmendonca/devflow
```

### Local Project Uninstall

```bash
cd /path/to/your/project
npm uninstall @pjmendonca/devflow
```

### Clean Uninstall (Remove All Data)

```bash
# Uninstall package
npm uninstall -g @pjmendonca/devflow

# Remove configuration and data (optional)
rm -rf ~/tooling/.automation/costs/
rm -rf ~/tooling/.automation/memory/
```

## Getting Help

- **Documentation**: [Main README](../README.md)
- **Issues**: [GitHub Issues](https://github.com/Pedro-Jose-da-Rocha-Mendonca/Devflow/issues)
- **Validate Setup**: Run `devflow-validate` to check your installation

## Next Steps

After installation:

1. **Validate**: Run `devflow-validate` to check setup
2. **Initialize**: Run `devflow-init` in your project directory
3. **Explore**: Try `devflow-cost --help` to see available options
4. **Read Docs**: Check [README.md](../README.md) for workflow guides

---

**Quick Reference:**

```bash
# Install
npm install -g @pjmendonca/devflow

# Validate
devflow-validate

# Initialize project
devflow-init

# View costs
devflow-cost

# Run story
devflow-story 1-3

# Get help
devflow-story --help
```
