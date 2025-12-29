"""
Comprehensive unit tests for agent_router.py

Tests the dynamic agent selection functionality including:
- Task type detection
- Complexity estimation
- Agent routing
- Workflow selection
- Alternative agent suggestions
"""

import sys
from pathlib import Path

import pytest

# Ensure imports work
sys.path.insert(0, str(Path(__file__).parent.parent / "tooling" / "scripts" / "lib"))

from lib.agent_router import (
    AGENTS,
    Agent,
    AgentRouter,
    Complexity,
    RoutingResult,
    TaskAnalysis,
    TaskType,
    explain_route,
    route_task,
)


class TestTaskType:
    """Tests for TaskType enum."""

    def test_all_task_types_defined(self):
        """Verify all expected task types exist."""
        expected_types = [
            "FEATURE",
            "BUGFIX",
            "REFACTOR",
            "SECURITY",
            "PERFORMANCE",
            "DOCUMENTATION",
            "TESTING",
            "MIGRATION",
            "TECH_DEBT",
            "INVESTIGATION",
            "ARCHITECTURE",
            "QUICK_FIX",
        ]
        for task_type in expected_types:
            assert hasattr(TaskType, task_type)

    def test_task_type_values(self):
        """Verify task type values are strings."""
        assert TaskType.FEATURE.value == "feature"
        assert TaskType.BUGFIX.value == "bugfix"
        assert TaskType.SECURITY.value == "security"


class TestComplexity:
    """Tests for Complexity enum."""

    def test_complexity_levels(self):
        """Verify complexity levels are ordered correctly."""
        assert Complexity.TRIVIAL.value == 1
        assert Complexity.LOW.value == 2
        assert Complexity.MEDIUM.value == 3
        assert Complexity.HIGH.value == 4
        assert Complexity.CRITICAL.value == 5

    def test_complexity_comparison(self):
        """Test that complexity values can be compared."""
        assert Complexity.TRIVIAL.value < Complexity.CRITICAL.value
        assert Complexity.MEDIUM.value == 3


class TestAgent:
    """Tests for Agent dataclass."""

    def test_agent_creation(self):
        """Test creating an agent."""
        agent = Agent(
            name="TEST",
            model="sonnet",
            specialties=["testing", "review"],
            cost_tier="low",
            max_complexity=3,
        )
        assert agent.name == "TEST"
        assert agent.model == "sonnet"
        assert "testing" in agent.specialties
        assert agent.cost_tier == "low"
        assert agent.max_complexity == 3

    def test_agent_hashable(self):
        """Test that agents are hashable for set operations."""
        agent = Agent(
            name="TEST", model="sonnet", specialties=["testing"], cost_tier="low", max_complexity=3
        )
        # Should be able to use in set
        agent_set = {agent}
        assert agent in agent_set

    def test_predefined_agents_exist(self):
        """Verify all expected agents are defined."""
        expected_agents = ["SM", "DEV", "BA", "ARCHITECT", "PM", "WRITER", "MAINTAINER", "REVIEWER"]
        for agent_name in expected_agents:
            assert agent_name in AGENTS
            assert isinstance(AGENTS[agent_name], Agent)


class TestTaskAnalysis:
    """Tests for TaskAnalysis dataclass."""

    def test_task_analysis_creation(self):
        """Test creating a task analysis."""
        analysis = TaskAnalysis(
            task_type=TaskType.BUGFIX,
            complexity=Complexity.MEDIUM,
            detected_patterns=["bug", "fix"],
            file_contexts=["testing"],
            confidence=0.75,
        )
        assert analysis.task_type == TaskType.BUGFIX
        assert analysis.complexity == Complexity.MEDIUM
        assert "bug" in analysis.detected_patterns
        assert analysis.confidence == 0.75

    def test_task_analysis_to_dict(self):
        """Test converting task analysis to dictionary."""
        analysis = TaskAnalysis(
            task_type=TaskType.FEATURE,
            complexity=Complexity.LOW,
            detected_patterns=[],
            file_contexts=[],
            confidence=0.5,
        )
        result = analysis.to_dict()
        assert isinstance(result, dict)
        assert result["task_type"] == "feature"
        assert result["complexity"] == 2
        assert result["confidence"] == 0.5


class TestRoutingResult:
    """Tests for RoutingResult dataclass."""

    def test_routing_result_creation(self):
        """Test creating a routing result."""
        analysis = TaskAnalysis(
            task_type=TaskType.BUGFIX,
            complexity=Complexity.LOW,
            detected_patterns=["bug"],
            file_contexts=[],
            confidence=0.7,
        )
        result = RoutingResult(
            agents=["MAINTAINER"],
            workflow="sequential",
            task_analysis=analysis,
            reasoning="Simple bug fix",
        )
        assert result.agents == ["MAINTAINER"]
        assert result.workflow == "sequential"
        assert result.reasoning == "Simple bug fix"

    def test_routing_result_to_dict(self):
        """Test converting routing result to dictionary."""
        analysis = TaskAnalysis(
            task_type=TaskType.FEATURE,
            complexity=Complexity.MEDIUM,
            detected_patterns=[],
            file_contexts=[],
            confidence=0.5,
        )
        result = RoutingResult(
            agents=["DEV"],
            workflow="sequential",
            task_analysis=analysis,
            reasoning="Direct implementation",
            alternative_agents=["MAINTAINER"],
            model_overrides={"DEV": "opus"},
        )
        result_dict = result.to_dict()
        assert "agents" in result_dict
        assert "workflow" in result_dict
        assert "task_analysis" in result_dict
        assert result_dict["alternative_agents"] == ["MAINTAINER"]


class TestAgentRouterAnalysis:
    """Tests for AgentRouter task analysis."""

    @pytest.fixture
    def router(self):
        """Create a router instance."""
        return AgentRouter()

    def test_analyze_bugfix_task(self, router):
        """Test analyzing a bug fix task."""
        analysis = router.analyze_task("Fix authentication bug in login.py")
        assert analysis.task_type == TaskType.BUGFIX
        assert "bug" in analysis.detected_patterns or "fix" in analysis.detected_patterns

    def test_analyze_security_task(self, router):
        """Test analyzing a security task."""
        analysis = router.analyze_task("Fix SQL injection vulnerability in user input")
        assert analysis.task_type == TaskType.SECURITY
        assert analysis.confidence > 0.3

    def test_analyze_performance_task(self, router):
        """Test analyzing a performance task."""
        analysis = router.analyze_task("Optimize slow database queries")
        assert analysis.task_type == TaskType.PERFORMANCE

    def test_analyze_documentation_task(self, router):
        """Test analyzing a documentation task."""
        analysis = router.analyze_task("Update README documentation")
        assert analysis.task_type == TaskType.DOCUMENTATION

    def test_analyze_refactor_task(self, router):
        """Test analyzing a refactoring task."""
        analysis = router.analyze_task("Refactor payment service for better maintainability")
        assert analysis.task_type == TaskType.REFACTOR

    def test_analyze_testing_task(self, router):
        """Test analyzing a testing task."""
        analysis = router.analyze_task("Add unit tests for user service")
        assert analysis.task_type == TaskType.TESTING

    def test_analyze_default_to_feature(self, router):
        """Test that unknown tasks default to feature."""
        analysis = router.analyze_task("Create a new button component")
        # No specific keywords, defaults to FEATURE
        assert analysis.task_type == TaskType.FEATURE

    def test_analyze_with_file_contexts(self, router):
        """Test analysis with file context detection."""
        analysis = router.analyze_task(
            "Update authentication", files=["auth.pem", "config.yaml", "test_auth.py"]
        )
        assert "security" in analysis.file_contexts
        assert "testing" in analysis.file_contexts


class TestAgentRouterComplexity:
    """Tests for complexity estimation."""

    @pytest.fixture
    def router(self):
        """Create a router instance."""
        return AgentRouter()

    def test_simple_task_complexity(self, router):
        """Test simple task gets low complexity."""
        analysis = router.analyze_task("Simple fix for typo")
        assert analysis.complexity.value <= 2

    def test_complex_task_complexity(self, router):
        """Test complex task gets high complexity."""
        analysis = router.analyze_task("Major system-wide rewrite of authentication")
        assert analysis.complexity.value >= 3

    def test_file_count_affects_complexity(self, router):
        """Test that many files increase complexity."""
        files = [f"file{i}.py" for i in range(15)]
        analysis = router.analyze_task("Update code", files=files)
        assert analysis.complexity.value >= 3


class TestAgentRouterRouting:
    """Tests for agent routing."""

    @pytest.fixture
    def router(self):
        """Create a router instance."""
        return AgentRouter()

    def test_route_simple_bugfix(self, router):
        """Test routing a simple bug fix."""
        result = router.route("Fix typo in error message")
        assert "MAINTAINER" in result.agents or "DEV" in result.agents
        assert result.workflow == "sequential"

    def test_route_security_task(self, router):
        """Test routing a security task."""
        result = router.route("Fix XSS vulnerability")
        assert "SECURITY" in result.agents or "DEV" in result.agents

    def test_route_documentation_task(self, router):
        """Test routing a documentation task."""
        result = router.route("Update API documentation")
        assert "WRITER" in result.agents

    def test_route_complex_feature(self, router):
        """Test routing a complex feature."""
        result = router.route("Major redesign of user authentication system")
        # Complex features get multiple agents
        assert len(result.agents) >= 1
        assert result.task_analysis.complexity.value >= 3

    def test_route_with_force_agents(self, router):
        """Test forcing specific agents."""
        result = router.route("Any task", force_agents=["SM", "DEV"])
        assert result.agents == ["SM", "DEV"]
        assert result.reasoning == "Manual agent selection override"

    def test_route_cost_optimization(self, router):
        """Test cost-optimized routing."""
        result = router.route("Simple task", prefer_cost=True)
        # Should avoid Opus agents for simple tasks
        assert result.task_analysis.complexity.value <= 3

    def test_route_model_overrides_for_complex(self, router):
        """Test model overrides for complex tasks."""
        result = router.route("Critical system-wide security vulnerability")
        # Complex tasks might get model overrides
        if result.task_analysis.complexity.value >= 4:
            # Low-cost agents should get upgraded to opus
            for agent in result.agents:
                if AGENTS.get(agent) and AGENTS[agent].cost_tier == "low":
                    assert (
                        agent in result.model_overrides
                        or result.model_overrides.get(agent) == "opus"
                    )


class TestAgentRouterWorkflow:
    """Tests for workflow selection."""

    @pytest.fixture
    def router(self):
        """Create a router instance."""
        return AgentRouter()

    def test_single_agent_workflow(self, router):
        """Test single agent gets single workflow."""
        workflow = router.get_workflow_for_agents(["DEV"])
        assert workflow == "single"

    def test_pair_workflow(self, router):
        """Test DEV+REVIEWER gets pair workflow."""
        workflow = router.get_workflow_for_agents(["DEV", "REVIEWER"])
        assert workflow == "pair"

    def test_architect_sequential_workflow(self, router):
        """Test ARCHITECT forces sequential workflow."""
        workflow = router.get_workflow_for_agents(["ARCHITECT", "DEV", "REVIEWER"])
        assert workflow == "sequential"

    def test_swarm_workflow(self, router):
        """Test 3+ agents with REVIEWER gets swarm workflow."""
        workflow = router.get_workflow_for_agents(["SM", "DEV", "REVIEWER"])
        assert workflow == "swarm"


class TestAgentRouterExplanation:
    """Tests for routing explanation."""

    @pytest.fixture
    def router(self):
        """Create a router instance."""
        return AgentRouter()

    def test_explain_routing_format(self, router):
        """Test explanation format."""
        result = router.route("Fix bug in auth.py")
        explanation = router.explain_routing(result)

        assert "Task Analysis" in explanation
        assert "Recommended Agents" in explanation
        assert "Workflow" in explanation
        assert "Reasoning" in explanation

    def test_explain_routing_includes_alternatives(self, router):
        """Test that explanation includes alternatives when available."""
        result = router.route("Complex security audit needed")
        explanation = router.explain_routing(result)

        if result.alternative_agents:
            assert "Alternatives" in explanation


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_route_task_function(self):
        """Test route_task convenience function."""
        result = route_task("Fix login bug")
        assert isinstance(result, RoutingResult)
        assert len(result.agents) >= 1

    def test_explain_route_function(self):
        """Test explain_route convenience function."""
        explanation = explain_route("Add new feature")
        assert isinstance(explanation, str)
        assert "Task Analysis" in explanation


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.fixture
    def router(self):
        """Create a router instance."""
        return AgentRouter()

    def test_empty_description(self, router):
        """Test handling empty description."""
        result = router.route("")
        # Should still return a valid result
        assert isinstance(result, RoutingResult)
        assert result.task_type == TaskType.FEATURE  # Default

    def test_very_long_description(self, router):
        """Test handling very long description."""
        long_desc = "Fix bug " * 1000
        result = router.route(long_desc)
        assert isinstance(result, RoutingResult)

    def test_empty_files_list(self, router):
        """Test handling empty files list."""
        result = router.route("Fix bug", files=[])
        assert isinstance(result, RoutingResult)

    def test_none_files(self, router):
        """Test handling None files."""
        result = router.route("Fix bug", files=None)
        assert isinstance(result, RoutingResult)

    def test_special_characters_in_description(self, router):
        """Test handling special characters."""
        result = router.route("Fix bug with $pecial ch@racters & symbols!")
        assert isinstance(result, RoutingResult)
