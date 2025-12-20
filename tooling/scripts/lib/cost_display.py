#!/usr/bin/env python3
"""
Cost Display - Real-time terminal display for cost monitoring.

Provides a rich, updating display of cost information during agent runs.

Usage:
    from lib.cost_display import CostDisplay
    from lib.cost_tracker import CostTracker

    tracker = CostTracker(story_key="3-5", budget_limit_usd=15.00)
    display = CostDisplay(tracker)
    display.refresh()  # Update display
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pathlib import Path

# Add parent for imports
sys.path.insert(0, str(Path(__file__).parent))

from cost_tracker import CostTracker, SessionCost
from currency_converter import CurrencyConverter, get_converter


class Colors:
    """ANSI color codes for terminal output."""
    # Reset
    RESET = '\033[0m'

    # Regular colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bold colors
    BOLD = '\033[1m'
    BOLD_RED = '\033[1;31m'
    BOLD_GREEN = '\033[1;32m'
    BOLD_YELLOW = '\033[1;33m'
    BOLD_BLUE = '\033[1;34m'
    BOLD_CYAN = '\033[1;36m'
    BOLD_WHITE = '\033[1;37m'

    # Background
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'

    # Dim
    DIM = '\033[2m'

    @staticmethod
    def strip(text: str) -> str:
        """Remove ANSI codes from text."""
        import re
        return re.sub(r'\033\[[0-9;]*m', '', text)


class CostDisplay:
    """
    Real-time cost display for terminal.

    Shows live updating cost information, token usage, and budget status.
    """

    # Box drawing characters
    BOX_TOP_LEFT = '╔'
    BOX_TOP_RIGHT = '╗'
    BOX_BOTTOM_LEFT = '╚'
    BOX_BOTTOM_RIGHT = '╝'
    BOX_HORIZONTAL = '═'
    BOX_VERTICAL = '║'
    BOX_T_LEFT = '╠'
    BOX_T_RIGHT = '╣'
    BOX_LINE = '─'

    def __init__(
        self,
        tracker: CostTracker,
        converter: Optional[CurrencyConverter] = None,
        width: int = 70,
        compact: bool = False
    ):
        """
        Initialize display.

        Args:
            tracker: CostTracker instance to display
            converter: CurrencyConverter for multi-currency display
            width: Display width in characters
            compact: Use compact display mode
        """
        self.tracker = tracker
        self.converter = converter or get_converter()
        self.width = width
        self.compact = compact
        self.start_time = datetime.now()
        self.last_refresh = None

    def _box_line(self, left: str, right: str, fill: str = BOX_HORIZONTAL) -> str:
        """Create a box line."""
        return f"{left}{fill * (self.width - 2)}{right}"

    def _content_line(self, content: str, align: str = "left") -> str:
        """Create a content line within the box."""
        # Remove color codes for length calculation
        clean_content = Colors.strip(content)
        padding = self.width - 4 - len(clean_content)

        if align == "center":
            left_pad = padding // 2
            right_pad = padding - left_pad
            return f"{self.BOX_VERTICAL} {' ' * left_pad}{content}{' ' * right_pad} {self.BOX_VERTICAL}"
        elif align == "right":
            return f"{self.BOX_VERTICAL} {' ' * padding}{content} {self.BOX_VERTICAL}"
        else:  # left
            return f"{self.BOX_VERTICAL} {content}{' ' * padding} {self.BOX_VERTICAL}"

    def _empty_line(self) -> str:
        """Create an empty content line."""
        return self._content_line("")

    def _section_header(self, title: str) -> str:
        """Create a section header."""
        line = f"{self.BOX_LINE * 3} {title} "
        remaining = self.width - 6 - len(title)
        return self._content_line(f"{Colors.BOLD}{line}{self.BOX_LINE * remaining}{Colors.RESET}")

    def _progress_bar(self, percent: float, width: int = 40) -> str:
        """Create a progress bar."""
        filled = int((percent / 100) * width)
        empty = width - filled

        # Color based on percentage
        if percent >= 90:
            color = Colors.RED
        elif percent >= 75:
            color = Colors.YELLOW
        else:
            color = Colors.GREEN

        bar = f"{color}{'█' * filled}{'░' * empty}{Colors.RESET}"
        return f"[{bar}] {percent:.0f}%"

    def _format_tokens(self, tokens: int) -> str:
        """Format token count with K/M suffix."""
        if tokens >= 1_000_000:
            return f"{tokens / 1_000_000:.1f}M"
        elif tokens >= 1_000:
            return f"{tokens / 1_000:.1f}K"
        return str(tokens)

    def _format_elapsed(self) -> str:
        """Format elapsed time."""
        elapsed = datetime.now() - self.start_time
        minutes = int(elapsed.total_seconds() // 60)
        seconds = int(elapsed.total_seconds() % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def _get_budget_color(self, percent: float) -> str:
        """Get color based on budget usage."""
        if percent >= 90:
            return Colors.BOLD_RED
        elif percent >= 75:
            return Colors.BOLD_YELLOW
        return Colors.BOLD_GREEN

    def render(self) -> str:
        """Render the full display as a string."""
        session = self.tracker.session
        lines = []

        # Header
        lines.append(f"{Colors.CYAN}{self._box_line(self.BOX_TOP_LEFT, self.BOX_TOP_RIGHT)}{Colors.RESET}")
        title = f"COST MONITOR - Story: {session.story_key}"
        lines.append(f"{Colors.CYAN}{self._content_line(Colors.BOLD + title + Colors.RESET, 'center')}{Colors.RESET}")
        lines.append(f"{Colors.CYAN}{self._box_line(self.BOX_T_LEFT, self.BOX_T_RIGHT)}{Colors.RESET}")

        # Current Session Info
        lines.append(self._empty_line())
        lines.append(self._section_header("CURRENT SESSION"))

        agent = self.tracker.current_agent or "N/A"
        model = self.tracker.current_model or "N/A"
        elapsed = self._format_elapsed()

        lines.append(self._content_line(
            f"Agent: {Colors.BOLD_CYAN}{agent:20}{Colors.RESET} Model: {Colors.BOLD_BLUE}{model}{Colors.RESET}"
        ))
        lines.append(self._content_line(
            f"Status: {Colors.BOLD_GREEN}Running{Colors.RESET}               Elapsed: {Colors.BOLD}{elapsed}{Colors.RESET}"
        ))

        # Tokens
        lines.append(self._empty_line())
        lines.append(self._section_header("TOKENS"))

        input_tokens = self._format_tokens(session.total_input_tokens)
        output_tokens = self._format_tokens(session.total_output_tokens)
        total_tokens = self._format_tokens(session.total_tokens)

        lines.append(self._content_line(
            f"Input:  {Colors.BOLD}{input_tokens:>12} tokens{Colors.RESET}    "
            f"Output: {Colors.BOLD}{output_tokens:>12} tokens{Colors.RESET}"
        ))
        lines.append(self._content_line(
            f"Total:  {Colors.BOLD_WHITE}{total_tokens:>12} tokens{Colors.RESET}"
        ))

        # Cost Breakdown by Agent
        if not self.compact:
            lines.append(self._empty_line())
            lines.append(self._section_header("COST BREAKDOWN"))

            # Table header
            lines.append(self._content_line(
                f"{Colors.DIM}{'Agent':<10} {'Model':<10} {'Input $':>10} {'Output $':>10} {'Total':>10}{Colors.RESET}"
            ))
            lines.append(self._content_line(f"{Colors.DIM}{self.BOX_LINE * 54}{Colors.RESET}"))

            # Aggregate by agent+model
            breakdown = {}
            for entry in session.entries:
                key = (entry.agent, entry.model)
                if key not in breakdown:
                    breakdown[key] = {"input": 0, "output": 0, "cost": 0}

                # Estimate input/output cost split
                input_cost = entry.cost_usd * 0.2  # Rough estimate
                output_cost = entry.cost_usd * 0.8
                breakdown[key]["input"] += input_cost
                breakdown[key]["output"] += output_cost
                breakdown[key]["cost"] += entry.cost_usd

            for (agent, model), data in breakdown.items():
                lines.append(self._content_line(
                    f"{agent:<10} {model:<10} "
                    f"${data['input']:>8.2f} ${data['output']:>8.2f} "
                    f"{Colors.BOLD}${data['cost']:>8.2f}{Colors.RESET}"
                ))

            # Total row
            total_cost = session.total_cost_usd
            lines.append(self._content_line(f"{Colors.DIM}{self.BOX_LINE * 54}{Colors.RESET}"))
            lines.append(self._content_line(
                f"{Colors.BOLD}{'TOTAL':<10} {'':10} "
                f"{'':>10} {'':>10} ${total_cost:>8.2f}{Colors.RESET}"
            ))

        # Budget
        lines.append(self._empty_line())
        lines.append(self._section_header("BUDGET"))

        budget_pct = session.budget_used_percent
        budget_color = self._get_budget_color(budget_pct)

        lines.append(self._content_line(
            f"Limit: {Colors.BOLD}${session.budget_limit_usd:.2f}{Colors.RESET}    "
            f"Used: {budget_color}${session.total_cost_usd:.2f}{Colors.RESET}    "
            f"Remaining: {Colors.BOLD}${session.budget_remaining:.2f}{Colors.RESET}"
        ))
        lines.append(self._content_line(self._progress_bar(budget_pct)))

        # Budget status message
        ok, level, msg = self.tracker.check_budget()
        if level == "critical":
            lines.append(self._content_line(f"{Colors.BG_RED}{Colors.WHITE} {msg} {Colors.RESET}"))
        elif level == "warning":
            lines.append(self._content_line(f"{Colors.YELLOW}{msg}{Colors.RESET}"))

        # Multi-currency
        lines.append(self._empty_line())
        lines.append(self._section_header("MULTI-CURRENCY"))
        lines.append(self._content_line(self.converter.format_all(session.total_cost_usd, " │ ")))

        # Footer
        lines.append(self._empty_line())
        lines.append(f"{Colors.CYAN}{self._box_line(self.BOX_BOTTOM_LEFT, self.BOX_BOTTOM_RIGHT)}{Colors.RESET}")
        lines.append(f"{Colors.DIM}Press Ctrl+C to stop monitoring{Colors.RESET}")

        return '\n'.join(lines)

    def refresh(self, clear: bool = True):
        """Refresh the display."""
        if clear:
            self.clear_screen()

        print(self.render())
        self.last_refresh = datetime.now()

    def clear_screen(self):
        """Clear the terminal screen."""
        if sys.platform == 'win32':
            os.system('cls')
        else:
            os.system('clear')
            # Alternative: print ANSI escape
            # print('\033[2J\033[H', end='')

    def update_in_place(self):
        """Update display in place without full clear."""
        # Move cursor to top
        lines = self.render().count('\n') + 1
        print(f'\033[{lines}A', end='')
        print(self.render())


class CompactCostDisplay:
    """Compact single-line cost display for inline monitoring."""

    def __init__(self, tracker: CostTracker, converter: Optional[CurrencyConverter] = None):
        self.tracker = tracker
        self.converter = converter or get_converter()

    def render(self) -> str:
        """Render compact display."""
        session = self.tracker.session
        pct = session.budget_used_percent

        # Color based on budget
        if pct >= 90:
            color = Colors.RED
        elif pct >= 75:
            color = Colors.YELLOW
        else:
            color = Colors.GREEN

        tokens = f"{session.total_tokens:,}"
        cost = self.converter.format(session.total_cost_usd, "USD")
        budget = f"{pct:.0f}%"

        return (
            f"{Colors.BOLD}Cost:{Colors.RESET} {color}{cost}{Colors.RESET} "
            f"({budget}) │ "
            f"{Colors.BOLD}Tokens:{Colors.RESET} {tokens}"
        )

    def print(self):
        """Print compact display."""
        print(f"\r{self.render()}", end='', flush=True)


if __name__ == "__main__":
    # Demo
    from cost_tracker import CostTracker

    tracker = CostTracker(story_key="demo-story", budget_limit_usd=15.00)

    # Simulate usage
    tracker.log_usage("SM", "sonnet", 15000, 3000)
    tracker.set_current_agent("DEV", "opus")
    tracker.log_usage("DEV", "opus", 50000, 15000)

    # Full display
    display = CostDisplay(tracker)
    display.refresh()

    print("\n" + "=" * 70 + "\n")

    # Compact display
    compact = CompactCostDisplay(tracker)
    print("Compact: ", end='')
    compact.print()
    print()
