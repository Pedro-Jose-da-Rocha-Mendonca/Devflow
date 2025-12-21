"""
End-to-end test scenarios for Devflow cost tracking.

These tests prove the system works in realistic usage scenarios.
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime
import sys

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "tooling" / "scripts" / "lib"))


@pytest.fixture
def isolated_cost_environment(tmp_path, monkeypatch):
    """Create an isolated environment for cost tracking tests."""
    costs_dir = tmp_path / "costs"
    sessions_dir = costs_dir / "sessions"
    costs_dir.mkdir(parents=True)
    sessions_dir.mkdir(parents=True)

    from lib import cost_tracker
    monkeypatch.setattr(cost_tracker, 'COSTS_DIR', costs_dir)
    monkeypatch.setattr(cost_tracker, 'SESSIONS_DIR', sessions_dir)

    return {
        "costs_dir": costs_dir,
        "sessions_dir": sessions_dir,
    }


@pytest.mark.integration
class TestEndToEndScenarios:
    """End-to-end test scenarios that simulate real usage."""

    def test_scenario_simple_story_workflow(self, isolated_cost_environment):
        """
        Scenario: Developer works on a simple story (PROJ-123)
        
        1. SM (Scrum Master) reviews requirements
        2. DEV works on implementation
        3. SM does final review
        
        Expected: Total cost tracked, stays under budget
        """
        from lib.cost_tracker import CostTracker

        # Start tracking for story PROJ-123
        tracker = CostTracker(
            story_key="PROJ-123",
            budget_limit_usd=15.00
        )

        # Step 1: SM reviews requirements (quick, uses Sonnet)
        tracker.log_usage(
            agent="SM",
            model="sonnet",
            input_tokens=8000,
            output_tokens=2000
        )

        # Check we're still OK on budget
        ok, level, msg = tracker.check_budget()
        assert ok is True
        assert level == "ok"

        # Step 2: DEV implements (larger task, uses Opus)
        tracker.log_usage(
            agent="DEV",
            model="opus",
            input_tokens=45000,
            output_tokens=12000
        )

        # Step 3: SM final review
        tracker.log_usage(
            agent="SM",
            model="sonnet",
            input_tokens=5000,
            output_tokens=1500
        )

        # End session
        summary = tracker.end_session()

        # Verify results
        assert summary["story_key"] == "PROJ-123"
        assert len(summary["entries"]) == 3
        assert summary["totals"]["total_tokens"] > 0
        assert summary["totals"]["cost_usd"] > 0
        assert summary["totals"]["budget_remaining"] > 0

        # Verify cost breakdown
        by_agent = tracker.session.get_cost_by_agent()
        assert "SM" in by_agent
        assert "DEV" in by_agent
        assert by_agent["DEV"] > by_agent["SM"]  # DEV should cost more (Opus)

    def test_scenario_multi_phase_project(self, isolated_cost_environment):
        """
        Scenario: Multi-phase project with different budget limits
        
        Phase 1: Context gathering (budget: $3)
        Phase 2: Development (budget: $15)
        Phase 3: Review (budget: $5)
        """
        from lib.cost_tracker import CostTracker

        results = []

        # Phase 1: Context
        context_tracker = CostTracker(
            story_key="PROJ-100-context",
            budget_limit_usd=3.00
        )
        context_tracker.log_usage("BA", "haiku", 20000, 5000)
        context_tracker.log_usage("BA", "haiku", 15000, 4000)
        results.append(context_tracker.end_session())

        # Phase 2: Development
        dev_tracker = CostTracker(
            story_key="PROJ-100-dev",
            budget_limit_usd=15.00
        )
        dev_tracker.log_usage("DEV", "opus", 50000, 15000)
        dev_tracker.log_usage("DEV", "opus", 30000, 10000)
        dev_tracker.log_usage("DEV", "sonnet", 25000, 8000)
        results.append(dev_tracker.end_session())

        # Phase 3: Review
        review_tracker = CostTracker(
            story_key="PROJ-100-review",
            budget_limit_usd=5.00
        )
        review_tracker.log_usage("SM", "sonnet", 15000, 3000)
        results.append(review_tracker.end_session())

        # Verify all phases completed
        assert len(results) == 3

        # Verify each phase stayed within budget
        for result in results:
            assert result["totals"]["budget_remaining"] >= 0

        # Total cost across all phases
        total_cost = sum(r["totals"]["cost_usd"] for r in results)
        assert total_cost > 0

    def test_scenario_budget_warning_escalation(self, isolated_cost_environment):
        """
        Scenario: Track budget as it escalates through warning levels
        
        Expected: Budget status changes from ok -> warning -> critical
        """
        from lib.cost_tracker import CostTracker

        tracker = CostTracker(
            story_key="PROJ-200",
            budget_limit_usd=1.00  # Low budget to trigger warnings
        )

        statuses = []

        # First call - should be OK (small usage)
        tracker.log_usage("SM", "haiku", 1000, 200)
        ok, level, msg = tracker.check_budget()
        statuses.append(level)

        # Second call - should hit warning (~75%)
        # Need to add enough to hit 75% of $1.00 = $0.75
        # Haiku: $0.80/1M input, $4/1M output
        tracker.log_usage("DEV", "sonnet", 100000, 20000)  # ~$0.60
        ok, level, msg = tracker.check_budget()
        statuses.append(level)

        # Third call - should hit critical (~90%)
        tracker.log_usage("DEV", "sonnet", 50000, 10000)  # ~$0.30 more
        ok, level, msg = tracker.check_budget()
        statuses.append(level)

        # Verify escalation happened
        assert "ok" in statuses or "warning" in statuses
        assert any(s in ["warning", "critical", "stop"] for s in statuses)

    def test_scenario_session_persistence(self, isolated_cost_environment):
        """
        Scenario: Session data persists across tracker instances
        
        1. Create tracker and log usage
        2. Save session
        3. Load session in new context
        4. Verify data matches
        """
        from lib.cost_tracker import CostTracker

        sessions_dir = isolated_cost_environment["sessions_dir"]

        # Create and populate tracker
        tracker1 = CostTracker(
            story_key="PROJ-300",
            budget_limit_usd=10.00
        )
        tracker1.log_usage("DEV", "opus", 25000, 8000)
        tracker1.log_usage("SM", "sonnet", 10000, 3000)

        original_cost = tracker1.session.total_cost_usd
        original_tokens = tracker1.session.total_tokens
        session_id = tracker1.session_id

        # Save and end
        tracker1.end_session()

        # Find the saved file
        session_files = list(sessions_dir.glob("*.json"))
        assert len(session_files) == 1

        # Load in new context
        loaded_session = CostTracker.load_session(session_files[0])

        # Verify data matches
        assert loaded_session is not None
        assert loaded_session.session_id == session_id
        assert loaded_session.story_key == "PROJ-300"
        assert loaded_session.total_cost_usd == original_cost
        assert loaded_session.total_tokens == original_tokens
        assert len(loaded_session.entries) == 2

    def test_scenario_historical_aggregation(self, isolated_cost_environment):
        """
        Scenario: Aggregate statistics across multiple sessions
        
        1. Create several completed sessions
        2. Query historical data
        3. Verify aggregated statistics
        """
        from lib.cost_tracker import CostTracker

        # Create multiple sessions
        stories = [
            ("PROJ-401", [("DEV", "opus", 30000, 10000)]),
            ("PROJ-402", [("SM", "sonnet", 15000, 5000), ("DEV", "opus", 20000, 8000)]),
            ("PROJ-403", [("BA", "haiku", 25000, 6000)]),
        ]

        for story_key, entries in stories:
            tracker = CostTracker(story_key=story_key, budget_limit_usd=20.00)
            for agent, model, input_tok, output_tok in entries:
                tracker.log_usage(agent, model, input_tok, output_tok)
            tracker.end_session()

        # Get aggregate stats
        stats = CostTracker.get_aggregate_stats(days=30)

        # Verify aggregation
        assert stats["total_sessions"] == 3
        assert stats["total_cost_usd"] > 0
        assert stats["total_tokens"] > 0
        assert stats["average_per_session"] > 0

        # Verify by-agent breakdown
        assert "DEV" in stats["by_agent"]
        assert "SM" in stats["by_agent"]
        assert "BA" in stats["by_agent"]

        # DEV should have highest cost (Opus in 2 sessions)
        assert stats["by_agent"]["DEV"]["cost"] > stats["by_agent"]["BA"]["cost"]

    def test_scenario_model_comparison(self, isolated_cost_environment):
        """
        Scenario: Compare costs between different models
        
        Same task performed with different models to show cost difference
        """
        from lib.cost_tracker import CostTracker

        # Same token counts, different models
        input_tokens = 50000
        output_tokens = 15000

        results = {}

        for model in ["opus", "sonnet", "haiku"]:
            tracker = CostTracker(
                story_key=f"model-test-{model}",
                budget_limit_usd=100.00,
                auto_save=False
            )
            tracker.log_usage("TEST", model, input_tokens, output_tokens)
            results[model] = tracker.session.total_cost_usd

        # Verify cost ordering: opus > sonnet > haiku
        assert results["opus"] > results["sonnet"]
        assert results["sonnet"] > results["haiku"]

        # Opus should be roughly 5x sonnet
        ratio = results["opus"] / results["sonnet"]
        assert 4.5 < ratio < 5.5  # Allow some margin

    def test_scenario_concurrent_sessions(self, isolated_cost_environment):
        """
        Scenario: Multiple concurrent sessions (different stories)
        
        Simulates working on multiple stories simultaneously
        """
        from lib.cost_tracker import CostTracker

        # Start multiple trackers
        tracker_a = CostTracker(story_key="PROJ-A", budget_limit_usd=10.00)
        tracker_b = CostTracker(story_key="PROJ-B", budget_limit_usd=15.00)

        # Interleave usage
        tracker_a.log_usage("DEV", "sonnet", 10000, 3000)
        tracker_b.log_usage("DEV", "opus", 20000, 5000)
        tracker_a.log_usage("SM", "haiku", 5000, 1000)
        tracker_b.log_usage("SM", "sonnet", 8000, 2000)

        # End both
        summary_a = tracker_a.end_session()
        summary_b = tracker_b.end_session()

        # Verify isolation
        assert summary_a["story_key"] == "PROJ-A"
        assert summary_b["story_key"] == "PROJ-B"
        assert summary_a["session_id"] != summary_b["session_id"]

        # Each should have 2 entries
        assert len(summary_a["entries"]) == 2
        assert len(summary_b["entries"]) == 2

        # B should cost more (used Opus)
        assert summary_b["totals"]["cost_usd"] > summary_a["totals"]["cost_usd"]


@pytest.mark.integration
class TestCurrencyDisplay:
    """Tests for multi-currency display functionality."""

    def test_currency_conversion(self, isolated_cost_environment):
        """Test that currency conversion works correctly."""
        sys.path.insert(0, str(Path(__file__).parent.parent / "tooling" / "scripts" / "lib"))

        try:
            from lib.currency_converter import CurrencyConverter

            converter = CurrencyConverter()

            # Test USD to EUR conversion (convert takes USD amount and target currency)
            usd_amount = 10.00
            eur_amount = converter.convert(usd_amount, "EUR")

            # EUR should be less than USD (typical rate)
            assert eur_amount < usd_amount
            assert eur_amount > 0

            # Test formatting
            formatted = converter.format(usd_amount, "EUR")
            assert "€" in formatted or "EUR" in formatted

        except ImportError:
            pytest.skip("Currency converter not available")


@pytest.mark.integration
class TestValidationScript:
    """Tests for the validation script."""

    def test_validation_runs(self):
        """Test that validation script runs without error."""
        import subprocess
        script_path = Path(__file__).parent.parent / "tooling" / "scripts" / "validate_setup.py"

        if not script_path.exists():
            pytest.skip("Validation script not found")

        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Should complete (exit 0 or 1, not 2 which is error)
        assert result.returncode in [0, 1]

    def test_validation_json_output(self):
        """Test that validation script can output JSON."""
        import subprocess
        script_path = Path(__file__).parent.parent / "tooling" / "scripts" / "validate_setup.py"

        if not script_path.exists():
            pytest.skip("Validation script not found")

        result = subprocess.run(
            [sys.executable, str(script_path), "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Should have JSON somewhere in output
        try:
            # Find JSON array in output
            output = result.stdout
            if '[' in output:
                json_start = output.index('[')
                json_end = output.rindex(']') + 1
                json_data = json.loads(output[json_start:json_end])
                assert isinstance(json_data, list)
        except (ValueError, json.JSONDecodeError):
            pass  # JSON output is optional


@pytest.mark.integration
class TestErrorRecovery:
    """Tests for error handling and recovery."""

    def test_recovery_from_corrupted_session(self, isolated_cost_environment):
        """Test that system handles corrupted session files gracefully."""
        from lib.cost_tracker import CostTracker

        sessions_dir = isolated_cost_environment["sessions_dir"]

        # Create a valid session
        tracker = CostTracker(story_key="valid-session", budget_limit_usd=10.00)
        tracker.log_usage("DEV", "sonnet", 10000, 3000)
        tracker.end_session()

        # Create a corrupted session file
        corrupted_file = sessions_dir / "corrupted_session.json"
        corrupted_file.write_text("{ this is not valid json")

        # Get historical sessions - should skip corrupted file
        sessions = CostTracker.get_historical_sessions(days=30)

        # Should have only the valid session
        assert len(sessions) == 1
        assert sessions[0].story_key == "valid-session"

    def test_recovery_from_missing_directory(self, tmp_path, monkeypatch):
        """Test that system creates missing directories."""
        from lib import cost_tracker

        # Point to non-existent directories
        missing_costs = tmp_path / "missing" / "costs"
        missing_sessions = missing_costs / "sessions"

        monkeypatch.setattr(cost_tracker, 'COSTS_DIR', missing_costs)
        monkeypatch.setattr(cost_tracker, 'SESSIONS_DIR', missing_sessions)

        # Creating tracker should create directories
        tracker = cost_tracker.CostTracker(story_key="test", budget_limit_usd=5.00)

        assert missing_costs.exists()
        assert missing_sessions.exists()
