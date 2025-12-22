#!/usr/bin/env bash
################################################################################
# INIT-PROJECT-WORKFLOW - Claude Code Workflow Initialization
#
# Sets up automated development workflow for any project using Claude Code CLI
#
# Usage:
#   ./init-project-workflow.sh
#
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[1;35m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

################################################################################
# Helper Functions
################################################################################

print_banner() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║         CLAUDE CODE WORKFLOW INITIALIZATION                   ║${NC}"
    echo -e "${CYAN}╠═══════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║  Automated Development Workflow Setup                         ║${NC}"
    echo -e "${CYAN}║  Version 1.7.0                                                ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    local step_num="$1"
    local step_title="$2"
    echo ""
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}  STEP $step_num: $step_title${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

prompt_input() {
    local prompt="$1"
    local default="$2"
    local result

    if [[ -n "$default" ]]; then
        echo -e "${YELLOW}$prompt${NC} ${BLUE}(default: $default)${NC}"
    else
        echo -e "${YELLOW}$prompt${NC}"
    fi

    read -r result
    echo "${result:-$default}"
}

prompt_yes_no() {
    local prompt="$1"
    local default="${2:-y}"

    echo -e "${YELLOW}$prompt (y/n)${NC} ${BLUE}[default: $default]${NC}"
    read -r response

    response="${response:-$default}"
    [[ "$response" =~ ^[Yy]$ ]]
}

################################################################################
# Setup Steps
################################################################################

detect_project_type() {
    echo -e "${BLUE}> Detecting project type...${NC}"

    local project_type="generic"

    if [[ -f "package.json" ]]; then
        project_type="node"
    elif [[ -f "pubspec.yaml" ]]; then
        project_type="flutter"
    elif [[ -f "Cargo.toml" ]]; then
        project_type="rust"
    elif [[ -f "go.mod" ]]; then
        project_type="go"
    elif [[ -f "requirements.txt" ]] || [[ -f "pyproject.toml" ]]; then
        project_type="python"
    elif [[ -f "Gemfile" ]]; then
        project_type="ruby"
    elif [[ -f "pom.xml" ]] || [[ -f "build.gradle" ]] || [[ -f "build.gradle.kts" ]]; then
        # Check if it's Android or pure Java/Kotlin
        if [[ -d "app/src/main/java" ]] || [[ -d "app/src/main/kotlin" ]]; then
            project_type="android"
        else
            project_type="java"
        fi
    elif [[ -f "Package.swift" ]] || [[ -d "*.xcodeproj" ]] || [[ -d "*.xcworkspace" ]]; then
        project_type="swift"
    elif [[ -f "settings.gradle.kts" ]] && [[ -f "build.gradle.kts" ]]; then
        project_type="kotlin"
    fi

    echo -e "${GREEN}  Detected: $project_type${NC}"
    echo "$project_type"
}

setup_directory_structure() {
    local project_root="$1"
    local workflow_mode="${2:-both}"  # greenfield, brownfield, or both

    echo -e "${BLUE}> Creating directory structure...${NC}"

    # Core directories (always created)
    mkdir -p "$project_root/tooling/.automation/agents"
    mkdir -p "$project_root/tooling/.automation/checkpoints"
    mkdir -p "$project_root/tooling/.automation/logs"
    mkdir -p "$project_root/tooling/.automation/costs"
    mkdir -p "$project_root/tooling/scripts/lib"
    mkdir -p "$project_root/tooling/docs"

    # Greenfield directories (for new feature development)
    if [[ "$workflow_mode" == "greenfield" || "$workflow_mode" == "both" ]]; then
        # Stories directory is the main docs directory
        echo -e "${BLUE}  Creating greenfield structure...${NC}"
    fi

    # Brownfield directories (for existing codebase maintenance)
    if [[ "$workflow_mode" == "brownfield" || "$workflow_mode" == "both" ]]; then
        mkdir -p "$project_root/tooling/docs/bugs"
        mkdir -p "$project_root/tooling/docs/refactors"
        mkdir -p "$project_root/tooling/docs/investigations"
        mkdir -p "$project_root/tooling/docs/migrations"
        mkdir -p "$project_root/tooling/docs/tech-debt"
        echo -e "${BLUE}  Creating brownfield structure...${NC}"
    fi

    echo -e "${GREEN}   Directories created${NC}"
}

copy_core_scripts() {
    local project_root="$1"
    local source_dir="$2"

    echo -e "${BLUE}> Copying core automation scripts...${NC}"

    # Core library scripts
    cp "$source_dir/lib/claude-cli.sh" "$project_root/tooling/scripts/lib/"
    cp "$source_dir/lib/checkpoint-integration.sh" "$project_root/tooling/scripts/lib/"

    # Main workflow scripts
    cp "$source_dir/run-story.sh" "$project_root/tooling/scripts/"
    cp "$source_dir/context_checkpoint.py" "$project_root/tooling/scripts/"
    cp "$source_dir/setup-checkpoint-service.sh" "$project_root/tooling/scripts/"
    cp "$source_dir/new-doc.sh" "$project_root/tooling/scripts/"

    # Make executable
    chmod +x "$project_root/tooling/scripts/"*.sh
    chmod +x "$project_root/tooling/scripts/"*.py
    chmod +x "$project_root/tooling/scripts/lib/"*.sh

    echo -e "${GREEN}   Scripts copied${NC}"
}

create_config_file() {
    local project_root="$1"
    local project_name="$2"
    local project_type="$3"
    local model_dev="$4"
    local model_planning="$5"
    local display_currency="${6:-USD}"

    echo -e "${BLUE}> Creating configuration file...${NC}"

    cat > "$project_root/tooling/.automation/config.sh" << EOF
#!/bin/zsh
################################################################################
# Automation Configuration
# Generated: $(date +%Y-%m-%d)
################################################################################

# Project settings
export PROJECT_NAME="$project_name"
export PROJECT_TYPE="$project_type"

# Claude Code CLI settings
export CLAUDE_CLI="\${CLAUDE_CLI:-claude}"
export CLAUDE_MODEL_DEV="$model_dev"
export CLAUDE_MODEL_PLANNING="$model_planning"

# Default model (can be overridden by individual tasks)
export CLAUDE_MODEL="\${CLAUDE_MODEL:-$model_planning}"

# Permission mode for automation
export PERMISSION_MODE="\${PERMISSION_MODE:-dangerouslySkipPermissions}"

# Auto-commit settings
export AUTO_COMMIT="\${AUTO_COMMIT:-true}"
export AUTO_PR="\${AUTO_PR:-false}"

# Budget limits (USD)
export MAX_BUDGET_CONTEXT=3.00
export MAX_BUDGET_DEV=15.00
export MAX_BUDGET_REVIEW=5.00

# Cost display settings
export COST_DISPLAY_CURRENCY="$display_currency"
export COST_WARNING_PERCENT=75
export COST_CRITICAL_PERCENT=90
export COST_AUTO_STOP="true"

# Paths
export AUTOMATION_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
export PROJECT_ROOT="\$(cd "\$AUTOMATION_DIR/../.." && pwd)"
export SCRIPTS_DIR="\$PROJECT_ROOT/tooling/scripts"
export DOCS_DIR="\$PROJECT_ROOT/tooling/docs"

# Tool configurations
export CHECKPOINT_THRESHOLDS="75,85,95"  # Warning, Critical, Emergency
EOF

    chmod +x "$project_root/tooling/.automation/config.sh"

    echo -e "${GREEN}   Configuration created${NC}"
}

create_agent_personas() {
    local project_root="$1"

    echo -e "${BLUE}> Creating agent persona definitions...${NC}"

    # SM (Scrum Master) Agent
    cat > "$project_root/tooling/.automation/agents/sm.md" << 'EOF'
# Scrum Master Agent

You are an experienced Scrum Master overseeing development workflow.

## Responsibilities
- Story context creation and planning
- Code review and quality assurance
- Story drafting and specification
- Sprint status management

## Approach
- Be thorough but efficient
- Focus on quality and completeness
- Follow Agile best practices
- Ensure acceptance criteria are met

## Communication Style
- Clear and professional
- Action-oriented
- Provide constructive feedback
EOF

    # DEV (Developer) Agent
    cat > "$project_root/tooling/.automation/agents/dev.md" << 'EOF'
# Developer Agent

You are a senior software developer implementing features.

## Responsibilities
- Implement stories according to specifications
- Write clean, maintainable code
- Create comprehensive tests
- Follow project patterns and conventions

## Approach
- Code first, explain later
- Prioritize working solutions
- Write self-documenting code
- Ensure tests pass before completion

## Communication Style
- Concise and technical
- Focus on implementation details
- Proactive problem-solving
EOF

    # BA (Business Analyst) Agent
    cat > "$project_root/tooling/.automation/agents/ba.md" << 'EOF'
# Business Analyst Agent

You are a Business Analyst specializing in requirements gathering.

## Responsibilities
- Analyze and document requirements
- Create user stories with INVEST criteria
- Define acceptance criteria
- Identify edge cases and business rules

## Approach
- User-centric thinking
- Detailed documentation
- Clear acceptance criteria
- Consider all scenarios

## Communication Style
- Clear and structured
- Business-focused
- Comprehensive but concise
EOF

    # ARCHITECT Agent
    cat > "$project_root/tooling/.automation/agents/architect.md" << 'EOF'
# Architect Agent

You are a Software Architect designing technical solutions.

## Responsibilities
- Create technical specifications
- Design system architecture
- Define data models and APIs
- Identify technical risks

## Approach
- Think holistically
- Follow architectural patterns
- Consider scalability and maintainability
- Balance pragmatism with quality

## Communication Style
- Technical and precise
- Diagram-driven when helpful
- Consider trade-offs
EOF

    # MAINTAINER Agent (for brownfield work)
    cat > "$project_root/tooling/.automation/agents/maintainer.md" << 'EOF'
# Maintainer Agent

You are a senior software maintainer specializing in existing codebase management.

## Primary Focus
Brownfield development - working with existing, production code.

## Responsibilities
- Bug investigation and root cause analysis
- Minimal, targeted bug fixes
- Code refactoring with safety nets
- Technical debt resolution
- Codebase investigation and documentation
- Migration planning and execution

## Core Principles

### Understand Before Changing
- ALWAYS explore the codebase before making changes
- Trace code paths to understand impact
- Read related tests to understand expected behavior

### Minimal Changes
- Make the smallest change that fixes the issue
- Avoid "while I'm here" improvements
- One concern per change

### Safety First
- Run existing tests before and after changes
- Add regression tests for bugs
- Ensure backwards compatibility

## Communication Style
- Precise and technical
- Focus on what changed and why
- Clear about risks and tradeoffs
EOF

    echo -e "${GREEN}   Agent personas created${NC}"
}

create_sprint_status() {
    local project_root="$1"
    local project_name="$2"

    echo -e "${BLUE}> Creating sprint status tracker...${NC}"

    cat > "$project_root/tooling/docs/sprint-status.yaml" << EOF
# Sprint Status - $project_name
# Updated: $(date +%Y-%m-%d)

sprint:
  number: 1
  start: $(date +%Y-%m-%d)
  end: $(date -v+14d +%Y-%m-%d 2>/dev/null || date -d "+14 days" +%Y-%m-%d 2>/dev/null)

# Story Status Values:
# - backlog: Not yet started
# - drafted: Story specification created
# - ready-for-dev: Context created, ready for implementation
# - in-progress: Currently being worked on
# - review: Implementation complete, awaiting review
# - done: Reviewed and approved

stories:
  # Add your stories here in format:
  # story-key: status
  # Example:
  # 1-1-setup-project: done
  # 1-2-implement-auth: in-progress
EOF

    echo -e "${GREEN}   Sprint status created${NC}"
}

create_documentation_standard() {
    local project_root="$1"
    local source_dir="$2"

    echo -e "${BLUE}> Creating documentation standard...${NC}"

    # Copy DOC-STANDARD if it exists, otherwise create basic one
    if [[ -f "$source_dir/../docs/DOC-STANDARD.md" ]]; then
        cp "$source_dir/../docs/DOC-STANDARD.md" "$project_root/tooling/docs/"
    else
        cat > "$project_root/tooling/docs/DOC-STANDARD.md" << 'EOF'
# Documentation Standard

**Version**: 1.0
**Last Updated**: $(date +%Y-%m-%d)

## File Naming

Format: `[TYPE]-[descriptive-name].md`

Types:
- GUIDE - User-facing guides
- SPEC - Technical specifications
- STATUS - Status reports
- REFERENCE - Quick reference sheets

## Required Sections

1. Title (H1)
2. Metadata block
3. Purpose
4. Main content
5. Related documents (if any)

## Example

```markdown
# Feature Name

**Type**: Guide
**Version**: 1.0
**Last Updated**: YYYY-MM-DD
**Status**: Active

## Purpose

Brief description of what this document covers.

## Content

...
```
EOF
    fi

    echo -e "${GREEN}   Documentation standard created${NC}"
}

setup_checkpoint_service() {
    local project_root="$1"

    echo -e "${BLUE}> Setting up checkpoint service...${NC}"

    if prompt_yes_no "Install checkpoint service as macOS LaunchAgent?"; then
        cd "$project_root/tooling/scripts"
        ./setup-checkpoint-service.sh
        echo -e "${GREEN}   Checkpoint service installed${NC}"
    else
        echo -e "${YELLOW}  ⊘ Skipped checkpoint service installation${NC}"
        echo -e "${BLUE}    You can install it later with: ./tooling/scripts/setup-checkpoint-service.sh${NC}"
    fi
}

create_readme() {
    local project_root="$1"
    local project_name="$2"

    echo -e "${BLUE}> Creating workflow README...${NC}"

    cat > "$project_root/tooling/README.md" << EOF
# $project_name - Development Workflow

Automated development workflow powered by Claude Code CLI.

## Quick Start

### Run a Story

\`\`\`bash
cd tooling/scripts
./run-story.sh <story-key>
\`\`\`

### Available Commands

\`\`\`bash
# Full pipeline (context + dev + review)
./run-story.sh 1-1

# Development only
./run-story.sh 1-1 --develop

# Review only
./run-story.sh 1-1 --review

# Context creation only
./run-story.sh 1-1 --context
\`\`\`

### Checkpoint Management

\`\`\`bash
# List checkpoints
./tooling/scripts/checkpoint --list

# Create manual checkpoint
./tooling/scripts/checkpoint --checkpoint

# Resume from checkpoint
./tooling/scripts/checkpoint --resume <checkpoint-id>
\`\`\`

### Create New Documentation

\`\`\`bash
./tooling/scripts/new-doc.sh --type guide --name "my-guide"
\`\`\`

## Directory Structure

\`\`\`
tooling/
├── .automation/
│   ├── agents/          # Agent persona definitions
│   ├── checkpoints/     # Context checkpoints
│   ├── logs/            # Execution logs
│   └── config.sh        # Configuration
├── scripts/
│   ├── lib/             # Script libraries
│   ├── run-story.sh     # Main automation runner
│   ├── checkpoint       # Checkpoint CLI (symlink)
│   └── new-doc.sh       # Documentation generator
└── docs/
    ├── DOC-STANDARD.md  # Documentation standard
    └── sprint-status.yaml # Sprint tracking
\`\`\`

## Configuration

Edit \`tooling/.automation/config.sh\` to customize:
- Claude Code models (Opus for dev, Sonnet for planning)
- Budget limits
- Auto-commit settings
- Permission modes

## Agent Personas

The workflow uses multiple agent personas:
- **SM (Scrum Master)**: Planning, context creation, code review
- **DEV (Developer)**: Story implementation
- **BA (Business Analyst)**: Requirements analysis
- **ARCHITECT**: Technical design

Each persona uses the appropriate Claude model for optimal cost/quality.

## Next Steps

1. Add your stories to \`tooling/docs/sprint-status.yaml\`
2. Create story specifications in \`tooling/docs/\`
3. Run your first story: \`./run-story.sh <story-key>\`

## Support

- Documentation: \`tooling/docs/\`
- Logs: \`tooling/.automation/logs/\`
- Checkpoints: \`tooling/.automation/checkpoints/\`
EOF

    echo -e "${GREEN}   README created${NC}"
}

################################################################################
# Main Setup Flow
################################################################################

main() {
    print_banner

    echo -e "${BLUE}This wizard will set up automated development workflow for your project.${NC}"
    echo -e "${BLUE}You'll be guided through the configuration process.${NC}"
    echo ""

    if ! prompt_yes_no "Continue with setup?"; then
        echo -e "${YELLOW}Setup cancelled.${NC}"
        exit 0
    fi

    # STEP 1: Project Information
    print_step "1" "Project Information"

    local project_root=$(prompt_input "Enter project root directory:" "$PWD")
    local project_name=$(prompt_input "Enter project name:" "$(basename "$project_root")")
    local project_type=$(detect_project_type)

    if ! prompt_yes_no "Is this correct? Type: $project_type"; then
        project_type=$(prompt_input "Enter project type manually:" "$project_type")
    fi

    # STEP 1.5: Workflow Mode Selection
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  WORKFLOW MODE${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}Select your primary workflow mode:${NC}"
    echo ""
    echo -e "  ${YELLOW}1. Greenfield${NC} - New project development"
    echo -e "     Best for: Starting fresh, new features, full sprint workflow"
    echo ""
    echo -e "  ${YELLOW}2. Brownfield${NC} - Existing codebase maintenance"
    echo -e "     Best for: Bug fixes, refactoring, tech debt, migrations"
    echo ""
    echo -e "  ${YELLOW}3. Both${NC} - Full workflow support (recommended)"
    echo -e "     Best for: Teams doing both new features and maintenance"
    echo ""

    local mode_choice=$(prompt_input "Enter choice (1-3):" "3")

    local workflow_mode="both"
    case "$mode_choice" in
        1) workflow_mode="greenfield" ;;
        2) workflow_mode="brownfield" ;;
        3) workflow_mode="both" ;;
        *) workflow_mode="both" ;;
    esac

    echo -e "${GREEN}  Selected: $workflow_mode${NC}"

    # STEP 2: Model Configuration
    print_step "2" "Claude Model Configuration"

    echo -e "${BLUE}For optimal cost/quality balance:${NC}"
    echo -e "${BLUE}  - Use Opus for code development and review (higher quality)${NC}"
    echo -e "${BLUE}  - Use Sonnet for planning and context creation (cost-effective)${NC}"
    echo ""

    local model_dev=$(prompt_input "Model for development/review:" "opus")
    local model_planning=$(prompt_input "Model for planning/context:" "sonnet")

    # Currency Selection
    echo ""
    echo -e "${BLUE}Select your preferred currency for cost display:${NC}"
    echo -e "  1. USD - US Dollar (\$)"
    echo -e "  2. EUR - Euro (€)"
    echo -e "  3. GBP - British Pound (£)"
    echo -e "  4. BRL - Brazilian Real (R\$)"
    echo -e "  5. CAD - Canadian Dollar (C\$)"
    echo -e "  6. AUD - Australian Dollar (A\$)"
    echo ""

    local currency_choice=$(prompt_input "Enter choice (1-6):" "1")

    local display_currency="USD"
    case "$currency_choice" in
        1) display_currency="USD" ;;
        2) display_currency="EUR" ;;
        3) display_currency="GBP" ;;
        4) display_currency="BRL" ;;
        5) display_currency="CAD" ;;
        6) display_currency="AUD" ;;
        *) display_currency="USD" ;;
    esac

    echo -e "${GREEN}  Selected: $display_currency${NC}"

    # STEP 3: Directory Structure
    print_step "3" "Directory Structure"

    setup_directory_structure "$project_root" "$workflow_mode"

    # STEP 4: Copy Scripts
    print_step "4" "Core Scripts"

    local source_dir="$SCRIPT_DIR"
    copy_core_scripts "$project_root" "$source_dir"

    # STEP 5: Configuration
    print_step "5" "Configuration Files"

    create_config_file "$project_root" "$project_name" "$project_type" "$model_dev" "$model_planning" "$display_currency"
    create_agent_personas "$project_root"
    create_sprint_status "$project_root" "$project_name"
    create_documentation_standard "$project_root" "$source_dir"

    # STEP 6: Checkpoint Service
    print_step "6" "Checkpoint Service (Optional)"

    echo -e "${BLUE}The checkpoint service monitors Claude sessions and auto-saves context.${NC}"
    echo -e "${BLUE}This prevents losing progress when context windows fill up.${NC}"
    echo ""

    setup_checkpoint_service "$project_root"

    # STEP 7: Documentation
    print_step "7" "Documentation"

    create_readme "$project_root" "$project_name"

    # STEP 8: Finalize
    print_step "8" "Setup Complete!"

    echo -e "${GREEN} Workflow initialization complete!${NC}"
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  NEXT STEPS${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}1. Review configuration:${NC}"
    echo -e "   ${BLUE}$project_root/tooling/.automation/config.sh${NC}"
    echo ""
    echo -e "${YELLOW}2. Add your first story:${NC}"
    echo -e "   ${BLUE}Edit: $project_root/tooling/docs/sprint-status.yaml${NC}"
    echo -e "   ${BLUE}Create: $project_root/tooling/docs/1-1-your-story.md${NC}"
    echo ""
    echo -e "${YELLOW}3. Run your first story:${NC}"
    echo -e "   ${BLUE}cd $project_root/tooling/scripts${NC}"
    echo -e "   ${BLUE}./run-story.sh 1-1${NC}"
    echo ""
    echo -e "${YELLOW}4. Read the workflow guide:${NC}"
    echo -e "   ${BLUE}$project_root/tooling/README.md${NC}"
    echo ""
    echo -e "${GREEN}Happy coding! ${NC}"
    echo ""
}

main "$@"
