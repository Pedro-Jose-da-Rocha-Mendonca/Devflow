#!/usr/bin/env python3
"""
Tests for Context Monitor module.

Tests context tracking, status line rendering, threshold detection,
and activity tracking functionality.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add the lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tooling" / "scripts" / "lib"))

from context_monitor import (
    THRESHOLD_CAUTION,
    THRESHOLD_CRITICAL,
    THRESHOLD_EMERGENCY,
    THRESHOLD_SAFE,
    THRESHOLD_WARNING,
    ContextLevel,
    ContextMonitor,
    ContextState,
    StatusLine,
    get_status_manager,
)


class TestContextLevel:
    """Tests for ContextLevel enum."""

    def test_context_level_values(self):
        """Test ContextLevel enum has expected values."""
        assert ContextLevel.SAFE.value == "safe"
        assert ContextLevel.CAUTION.value == "caution"
        assert ContextLevel.WARNING.value == "warning"
        assert ContextLevel.CRITICAL.value == "critical"
        assert ContextLevel.EMERGENCY.value == "emergency"


class TestContextState:
    """Tests for ContextState dataclass."""

    def test_default_state(self):
        """Test default state initialization."""
        state = ContextState(story_key="test-story")
        assert state.story_key == "test-story"
        assert state.model == "sonnet"
        assert state.context_window == 200_000
        assert state.total_input_tokens == 0
        assert state.total_output_tokens == 0
        assert state.estimated_context_tokens == 0

    def test_total_tokens(self):
        """Test total_tokens property."""
        state = ContextState(
            story_key="test", total_input_tokens=10000, total_output_tokens=5000
        )
        assert state.total_tokens == 15000

    def test_context_usage_ratio(self):
        """Test context_usage_ratio calculation."""
        state = ContextState(
            story_key="test",
            context_window=200_000,
            estimated_context_tokens=100_000,
        )
        assert state.context_usage_ratio == 0.5

    def test_context_usage_ratio_zero_window(self):
        """Test context_usage_ratio with zero window."""
        state = ContextState(story_key="test", context_window=0)
        assert state.context_usage_ratio == 0.0

    def test_context_usage_percent(self):
        """Test context_usage_percent calculation."""
        state = ContextState(
            story_key="test",
            context_window=200_000,
            estimated_context_tokens=150_000,
        )
        assert state.context_usage_percent == 75.0

    def test_context_level_safe(self):
        """Test context_level returns SAFE for low usage."""
        state = ContextState(
            story_key="test",
            context_window=200_000,
            estimated_context_tokens=50_000,  # 25%
        )
        assert state.context_level == ContextLevel.SAFE

    def test_context_level_caution(self):
        """Test context_level returns CAUTION at threshold."""
        state = ContextState(
            story_key="test",
            context_window=200_000,
            estimated_context_tokens=140_000,  # 70%
        )
        assert state.context_level == ContextLevel.CAUTION

    def test_context_level_warning(self):
        """Test context_level returns WARNING at threshold."""
        state = ContextState(
            story_key="test",
            context_window=200_000,
            estimated_context_tokens=155_000,  # 77.5%
        )
        assert state.context_level == ContextLevel.WARNING

    def test_context_level_critical(self):
        """Test context_level returns CRITICAL at threshold."""
        state = ContextState(
            story_key="test",
            context_window=200_000,
            estimated_context_tokens=175_000,  # 87.5%
        )
        assert state.context_level == ContextLevel.CRITICAL

    def test_context_level_emergency(self):
        """Test context_level returns EMERGENCY at threshold."""
        state = ContextState(
            story_key="test",
            context_window=200_000,
            estimated_context_tokens=195_000,  # 97.5%
        )
        assert state.context_level == ContextLevel.EMERGENCY

    def test_tokens_remaining(self):
        """Test tokens_remaining calculation."""
        state = ContextState(
            story_key="test",
            context_window=200_000,
            estimated_context_tokens=150_000,
        )
        assert state.tokens_remaining == 50_000

    def test_tokens_remaining_overflow(self):
        """Test tokens_remaining doesn't go negative."""
        state = ContextState(
            story_key="test",
            context_window=200_000,
            estimated_context_tokens=250_000,  # Over limit
        )
        assert state.tokens_remaining == 0

    def test_exchanges_remaining(self):
        """Test exchanges_remaining estimation."""
        state = ContextState(
            story_key="test",
            context_window=200_000,
            estimated_context_tokens=150_000,  # 50K remaining
        )
        # 50K / 5K per exchange = 10 exchanges
        assert state.exchanges_remaining == 10

    def test_activity_tracking_fields(self):
        """Test activity tracking fields exist."""
        state = ContextState(story_key="test")
        assert state.current_agent is None
        assert state.current_task is None
        assert state.current_phase is None
        assert state.phase_start_time is None
        assert state.phases_completed == 0
        assert state.total_phases == 0


class TestContextMonitor:
    """Tests for ContextMonitor class."""

    @pytest.fixture
    def monitor(self, tmp_path):
        """Create a test monitor with temporary storage."""
        return ContextMonitor(story_key="test-story", model="sonnet", state_dir=tmp_path)

    def test_initialization(self, monitor):
        """Test monitor initialization."""
        assert monitor.story_key == "test-story"
        assert monitor.model == "sonnet"
        assert monitor.state.context_window == 200_000

    def test_update_from_tokens(self, monitor):
        """Test updating from token counts."""
        monitor.update_from_tokens(input_tokens=10000, output_tokens=5000)
        assert monitor.state.total_input_tokens == 10000
        assert monitor.state.total_output_tokens == 5000
        assert monitor.state.estimated_context_tokens == 15000

    def test_update_accumulates(self, monitor):
        """Test multiple updates accumulate."""
        monitor.update_from_tokens(input_tokens=10000, output_tokens=5000)
        monitor.update_from_tokens(input_tokens=8000, output_tokens=3000)
        assert monitor.state.total_input_tokens == 18000
        assert monitor.state.total_output_tokens == 8000

    def test_threshold_callback(self, tmp_path):
        """Test threshold callback is triggered."""
        callback = MagicMock()

        monitor = ContextMonitor(
            story_key="test", model="sonnet", on_threshold=callback, state_dir=tmp_path
        )

        # Push to warning threshold
        monitor.update_from_tokens(input_tokens=160_000, output_tokens=0)
        callback.assert_called()
        call_args = callback.call_args[0]
        assert call_args[0] == ContextLevel.WARNING

    def test_record_checkpoint(self, monitor):
        """Test checkpoint recording."""
        monitor.update_from_tokens(input_tokens=100_000, output_tokens=0)
        monitor.record_checkpoint()
        assert monitor.state.checkpoint_count == 1
        assert monitor.state.last_checkpoint_at == 0.5

    def test_reset_context(self, monitor):
        """Test context reset."""
        monitor.update_from_tokens(input_tokens=100_000, output_tokens=50_000)
        monitor.reset_context()
        assert monitor.state.estimated_context_tokens == 0
        assert len(monitor.state.token_history) == 0

    def test_set_current_activity(self, monitor):
        """Test setting current activity."""
        monitor.set_current_activity(
            agent="DEV",
            task="Implementing feature",
            phase="Development",
            phases_completed=1,
            total_phases=3,
        )
        assert monitor.state.current_agent == "DEV"
        assert monitor.state.current_task == "Implementing feature"
        assert monitor.state.current_phase == "Development"
        assert monitor.state.phases_completed == 1
        assert monitor.state.total_phases == 3

    def test_clear_current_activity(self, monitor):
        """Test clearing current activity."""
        monitor.set_current_activity(agent="DEV", task="Working")
        monitor.clear_current_activity()
        assert monitor.state.current_agent is None
        assert monitor.state.current_task is None
        assert monitor.state.current_phase is None

    def test_get_recommendation_safe(self, monitor):
        """Test recommendation for safe level."""
        rec = monitor.get_recommendation()
        assert "healthy" in rec.lower()

    def test_get_recommendation_warning(self, monitor):
        """Test recommendation for warning level."""
        monitor.update_from_tokens(input_tokens=160_000, output_tokens=0)
        rec = monitor.get_recommendation()
        assert "checkpoint" in rec.lower() or "monitor" in rec.lower()

    def test_get_recommendation_critical(self, monitor):
        """Test recommendation for critical level."""
        monitor.update_from_tokens(input_tokens=175_000, output_tokens=0)
        rec = monitor.get_recommendation()
        assert "checkpoint" in rec.lower()

    def test_should_checkpoint(self, monitor):
        """Test should_checkpoint logic."""
        assert not monitor.should_checkpoint()

        # Push to critical
        monitor.update_from_tokens(input_tokens=175_000, output_tokens=0)
        assert monitor.should_checkpoint()

    def test_should_warn(self, monitor):
        """Test should_warn logic."""
        assert not monitor.should_warn()

        # Push to warning
        monitor.update_from_tokens(input_tokens=155_000, output_tokens=0)
        assert monitor.should_warn()


class TestStatusLine:
    """Tests for StatusLine class."""

    @pytest.fixture
    def status_line(self, tmp_path):
        """Create a test status line."""
        monitor = ContextMonitor(story_key="test-story", state_dir=tmp_path)
        return StatusLine(context_monitor=monitor)

    def test_render_basic(self, status_line):
        """Test basic status line rendering."""
        output = status_line.render()
        assert output  # Should produce output
        assert "Ctx:" in output or "Idle" in output

    def test_render_with_activity(self, status_line):
        """Test status line with activity set."""
        status_line.context_monitor.set_current_activity(
            agent="DEV",
            phase="Development",
            phases_completed=1,
            total_phases=3,
        )
        output = status_line.render()
        assert "DEV" in output
        assert "[2/3]" in output  # phases_completed + 1 / total

    def test_render_with_border(self, status_line):
        """Test status line with border."""
        output = status_line.render(include_border=True)
        assert "─" in output

    def test_render_warning_safe(self, status_line):
        """Test no warning at safe level."""
        warning = status_line.render_warning()
        assert warning is None

    def test_render_warning_critical(self, status_line):
        """Test warning at critical level."""
        status_line.context_monitor.update_from_tokens(175_000, 0)
        warning = status_line.render_warning()
        assert warning is not None
        assert "CRITICAL" in warning

    def test_agent_colors(self):
        """Test agent color mapping exists."""
        assert "SM" in StatusLine.AGENT_COLORS
        assert "DEV" in StatusLine.AGENT_COLORS
        assert "REVIEWER" in StatusLine.AGENT_COLORS


class TestThresholds:
    """Tests for threshold constants."""

    def test_threshold_ordering(self):
        """Test thresholds are in correct order."""
        assert THRESHOLD_SAFE < THRESHOLD_CAUTION
        assert THRESHOLD_CAUTION < THRESHOLD_WARNING
        assert THRESHOLD_WARNING < THRESHOLD_CRITICAL
        assert THRESHOLD_CRITICAL < THRESHOLD_EMERGENCY

    def test_threshold_values(self):
        """Test threshold values are reasonable."""
        assert 0.4 <= THRESHOLD_SAFE <= 0.6
        assert 0.6 <= THRESHOLD_CAUTION <= 0.7
        assert 0.7 <= THRESHOLD_WARNING <= 0.8
        assert 0.8 <= THRESHOLD_CRITICAL <= 0.9
        assert 0.9 <= THRESHOLD_EMERGENCY <= 1.0


class TestStatusLineManager:
    """Tests for StatusLineManager singleton."""

    def test_get_status_manager(self, tmp_path):
        """Test getting status manager."""
        # Reset singleton for test
        from context_monitor import StatusLineManager
        StatusLineManager._instance = None

        with patch("context_monitor.CONTEXT_STATE_DIR", tmp_path):
            manager = get_status_manager(story_key="test-story")
            assert manager is not None
            assert manager.story_key == "test-story"

    def test_singleton_pattern(self, tmp_path):
        """Test manager is singleton."""
        # Reset singleton for test
        from context_monitor import StatusLineManager
        StatusLineManager._instance = None

        with patch("context_monitor.CONTEXT_STATE_DIR", tmp_path):
            manager1 = get_status_manager(story_key="story1")
            manager2 = get_status_manager()  # Should return same instance
            assert manager1 is manager2
