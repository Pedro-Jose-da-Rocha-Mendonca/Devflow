---
description: View cost dashboard and spending analytics
argument-hint: [--period day|week|month]
---

View Devflow cost dashboard: $ARGUMENTS

Execute: `npx @pjmendonca/devflow costs $ARGUMENTS`

This displays cost tracking and analytics:
- Total spend by model (Opus, Sonnet, Haiku)
- Cost breakdown by agent
- Cost breakdown by story/task
- Budget utilization tracking
- Cost trends over time

Options:
- `--period day` - Show today's costs
- `--period week` - Show this week's costs
- `--period month` - Show this month's costs
- `--export csv` - Export to CSV file

Examples:
- `/costs` - Show current cost dashboard
- `/costs --period week` - Show weekly breakdown
- `/costs --by-agent` - Group costs by agent

