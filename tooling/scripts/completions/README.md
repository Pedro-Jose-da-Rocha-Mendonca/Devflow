# GDS CLI Autocomplete

Zsh completions for GDS Automation CLI commands.

## Quick Setup

Run the setup command:

```bash
./tooling/scripts/gds setup
```

Then reload your shell:

```bash
source ~/.zshrc
autoload -Uz compinit && compinit
```

## Manual Setup

Add to your `~/.zshrc`:

```bash
# GDS Automation CLI
export GDS_PROJECT_ROOT="/path/to/your/project"
fpath=(/path/to/tooling/scripts/completions $fpath)
alias gds="/path/to/tooling/scripts/gds"
alias run-story="/path/to/tooling/scripts/run-story.sh"

autoload -Uz compinit && compinit
```

## What Gets Completed

### Commands

```bash
gds <TAB>
# Shows: story, develop, review, adversarial, bugfix, refactor, ...
```

### Story Keys

```bash
gds story <TAB>
# Shows: 3-1, 3-2, 3-3, ... (from sprint-status.yaml)
```

### Modes

```bash
./run-story.sh 3-5 <TAB>
# Shows: --develop, --review, --adversarial, --bugfix, ...
```

### Models

```bash
gds story 3-5 --model <TAB>
# Shows: sonnet, opus, haiku
```

### Agents

```bash
gds agent <TAB>
# Shows: dev, sm, pm, architect, reviewer, ...
```

### Overrides

```bash
gds override <TAB>
# Shows: dev, sm, reviewer, ... (from overrides directory)
```

## Completion Files

| File | Description |
|------|-------------|
| `_run-story` | Completions for `run-story.sh` |
| `_gds` | Completions for `gds` wrapper |

## Troubleshooting

### Completions not working

1. Ensure completions directory is in fpath:
   ```bash
   echo $fpath | tr ' ' '\n' | grep completions
   ```

2. Rebuild completion cache:
   ```bash
   rm -f ~/.zcompdump*
   autoload -Uz compinit && compinit
   ```

3. Check completion is loaded:
   ```bash
   which _gds
   ```

### Story keys not showing

Ensure `sprint-status.yaml` exists and has proper format:

```yaml
stories:
  3-1-story-name: done
  3-2-another-story: in-progress
```

The completion extracts abbreviated keys (e.g., `3-1`, `3-2`) from this file.
