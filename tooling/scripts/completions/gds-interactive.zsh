#!/bin/zsh
################################################################################
# GDS Interactive Autocomplete
#
# Provides visual autocomplete triggered by '.' similar to Claude's '/' commands
#
# Usage:
#   source this file in your .zshrc
#   Type '.' to trigger the interactive menu
#   Type 'gds.' or 'gds .' for context-aware completion
#
################################################################################

# Project root detection
GDS_PROJECT_ROOT="${GDS_PROJECT_ROOT:-$(pwd)}"

# Colors
typeset -A GDS_COLORS
GDS_COLORS=(
    [header]='\033[1;36m'
    [selected]='\033[1;32m'
    [dimmed]='\033[0;90m'
    [reset]='\033[0m'
    [yellow]='\033[1;33m'
    [blue]='\033[0;34m'
)

################################################################################
# Menu Data
################################################################################

# Get story keys from sprint-status.yaml
_gds_get_stories() {
    local sprint_status="$GDS_PROJECT_ROOT/tooling/docs/sprint-status.yaml"
    [[ -f "$sprint_status" ]] || sprint_status="$GDS_PROJECT_ROOT/docs/sprint-status.yaml"

    if [[ -f "$sprint_status" ]]; then
        grep -E "^  [0-9]+-[0-9]+" "$sprint_status" 2>/dev/null | \
            sed 's/:.*//' | sed 's/^[[:space:]]*//' | \
            sed 's/^\([0-9]*-[0-9]*\).*/\1/' | sort -u
    fi
}

# Get agents
_gds_get_agents() {
    local agents_dir="$GDS_PROJECT_ROOT/tooling/.automation/agents"
    [[ -d "$agents_dir" ]] && ls "$agents_dir" 2>/dev/null | sed 's/\.md$//'
}

# Main commands with descriptions
typeset -A GDS_COMMANDS
GDS_COMMANDS=(
    # Story commands
    [story]="Run full story pipeline (context + dev + review)"
    [develop]="Run development phase only"
    [review]="Run standard code review"
    [adversarial]="Run adversarial review (critical, Opus)"
    [context]="Create story context only"

    # Brownfield
    [bugfix]="Fix a bug"
    [refactor]="Refactor code"
    [investigate]="Investigate codebase (read-only)"
    [quickfix]="Quick, minimal change"
    [migrate]="Run a migration"
    [tech-debt]="Resolve technical debt"

    # Agent commands
    [agent]="Invoke a specific agent"
    [agents]="List available agents"

    # Personalization
    [profile]="Edit user profile"
    [override]="Edit agent override"
    [memory]="Manage agent memory"

    # Utilities
    [status]="Show sprint status"
    [logs]="View automation logs"
    [help]="Show help"
)

# Command categories for display
typeset -a GDS_STORY_CMDS GDS_BROWNFIELD_CMDS GDS_AGENT_CMDS GDS_UTIL_CMDS
GDS_STORY_CMDS=(story develop review adversarial context)
GDS_BROWNFIELD_CMDS=(bugfix refactor investigate quickfix migrate tech-debt)
GDS_AGENT_CMDS=(agent agents profile override memory)
GDS_UTIL_CMDS=(status logs help)

################################################################################
# Interactive Menu Display
################################################################################

# Draw the interactive menu
_gds_draw_menu() {
    local -a items=("$@")
    local selected=${GDS_SELECTED:-1}
    local filter="${GDS_FILTER:-}"
    local context="${GDS_CONTEXT:-commands}"
    local max_display=12
    local start_idx=1

    # Filter items
    local -a filtered_items
    if [[ -n "$filter" ]]; then
        for item in "${items[@]}"; do
            if [[ "${item:l}" == *"${filter:l}"* ]]; then
                filtered_items+=("$item")
            fi
        done
    else
        filtered_items=("${items[@]}")
    fi

    # Adjust selected if out of bounds
    (( selected > ${#filtered_items} )) && selected=${#filtered_items}
    (( selected < 1 )) && selected=1
    GDS_SELECTED=$selected

    # Calculate scroll offset
    if (( selected > max_display )); then
        start_idx=$(( selected - max_display + 1 ))
    fi

    # Clear menu area
    printf '\033[2K'  # Clear line

    # Header
    printf "${GDS_COLORS[header]}╭─ GDS Commands "
    if [[ -n "$filter" ]]; then
        printf "${GDS_COLORS[yellow]}(filter: $filter)"
    fi
    printf "${GDS_COLORS[header]} ─────────────────────────────╮${GDS_COLORS[reset]}\n"

    # Items
    local idx=0
    local display_count=0
    for item in "${filtered_items[@]}"; do
        (( idx++ ))
        (( idx < start_idx )) && continue
        (( display_count >= max_display )) && break
        (( display_count++ ))

        local desc=""
        local prefix=""

        # Get description based on context
        case "$context" in
            commands)
                desc="${GDS_COMMANDS[$item]:-}"
                # Add category prefix
                if (( ${GDS_STORY_CMDS[(I)$item]} )); then
                    prefix="${GDS_COLORS[blue]}[story]${GDS_COLORS[reset]} "
                elif (( ${GDS_BROWNFIELD_CMDS[(I)$item]} )); then
                    prefix="${GDS_COLORS[yellow]}[maint]${GDS_COLORS[reset]} "
                elif (( ${GDS_AGENT_CMDS[(I)$item]} )); then
                    prefix="${GDS_COLORS[header]}[agent]${GDS_COLORS[reset]} "
                fi
                ;;
            stories)
                desc="Story $item"
                ;;
            agents)
                desc="Invoke $item agent"
                ;;
        esac

        if (( idx == selected )); then
            printf "${GDS_COLORS[selected]}│ ▶ %-12s${GDS_COLORS[reset]} $prefix${GDS_COLORS[dimmed]}$desc${GDS_COLORS[reset]}\n" "$item"
        else
            printf "${GDS_COLORS[dimmed]}│   %-12s${GDS_COLORS[reset]} $prefix${GDS_COLORS[dimmed]}$desc${GDS_COLORS[reset]}\n" "$item"
        fi
    done

    # Footer
    printf "${GDS_COLORS[header]}╰─ ↑/↓:navigate  enter:select  esc:cancel  type:filter ─╯${GDS_COLORS[reset]}\n"

    # Move cursor back up
    local total_lines=$(( display_count + 2 ))
    printf "\033[${total_lines}A"
}

# Handle key input
_gds_handle_key() {
    local key="$1"
    local -a items=("${@:2}")

    case "$key" in
        $'\e[A'|k)  # Up arrow or k
            (( GDS_SELECTED-- ))
            (( GDS_SELECTED < 1 )) && GDS_SELECTED=1
            ;;
        $'\e[B'|j)  # Down arrow or j
            (( GDS_SELECTED++ ))
            (( GDS_SELECTED > ${#items} )) && GDS_SELECTED=${#items}
            ;;
        $'\e')  # Escape
            return 1
            ;;
        '')  # Enter
            return 0
            ;;
        $'\177'|$'\b')  # Backspace
            GDS_FILTER="${GDS_FILTER%?}"
            GDS_SELECTED=1
            ;;
        *)  # Filter character
            if [[ "$key" =~ [a-zA-Z0-9_-] ]]; then
                GDS_FILTER+="$key"
                GDS_SELECTED=1
            fi
            ;;
    esac
    return 2  # Continue
}

################################################################################
# Main Interactive Function
################################################################################

_gds_interactive_complete() {
    local context="${1:-commands}"
    local -a items

    # Determine items based on context
    case "$context" in
        commands)
            items=(${(k)GDS_COMMANDS})
            ;;
        stories)
            items=("${(@f)$(_gds_get_stories)}")
            ;;
        agents)
            items=("${(@f)$(_gds_get_agents)}")
            ;;
    esac

    [[ ${#items} -eq 0 ]] && return 1

    # Initialize state
    GDS_SELECTED=1
    GDS_FILTER=""
    GDS_CONTEXT="$context"

    # Save cursor and switch to alternate screen buffer
    printf '\033[?1049h'  # Enter alternate screen
    printf '\033[H'       # Move to top

    # Main loop
    local result=""
    while true; do
        # Apply filter
        local -a filtered_items
        if [[ -n "$GDS_FILTER" ]]; then
            for item in "${items[@]}"; do
                if [[ "${item:l}" == *"${GDS_FILTER:l}"* ]]; then
                    filtered_items+=("$item")
                fi
            done
        else
            filtered_items=("${items[@]}")
        fi

        [[ ${#filtered_items} -eq 0 ]] && filtered_items=("(no matches)")

        _gds_draw_menu "${filtered_items[@]}"

        # Read key
        local key
        read -rsk1 key

        # Handle escape sequences
        if [[ "$key" == $'\e' ]]; then
            read -rsk2 -t 0.1 escape_seq
            key+="$escape_seq"
        fi

        _gds_handle_key "$key" "${filtered_items[@]}"
        local ret=$?

        if (( ret == 0 )); then
            # Selection made
            result="${filtered_items[$GDS_SELECTED]}"
            [[ "$result" == "(no matches)" ]] && result=""
            break
        elif (( ret == 1 )); then
            # Cancelled
            result=""
            break
        fi
    done

    # Restore screen
    printf '\033[?1049l'  # Exit alternate screen

    # Return result
    if [[ -n "$result" ]]; then
        echo "$result"
        return 0
    fi
    return 1
}

################################################################################
# ZLE Widget for '.' trigger
################################################################################

_gds_dot_complete() {
    local current_buffer="$BUFFER"
    local cursor_pos="$CURSOR"

    # Check if we should trigger interactive completion
    # Trigger on: empty line + '.', 'gds.', 'gds .', or after 'gds <cmd> .'

    local should_trigger=0
    local context="commands"
    local prefix=""

    if [[ -z "$current_buffer" || "$current_buffer" =~ ^[[:space:]]*$ ]]; then
        # Empty line - show all commands
        should_trigger=1
        prefix="gds "
        context="commands"
    elif [[ "$current_buffer" =~ ^[[:space:]]*gds[[:space:]]*$ ]]; then
        # "gds " - show commands
        should_trigger=1
        prefix=""
        context="commands"
    elif [[ "$current_buffer" =~ ^[[:space:]]*gds[[:space:]]+(story|develop|review|adversarial|context)[[:space:]]*$ ]]; then
        # "gds story " - show stories
        should_trigger=1
        prefix=""
        context="stories"
    elif [[ "$current_buffer" =~ ^[[:space:]]*gds[[:space:]]+(agent|override|memory)[[:space:]]*$ ]]; then
        # "gds agent " - show agents
        should_trigger=1
        prefix=""
        context="agents"
    elif [[ "$current_buffer" =~ ^[[:space:]]*(\.\/)?run-story\.sh[[:space:]]*$ ]]; then
        # "run-story.sh " - show stories
        should_trigger=1
        prefix=""
        context="stories"
    elif [[ "$current_buffer" =~ ^[[:space:]]*(\.\/)?run-story\.sh[[:space:]]+[0-9]+-[0-9]+[[:space:]]*$ ]]; then
        # "run-story.sh 3-5 " - show modes
        should_trigger=1
        prefix=""
        context="commands"  # Will show modes
    fi

    if (( should_trigger )); then
        # Get selection
        local selection
        selection=$(_gds_interactive_complete "$context")

        if [[ -n "$selection" ]]; then
            # Insert selection
            BUFFER="${current_buffer}${prefix}${selection} "
            CURSOR=${#BUFFER}
        fi

        zle redisplay
    else
        # Not a trigger context, insert literal '.'
        BUFFER="${current_buffer}."
        CURSOR=$(( cursor_pos + 1 ))
    fi
}

# Simpler widget that just triggers on Tab after 'gds'
_gds_tab_complete() {
    local current_buffer="$BUFFER"

    # Check if we're in a gds context
    if [[ "$current_buffer" =~ ^[[:space:]]*gds[[:space:]]*$ ]] || \
       [[ "$current_buffer" =~ ^[[:space:]]*gds[[:space:]]+(story|develop|review|adversarial|context)[[:space:]]*$ ]] || \
       [[ "$current_buffer" =~ ^[[:space:]]*gds[[:space:]]+(agent|override|memory)[[:space:]]*$ ]]; then

        local context="commands"

        if [[ "$current_buffer" =~ (story|develop|review|adversarial|context)[[:space:]]*$ ]]; then
            context="stories"
        elif [[ "$current_buffer" =~ (agent|override|memory)[[:space:]]*$ ]]; then
            context="agents"
        fi

        local selection
        selection=$(_gds_interactive_complete "$context")

        if [[ -n "$selection" ]]; then
            BUFFER="${current_buffer}${selection} "
            CURSOR=${#BUFFER}
        fi

        zle redisplay
    else
        # Fall back to normal completion
        zle expand-or-complete
    fi
}

################################################################################
# Quick Menu (fzf-style without fzf)
################################################################################

# Simpler inline menu for quick selection
gds.() {
    local selection
    selection=$(_gds_interactive_complete "commands")

    if [[ -n "$selection" ]]; then
        # Execute the command
        print -z "gds $selection "
    fi
}

# Story selection shortcut
gds.story() {
    local story
    story=$(_gds_interactive_complete "stories")

    if [[ -n "$story" ]]; then
        print -z "gds story $story "
    fi
}

# Agent selection shortcut
gds.agent() {
    local agent
    agent=$(_gds_interactive_complete "agents")

    if [[ -n "$agent" ]]; then
        print -z "gds agent $agent "
    fi
}

################################################################################
# FZF Integration (if available)
################################################################################

if command -v fzf &>/dev/null; then
    # Enhanced completion with fzf
    _gds_fzf_complete() {
        local context="${1:-commands}"
        local -a items

        case "$context" in
            commands)
                # Format: command:description
                for cmd in ${(k)GDS_COMMANDS}; do
                    items+=("$cmd:${GDS_COMMANDS[$cmd]}")
                done
                ;;
            stories)
                items=("${(@f)$(_gds_get_stories)}")
                ;;
            agents)
                items=("${(@f)$(_gds_get_agents)}")
                ;;
        esac

        local selection
        selection=$(printf '%s\n' "${items[@]}" | fzf \
            --height=40% \
            --layout=reverse \
            --border=rounded \
            --prompt="gds> " \
            --header="Select a command (type to filter)" \
            --preview-window=hidden \
            --delimiter=':' \
            --with-nth=1 \
            --bind='ctrl-/:toggle-preview' \
        )

        # Extract just the command name (before :)
        echo "${selection%%:*}"
    }

    # Override the interactive function to use fzf
    _gds_interactive_complete_fzf() {
        _gds_fzf_complete "$@"
    }
fi

################################################################################
# Setup
################################################################################

_gds_setup_interactive() {
    # Create the ZLE widgets
    zle -N _gds_dot_complete
    zle -N _gds_tab_complete

    # Bind '.' to trigger completion in specific contexts
    # This is optional - uncomment if you want '.' to trigger
    # bindkey '.' _gds_dot_complete

    # Alternative: Bind to a specific key combo like Ctrl+.
    bindkey '^[.' _gds_dot_complete  # Alt+.

    # Or use Tab for context-aware completion
    # bindkey '^I' _gds_tab_complete

    echo "GDS interactive completion loaded."
    echo "  Alt+.  : Open interactive menu"
    echo "  gds.   : Quick command menu"
    echo "  gds.story : Quick story selection"
}

# Auto-setup when sourced
_gds_setup_interactive
