#!/bin/zsh
################################################################################
# GDS Enhanced Autocomplete
#
# Extends native zsh completion with:
# - Short aliases (g, gs, ga, gr, gd, gc, go)
# - Enhanced completion menu styling
# - Quick functions (gds., gds.s, gds.a)
#
################################################################################

GDS_PROJECT_ROOT="${GDS_PROJECT_ROOT:-$(pwd)}"

################################################################################
# Data Sources
################################################################################

_gds_get_stories() {
    local sprint_status="$GDS_PROJECT_ROOT/tooling/docs/sprint-status.yaml"
    [[ -f "$sprint_status" ]] || sprint_status="$GDS_PROJECT_ROOT/docs/sprint-status.yaml"

    if [[ -f "$sprint_status" ]]; then
        grep -E "^  [0-9]+-[0-9]+" "$sprint_status" 2>/dev/null | \
            sed 's/:.*//' | sed 's/^[[:space:]]*//' | \
            sed 's/^\([0-9]*-[0-9]*\).*/\1/' | sort -u
    fi
}

_gds_get_agents() {
    local agents_dir="$GDS_PROJECT_ROOT/tooling/.automation/agents"
    [[ -d "$agents_dir" ]] && ls "$agents_dir" 2>/dev/null | sed 's/\.md$//'
}

################################################################################
# Completion Style Configuration
################################################################################

# Enable menu selection for completions
zstyle ':completion:*' menu select

# Group completions by type
zstyle ':completion:*' group-name ''
zstyle ':completion:*:descriptions' format '%F{cyan}── %d ──%f'

# Colorize completions
zstyle ':completion:*:*:gds:*:commands' list-colors '=(#b)(*)=34=33'
zstyle ':completion:*:*:gds:*:stories' list-colors '=(#b)(*)=32'
zstyle ':completion:*:*:gds:*:agents' list-colors '=(#b)(*)=35'

################################################################################
# Quick Functions
################################################################################

# Type 'gds.' to start a gds command with completion
gds.() {
    print -z "gds "
}

# Type 'gds.s' to start story selection
gds.s() {
    print -z "gds story "
}

# Type 'gds.a' to start agent selection
gds.a() {
    print -z "gds agent "
}

# Type 'gds.r' to start review
gds.r() {
    print -z "gds review "
}

# Type 'gds.d' to start develop
gds.d() {
    print -z "gds develop "
}

################################################################################
# Short Aliases
################################################################################

alias g='gds'
alias gs='gds story'
alias ga='gds agent'
alias gr='gds review'
alias gd='gds develop'
alias gc='gds context'
alias go='gds override'

################################################################################
# Setup
################################################################################

# Guard against double initialization
if [[ -z "$_GDS_COMPLETION_LOADED" ]]; then
    _gds_interactive_setup() {
        local completions_dir="${GDS_PROJECT_ROOT}/tooling/scripts/completions"
        local scripts_dir="${GDS_PROJECT_ROOT}/tooling/scripts"

        # Add scripts directory to PATH if not already there
        if [[ -d "$scripts_dir" ]] && [[ ! ":$PATH:" =~ ":${scripts_dir}:" ]]; then
            export PATH="$scripts_dir:$PATH"
        fi

        # Add completions directory to fpath if not already there
        if [[ -d "$completions_dir" ]] && [[ ! " ${fpath[*]} " =~ " ${completions_dir} " ]]; then
            fpath=("$completions_dir" $fpath)
        fi

        # Initialize completion system
        autoload -Uz compinit
        compinit -u 2>/dev/null

        # Explicitly load the _gds completion function
        autoload -Uz _gds 2>/dev/null

        # Register _gds as the completion for gds command
        compdef _gds gds 2>/dev/null

        # Bind aliases to use the same completion as gds
        compdef g=gds 2>/dev/null
        compdef gs=gds 2>/dev/null
        compdef ga=gds 2>/dev/null
        compdef gr=gds 2>/dev/null
        compdef gd=gds 2>/dev/null
        compdef gc=gds 2>/dev/null
        compdef go=gds 2>/dev/null

        echo "GDS autocomplete loaded"
        echo "  Aliases: g, gs, ga, gr, gd, gc, go"
        echo "  Use Tab for completions"
    }

    _gds_interactive_setup
    _GDS_COMPLETION_LOADED=1
fi
