# Override Templates

Pre-configured override templates for common project types and agent personas. Copy the appropriate template to customize your agent behavior.

## Project Type Templates

| Template | Best For |
|----------|----------|
| `web-frontend.override.yaml` | React, Vue, Angular, Svelte web apps |
| `backend-api.override.yaml` | Node.js, Python, Go, Rust, Java APIs |
| `data-science.override.yaml` | ML, data analysis, Jupyter notebooks |
| `devops.override.yaml` | Infrastructure, CI/CD, Kubernetes |
| `mobile-native.override.yaml` | iOS (Swift), Android (Kotlin/Java) |

## Agent Persona Templates

Each agent has pre-built persona templates in their respective directories:

| Agent | Templates | Description |
|-------|-----------|-------------|
| [`dev/`](dev/) | 5 templates | Developer personas (senior, junior, security, performance, prototyper) |
| [`reviewer/`](reviewer/) | 3 templates | Code reviewer styles (thorough, mentoring, quick) |
| [`sm/`](sm/) | 3 templates | Scrum master approaches (agile coach, tech lead, startup) |
| [`architect/`](architect/) | 3 templates | Architecture focus (enterprise, cloud-native, minimalist) |
| [`ba/`](ba/) | 3 templates | Business analyst styles (requirements, agile, domain) |
| [`pm/`](pm/) | 3 templates | Project management approaches (traditional, agile, hybrid) |
| [`writer/`](writer/) | 3 templates | Documentation focus (API, user guide, docs-as-code) |
| [`maintainer/`](maintainer/) | 3 templates | Maintenance styles (OSS, legacy, DevOps) |

### Using the Personalization Wizard

The easiest way to apply templates is with the wizard:

```bash
python3 tooling/scripts/personalize_agent.py [agent]

# Or use the Claude Code slash command
/personalize dev
```

## How to Use

1. **Copy the template** to your overrides directory:
   ```bash
   cp templates/web-frontend.override.yaml ../dev.override.yaml
   ```

2. **Customize** the copied file:
   - Uncomment sections relevant to your framework
   - Add project-specific memories
   - Adjust rules to match your conventions

3. **Test** by running a story or invoking an agent

## Template Structure

Each template includes:

- **persona**: Customizes the agent's role and communication style
- **additional_rules**: Extra rules appended to the base agent
- **memories**: Facts the agent should always remember
- **critical_actions**: Actions to perform before completing tasks
- **Framework sections**: Commented sections for popular frameworks

## Creating Custom Templates

Use these templates as starting points. Key sections to customize:

```yaml
# Your persona
persona:
  role: "Your Role Title"
  identity: "Description of approach"
  principles:
    - "Your guiding principles"

# Project-specific rules
additional_rules:
  - "Your coding standards"

# What the agent should always know
memories:
  - "Project-specific facts"

# Verification steps
critical_actions:
  - "Pre-completion checks"
```

## Contributing New Templates

We welcome new templates for:
- Game development (Unity, Unreal)
- Embedded systems
- Desktop applications (Electron, Tauri)
- Blockchain/Web3
- Specific frameworks (Django, Rails, Spring Boot)

See [CONTRIBUTING.md](../../../../CONTRIBUTING.md) for guidelines.
