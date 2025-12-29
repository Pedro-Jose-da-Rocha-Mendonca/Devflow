"""
Comprehensive unit tests for cost_tracker.py

Tests the critical cost tracking functionality including:
- Cost calculations
- Budget monitoring
- Session management
- Token usage parsing
- Historical data aggregation
"""

import sys
from datetime import datetime
from pathlib import Path

# Ensure imports work
sys.path.insert(0, str(Path(__file__).parent.parent / "tooling" / "scripts" / "lib"))

from lib.cost_tracker import (
    DEFAULT_THRESHOLDS,
    PRICING,
    CostEntry,
    CostTracker,
    SessionCost,
    get_tracker,
    parse_token_usage,
    set_tracker,
    start_tracking,
)


class TestCostEntry:
    """Tests for CostEntry dataclass."""

    def test_cost_entry_creation(self):
        """Test creating a cost entry."""
        entry = CostEntry(
            timestamp="2024-12-21T10:30:00",
            agent="DEV",
            model="opus",
            input_tokens=1000,
            output_tokens=500,
            cost_usd=0.0525,
        )
        assert entry.agent == "DEV"
        assert entry.model == "opus"
        assert entry.input_tokens == 1000
        assert entry.output_tokens == 500
        assert entry.cost_usd == 0.0525

    def test_cost_entry_to_dict(self):
        """Test converting cost entry to dictionary."""
        entry = CostEntry(
            timestamp="2024-12-21T10:30:00",
            agent="SM",
            model="sonnet",
            input_tokens=5000,
            output_tokens=1000,
            cost_usd=0.030,
        )
        result = entry.to_dict()
        assert isinstance(result, dict)
        assert result["agent"] == "SM"
        assert result["model"] == "sonnet"
        assert result["input_tokens"] == 5000


class TestSessionCost:
    """Tests for SessionCost dataclass."""

    def test_session_cost_creation(self):
        """Test creating a session cost."""
        session = SessionCost(
            session_id="test_session",
            story_key="PROJ-123",
            start_time="2024-12-21T10:00:00",
            budget_limit_usd=15.00,
        )
        assert session.session_id == "test_session"
        assert session.story_key == "PROJ-123"
        assert session.budget_limit_usd == 15.00
        assert len(session.entries) == 0

    def test_session_total_tokens(self):
        """Test total token calculations."""
        session = SessionCost(session_id="test", story_key="test", start_time="2024-12-21T10:00:00")
        session.entries.append(
            CostEntry(
                timestamp="2024-12-21T10:01:00",
                agent="DEV",
                model="opus",
                input_tokens=1000,
                output_tokens=500,
                cost_usd=0.05,
            )
        )
        session.entries.append(
            CostEntry(
                timestamp="2024-12-21T10:02:00",
                agent="SM",
                model="sonnet",
                input_tokens=2000,
                output_tokens=1000,
                cost_usd=0.02,
            )
        )

        assert session.total_input_tokens == 3000
        assert session.total_output_tokens == 1500
        assert session.total_tokens == 4500

    def test_session_total_cost(self):
        """Test total cost calculation."""
        session = SessionCost(session_id="test", story_key="test", start_time="2024-12-21T10:00:00")
        session.entries.append(
            CostEntry(
                timestamp="2024-12-21T10:01:00",
                agent="DEV",
                model="opus",
                input_tokens=1000,
                output_tokens=500,
                cost_usd=0.05,
            )
        )
        session.entries.append(
            CostEntry(
                timestamp="2024-12-21T10:02:00",
                agent="SM",
                model="sonnet",
                input_tokens=2000,
                output_tokens=1000,
                cost_usd=0.02,
            )
        )

        assert session.total_cost_usd == 0.07

    def test_session_budget_remaining(self):
        """Test budget remaining calculation."""
        session = SessionCost(
            session_id="test",
            story_key="test",
            start_time="2024-12-21T10:00:00",
            budget_limit_usd=10.00,
        )
        session.entries.append(
            CostEntry(
                timestamp="2024-12-21T10:01:00",
                agent="DEV",
                model="opus",
                input_tokens=1000,
                output_tokens=500,
                cost_usd=3.00,
            )
        )

        assert session.budget_remaining == 7.00
        assert session.budget_used_percent == 30.0

    def test_session_budget_remaining_exceeds(self):
        """Test budget remaining when cost exceeds budget."""
        session = SessionCost(
            session_id="test",
            story_key="test",
            start_time="2024-12-21T10:00:00",
            budget_limit_usd=5.00,
        )
        session.entries.append(
            CostEntry(
                timestamp="2024-12-21T10:01:00",
                agent="DEV",
                model="opus",
                input_tokens=1000,
                output_tokens=500,
                cost_usd=7.00,
            )
        )

        assert session.budget_remaining == 0  # Should not go negative
        assert session.budget_used_percent == 100  # Capped at 100%

    def test_session_get_cost_by_agent(self):
        """Test cost breakdown by agent."""
        session = SessionCost(session_id="test", story_key="test", start_time="2024-12-21T10:00:00")
        session.entries.append(
            CostEntry(
                timestamp="2024-12-21T10:01:00",
                agent="DEV",
                model="opus",
                input_tokens=1000,
                output_tokens=500,
                cost_usd=0.05,
            )
        )
        session.entries.append(
            CostEntry(
                timestamp="2024-12-21T10:02:00",
                agent="SM",
                model="sonnet",
                input_tokens=2000,
                output_tokens=1000,
                cost_usd=0.02,
            )
        )
        session.entries.append(
            CostEntry(
                timestamp="2024-12-21T10:03:00",
                agent="DEV",
                model="opus",
                input_tokens=500,
                output_tokens=250,
                cost_usd=0.03,
            )
        )

        by_agent = session.get_cost_by_agent()
        assert by_agent["DEV"] == 0.08
        assert by_agent["SM"] == 0.02

    def test_session_get_cost_by_model(self):
        """Test cost breakdown by model."""
        session = SessionCost(session_id="test", story_key="test", start_time="2024-12-21T10:00:00")
        session.entries.append(
            CostEntry(
                timestamp="2024-12-21T10:01:00",
                agent="DEV",
                model="opus",
                input_tokens=1000,
                output_tokens=500,
                cost_usd=0.05,
            )
        )
        session.entries.append(
            CostEntry(
                timestamp="2024-12-21T10:02:00",
                agent="SM",
                model="sonnet",
                input_tokens=2000,
                output_tokens=1000,
                cost_usd=0.02,
            )
        )

        by_model = session.get_cost_by_model()
        assert by_model["opus"] == 0.05
        assert by_model["sonnet"] == 0.02

    def test_session_to_dict(self):
        """Test session serialization."""
        session = SessionCost(
            session_id="test",
            story_key="test",
            start_time="2024-12-21T10:00:00",
            budget_limit_usd=15.00,
        )
        result = session.to_dict()

        assert result["session_id"] == "test"
        assert result["story_key"] == "test"
        assert "totals" in result
        assert result["totals"]["total_tokens"] == 0


class TestCostTracker:
    """Tests for the main CostTracker class."""

    def test_tracker_initialization(self, mock_costs_directories):
        """Test tracker initialization."""
        tracker = CostTracker(story_key="PROJ-123", budget_limit_usd=20.00)

        assert tracker.story_key == "PROJ-123"
        assert tracker.budget_limit_usd == 20.00
        assert tracker.session is not None
        assert tracker.session.story_key == "PROJ-123"

    def test_tracker_session_id_format(self, mock_costs_directories):
        """Test that session ID is properly formatted."""
        tracker = CostTracker(story_key="test")

        # Session ID should contain date and random hex
        parts = tracker.session_id.split("_")
        assert len(parts) == 3  # date, time, hex
        assert len(parts[2]) == 8  # 8 hex chars

    def test_calculate_cost_opus(self, sample_tracker):
        """Test cost calculation for opus model."""
        # Opus: $15/1M input, $75/1M output
        cost = sample_tracker.calculate_cost("opus", 1_000_000, 100_000)
        expected = 15.00 + 7.50  # $15 input + $7.50 output
        assert cost == expected

    def test_calculate_cost_sonnet(self, sample_tracker):
        """Test cost calculation for sonnet model."""
        # Sonnet: $3/1M input, $15/1M output
        cost = sample_tracker.calculate_cost("sonnet", 1_000_000, 100_000)
        expected = 3.00 + 1.50  # $3 input + $1.50 output
        assert cost == expected

    def test_calculate_cost_haiku(self, sample_tracker):
        """Test cost calculation for haiku model."""
        # Haiku: $0.80/1M input, $4/1M output
        cost = sample_tracker.calculate_cost("haiku", 1_000_000, 100_000)
        expected = 0.80 + 0.40  # $0.80 input + $0.40 output
        assert abs(cost - expected) < 0.0001  # Use approximate comparison for floats

    def test_calculate_cost_unknown_model(self, sample_tracker):
        """Test that unknown models default to sonnet pricing."""
        cost = sample_tracker.calculate_cost("unknown-model", 1_000_000, 100_000)
        # Should use sonnet pricing: $3/1M input, $15/1M output
        expected = 3.00 + 1.50
        assert cost == expected

    def test_calculate_cost_full_model_name(self, sample_tracker):
        """Test cost calculation with full model names."""
        cost = sample_tracker.calculate_cost("claude-opus-4-5-20251101", 1_000_000, 100_000)
        expected = 15.00 + 7.50  # Opus pricing
        assert cost == expected

    def test_log_usage(self, sample_tracker):
        """Test logging usage."""
        entry = sample_tracker.log_usage(
            agent="DEV", model="opus", input_tokens=10000, output_tokens=5000
        )

        assert entry.agent == "DEV"
        assert entry.model == "opus"
        assert entry.input_tokens == 10000
        assert entry.output_tokens == 5000
        assert entry.cost_usd > 0
        assert len(sample_tracker.session.entries) == 1

    def test_log_usage_updates_current_agent(self, sample_tracker):
        """Test that logging usage updates current agent tracking."""
        sample_tracker.log_usage("SM", "sonnet", 1000, 500)
        assert sample_tracker.current_agent == "SM"
        assert sample_tracker.current_model == "sonnet"

        sample_tracker.log_usage("DEV", "opus", 2000, 1000)
        assert sample_tracker.current_agent == "DEV"
        assert sample_tracker.current_model == "opus"

    def test_set_current_agent(self, sample_tracker):
        """Test setting current agent manually."""
        sample_tracker.set_current_agent("BA", "haiku")
        assert sample_tracker.current_agent == "BA"
        assert sample_tracker.current_model == "haiku"

    def test_check_budget_ok(self, sample_tracker):
        """Test budget check when under budget."""
        sample_tracker.log_usage("SM", "sonnet", 1000, 500)

        ok, level, msg = sample_tracker.check_budget()
        assert ok is True
        assert level == "ok"

    def test_check_budget_warning(self, mock_costs_directories):
        """Test budget check at warning level."""
        tracker = CostTracker(story_key="test", budget_limit_usd=1.00)
        # Log usage that costs ~$0.77 (77% of $1)
        # Need to calculate tokens to get to 77%
        # Using sonnet: $3/1M input, $15/1M output
        # $0.77 = input_tokens * 3/1M + output_tokens * 15/1M
        # Assuming equal split: $0.77/2 = $0.385 each
        # input_tokens = 0.385 * 1M / 3 = ~128,333
        tracker.log_usage("SM", "sonnet", 128333, 25667)

        ok, level, msg = tracker.check_budget()
        assert ok is True
        assert level == "warning"
        assert "WARNING" in msg

    def test_check_budget_critical(self, mock_costs_directories):
        """Test budget check at critical level."""
        tracker = CostTracker(story_key="test", budget_limit_usd=1.00)
        # Log usage that costs ~$0.92 (92% of $1)
        tracker.log_usage("SM", "sonnet", 160000, 30667)

        ok, level, msg = tracker.check_budget()
        assert ok is True
        assert level == "critical"
        assert "CRITICAL" in msg

    def test_check_budget_exceeded(self, mock_costs_directories):
        """Test budget check when exceeded."""
        tracker = CostTracker(story_key="test", budget_limit_usd=0.01)
        tracker.log_usage("DEV", "opus", 10000, 5000)

        ok, level, msg = tracker.check_budget()
        assert ok is False
        assert level == "stop"
        assert "EXCEEDED" in msg

    def test_check_budget_no_limit(self, mock_costs_directories):
        """Test budget check with no limit set."""
        tracker = CostTracker(story_key="test", budget_limit_usd=0)
        tracker.log_usage("DEV", "opus", 100000, 50000)

        ok, level, msg = tracker.check_budget()
        assert ok is True
        assert level == "ok"
        assert "No budget limit" in msg

    def test_get_session_summary(self, sample_tracker, sample_entries):
        """Test getting session summary."""
        for entry in sample_entries:
            sample_tracker.log_usage(**entry)

        summary = sample_tracker.get_session_summary()

        assert "session_id" in summary
        assert "story_key" in summary
        assert "totals" in summary
        assert summary["story_key"] == "test-story"
        assert summary["totals"]["total_tokens"] > 0

    def test_save_and_load_session(self, mock_costs_directories, sample_tracker):
        """Test saving and loading session."""
        sample_tracker.log_usage("DEV", "opus", 10000, 5000)
        sample_tracker.save_session()

        # Find the saved file
        sessions_dir = mock_costs_directories / "sessions"
        files = list(sessions_dir.glob("*.json"))
        assert len(files) == 1

        # Load and verify
        loaded = CostTracker.load_session(files[0])
        assert loaded is not None
        assert loaded.story_key == "test-story"
        assert len(loaded.entries) == 1
        assert loaded.entries[0].agent == "DEV"

    def test_end_session(self, sample_tracker):
        """Test ending a session."""
        sample_tracker.log_usage("SM", "sonnet", 5000, 2000)

        result = sample_tracker.end_session()

        assert result["end_time"] is not None
        assert sample_tracker.session.end_time is not None

    def test_custom_thresholds(self, mock_costs_directories):
        """Test custom budget thresholds."""
        custom_thresholds = {
            "warning": 0.50,  # 50%
            "critical": 0.80,  # 80%
            "stop": 0.95,  # 95%
        }
        tracker = CostTracker(story_key="test", budget_limit_usd=1.00, thresholds=custom_thresholds)
        # Log usage at ~55% ($0.55 of $1)
        tracker.log_usage("SM", "sonnet", 90000, 18000)

        ok, level, msg = tracker.check_budget()
        assert level == "warning"  # Should hit custom 50% threshold

    def test_auto_save_disabled(self, mock_costs_directories):
        """Test that auto_save can be disabled."""
        tracker = CostTracker(story_key="test", budget_limit_usd=10.00, auto_save=False)
        tracker.log_usage("DEV", "opus", 10000, 5000)

        sessions_dir = mock_costs_directories / "sessions"
        files = list(sessions_dir.glob("*.json"))
        assert len(files) == 0  # Should not have auto-saved


class TestParseTokenUsage:
    """Tests for parse_token_usage function."""

    def test_parse_total_format(self):
        """Test parsing 'Token usage: X/Y' format returns None (cannot determine split)."""
        output = "Processing complete. Token usage: 45000/200000"
        result = parse_token_usage(output)

        # Total-only format now returns None since we can't accurately determine
        # input/output split. This is intentional - arbitrary 80/20 split was inaccurate.
        assert result is None

    def test_parse_in_out_format(self):
        """Test parsing 'X in / Y out' format."""
        output = "Tokens: 45000 in / 12000 out"
        result = parse_token_usage(output)

        assert result is not None
        assert result == (45000, 12000)

    def test_parse_labeled_format(self):
        """Test parsing 'Input: X, Output: Y' format."""
        output = "Token stats - Input: 30000, Output: 8000"
        result = parse_token_usage(output)

        assert result is not None
        assert result == (30000, 8000)

    def test_parse_no_match(self):
        """Test parsing when no pattern matches."""
        output = "This output has no token information"
        result = parse_token_usage(output)

        assert result is None

    def test_parse_case_insensitive(self):
        """Test case-insensitive parsing."""
        output = "INPUT: 25000, OUTPUT: 5000"
        result = parse_token_usage(output)

        assert result is not None
        assert result == (25000, 5000)


class TestModuleFunctions:
    """Tests for module-level convenience functions."""

    def test_start_tracking(self, mock_costs_directories):
        """Test start_tracking function."""
        tracker = start_tracking("test-story", 25.00)

        assert tracker is not None
        assert tracker.story_key == "test-story"
        assert tracker.budget_limit_usd == 25.00

    def test_get_and_set_tracker(self, sample_tracker):
        """Test get_tracker and set_tracker functions."""
        set_tracker(sample_tracker)
        retrieved = get_tracker()

        assert retrieved is sample_tracker
        assert retrieved.story_key == "test-story"


class TestHistoricalData:
    """Tests for historical session data."""

    def test_get_historical_sessions_empty(self, mock_costs_directories):
        """Test getting historical sessions when none exist."""
        sessions = CostTracker.get_historical_sessions(days=30)
        assert len(sessions) == 0

    def test_get_historical_sessions(self, mock_costs_directories):
        """Test getting historical sessions."""
        # Create a few sessions
        tracker1 = CostTracker(story_key="story-1", budget_limit_usd=10.00)
        tracker1.log_usage("DEV", "opus", 10000, 5000)
        tracker1.end_session()

        tracker2 = CostTracker(story_key="story-2", budget_limit_usd=15.00)
        tracker2.log_usage("SM", "sonnet", 5000, 2000)
        tracker2.end_session()

        sessions = CostTracker.get_historical_sessions(days=30)
        assert len(sessions) == 2

    def test_get_aggregate_stats_empty(self, mock_costs_directories):
        """Test aggregate stats with no sessions."""
        stats = CostTracker.get_aggregate_stats(days=30)

        assert stats["total_sessions"] == 0
        assert stats["total_cost_usd"] == 0
        assert stats["total_tokens"] == 0

    def test_get_aggregate_stats(self, mock_costs_directories):
        """Test aggregate statistics."""
        tracker1 = CostTracker(story_key="story-1", budget_limit_usd=10.00)
        tracker1.log_usage("DEV", "opus", 10000, 5000)
        tracker1.end_session()

        tracker2 = CostTracker(story_key="story-2", budget_limit_usd=15.00)
        tracker2.log_usage("SM", "sonnet", 5000, 2000)
        tracker2.log_usage("DEV", "opus", 3000, 1000)
        tracker2.end_session()

        stats = CostTracker.get_aggregate_stats(days=30)

        assert stats["total_sessions"] == 2
        assert stats["total_cost_usd"] > 0
        assert stats["total_tokens"] > 0
        assert "DEV" in stats["by_agent"]
        assert "SM" in stats["by_agent"]
        assert stats["average_per_session"] > 0


class TestPricingConfiguration:
    """Tests for pricing configuration."""

    def test_all_models_have_pricing(self):
        """Test that all expected models have pricing defined."""
        expected_models = ["opus", "sonnet", "haiku"]
        for model in expected_models:
            assert model in PRICING
            assert "input" in PRICING[model]
            assert "output" in PRICING[model]

    def test_pricing_values_are_positive(self):
        """Test that all pricing values are positive."""
        for model, prices in PRICING.items():
            assert prices["input"] > 0, f"{model} has non-positive input price"
            assert prices["output"] > 0, f"{model} has non-positive output price"

    def test_output_more_expensive_than_input(self):
        """Test that output is more expensive than input (expected for LLMs)."""
        for model, prices in PRICING.items():
            assert prices["output"] >= prices["input"], f"{model} output should cost >= input"


class TestDefaultThresholds:
    """Tests for default threshold configuration."""

    def test_thresholds_are_ordered(self):
        """Test that thresholds are in correct order."""
        assert DEFAULT_THRESHOLDS["warning"] < DEFAULT_THRESHOLDS["critical"]
        assert DEFAULT_THRESHOLDS["critical"] < DEFAULT_THRESHOLDS["stop"]

    def test_thresholds_are_percentages(self):
        """Test that thresholds are valid percentages (0-1)."""
        for name, value in DEFAULT_THRESHOLDS.items():
            assert 0 <= value <= 1, f"{name} threshold should be between 0 and 1"


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_zero_tokens(self, sample_tracker):
        """Test logging zero tokens."""
        entry = sample_tracker.log_usage("SM", "sonnet", 0, 0)
        assert entry.cost_usd == 0

    def test_very_large_tokens(self, sample_tracker):
        """Test with very large token counts."""
        # 100M tokens
        entry = sample_tracker.log_usage("DEV", "opus", 100_000_000, 50_000_000)
        assert entry.cost_usd > 0
        # Opus: $15/1M input, $75/1M output
        # Expected: 100*15 + 50*75 = 1500 + 3750 = 5250
        assert entry.cost_usd == 5250.0

    def test_load_corrupted_session(self, mock_costs_directories):
        """Test loading a corrupted session file."""
        sessions_dir = mock_costs_directories / "sessions"
        bad_file = sessions_dir / "bad_session.json"
        bad_file.write_text("not valid json")

        result = CostTracker.load_session(bad_file)
        assert result is None

    def test_load_missing_session(self, mock_costs_directories):
        """Test loading a non-existent session file."""
        missing_file = mock_costs_directories / "sessions" / "missing.json"
        result = CostTracker.load_session(missing_file)
        assert result is None

    def test_budget_exactly_at_threshold(self, mock_costs_directories):
        """Test budget exactly at threshold boundaries."""
        tracker = CostTracker(story_key="test", budget_limit_usd=1.00)

        # Create an entry that puts us exactly at 75% (warning threshold)
        # Using sonnet: need to calculate precisely
        # $0.75 = cost, use haiku for easier math: $0.80/1M in, $4/1M out
        # For simplicity, mock the entries directly
        entry = CostEntry(
            timestamp=datetime.now().isoformat(),
            agent="SM",
            model="haiku",
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.75,  # Exactly 75%
        )
        tracker.session.entries.append(entry)

        ok, level, msg = tracker.check_budget()
        assert ok is True
        assert level == "warning"
