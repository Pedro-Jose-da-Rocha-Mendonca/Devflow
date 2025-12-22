#!/usr/bin/env python3
"""
Cost Dashboard - CLI for viewing and managing cost data.

Provides commands for viewing session history, generating summaries,
and exporting cost reports in multiple formats.

Usage:
    python cost_dashboard.py                    # Show current/latest session
    python cost_dashboard.py --history 10       # Show last 10 sessions
    python cost_dashboard.py --summary          # Show aggregate summary
    python cost_dashboard.py --story 3-5        # Show costs for story
    python cost_dashboard.py --export costs.csv # Export to file
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Lowercase generic types for Python 3.9+ compatibility
# Using 'list' instead of 'List' from typing

# Add lib directory for imports
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from cost_display import Colors
from cost_tracker import SESSIONS_DIR, CostTracker, SessionCost
from currency_converter import get_converter


class CostDashboard:
    """
    CLI Dashboard for cost analysis.

    Provides commands for viewing, summarizing, and exporting cost data.
    """

    # Box drawing
    BOX_TOP_LEFT = '╔'
    BOX_TOP_RIGHT = '╗'
    BOX_BOTTOM_LEFT = '╚'
    BOX_BOTTOM_RIGHT = '╝'
    BOX_HORIZONTAL = '═'
    BOX_VERTICAL = '║'
    BOX_T_LEFT = '╠'
    BOX_T_RIGHT = '╣'
    BOX_LINE = '─'

    def __init__(self, width: int = 70):
        self.width = width
        self.converter = get_converter()

    def _box_line(self, left: str, right: str, fill: str = '═') -> str:
        """Create a box line."""
        return f"{left}{fill * (self.width - 2)}{right}"

    def _content_line(self, content: str, align: str = "left") -> str:
        """Create a content line within the box."""
        clean_content = Colors.strip(content)
        padding = self.width - 4 - len(clean_content)

        if align == "center":
            left_pad = padding // 2
            right_pad = padding - left_pad
            return f"{self.BOX_VERTICAL} {' ' * left_pad}{content}{' ' * right_pad} {self.BOX_VERTICAL}"
        elif align == "right":
            return f"{self.BOX_VERTICAL} {' ' * padding}{content} {self.BOX_VERTICAL}"
        else:
            return f"{self.BOX_VERTICAL} {content}{' ' * padding} {self.BOX_VERTICAL}"

    def _empty_line(self) -> str:
        """Create an empty content line."""
        return self._content_line("")

    def _section_header(self, title: str) -> str:
        """Create a section header."""
        line = f"{self.BOX_LINE * 3} {title} "
        remaining = self.width - 6 - len(title)
        return self._content_line(f"{Colors.BOLD}{line}{self.BOX_LINE * remaining}{Colors.RESET}")

    def _format_tokens(self, tokens: int) -> str:
        """Format token count with K/M suffix."""
        if tokens >= 1_000_000:
            return f"{tokens / 1_000_000:.1f}M"
        elif tokens >= 1_000:
            return f"{tokens / 1_000:.1f}K"
        return str(tokens)

    def show_session(self, session: SessionCost):
        """Display a single session."""
        lines = []

        # Header
        lines.append(f"{Colors.CYAN}{self._box_line(self.BOX_TOP_LEFT, self.BOX_TOP_RIGHT)}{Colors.RESET}")
        title = f"SESSION: {session.session_id[:20]}"
        lines.append(f"{Colors.CYAN}{self._content_line(Colors.BOLD + title + Colors.RESET, 'center')}{Colors.RESET}")
        lines.append(f"{Colors.CYAN}{self._box_line(self.BOX_T_LEFT, self.BOX_T_RIGHT)}{Colors.RESET}")

        # Session info
        lines.append(self._empty_line())
        lines.append(self._content_line(f"Story: {Colors.BOLD_CYAN}{session.story_key}{Colors.RESET}"))
        lines.append(self._content_line(f"Start: {session.start_time[:19]}"))
        if session.end_time:
            lines.append(self._content_line(f"End:   {session.end_time[:19]}"))

        # Tokens
        lines.append(self._empty_line())
        lines.append(self._section_header("TOKENS"))
        lines.append(self._content_line(
            f"Input:  {Colors.BOLD}{self._format_tokens(session.total_input_tokens):>10}{Colors.RESET}    "
            f"Output: {Colors.BOLD}{self._format_tokens(session.total_output_tokens):>10}{Colors.RESET}"
        ))
        lines.append(self._content_line(
            f"Total:  {Colors.BOLD_WHITE}{self._format_tokens(session.total_tokens):>10}{Colors.RESET}"
        ))

        # Cost by agent
        lines.append(self._empty_line())
        lines.append(self._section_header("COST BY AGENT"))

        by_agent = session.get_cost_by_agent()
        if by_agent:
            for agent, cost in sorted(by_agent.items(), key=lambda x: -x[1]):
                pct = (cost / session.total_cost_usd * 100) if session.total_cost_usd > 0 else 0
                lines.append(self._content_line(
                    f"{agent:<12} {Colors.BOLD}${cost:>8.2f}{Colors.RESET}  ({pct:>5.1f}%)"
                ))
        else:
            lines.append(self._content_line(f"{Colors.DIM}No entries{Colors.RESET}"))

        # Cost by model
        lines.append(self._empty_line())
        lines.append(self._section_header("COST BY MODEL"))

        by_model = session.get_cost_by_model()
        if by_model:
            for model, cost in sorted(by_model.items(), key=lambda x: -x[1]):
                pct = (cost / session.total_cost_usd * 100) if session.total_cost_usd > 0 else 0
                lines.append(self._content_line(
                    f"{model:<12} {Colors.BOLD}${cost:>8.2f}{Colors.RESET}  ({pct:>5.1f}%)"
                ))

        # Total
        lines.append(self._empty_line())
        lines.append(self._section_header("TOTAL"))
        lines.append(self._content_line(
            f"Cost: {Colors.BOLD_GREEN}${session.total_cost_usd:.2f}{Colors.RESET}    "
            f"Budget: ${session.budget_limit_usd:.2f}    "
            f"Used: {session.budget_used_percent:.0f}%"
        ))

        # Multi-currency
        lines.append(self._empty_line())
        lines.append(self._content_line(self.converter.format_all(session.total_cost_usd, " │ ")))

        # Footer
        lines.append(self._empty_line())
        lines.append(f"{Colors.CYAN}{self._box_line(self.BOX_BOTTOM_LEFT, self.BOX_BOTTOM_RIGHT)}{Colors.RESET}")

        print('\n'.join(lines))

    def show_history(self, sessions: list[SessionCost], limit: int = 10):
        """Display session history."""
        sessions = sessions[:limit]

        lines = []

        # Header
        lines.append(f"{Colors.CYAN}{self._box_line(self.BOX_TOP_LEFT, self.BOX_TOP_RIGHT)}{Colors.RESET}")
        title = f"SESSION HISTORY - Last {len(sessions)} Sessions"
        lines.append(f"{Colors.CYAN}{self._content_line(Colors.BOLD + title + Colors.RESET, 'center')}{Colors.RESET}")
        lines.append(f"{Colors.CYAN}{self._box_line(self.BOX_T_LEFT, self.BOX_T_RIGHT)}{Colors.RESET}")

        # Table header
        lines.append(self._empty_line())
        lines.append(self._content_line(
            f"{Colors.DIM}{'Date':<12} {'Story':<10} {'Tokens':>10} {'Cost':>10} {'Budget%':>8}{Colors.RESET}"
        ))
        lines.append(self._content_line(f"{Colors.DIM}{self.BOX_LINE * 54}{Colors.RESET}"))

        # Sessions
        total_cost = 0
        total_tokens = 0

        for session in sessions:
            date_str = session.start_time[:10]
            tokens = self._format_tokens(session.total_tokens)
            cost = f"${session.total_cost_usd:.2f}"
            budget_pct = f"{session.budget_used_percent:.0f}%"

            # Color based on budget usage
            if session.budget_used_percent >= 90:
                color = Colors.RED
            elif session.budget_used_percent >= 75:
                color = Colors.YELLOW
            else:
                color = Colors.GREEN

            lines.append(self._content_line(
                f"{date_str:<12} {session.story_key:<10} {tokens:>10} "
                f"{color}{cost:>10}{Colors.RESET} {budget_pct:>8}"
            ))

            total_cost += session.total_cost_usd
            total_tokens += session.total_tokens

        # Totals
        lines.append(self._content_line(f"{Colors.DIM}{self.BOX_LINE * 54}{Colors.RESET}"))
        lines.append(self._content_line(
            f"{Colors.BOLD}{'TOTAL':<12} {'':<10} {self._format_tokens(total_tokens):>10} "
            f"${total_cost:>9.2f}{Colors.RESET}"
        ))

        # Footer
        lines.append(self._empty_line())
        lines.append(f"{Colors.CYAN}{self._box_line(self.BOX_BOTTOM_LEFT, self.BOX_BOTTOM_RIGHT)}{Colors.RESET}")

        print('\n'.join(lines))

    def show_summary(self, days: int = 30):
        """Display aggregate summary."""
        stats = CostTracker.get_aggregate_stats(days)

        lines = []

        # Header
        lines.append(f"{Colors.CYAN}{self._box_line(self.BOX_TOP_LEFT, self.BOX_TOP_RIGHT)}{Colors.RESET}")
        title = f"COST SUMMARY - Last {days} Days"
        lines.append(f"{Colors.CYAN}{self._content_line(Colors.BOLD + title + Colors.RESET, 'center')}{Colors.RESET}")
        lines.append(f"{Colors.CYAN}{self._box_line(self.BOX_T_LEFT, self.BOX_T_RIGHT)}{Colors.RESET}")

        # Overview
        lines.append(self._empty_line())
        lines.append(self._section_header("OVERVIEW"))
        lines.append(self._content_line(
            f"Total Sessions: {Colors.BOLD}{stats['total_sessions']}{Colors.RESET}"
        ))
        lines.append(self._content_line(
            f"Total Tokens:   {Colors.BOLD}{self._format_tokens(stats['total_tokens'])}{Colors.RESET}"
        ))
        lines.append(self._content_line(
            f"Total Cost:     {Colors.BOLD_GREEN}${stats['total_cost_usd']:.2f}{Colors.RESET}"
        ))
        lines.append(self._content_line(
            f"Avg/Session:    {Colors.BOLD}${stats.get('average_per_session', 0):.2f}{Colors.RESET}"
        ))

        # Multi-currency total
        lines.append(self._empty_line())
        lines.append(self._content_line(self.converter.format_all(stats['total_cost_usd'], " │ ")))

        # By Agent
        if stats.get('by_agent'):
            lines.append(self._empty_line())
            lines.append(self._section_header("BY AGENT"))
            lines.append(self._content_line(
                f"{Colors.DIM}{'Agent':<12} {'Sessions':>10} {'Cost':>12}{Colors.RESET}"
            ))
            lines.append(self._content_line(f"{Colors.DIM}{self.BOX_LINE * 38}{Colors.RESET}"))

            for agent, data in sorted(stats['by_agent'].items(), key=lambda x: -x[1]['cost']):
                lines.append(self._content_line(
                    f"{agent:<12} {data['sessions']:>10} {Colors.BOLD}${data['cost']:>10.2f}{Colors.RESET}"
                ))

        # By Model
        if stats.get('by_model'):
            lines.append(self._empty_line())
            lines.append(self._section_header("BY MODEL"))
            lines.append(self._content_line(
                f"{Colors.DIM}{'Model':<20} {'Cost':>12}{Colors.RESET}"
            ))
            lines.append(self._content_line(f"{Colors.DIM}{self.BOX_LINE * 36}{Colors.RESET}"))

            for model, data in sorted(stats['by_model'].items(), key=lambda x: -x[1]['cost']):
                lines.append(self._content_line(
                    f"{model:<20} {Colors.BOLD}${data['cost']:>10.2f}{Colors.RESET}"
                ))

        # Footer
        lines.append(self._empty_line())
        lines.append(f"{Colors.CYAN}{self._box_line(self.BOX_BOTTOM_LEFT, self.BOX_BOTTOM_RIGHT)}{Colors.RESET}")

        print('\n'.join(lines))

    def show_story(self, story_key: str):
        """Display costs for a specific story."""
        sessions = CostTracker.get_historical_sessions(days=365)
        story_sessions = [s for s in sessions if s.story_key == story_key]

        if not story_sessions:
            print(f"{Colors.YELLOW}No sessions found for story: {story_key}{Colors.RESET}")
            return

        lines = []

        # Header
        lines.append(f"{Colors.CYAN}{self._box_line(self.BOX_TOP_LEFT, self.BOX_TOP_RIGHT)}{Colors.RESET}")
        title = f"STORY COSTS: {story_key}"
        lines.append(f"{Colors.CYAN}{self._content_line(Colors.BOLD + title + Colors.RESET, 'center')}{Colors.RESET}")
        lines.append(f"{Colors.CYAN}{self._box_line(self.BOX_T_LEFT, self.BOX_T_RIGHT)}{Colors.RESET}")

        # Summary
        total_cost = sum(s.total_cost_usd for s in story_sessions)
        total_tokens = sum(s.total_tokens for s in story_sessions)

        lines.append(self._empty_line())
        lines.append(self._content_line(f"Sessions:     {Colors.BOLD}{len(story_sessions)}{Colors.RESET}"))
        lines.append(self._content_line(f"Total Tokens: {Colors.BOLD}{self._format_tokens(total_tokens)}{Colors.RESET}"))
        lines.append(self._content_line(f"Total Cost:   {Colors.BOLD_GREEN}${total_cost:.2f}{Colors.RESET}"))

        # Multi-currency
        lines.append(self._empty_line())
        lines.append(self._content_line(self.converter.format_all(total_cost, " │ ")))

        # Sessions
        lines.append(self._empty_line())
        lines.append(self._section_header("SESSIONS"))
        lines.append(self._content_line(
            f"{Colors.DIM}{'Date':<12} {'Duration':<10} {'Tokens':>10} {'Cost':>10}{Colors.RESET}"
        ))
        lines.append(self._content_line(f"{Colors.DIM}{self.BOX_LINE * 46}{Colors.RESET}"))

        for session in story_sessions:
            date_str = session.start_time[:10]

            # Calculate duration
            if session.end_time:
                try:
                    start = datetime.fromisoformat(session.start_time)
                    end = datetime.fromisoformat(session.end_time)
                    duration = end - start
                    duration_str = f"{int(duration.total_seconds() // 60)}m"
                except (ValueError, TypeError):
                    duration_str = "N/A"
            else:
                duration_str = "Running"

            lines.append(self._content_line(
                f"{date_str:<12} {duration_str:<10} "
                f"{self._format_tokens(session.total_tokens):>10} "
                f"${session.total_cost_usd:>9.2f}"
            ))

        # Footer
        lines.append(self._empty_line())
        lines.append(f"{Colors.CYAN}{self._box_line(self.BOX_BOTTOM_LEFT, self.BOX_BOTTOM_RIGHT)}{Colors.RESET}")

        print('\n'.join(lines))

    def export_data(self, filepath: str, sessions: Optional[list[SessionCost]] = None):
        """Export cost data to file."""
        if sessions is None:
            sessions = CostTracker.get_historical_sessions(days=365)

        path = Path(filepath)
        ext = path.suffix.lower()

        if ext == '.csv':
            self._export_csv(path, sessions)
        elif ext == '.json':
            self._export_json(path, sessions)
        elif ext == '.md':
            self._export_markdown(path, sessions)
        else:
            print(f"{Colors.RED}Unsupported format: {ext}{Colors.RESET}")
            print("Supported formats: .csv, .json, .md")
            return

        print(f"{Colors.GREEN}Exported to: {filepath}{Colors.RESET}")
        print(f"  Sessions: {len(sessions)}")
        print(f"  Total Cost: ${sum(s.total_cost_usd for s in sessions):.2f}")

    def _export_csv(self, path: Path, sessions: list[SessionCost]):
        """Export to CSV."""
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'session_id', 'story_key', 'start_time', 'end_time',
                'input_tokens', 'output_tokens', 'total_tokens',
                'cost_usd', 'budget_limit', 'budget_used_pct'
            ])

            # Data
            for session in sessions:
                writer.writerow([
                    session.session_id,
                    session.story_key,
                    session.start_time,
                    session.end_time or '',
                    session.total_input_tokens,
                    session.total_output_tokens,
                    session.total_tokens,
                    round(session.total_cost_usd, 4),
                    session.budget_limit_usd,
                    round(session.budget_used_percent, 2)
                ])

    def _export_json(self, path: Path, sessions: list[SessionCost]):
        """Export to JSON."""
        data = {
            'exported_at': datetime.now().isoformat(),
            'total_sessions': len(sessions),
            'total_cost_usd': sum(s.total_cost_usd for s in sessions),
            'sessions': [s.to_dict() for s in sessions]
        }

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def _export_markdown(self, path: Path, sessions: list[SessionCost]):
        """Export to Markdown."""
        total_cost = sum(s.total_cost_usd for s in sessions)
        total_tokens = sum(s.total_tokens for s in sessions)

        lines = [
            "# Cost Report",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## Summary",
            "",
            f"- **Total Sessions**: {len(sessions)}",
            f"- **Total Tokens**: {total_tokens:,}",
            f"- **Total Cost**: ${total_cost:.2f}",
            f"- **Average per Session**: ${total_cost / len(sessions):.2f}" if sessions else "",
            "",
            "### Multi-Currency",
            "",
            f"- USD: ${total_cost:.2f}",
            f"- EUR: {self.converter.format(total_cost, 'EUR')}",
            f"- GBP: {self.converter.format(total_cost, 'GBP')}",
            f"- BRL: {self.converter.format(total_cost, 'BRL')}",
            "",
            "## Sessions",
            "",
            "| Date | Story | Tokens | Cost | Budget % |",
            "|------|-------|--------|------|----------|",
        ]

        for session in sessions:
            lines.append(
                f"| {session.start_time[:10]} | {session.story_key} | "
                f"{session.total_tokens:,} | ${session.total_cost_usd:.2f} | "
                f"{session.budget_used_percent:.0f}% |"
            )

        with open(path, 'w') as f:
            f.write('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(
        description="Cost Dashboard - View and manage cost data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cost_dashboard.py                    # Show latest session
  python cost_dashboard.py --history 10       # Show last 10 sessions
  python cost_dashboard.py --summary          # Show 30-day summary
  python cost_dashboard.py --story 3-5        # Show costs for story
  python cost_dashboard.py --export costs.csv # Export to CSV
  python cost_dashboard.py --export report.md # Export to Markdown
        """
    )

    parser.add_argument(
        '--history', '-H',
        type=int,
        metavar='N',
        help='Show last N sessions'
    )
    parser.add_argument(
        '--summary', '-s',
        action='store_true',
        help='Show aggregate summary'
    )
    parser.add_argument(
        '--days', '-d',
        type=int,
        default=30,
        help='Number of days for summary (default: 30)'
    )
    parser.add_argument(
        '--story',
        type=str,
        metavar='KEY',
        help='Show costs for specific story'
    )
    parser.add_argument(
        '--export', '-e',
        type=str,
        metavar='FILE',
        help='Export to file (.csv, .json, .md)'
    )
    parser.add_argument(
        '--from-date',
        type=str,
        metavar='YYYY-MM-DD',
        help='Filter from date'
    )
    parser.add_argument(
        '--to-date',
        type=str,
        metavar='YYYY-MM-DD',
        help='Filter to date'
    )

    args = parser.parse_args()
    dashboard = CostDashboard()

    # Get sessions
    sessions = CostTracker.get_historical_sessions(days=args.days)

    # Apply date filters
    if args.from_date:
        try:
            from_dt = datetime.fromisoformat(args.from_date)
            sessions = [s for s in sessions if datetime.fromisoformat(s.start_time) >= from_dt]
        except ValueError:
            print(f"{Colors.RED}Invalid from-date format. Use YYYY-MM-DD{Colors.RESET}")
            return 1

    if args.to_date:
        try:
            to_dt = datetime.fromisoformat(args.to_date)
            sessions = [s for s in sessions if datetime.fromisoformat(s.start_time) <= to_dt]
        except ValueError:
            print(f"{Colors.RED}Invalid to-date format. Use YYYY-MM-DD{Colors.RESET}")
            return 1

    # Execute command
    if args.export:
        dashboard.export_data(args.export, sessions)
    elif args.summary:
        dashboard.show_summary(args.days)
    elif args.story:
        dashboard.show_story(args.story)
    elif args.history:
        dashboard.show_history(sessions, args.history)
    else:
        # Show latest session
        if sessions:
            dashboard.show_session(sessions[0])
        else:
            print(f"{Colors.YELLOW}No session data found.{Colors.RESET}")
            print(f"Session data is stored in: {SESSIONS_DIR}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
