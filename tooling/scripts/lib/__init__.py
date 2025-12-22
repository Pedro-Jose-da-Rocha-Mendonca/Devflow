"""
Devflow Library - Core modules for the Devflow automation system.

This package provides:
- cost_tracker: Token usage and cost tracking
- cost_display: Terminal-based cost monitoring display
- cost_config: Configuration management for costs
- currency_converter: Multi-currency support
- errors: Enhanced error handling
- agent_router: Dynamic agent selection
- agent_handoff: Structured agent transitions
- shared_memory: Cross-agent knowledge sharing
- swarm_orchestrator: Multi-agent collaboration
- pair_programming: DEV + REVIEWER collaboration

Usage:
    from lib.cost_tracker import CostTracker
    from lib.agent_router import AgentRouter
"""

__version__ = "1.8.0"

# Lazy imports to avoid circular dependencies
__all__ = [
    "cost_tracker",
    "cost_display",
    "cost_config",
    "currency_converter",
    "errors",
    "agent_router",
    "agent_handoff",
    "shared_memory",
    "swarm_orchestrator",
    "pair_programming",
]
