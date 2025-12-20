#!/usr/bin/env python3
"""
Cost Tracker - Core cost tracking engine for Claude Code automation.

Tracks token usage, calculates costs, monitors budgets, and stores session data.

Usage:
    from lib.cost_tracker import CostTracker

    tracker = CostTracker(story_key="3-5", budget_limit_usd=15.00)
    tracker.log_usage(agent="DEV", model="opus", input_tokens=1000, output_tokens=500)
    print(tracker.get_session_summary())
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple, Optional
import sys

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

# Token pricing per 1M tokens (USD) - December 2024
PRICING = {
    # Claude 4 models
    "claude-opus-4-5-20251101": {"input": 15.00, "output": 75.00},
    "claude-sonnet-4-5-20251101": {"input": 3.00, "output": 15.00},
    "opus": {"input": 15.00, "output": 75.00},
    "sonnet": {"input": 3.00, "output": 15.00},
    "haiku": {"input": 0.80, "output": 4.00},
    # Aliases
    "claude-opus-4": {"input": 15.00, "output": 75.00},
    "claude-sonnet-4": {"input": 3.00, "output": 15.00},
    "claude-haiku-3.5": {"input": 0.80, "output": 4.00},
}

# Default budget thresholds
DEFAULT_THRESHOLDS = {
    "warning": 0.75,    # 75% - Yellow warning
    "critical": 0.90,   # 90% - Red warning
    "stop": 1.00,       # 100% - Auto-stop
}

# Storage paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
COSTS_DIR = PROJECT_ROOT / "tooling" / ".automation" / "costs"
SESSIONS_DIR = COSTS_DIR / "sessions"


@dataclass
class CostEntry:
    """Single cost entry for a Claude API call."""
    timestamp: str
    agent: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SessionCost:
    """Complete cost data for a session."""
    session_id: str
    story_key: str
    start_time: str
    end_time: Optional[str] = None
    budget_limit_usd: float = 15.00
    entries: List[CostEntry] = field(default_factory=list)

    @property
    def total_input_tokens(self) -> int:
        return sum(e.input_tokens for e in self.entries)

    @property
    def total_output_tokens(self) -> int:
        return sum(e.output_tokens for e in self.entries)

    @property
    def total_tokens(self) -> int:
        return self.total_input_tokens + self.total_output_tokens

    @property
    def total_cost_usd(self) -> float:
        return sum(e.cost_usd for e in self.entries)

    @property
    def budget_remaining(self) -> float:
        return max(0, self.budget_limit_usd - self.total_cost_usd)

    @property
    def budget_used_percent(self) -> float:
        if self.budget_limit_usd <= 0:
            return 0
        return min(100, (self.total_cost_usd / self.budget_limit_usd) * 100)

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "story_key": self.story_key,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "budget_limit_usd": self.budget_limit_usd,
            "entries": [e.to_dict() for e in self.entries],
            "totals": {
                "input_tokens": self.total_input_tokens,
                "output_tokens": self.total_output_tokens,
                "total_tokens": self.total_tokens,
                "cost_usd": round(self.total_cost_usd, 4),
                "budget_remaining": round(self.budget_remaining, 4),
                "budget_used_percent": round(self.budget_used_percent, 2),
            }
        }

    def get_cost_by_agent(self) -> Dict[str, float]:
        """Get cost breakdown by agent."""
        costs = {}
        for entry in self.entries:
            if entry.agent not in costs:
                costs[entry.agent] = 0
            costs[entry.agent] += entry.cost_usd
        return costs

    def get_cost_by_model(self) -> Dict[str, float]:
        """Get cost breakdown by model."""
        costs = {}
        for entry in self.entries:
            if entry.model not in costs:
                costs[entry.model] = 0
            costs[entry.model] += entry.cost_usd
        return costs

    def get_tokens_by_agent(self) -> Dict[str, Dict[str, int]]:
        """Get token breakdown by agent."""
        tokens = {}
        for entry in self.entries:
            if entry.agent not in tokens:
                tokens[entry.agent] = {"input": 0, "output": 0}
            tokens[entry.agent]["input"] += entry.input_tokens
            tokens[entry.agent]["output"] += entry.output_tokens
        return tokens


class CostTracker:
    """
    Main cost tracking class.

    Tracks token usage, calculates costs, monitors budgets.
    """

    def __init__(
        self,
        story_key: str = "unknown",
        budget_limit_usd: float = 15.00,
        thresholds: Optional[Dict[str, float]] = None,
        auto_save: bool = True
    ):
        self.story_key = story_key
        self.budget_limit_usd = budget_limit_usd
        self.thresholds = thresholds or DEFAULT_THRESHOLDS.copy()
        self.auto_save = auto_save

        # Generate session ID
        self.session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        # Initialize session
        self.session = SessionCost(
            session_id=self.session_id,
            story_key=story_key,
            start_time=datetime.now().isoformat(),
            budget_limit_usd=budget_limit_usd,
        )

        # Ensure directories exist
        COSTS_DIR.mkdir(parents=True, exist_ok=True)
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

        # Current agent/model tracking
        self.current_agent = None
        self.current_model = None

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a given usage."""
        model_lower = model.lower()

        # Find pricing
        pricing = None
        for key, price in PRICING.items():
            if key in model_lower or model_lower in key:
                pricing = price
                break

        if not pricing:
            # Default to sonnet pricing if unknown
            pricing = PRICING["sonnet"]

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return round(input_cost + output_cost, 6)

    def log_usage(
        self,
        agent: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> CostEntry:
        """
        Log a usage entry.

        Args:
            agent: Agent name (SM, DEV, BA, etc.)
            model: Model name (opus, sonnet, haiku)
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            The created CostEntry
        """
        cost = self.calculate_cost(model, input_tokens, output_tokens)

        entry = CostEntry(
            timestamp=datetime.now().isoformat(),
            agent=agent,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
        )

        self.session.entries.append(entry)
        self.current_agent = agent
        self.current_model = model

        if self.auto_save:
            self.save_session()

        return entry

    def set_current_agent(self, agent: str, model: str):
        """Set the current agent and model (for display purposes)."""
        self.current_agent = agent
        self.current_model = model

    def check_budget(self) -> Tuple[bool, str, str]:
        """
        Check budget status.

        Returns:
            Tuple of (is_ok, status_level, message)
            - is_ok: True if can continue, False if should stop
            - status_level: "ok", "warning", "critical", or "stop"
            - message: Human-readable status message
        """
        if self.budget_limit_usd <= 0:
            return (True, "ok", "No budget limit set")

        usage_pct = self.session.total_cost_usd / self.budget_limit_usd

        if usage_pct >= self.thresholds["stop"]:
            return (
                False,
                "stop",
                f"BUDGET EXCEEDED - ${self.session.total_cost_usd:.2f} / ${self.budget_limit_usd:.2f}"
            )
        elif usage_pct >= self.thresholds["critical"]:
            return (
                True,
                "critical",
                f"CRITICAL: {usage_pct*100:.0f}% of budget used (${self.session.total_cost_usd:.2f})"
            )
        elif usage_pct >= self.thresholds["warning"]:
            return (
                True,
                "warning",
                f"WARNING: {usage_pct*100:.0f}% of budget used (${self.session.total_cost_usd:.2f})"
            )

        return (True, "ok", f"Budget OK: {usage_pct*100:.0f}% used")

    def get_session_summary(self) -> Dict:
        """Get session summary as dictionary."""
        return self.session.to_dict()

    def save_session(self):
        """Save session to disk."""
        self.session.end_time = datetime.now().isoformat()

        filename = f"{datetime.now().strftime('%Y-%m-%d')}_{self.session_id}.json"
        filepath = SESSIONS_DIR / filename

        with open(filepath, 'w') as f:
            json.dump(self.session.to_dict(), f, indent=2)

    def end_session(self) -> Dict:
        """End session and save final state."""
        self.session.end_time = datetime.now().isoformat()
        self.save_session()
        return self.session.to_dict()

    @staticmethod
    def load_session(session_file: Path) -> Optional[SessionCost]:
        """Load a session from file."""
        try:
            with open(session_file, 'r') as f:
                data = json.load(f)

            entries = [CostEntry(**e) for e in data.get("entries", [])]

            return SessionCost(
                session_id=data["session_id"],
                story_key=data["story_key"],
                start_time=data["start_time"],
                end_time=data.get("end_time"),
                budget_limit_usd=data.get("budget_limit_usd", 15.00),
                entries=entries,
            )
        except Exception as e:
            print(f"Error loading session: {e}")
            return None

    @staticmethod
    def get_historical_sessions(days: int = 30) -> List[SessionCost]:
        """Get historical sessions from the last N days."""
        sessions = []

        if not SESSIONS_DIR.exists():
            return sessions

        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)

        for file in sorted(SESSIONS_DIR.glob("*.json"), reverse=True):
            if file.stat().st_mtime >= cutoff:
                session = CostTracker.load_session(file)
                if session:
                    sessions.append(session)

        return sessions

    @staticmethod
    def get_aggregate_stats(days: int = 30) -> Dict:
        """Get aggregate statistics for the last N days."""
        sessions = CostTracker.get_historical_sessions(days)

        if not sessions:
            return {
                "total_sessions": 0,
                "total_cost_usd": 0,
                "total_tokens": 0,
                "by_agent": {},
                "by_model": {},
            }

        total_cost = sum(s.total_cost_usd for s in sessions)
        total_tokens = sum(s.total_tokens for s in sessions)

        # Aggregate by agent
        by_agent = {}
        for session in sessions:
            for agent, cost in session.get_cost_by_agent().items():
                if agent not in by_agent:
                    by_agent[agent] = {"cost": 0, "sessions": 0}
                by_agent[agent]["cost"] += cost
                by_agent[agent]["sessions"] += 1

        # Aggregate by model
        by_model = {}
        for session in sessions:
            for model, cost in session.get_cost_by_model().items():
                if model not in by_model:
                    by_model[model] = {"cost": 0}
                by_model[model]["cost"] += cost

        return {
            "total_sessions": len(sessions),
            "total_cost_usd": round(total_cost, 2),
            "total_tokens": total_tokens,
            "average_per_session": round(total_cost / len(sessions), 2) if sessions else 0,
            "by_agent": by_agent,
            "by_model": by_model,
        }


def parse_token_usage(output: str) -> Optional[Tuple[int, int]]:
    """
    Parse token usage from Claude CLI output.

    Looks for patterns like:
    - "Token usage: 45000/200000"
    - "Tokens: 45000 in / 12000 out"

    Returns:
        Tuple of (input_tokens, output_tokens) or None if not found
    """
    import re

    # Pattern 1: "Token usage: X/Y" (total/limit)
    match = re.search(r'Token usage:\s*(\d+)/(\d+)', output)
    if match:
        total = int(match.group(1))
        # Estimate 80% input, 20% output
        return (int(total * 0.8), int(total * 0.2))

    # Pattern 2: "X in / Y out"
    match = re.search(r'(\d+)\s*in\s*/\s*(\d+)\s*out', output, re.IGNORECASE)
    if match:
        return (int(match.group(1)), int(match.group(2)))

    # Pattern 3: Input: X, Output: Y
    input_match = re.search(r'[Ii]nput[:\s]+(\d+)', output)
    output_match = re.search(r'[Oo]utput[:\s]+(\d+)', output)
    if input_match and output_match:
        return (int(input_match.group(1)), int(output_match.group(1)))

    return None


# Module-level convenience functions
_current_tracker: Optional[CostTracker] = None


def get_tracker() -> Optional[CostTracker]:
    """Get the current global tracker."""
    return _current_tracker


def set_tracker(tracker: CostTracker):
    """Set the current global tracker."""
    global _current_tracker
    _current_tracker = tracker


def start_tracking(story_key: str, budget_limit_usd: float = 15.00) -> CostTracker:
    """Start a new tracking session."""
    global _current_tracker
    _current_tracker = CostTracker(story_key, budget_limit_usd)
    return _current_tracker


if __name__ == "__main__":
    # Demo/test
    tracker = CostTracker(story_key="test-story", budget_limit_usd=10.00)

    # Simulate some usage
    tracker.log_usage("SM", "sonnet", 15000, 3000)
    tracker.log_usage("DEV", "opus", 50000, 15000)
    tracker.log_usage("SM", "sonnet", 10000, 2000)

    # Print summary
    import pprint
    pprint.pprint(tracker.get_session_summary())

    # Check budget
    ok, level, msg = tracker.check_budget()
    print(f"\nBudget status: {level} - {msg}")
