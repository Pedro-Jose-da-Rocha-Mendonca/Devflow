#!/bin/zsh
################################################################################
# RUN-STORY - Simple Automated Story Implementation
#
# This script invokes Claude Code to implement a story automatically.
#
# Usage:
#   ./run-story.sh <story-key>           # Full pipeline (context + dev + review)
#   ./run-story.sh <story-key> --develop # Development only
#   ./run-story.sh <story-key> --review  # Review only
#
# Examples:
#   ./run-story.sh 3-5                   # Run full automation for story 3-5
#   ./run-story.sh 3-5 --develop         # Just run development phase
#
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SPRINT_STATUS="$PROJECT_ROOT/docs/sprint-status.yaml"

# Load configuration
source "$PROJECT_ROOT/.automation/config.sh"

# Load CLI library
source "$SCRIPT_DIR/lib/claude-cli.sh"

# Expand abbreviated story key (e.g., "3-5" -> "3-5-build-goal-detail-screen-with-edit-delete")
expand_story_key() {
    local input_key="$1"

    # If already a full key (has more than two dashes), return as-is
    if [[ "$input_key" =~ ^[0-9]+-[0-9]+-[a-z] ]]; then
        echo "$input_key"
        return
    fi

    # If abbreviated (e.g., "3-5"), look up full key
    if [[ "$input_key" =~ ^[0-9]+-[0-9]+$ ]]; then
        local full_key=$(grep -E "^  $input_key-[a-z]" "$SPRINT_STATUS" 2>/dev/null | head -1 | awk '{print $1}' | sed 's/://' || echo "")

        if [[ -n "$full_key" ]]; then
            echo "$full_key"
            return
        fi
    fi

    echo "$input_key"
}

print_header() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  AUTOMATED STORY RUNNER${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_usage() {
    echo "Usage: ./run-story.sh <story-key> [options]"
    echo ""
    echo "Options:"
    echo "  --develop       Run development phase only"
    echo "  --review        Run review phase only"
    echo "  --context       Create story context only"
    echo "  --no-commit     Disable auto-commit after development"
    echo "  --with-pr       Enable auto-PR creation (requires gh CLI)"
    echo "  --model <name>  Use specific Claude model (sonnet|opus|haiku)"
    echo "  (default)       Run full pipeline with auto-commit"
    echo ""
    echo "Environment Variables:"
    echo "  AUTO_COMMIT=true|false    Enable/disable auto-commit (default: true)"
    echo "  AUTO_PR=true|false        Enable/disable auto-PR (default: false)"
    echo "  CLAUDE_MODEL=<name>       Set Claude model (default: sonnet)"
    echo ""
    echo "Examples:"
    echo "  ./run-story.sh 3-5                    # Full pipeline with auto-commit"
    echo "  ./run-story.sh 3-5 --develop          # Development only with auto-commit"
    echo "  ./run-story.sh 3-5 --no-commit        # Disable auto-commit"
    echo "  ./run-story.sh 3-5 --with-pr          # Enable auto-PR creation"
    echo "  ./run-story.sh 3-5 --model opus       # Use Claude Opus"
    echo "  AUTO_COMMIT=false ./run-story.sh 3-5  # Disable via env var"
    echo ""
}

main() {
    if [[ $# -eq 0 ]]; then
        print_usage
        exit 1
    fi

    # Expand abbreviated story key
    local story_key=$(expand_story_key "$1")
    shift

    # Parse options
    local mode="full"
    export AUTO_COMMIT="${AUTO_COMMIT:-true}"
    export AUTO_PR="${AUTO_PR:-false}"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            "--develop"|"--dev")
                mode="develop"
                ;;
            "--review")
                mode="review"
                ;;
            "--context")
                mode="context"
                ;;
            "--no-commit")
                AUTO_COMMIT="false"
                ;;
            "--with-pr")
                AUTO_PR="true"
                ;;
            "--model")
                shift
                if [[ $# -eq 0 ]]; then
                    echo "Error: --model requires an argument (sonnet|opus|haiku)"
                    print_usage
                    exit 1
                fi
                export CLAUDE_MODEL="$1"
                ;;
            *)
                echo "Unknown option: $1"
                print_usage
                exit 1
                ;;
        esac
        shift
    done

    print_header
    echo -e "${BLUE}Story:${NC} $story_key"
    echo -e "${BLUE}Mode:${NC} $mode"
    echo -e "${BLUE}Model:${NC} $CLAUDE_MODEL"
    echo -e "${BLUE}Auto-commit:${NC} $AUTO_COMMIT"
    echo -e "${BLUE}Auto-PR:${NC} $AUTO_PR"
    echo ""

    # Check for existing checkpoint and offer to resume
    if type has_checkpoint &>/dev/null && has_checkpoint "$story_key"; then
        echo -e "${CYAN}📂 Found existing checkpoint for story: $story_key${NC}"
        echo -e "${YELLOW}Would you like to resume from the checkpoint? (y/n)${NC}"
        read -r RESUME_CHOICE

        if [[ "$RESUME_CHOICE" =~ ^[Yy]$ ]]; then
            if type resume_from_checkpoint &>/dev/null; then
                resume_from_checkpoint "$story_key"
                return 0
            fi
        else
            echo -e "${GREEN}Starting fresh implementation...${NC}"
            echo ""
        fi
    fi

    # Create pre-start checkpoint
    if type create_story_checkpoint &>/dev/null; then
        echo -e "${CYAN}💾 Creating pre-start checkpoint...${NC}"
        create_story_checkpoint "$story_key" "pre-start" 2>&1 | grep -v "Could not export"
        echo ""
    fi

    case "$mode" in
        "develop")
            echo -e "${YELLOW}▶ Running development phase...${NC}"
            echo ""
            invoke_dev_story "$story_key"
            local exit_code=$?

            # Update status to 'review' if successful
            if [[ $exit_code -eq 0 ]]; then
                update_story_status "$story_key" "review"
            fi

            # Auto-commit after dev if enabled
            if [[ $exit_code -eq 0 && "$AUTO_COMMIT" == "true" ]]; then
                auto_commit_changes "$story_key"
            fi

            # Auto-PR if enabled
            if [[ $exit_code -eq 0 && "$AUTO_PR" == "true" ]]; then
                auto_create_pr "$story_key"
            fi
            ;;
        "review")
            echo -e "${YELLOW}▶ Running review phase...${NC}"
            echo ""
            invoke_sm_code_review "$story_key"
            exit_code=$?
            ;;
        "context")
            echo -e "${YELLOW}▶ Creating story context...${NC}"
            echo ""
            invoke_sm_story_context "$story_key"
            exit_code=$?
            ;;
        *)
            echo -e "${YELLOW}▶ Running full pipeline...${NC}"
            echo ""
            run_full_pipeline "$story_key"
            exit_code=$?
            ;;
    esac

    # Create completion checkpoint if successful
    if [[ $exit_code -eq 0 && "$mode" != "context" ]]; then
        if type create_story_checkpoint &>/dev/null; then
            echo -e "${CYAN}💾 Creating completion checkpoint...${NC}"
            create_story_checkpoint "$story_key" "complete" 2>&1 | grep -v "Could not export"
            echo ""
        fi
    fi

    # Cleanup old checkpoints (keep last 10)
    if type cleanup_old_checkpoints &>/dev/null; then
        cleanup_old_checkpoints 10 2>&1 | grep -E "^(🧹|✅|Deleted)"
        echo ""
    fi

    echo ""
    if [[ $exit_code -eq 0 ]]; then
        echo -e "${GREEN}✅ Complete!${NC}"
    else
        echo -e "${RED}❌ Failed with exit code: $exit_code${NC}"
    fi

    echo ""
    echo -e "${BLUE}Log files:${NC} $PROJECT_ROOT/.automation/logs/"
    echo -e "${BLUE}Checkpoints:${NC} $PROJECT_ROOT/.automation/checkpoints/"
    echo ""

    return $exit_code
}

main "$@"
