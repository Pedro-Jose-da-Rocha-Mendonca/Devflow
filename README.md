# Claude Code Workflow Template

> Automated development workflow powered by Claude Code CLI - A complete agent-based development system with smart model usage, context preservation, and multi-persona automation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude-Code-5A67D8)](https://claude.com/claude-code)

## What is This?

A production-ready, portable workflow automation system that uses Claude Code CLI to implement user stories with minimal human intervention. Think "CI/CD for development" - but instead of deploying code, it writes code.

Find us at our [discord](https://discord.gg/mHdyQ7VN8R)

### Key Features

- **Multi-Persona Agent System** - 8 specialized AI agents (SM, DEV, BA, ARCHITECT, PM, WRITER, MAINTAINER, REVIEWER)
- **Smart Model Usage** - Opus for development, Sonnet for planning (40-60% cost savings)
- **Context Preservation** - Automatic checkpoints prevent work loss from context limits
- **Full Automation** - Context -> Development -> Testing -> Review -> Commit pipeline
- **Greenfield + Brownfield** - Supports both new features AND existing codebase maintenance
- **Agent Personalization** - Agent overrides and persistent agent memory
- **Claude Code Integration** - Native slash commands (`/story`, `/swarm`, `/pair`, `/route`, etc.)
- **Multi-Agent Collaboration** - Swarm mode, pair programming, and auto-routing
- **Knowledge Graph** - Queryable database of all architectural decisions and design choices
- **Shared Memory** - Cross-agent memory pool for context sharing and learnings
- **Agent Handoff System** - Structured context preservation between agent transitions
- **Multi-Currency Cost Tracking** - Customizable currency display with budget controls and alerts
- **Persistent Status Line** - Real-time context and cost percentage display in CLI
- **Validation Framework** - Three-tier automated validation with auto-fix capability
- **Project Agnostic** - Works with Flutter, Node.js, Python, Rust, Go, Ruby, etc.
- **Guided Setup** - Interactive wizard guides you through installation

## Quick Start

### Prerequisites

**macOS/Linux:**
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) - See [installation guide](https://docs.anthropic.com/en/docs/claude-code/getting-started)
- Python 3.9+
- Git
- Bash or Zsh shell

**Windows:**
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) - See [installation guide](https://docs.anthropic.com/en/docs/claude-code/getting-started)
- Python 3.9+ (from python.org or Microsoft Store)
- Git for Windows
- PowerShell 5.1+ (included with Windows 10/11)

### Installation

Choose the method that best fits your needs:

#### Option 1: Add to Existing Project (Recommended)

```bash
# Navigate to your project directory
cd your-project

# Install Devflow into your existing project
npx @pjmendonca/devflow@latest install

# This will:
# 1. Copy .claude/ and tooling/ directories into your project
# 2. Claude Code automatically detects the slash commands
# 3. Optionally run the setup wizard (use --skip-setup to skip)

# Start using immediately:
/story <key>
```

#### Option 2: Create Standalone Project

```bash
# Create a new Devflow directory
npx @pjmendonca/devflow@latest

# Or use npm create:
npm create @pjmendonca/devflow

# This will:
# 1. Create a "Devflow" folder in your current directory
# 2. Copy all essential files into it
# 3. Run the interactive setup wizard

# Then use it:
cd Devflow
/story <key>
```

#### Option 3: Global Installation

```bash
# Install globally for system-wide access
npm install -g @pjmendonca/devflow

# Then run from anywhere:
devflow install          # Add to existing project
devflow --help           # Show available commands
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

## Claude Slash Commands

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

## Knowledge Graph & Shared Memory

Devflow features a sophisticated memory system that enables agents to share context, track decisions, and maintain institutional knowledge across the entire development workflow.

### Knowledge Graph

The Knowledge Graph is a queryable database of all architectural decisions, design choices, and key learnings made during development.

**Features:**
- **Decision Tracking** - All major decisions are recorded with context, rationale, and timestamps
- **Semantic Queries** - Ask natural language questions about past decisions
- **Decision Supersession** - Track when decisions are updated or replaced
- **Agent Attribution** - Know which agent made each decision

```bash
# Query the knowledge graph
python tooling/scripts/run-collab.py 3-5 --query "What authentication approach was decided?"

# View all decisions for a story
python tooling/scripts/run-collab.py 3-5 --decisions

# Add a decision programmatically
python -c "
from tooling.scripts.lib.shared_memory import get_knowledge_graph
kg = get_knowledge_graph('3-5')
kg.add_decision('ARCHITECT', 'auth-approach', 'Use JWT with refresh tokens',
                context={'reason': 'Stateless, scalable'})
"
```

**Decision Structure:**
- `id` - Unique identifier
- `topic` - Decision category (e.g., "auth-approach", "database-choice")
- `decision` - The actual decision text
- `context` - Supporting rationale and metadata
- `status` - active, superseded, or revoked

### Shared Memory Pool

The Shared Memory system allows all agents to contribute and access shared context, learnings, and notes throughout the workflow.

**Features:**
- **Cross-Agent Sharing** - Any agent can add entries, all agents can read
- **Tagging System** - Organize entries with searchable tags
- **References** - Link related memory entries together
- **Persistent Storage** - Memory persists across sessions

```bash
# View shared memory for a story
python tooling/scripts/run-collab.py 3-5 --memory

# Search memory entries
python tooling/scripts/run-collab.py 3-5 --memory --search "database"

# Add to shared memory programmatically
python -c "
from tooling.scripts.lib.shared_memory import get_shared_memory
memory = get_shared_memory('3-5')
memory.add('DEV', 'Decided to use PostgreSQL for user data', tags=['database', 'decision'])
"
```

**Memory Entry Structure:**
- `agent` - Which agent contributed the entry
- `content` - The actual memory content
- `tags` - Searchable categorization tags
- `references` - Links to related entries

## Agent Handoff System

The Agent Handoff System ensures seamless transitions between agents with structured context preservation. When one agent finishes their work, a comprehensive handoff summary is automatically generated for the next agent.

**Features:**
- **Automatic Context Extraction** - Key decisions, files changed, and blockers are auto-detected
- **Git Diff Analysis** - Changed files are analyzed and summarized
- **Warning/Blocker Identification** - Critical issues are highlighted for the next agent
- **Structured Templates** - Each agent transition has specific focus areas

```bash
# View handoff summaries between agents
python tooling/scripts/run-collab.py 3-5 --handoffs

# Generate a manual handoff
python -c "
from tooling.scripts.lib.agent_handoff import create_handoff
handoff = create_handoff(
    story_key='3-5',
    from_agent='SM',
    to_agent='DEV',
    work_summary='Created story context with all acceptance criteria'
)
print(handoff)
"
```

**Handoff Contents:**
- **Summary** - What was accomplished
- **Key Decisions** - Important choices made
- **Blockers Resolved** - Issues that were addressed
- **Watch Out For** - Warnings and concerns
- **Files Modified** - List of changed files
- **Next Steps** - Recommended actions for the next agent

**Standard Handoff Transitions:**

| From | To | Focus Areas |
|------|-----|-------------|
| SM -> DEV | Acceptance criteria, technical context, patterns to follow |
| SM -> ARCHITECT | High-level requirements, system constraints, scale requirements |
| ARCHITECT -> DEV | Architecture decisions, design patterns, interface definitions |
| DEV -> REVIEWER | Implementation approach, key decisions, test coverage |
| REVIEWER -> DEV | Issues found, required changes, approval status |
| BA -> DEV | Refined requirements, acceptance criteria, edge cases |

## Multi-Agent Collaboration

Devflow supports advanced multi-agent collaboration modes for complex development tasks.

### Swarm Mode (Multi-Agent Debate)

Multiple agents work together, debating and iterating until consensus:

```bash
# Run swarm with default agents (ARCHITECT, DEV, REVIEWER)
npx @pjmendonca/devflow story 3-5 --swarm

# Custom agent selection
npx @pjmendonca/devflow story 3-5 --swarm --agents ARCHITECT,DEV,REVIEWER

# Control iterations
npx @pjmendonca/devflow story 3-5 --swarm --max-iter 5

# Set budget limits
npx @pjmendonca/devflow story 3-5 --swarm --budget 20.00
```

**Swarm Configuration Options:**
- `max_iterations` - Maximum debate rounds (default: 3)
- `consensus_type` - unanimous, majority, quorum, or reviewer_approval
- `parallel_execution` - Run independent agents simultaneously
- `auto_fix_enabled` - DEV automatically addresses REVIEWER issues
- `budget_limit_usd` - Maximum cost for the swarm session

**Consensus Types:**
| Type | Description |
|------|-------------|
| `unanimous` | All agents must agree |
| `majority` | >50% of agents agree |
| `quorum` | N of M agents agree |
| `reviewer_approval` | REVIEWER must approve (default) |

**How it works:**
1. All agents analyze the task
2. Agents provide feedback on each other's work
3. Issues are addressed iteratively
4. Continues until consensus or max iterations

### Pair Programming Mode

DEV and REVIEWER work together in real-time:

```bash
npx @pjmendonca/devflow story 3-5 --pair
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
npx @pjmendonca/devflow story "fix authentication bug" --auto-route

# Works with any task description
npx @pjmendonca/devflow story "add user profile feature" --auto-route
```

**How it works:**
- Analyzes task description for keywords
- Considers file types and complexity
- Routes to appropriate specialists (e.g., bugs -> MAINTAINER agent, new features -> DEV agent)

## Cost Tracking & Currency Configuration

Devflow includes a comprehensive cost tracking system with multi-currency support and budget controls.

### Currency Selection

During setup, the initialization wizard prompts you to select your preferred currency for cost display. Supported currencies include:

| Currency | Symbol | Name |
|----------|--------|------|
| USD | $ | US Dollar |
| EUR | € | Euro |
| GBP | £ | British Pound |
| BRL | R$ | Brazilian Real |
| CAD | C$ | Canadian Dollar |
| AUD | A$ | Australian Dollar |
| JPY | ¥ | Japanese Yen |
| CNY | ¥ | Chinese Yuan |
| INR | ₹ | Indian Rupee |
| MXN | $ | Mexican Peso |

**Setting currency in setup wizard:**
```bash
./init-project-workflow.sh
# or
.\init-project-workflow.ps1
```

**Setting currency manually:**
```bash
# In your config file or environment
export COST_DISPLAY_CURRENCY="EUR"

# Set custom exchange rates (optional)
export CURRENCY_RATE_EUR=0.92
export CURRENCY_RATE_GBP=0.79
export CURRENCY_RATE_BRL=6.10
```

### Budget Controls

Set spending limits for different phases of the workflow:

```bash
export MAX_BUDGET_CONTEXT=3.00   # Context creation: $3 max
export MAX_BUDGET_DEV=15.00      # Development: $15 max
export MAX_BUDGET_REVIEW=5.00    # Code review: $5 max
```

### Budget Alerts

The system provides automatic alerts at configurable thresholds:

```bash
export COST_WARNING_PERCENT=75   # Yellow warning at 75%
export COST_CRITICAL_PERCENT=90  # Red warning at 90%
export COST_AUTO_STOP="true"     # Auto-stop at 100%
```

### Cost Dashboard

View detailed cost information with the cost dashboard:

```bash
# Show current/latest session
python tooling/scripts/cost_dashboard.py

# Show last 10 sessions
python tooling/scripts/cost_dashboard.py --history 10

# Show costs for a specific story
python tooling/scripts/cost_dashboard.py --story 3-5

# Export to CSV
python tooling/scripts/cost_dashboard.py --export costs.csv

# Show aggregate summary
python tooling/scripts/cost_dashboard.py --summary
```

**Dashboard Features:**
- Real-time cost display during runs
- Multi-currency display (shows all selected currencies)
- Token usage breakdown (input/output)
- Cost by agent breakdown
- Budget utilization tracking
- Session history and analytics

### Cost Optimization Tips

- **Use Opus sparingly** - Reserve for development and critical reviews
- **Use Sonnet for planning** - Context creation, documentation, and summaries
- **Set budget limits** - Prevent runaway costs with phase-specific limits
- **Monitor the dashboard** - Track spending patterns across stories

### Status Line

Devflow provides a persistent status line in Claude Code that shows real-time metrics:

```
[Devflow] Claude Opus 4.5 | Context: 12.3% | Cost: $0.1234 (8.2%) | +45 -12 lines
```

**What it shows:**
- **Model** - Current Claude model in use
- **Context** - Percentage of context window used (with color coding)
- **Cost** - Cumulative cost with subscription usage percentage
- **Lines** - Lines added/removed in the session

**Retroactive Cost Tracking:**

The cost percentage is calculated retroactively across all sessions in your billing period:
- Reads all session files from `tooling/.automation/costs/sessions/`
- Sums tokens used within the billing period (default: 30 days)
- Shows percentage of your subscription token limit used
- Updates in real-time as you work

**Color coding for cost percentage:**
- **Green** - Under 75% of subscription limit
- **Yellow** - 75-89% of subscription limit (warning)
- **Red** - 90%+ of subscription limit (critical)

**Configuration:**

The status line reads currency settings from `tooling/.automation/costs/config.json`. To customize:

```bash
# Set display currency
export COST_DISPLAY_CURRENCY="EUR"

# Or edit config.json:
{
  "display_currency": "BRL",
  "currency_rates": {
    "USD": 1.0,
    "BRL": 6.10,
    "EUR": 0.92
  }
}
```

### Subscription Usage Tracking

Track your usage against API subscription limits:

```bash
# View subscription usage
python tooling/scripts/cost_dashboard.py --subscription

# Set your plan manually
python tooling/scripts/cost_dashboard.py --set-plan pro

# View usage projection
python tooling/scripts/cost_dashboard.py --subscription
```

**Auto-Detection:**

Devflow automatically detects your subscription plan based on the model you're using:
- **Opus** users -> Pro plan (5M tokens/month)
- **Sonnet** users -> Developer plan (1M tokens/month)
- **Haiku** users -> Free plan (100K tokens/month)

The detected plan is saved to `tooling/.automation/costs/config.json` for future sessions.

**Available plans:** free, developer, pro, scale, enterprise

**Manual configuration (overrides auto-detection):**
```bash
export SUBSCRIPTION_PLAN="pro"           # Use a preset plan
export SUBSCRIPTION_TOKEN_LIMIT=5000000  # Or set custom limit
```

### Model Efficiency Metrics

Analyze which models give you the best value:

```bash
python tooling/scripts/cost_dashboard.py --efficiency
```

Shows cost-per-output-token for each model, helping optimize model selection.

### Usage Projection & Forecasting

Predict when you'll reach your subscription limits:

```bash
# View usage projection in subscription view
python tooling/scripts/cost_dashboard.py --subscription
```

**What it shows:**
- Daily average token consumption
- Projected days until limit reached
- End-of-period usage forecast vs limit
- Color-coded status: on-track (green), warning (yellow), critical (red)

### Analytics Export System

Generate comprehensive analytics reports:

```bash
# Generate full analytics report (Markdown)
python tooling/scripts/cost_dashboard.py --schedule-export report.md

# Export to JSON format
python tooling/scripts/cost_dashboard.py --schedule-export report.json
```

**Report contents:**
- Daily usage trends (last 14 days with tokens, cost, sessions)
- Per-story cost rankings (top 10 by token consumption)
- Period comparison (current vs previous period with deltas)
- API rate statistics (calls/day, calls/hour, peak times)

### API Rate Tracking

Monitor your API call patterns:

```bash
python tooling/scripts/cost_dashboard.py --summary
```

**Metrics tracked:**
- Total API calls in period
- Average calls per day/hour
- Peak usage hour and day
- Hourly and daily distribution data

## Validation Framework

Devflow includes a three-tier validation system that ensures code quality throughout the development pipeline.

### Validation Tiers

| Tier | Name | When | Validates |
|------|------|------|-----------|
| 1 | Pre-flight | Before starting | Story exists, budget available, dependencies |
| 2 | Inter-phase | Between phases | Code compiles, lint passes, phase transitions |
| 3 | Post-completion | After finishing | Tests pass, types valid, version synced |

### Running Validation

```bash
# Validate a story
/validate 3-5

# Run specific tier
/validate 3-5 --tier pre-flight

# Run with auto-fix for lint issues
/validate 3-5 --auto-fix
```

### Validation Gates

**Pre-flight (Tier 1):**
- Story file exists
- Budget is available
- Required dependencies installed

**Inter-phase (Tier 2):**
- TypeScript/Python compilation
- Linting (with auto-fix option)
- Phase transition rules

**Post-completion (Tier 3):**
- Test suite passes
- Type checking passes
- Version sync validated

### Configuration

Customize validation in `tooling/.automation/validation-config.yaml`:

```yaml
gates:
  lint:
    enabled: true
    auto_fix: true
    timeout: 60
  test:
    enabled: true
    command: "npm test"
    timeout: 300
```

## Shell Completion

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

##  Security Considerations

### API Key Management

Devflow relies on the Claude Code CLI for API authentication. The CLI handles API keys securely:

- **API keys are managed by Claude Code CLI** - Devflow never directly handles or stores API keys
- **Keys are stored in the Claude CLI's secure configuration**, not in Devflow's project files
- **Never commit API keys** - The `.gitignore` should exclude any files containing sensitive data

**Best practices:**

1. **Use Claude CLI's built-in authentication**:
   ```bash
   claude login  # Authenticate via the CLI
   ```

2. **For CI/CD environments**, use environment variables:
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   ```

3. **Verify your `.gitignore` includes**:
   ```
   .env
   .env.local
   *.pem
   *.key
   tooling/.automation/config.sh  # Contains environment-specific settings
   ```

4. **Review logs before sharing** - Cost tracking logs in `tooling/.automation/logs/` may contain session metadata

### Data Privacy

- Session cost data is stored locally in `tooling/.automation/costs/`
- No data is sent to external servers by Devflow (only to Anthropic's API via Claude CLI)
- Context checkpoints may contain code snippets - review before sharing

## License

MIT License - see [LICENSE](LICENSE) for details.

Free to use in commercial and personal projects.

## Acknowledgments

- Built for [Claude Code CLI](https://claude.com/claude-code)
- Agent override system inspired by [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)
- Agent-based architecture influenced by AutoGPT, CrewAI


<!-- VERSION_START - Auto-updated by update_version.py -->
**Version**: 1.19.0
**Status**: Production Ready
**Last Updated**: 2026-01-03
<!-- VERSION_END -->
