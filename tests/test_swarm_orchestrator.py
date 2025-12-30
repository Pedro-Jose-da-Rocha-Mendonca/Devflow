"""
Comprehensive unit tests for swarm_orchestrator.py

Tests the swarm orchestration functionality including:
- Data classes (AgentResponse, SwarmIteration, SwarmResult, SwarmConfig)
- Consensus mechanisms
- Issue/approval/suggestion extraction
- Vote determination
- Cost estimation
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure imports work
sys.path.insert(0, str(Path(__file__).parent.parent / "tooling" / "scripts" / "lib"))

from lib.swarm_orchestrator import (
    AgentResponse,
    ConsensusType,
    SwarmConfig,
    SwarmIteration,
    SwarmOrchestrator,
    SwarmResult,
    SwarmState,
)


class TestSwarmState:
    """Tests for SwarmState enum."""

    def test_all_states_defined(self):
        """Test all swarm states are defined."""
        states = [
            SwarmState.INITIALIZING,
            SwarmState.RUNNING,
            SwarmState.DEBATING,
            SwarmState.CONVERGING,
            SwarmState.CONSENSUS,
            SwarmState.COMPLETED,
            SwarmState.FAILED,
            SwarmState.MAX_ITERATIONS,
        ]
        for state in states:
            assert state.value is not None

    def test_state_values(self):
        """Test state values are strings."""
        assert SwarmState.INITIALIZING.value == "initializing"
        assert SwarmState.COMPLETED.value == "completed"


class TestConsensusType:
    """Tests for ConsensusType enum."""

    def test_all_consensus_types(self):
        """Test all consensus types are defined."""
        types = [
            ConsensusType.UNANIMOUS,
            ConsensusType.MAJORITY,
            ConsensusType.QUORUM,
            ConsensusType.REVIEWER_APPROVAL,
        ]
        for t in types:
            assert t.value is not None

    def test_consensus_values(self):
        """Test consensus type values."""
        assert ConsensusType.UNANIMOUS.value == "unanimous"
        assert ConsensusType.MAJORITY.value == "majority"


class TestAgentResponse:
    """Tests for AgentResponse dataclass."""

    def test_minimal_response(self):
        """Test creating minimal response."""
        response = AgentResponse(
            agent="DEV",
            model="opus",
            content="Test content",
            timestamp="2024-12-21T10:00:00",
            iteration=0,
        )
        assert response.agent == "DEV"
        assert response.model == "opus"
        assert response.tokens_used == 0
        assert response.vote is None
        assert response.issues_found == []

    def test_full_response(self):
        """Test creating full response."""
        response = AgentResponse(
            agent="REVIEWER",
            model="opus",
            content="Review content",
            timestamp="2024-12-21T10:00:00",
            iteration=1,
            tokens_used=500,
            cost_usd=0.05,
            issues_found=["Issue 1", "Issue 2"],
            approvals=["LGTM"],
            suggestions=["Consider X"],
            vote="approve",
        )
        assert response.tokens_used == 500
        assert response.vote == "approve"
        assert len(response.issues_found) == 2

    def test_response_to_dict(self):
        """Test converting response to dictionary."""
        response = AgentResponse(
            agent="DEV",
            model="opus",
            content="Test content",
            timestamp="2024-12-21T10:00:00",
            iteration=0,
            vote="approve",
        )
        result = response.to_dict()
        assert isinstance(result, dict)
        assert result["agent"] == "DEV"
        assert result["vote"] == "approve"

    def test_response_to_dict_truncates_long_content(self):
        """Test that to_dict truncates long content."""
        long_content = "x" * 1000
        response = AgentResponse(
            agent="DEV",
            model="opus",
            content=long_content,
            timestamp="2024-12-21T10:00:00",
            iteration=0,
        )
        result = response.to_dict()
        assert len(result["content"]) < 600
        assert result["content"].endswith("...")


class TestSwarmIteration:
    """Tests for SwarmIteration dataclass."""

    def test_empty_iteration(self):
        """Test creating empty iteration."""
        iteration = SwarmIteration(iteration_num=0)
        assert iteration.iteration_num == 0
        assert iteration.responses == []
        assert not iteration.consensus_reached

    def test_iteration_with_responses(self):
        """Test iteration with responses."""
        response = AgentResponse(
            agent="DEV",
            model="opus",
            content="Content",
            timestamp="2024-12-21T10:00:00",
            iteration=0,
        )
        iteration = SwarmIteration(
            iteration_num=1,
            responses=[response],
            consensus_reached=True,
            issues_remaining=["Issue"],
            decisions_made=["DEV: approve"],
        )
        assert len(iteration.responses) == 1
        assert iteration.consensus_reached

    def test_iteration_to_dict(self):
        """Test converting iteration to dictionary."""
        iteration = SwarmIteration(
            iteration_num=0, consensus_reached=False, issues_remaining=["Issue 1"]
        )
        result = iteration.to_dict()
        assert isinstance(result, dict)
        assert result["iteration_num"] == 0
        assert "Issue 1" in result["issues_remaining"]


class TestSwarmResult:
    """Tests for SwarmResult dataclass."""

    def test_create_result(self):
        """Test creating swarm result."""
        result = SwarmResult(
            story_key="test-1",
            task="Test task",
            state=SwarmState.COMPLETED,
            iterations=[],
            final_output="Final output",
            agents_involved=["DEV", "REVIEWER"],
            total_tokens=1000,
            total_cost_usd=0.10,
            start_time="2024-12-21T10:00:00",
            end_time="2024-12-21T10:05:00",
            consensus_type=ConsensusType.MAJORITY,
        )
        assert result.story_key == "test-1"
        assert result.state == SwarmState.COMPLETED

    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = SwarmResult(
            story_key="test-1",
            task="Test task",
            state=SwarmState.CONSENSUS,
            iterations=[],
            final_output="Done",
            agents_involved=["DEV"],
            total_tokens=500,
            total_cost_usd=0.05,
            start_time="2024-12-21T10:00:00",
            end_time="2024-12-21T10:01:00",
            consensus_type=ConsensusType.UNANIMOUS,
        )
        d = result.to_dict()
        assert d["state"] == "consensus"
        assert d["consensus_type"] == "unanimous"

    def test_result_to_summary(self):
        """Test generating summary."""
        result = SwarmResult(
            story_key="test-1",
            task="Test task",
            state=SwarmState.CONSENSUS,
            iterations=[],
            final_output="Implementation complete",
            agents_involved=["DEV", "REVIEWER"],
            total_tokens=1000,
            total_cost_usd=0.15,
            start_time="2024-12-21T10:00:00",
            end_time="2024-12-21T10:05:00",
            consensus_type=ConsensusType.REVIEWER_APPROVAL,
        )
        summary = result.to_summary()
        assert "test-1" in summary
        assert "[CONSENSUS]" in summary  # Adversarial format
        assert "consensus" in summary.lower()

    def test_result_summary_max_iterations(self):
        """Test summary for max iterations state."""
        result = SwarmResult(
            story_key="test-1",
            task="Test task",
            state=SwarmState.MAX_ITERATIONS,
            iterations=[],
            final_output="Partial output",
            agents_involved=["DEV"],
            total_tokens=1000,
            total_cost_usd=0.10,
            start_time="2024-12-21T10:00:00",
            end_time="2024-12-21T10:05:00",
            consensus_type=ConsensusType.MAJORITY,
        )
        summary = result.to_summary()
        assert "[MAX ROUNDS]" in summary  # Adversarial format


class TestSwarmConfig:
    """Tests for SwarmConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values (adversarial mode)."""
        config = SwarmConfig()
        assert config.max_iterations == 3  # Limited rounds for diminishing returns
        assert config.consensus_type == ConsensusType.MAJORITY  # Adversarial default
        assert config.quorum_size == 2
        assert config.timeout_seconds == 300
        assert not config.parallel_execution
        assert config.auto_fix_enabled
        assert config.verbose

    def test_custom_config(self):
        """Test custom configuration."""
        config = SwarmConfig(
            max_iterations=5,
            consensus_type=ConsensusType.UNANIMOUS,
            parallel_execution=True,
            budget_limit_usd=50.0,
        )
        assert config.max_iterations == 5
        assert config.consensus_type == ConsensusType.UNANIMOUS
        assert config.parallel_execution
        assert config.budget_limit_usd == 50.0

    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = SwarmConfig(max_iterations=4)
        d = config.to_dict()
        assert d["max_iterations"] == 4
        assert "consensus_type" in d


class TestSwarmOrchestrator:
    """Tests for SwarmOrchestrator class."""

    @pytest.fixture
    def mock_dependencies(self):
        """Mock external dependencies."""
        with (
            patch("lib.swarm_orchestrator.get_shared_memory") as mock_sm,
            patch("lib.swarm_orchestrator.get_knowledge_graph") as mock_kg,
            patch("lib.swarm_orchestrator.HandoffGenerator") as mock_hg,
            patch("lib.swarm_orchestrator.AgentRouter") as mock_router,
        ):
            mock_sm.return_value = MagicMock()
            mock_kg.return_value = MagicMock()
            mock_hg.return_value = MagicMock()
            mock_hg.return_value.generate_context_for_agent.return_value = "Context"
            mock_router.return_value = MagicMock()

            yield {
                "shared_memory": mock_sm,
                "knowledge_graph": mock_kg,
                "handoff_generator": mock_hg,
                "router": mock_router,
            }

    def test_orchestrator_creation(self, mock_dependencies):
        """Test creating orchestrator."""
        orchestrator = SwarmOrchestrator(story_key="test-1")
        assert orchestrator.story_key == "test-1"
        assert orchestrator.state == SwarmState.INITIALIZING
        assert orchestrator.total_tokens == 0
        assert orchestrator.total_cost == 0.0

    def test_orchestrator_with_config(self, mock_dependencies):
        """Test creating orchestrator with config."""
        config = SwarmConfig(max_iterations=5, verbose=False)
        orchestrator = SwarmOrchestrator(story_key="test-1", config=config)
        assert orchestrator.config.max_iterations == 5
        assert not orchestrator.config.verbose

    def test_agent_models_mapping(self, mock_dependencies):
        """Test agent to model mapping."""
        orchestrator = SwarmOrchestrator(story_key="test-1")
        assert orchestrator.agent_models["DEV"] == "opus"
        assert orchestrator.agent_models["SM"] == "sonnet"
        assert orchestrator.agent_models["REVIEWER"] == "opus"
        assert orchestrator.agent_models["ARCHITECT"] == "sonnet"

    def test_extract_issues(self, mock_dependencies):
        """Test extracting issues from content."""
        orchestrator = SwarmOrchestrator(story_key="test-1")

        content = """
        Here are some issues:
        Issue: Missing error handling
         No input validation
        [ISSUE] Memory leak detected
        - Problem: Race condition
        """
        issues = orchestrator._extract_issues(content)
        assert len(issues) > 0
        assert any("error handling" in issue.lower() for issue in issues)

    def test_extract_approvals(self, mock_dependencies):
        """Test extracting approvals from content."""
        orchestrator = SwarmOrchestrator(story_key="test-1")

        content = """
        LGTM! This looks good.
         Well implemented
        [APPROVED] Ready to merge
        """
        approvals = orchestrator._extract_approvals(content)
        assert len(approvals) > 0

    def test_extract_suggestions(self, mock_dependencies):
        """Test extracting suggestions from content."""
        orchestrator = SwarmOrchestrator(story_key="test-1")

        content = """
        Suggest: Use async/await
         Consider caching
        [SUGGESTION] Add more tests
        """
        suggestions = orchestrator._extract_suggestions(content)
        assert len(suggestions) > 0

    def test_determine_vote_approve(self, mock_dependencies):
        """Test determining approve vote."""
        orchestrator = SwarmOrchestrator(story_key="test-1")

        vote = orchestrator._determine_vote(
            "LGTM! Approved for merge.", issues=[], approvals=["Approved"]
        )
        assert vote == "approve"

    def test_determine_vote_reject(self, mock_dependencies):
        """Test determining reject vote."""
        orchestrator = SwarmOrchestrator(story_key="test-1")

        vote = orchestrator._determine_vote(
            "This needs work. Do not merge.", issues=["Issue 1", "Issue 2"], approvals=[]
        )
        assert vote == "reject"

    def test_determine_vote_abstain(self, mock_dependencies):
        """Test determining abstain vote."""
        orchestrator = SwarmOrchestrator(story_key="test-1")

        vote = orchestrator._determine_vote("Some observations here.", issues=[], approvals=[])
        assert vote == "abstain"

    def test_estimate_cost_opus(self, mock_dependencies):
        """Test cost estimation for opus model."""
        orchestrator = SwarmOrchestrator(story_key="test-1")
        cost = orchestrator._estimate_cost(1000, "opus")
        assert cost > 0

    def test_estimate_cost_sonnet(self, mock_dependencies):
        """Test cost estimation for sonnet model."""
        orchestrator = SwarmOrchestrator(story_key="test-1")
        cost = orchestrator._estimate_cost(1000, "sonnet")
        assert cost > 0
        # Sonnet should be cheaper than opus
        opus_cost = orchestrator._estimate_cost(1000, "opus")
        assert cost < opus_cost

    def test_estimate_cost_haiku(self, mock_dependencies):
        """Test cost estimation for haiku model."""
        orchestrator = SwarmOrchestrator(story_key="test-1")
        cost = orchestrator._estimate_cost(1000, "haiku")
        assert cost > 0
        # Haiku should be cheapest
        sonnet_cost = orchestrator._estimate_cost(1000, "sonnet")
        assert cost < sonnet_cost

    def test_check_consensus_unanimous(self, mock_dependencies):
        """Test unanimous consensus check."""
        config = SwarmConfig(consensus_type=ConsensusType.UNANIMOUS)
        orchestrator = SwarmOrchestrator(story_key="test-1", config=config)

        responses = [
            AgentResponse(
                agent="DEV", model="opus", content="", timestamp="", iteration=0, vote="approve"
            ),
            AgentResponse(
                agent="REVIEWER",
                model="opus",
                content="",
                timestamp="",
                iteration=0,
                vote="approve",
            ),
        ]
        assert orchestrator._check_consensus(responses)

        responses[1].vote = "reject"
        assert not orchestrator._check_consensus(responses)

    def test_check_consensus_majority(self, mock_dependencies):
        """Test majority consensus check."""
        config = SwarmConfig(consensus_type=ConsensusType.MAJORITY)
        orchestrator = SwarmOrchestrator(story_key="test-1", config=config)

        responses = [
            AgentResponse(
                agent="DEV", model="opus", content="", timestamp="", iteration=0, vote="approve"
            ),
            AgentResponse(
                agent="REVIEWER",
                model="opus",
                content="",
                timestamp="",
                iteration=0,
                vote="approve",
            ),
            AgentResponse(
                agent="ARCHITECT",
                model="sonnet",
                content="",
                timestamp="",
                iteration=0,
                vote="reject",
            ),
        ]
        assert orchestrator._check_consensus(responses)

    def test_check_consensus_quorum(self, mock_dependencies):
        """Test quorum consensus check."""
        config = SwarmConfig(consensus_type=ConsensusType.QUORUM, quorum_size=2)
        orchestrator = SwarmOrchestrator(story_key="test-1", config=config)

        responses = [
            AgentResponse(
                agent="DEV", model="opus", content="", timestamp="", iteration=0, vote="approve"
            ),
            AgentResponse(
                agent="REVIEWER",
                model="opus",
                content="",
                timestamp="",
                iteration=0,
                vote="approve",
            ),
            AgentResponse(
                agent="ARCHITECT",
                model="sonnet",
                content="",
                timestamp="",
                iteration=0,
                vote="reject",
            ),
        ]
        assert orchestrator._check_consensus(responses)

    def test_check_consensus_reviewer_approval(self, mock_dependencies):
        """Test reviewer approval consensus check."""
        config = SwarmConfig(consensus_type=ConsensusType.REVIEWER_APPROVAL)
        orchestrator = SwarmOrchestrator(story_key="test-1", config=config)

        responses = [
            AgentResponse(
                agent="DEV", model="opus", content="", timestamp="", iteration=0, vote="approve"
            ),
            AgentResponse(
                agent="REVIEWER",
                model="opus",
                content="",
                timestamp="",
                iteration=0,
                vote="approve",
            ),
        ]
        assert orchestrator._check_consensus(responses)

        responses[1].vote = "reject"
        assert not orchestrator._check_consensus(responses)

    def test_check_consensus_no_votes(self, mock_dependencies):
        """Test consensus with no votes."""
        orchestrator = SwarmOrchestrator(story_key="test-1")
        responses = [
            AgentResponse(
                agent="DEV", model="opus", content="", timestamp="", iteration=0, vote=None
            ),
        ]
        assert not orchestrator._check_consensus(responses)

    def test_collect_issues(self, mock_dependencies):
        """Test collecting issues from responses."""
        orchestrator = SwarmOrchestrator(story_key="test-1")

        responses = [
            AgentResponse(
                agent="DEV",
                model="opus",
                content="",
                timestamp="",
                iteration=0,
                issues_found=["Issue 1", "Issue 2"],
            ),
            AgentResponse(
                agent="REVIEWER",
                model="opus",
                content="",
                timestamp="",
                iteration=0,
                issues_found=["Issue 2", "Issue 3"],
            ),
        ]
        issues = orchestrator._collect_issues(responses)
        assert len(issues) == 3  # Unique issues
        assert "Issue 1" in issues
        assert "Issue 3" in issues

    def test_build_iteration_prompt_first(self, mock_dependencies):
        """Test building prompt for first iteration."""
        orchestrator = SwarmOrchestrator(story_key="test-1")

        prompt = orchestrator._build_iteration_prompt(
            agent="DEV",
            task="Implement feature X",
            iteration=0,
            previous_responses=[],
            issues_to_fix=[],
        )
        assert "DEV" in prompt
        assert "Implement feature X" in prompt
        assert "APPROVE" in prompt or "approve" in prompt.lower()

    def test_build_iteration_prompt_subsequent(self, mock_dependencies):
        """Test building prompt for subsequent iteration."""
        orchestrator = SwarmOrchestrator(story_key="test-1")

        previous_responses = [
            AgentResponse(
                agent="REVIEWER",
                model="opus",
                content="",
                timestamp="",
                iteration=0,
                issues_found=["Missing tests"],
                suggestions=["Add unit tests"],
            )
        ]

        prompt = orchestrator._build_iteration_prompt(
            agent="DEV",
            task="Implement feature X",
            iteration=1,
            previous_responses=previous_responses,
            issues_to_fix=["Missing tests"],
        )
        assert "DEV" in prompt
        assert "round 2" in prompt.lower()  # Adversarial uses "round" instead of "iteration"
        assert "Missing tests" in prompt
        assert "REVIEWER" in prompt  # Shows other agent's position

    def test_log_verbose(self, mock_dependencies, capsys):
        """Test logging in verbose mode."""
        config = SwarmConfig(verbose=True)
        orchestrator = SwarmOrchestrator(story_key="test-1", config=config)

        orchestrator._log("Test message", "INFO")
        captured = capsys.readouterr()
        assert "Test message" in captured.out

    def test_log_silent(self, mock_dependencies, capsys):
        """Test logging in silent mode."""
        config = SwarmConfig(verbose=False)
        orchestrator = SwarmOrchestrator(story_key="test-1", config=config)

        orchestrator._log("Test message", "INFO")
        captured = capsys.readouterr()
        assert "Test message" not in captured.out
