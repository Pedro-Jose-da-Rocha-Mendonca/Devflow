"""Pytest configuration and fixtures."""

import sys
from datetime import datetime
from pathlib import Path

import pytest

# Add tooling scripts to path for imports
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "tooling" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "tooling" / "scripts" / "lib"))


@pytest.fixture
def temp_costs_dir(tmp_path):
    """Create a temporary directory for cost tracking data."""
    costs_dir = tmp_path / "costs"
    sessions_dir = costs_dir / "sessions"
    costs_dir.mkdir(parents=True)
    sessions_dir.mkdir(parents=True)
    return costs_dir


@pytest.fixture
def mock_costs_directories(temp_costs_dir, monkeypatch):
    """Mock the COSTS_DIR and SESSIONS_DIR to use temp directories."""
    from lib import cost_tracker

    monkeypatch.setattr(cost_tracker, "COSTS_DIR", temp_costs_dir)
    monkeypatch.setattr(cost_tracker, "SESSIONS_DIR", temp_costs_dir / "sessions")
    return temp_costs_dir


@pytest.fixture
def sample_tracker(mock_costs_directories):
    """Create a sample CostTracker with mocked directories."""
    from lib.cost_tracker import CostTracker

    return CostTracker(story_key="test-story", budget_limit_usd=10.00)


@pytest.fixture
def sample_entries():
    """Sample usage data for testing."""
    return [
        {"agent": "SM", "model": "sonnet", "input_tokens": 15000, "output_tokens": 3000},
        {"agent": "DEV", "model": "opus", "input_tokens": 50000, "output_tokens": 15000},
        {"agent": "SM", "model": "sonnet", "input_tokens": 10000, "output_tokens": 2000},
        {"agent": "BA", "model": "haiku", "input_tokens": 5000, "output_tokens": 1000},
    ]


@pytest.fixture
def fixed_datetime():
    """Fixture for mocking datetime."""
    return datetime(2024, 12, 21, 10, 30, 0)
