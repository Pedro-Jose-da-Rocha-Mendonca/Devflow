"""Tests for the collaboration system modules."""

import sys
from pathlib import Path

import pytest

# Add tooling scripts to path for imports
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "tooling" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "tooling" / "scripts" / "lib"))


# ============================================================================
# Shared Memory Tests
# ============================================================================


class TestSharedMemory:
    """Tests for the shared memory system."""

    @pytest.fixture
    def temp_memory_dir(self, tmp_path):
        """Create a temporary directory for memory data."""
        memory_dir = tmp_path / "memory"
        shared_dir = memory_dir / "shared"
        knowledge_dir = memory_dir / "knowledge"
        shared_dir.mkdir(parents=True)
        knowledge_dir.mkdir(parents=True)
        return memory_dir

    @pytest.fixture
    def mock_memory_dirs(self, temp_memory_dir, monkeypatch):
        """Mock the memory directories to use temp directories."""
        from lib import shared_memory

        monkeypatch.setattr(shared_memory, "MEMORY_DIR", temp_memory_dir)
        monkeypatch.setattr(shared_memory, "SHARED_MEMORY_DIR", temp_memory_dir / "shared")
        monkeypatch.setattr(shared_memory, "KNOWLEDGE_GRAPH_DIR", temp_memory_dir / "knowledge")
        return temp_memory_dir

    def test_shared_memory_add_entry(self, mock_memory_dirs):
        """Test adding entries to shared memory."""
        from lib.shared_memory import SharedMemory

        memory = SharedMemory(story_key="test-story")
        entry = memory.add("DEV", "Test learning", tags=["test"])

        assert entry.agent == "DEV"
        assert entry.content == "Test learning"
        assert "test" in entry.tags
        assert entry.id.startswith("mem_")

    def test_shared_memory_search(self, mock_memory_dirs):
        """Test searching shared memory."""
        from lib.shared_memory import SharedMemory

        memory = SharedMemory(story_key="test-story")
        memory.add("DEV", "Implemented user service", tags=["implementation"])
        memory.add("ARCHITECT", "Decided on PostgreSQL", tags=["database", "decision"])
        memory.add("REVIEWER", "Found security issue", tags=["security"])

        # Search by content
        results = memory.search("PostgreSQL")
        assert len(results) == 1
        assert results[0].agent == "ARCHITECT"

        # Search by tag
        results = memory.search("", tags=["security"])
        assert len(results) == 1
        assert results[0].agent == "REVIEWER"

    def test_shared_memory_persistence(self, mock_memory_dirs):
        """Test that shared memory persists to disk."""
        from lib.shared_memory import SharedMemory

        # Create and add entry
        memory1 = SharedMemory(story_key="persist-test")
        memory1.add("DEV", "Persistent entry")

        # Create new instance (should load from disk)
        memory2 = SharedMemory(story_key="persist-test")

        assert len(memory2.entries) == 1
        assert memory2.entries[0].content == "Persistent entry"

    def test_shared_memory_to_context_string(self, mock_memory_dirs):
        """Test generating context string."""
        from lib.shared_memory import SharedMemory

        memory = SharedMemory(story_key="test-story")
        memory.add("DEV", "Entry 1")
        memory.add("REVIEWER", "Entry 2")

        context = memory.to_context_string()

        assert "Shared Team Memory" in context
        assert "DEV" in context
        assert "REVIEWER" in context


class TestKnowledgeGraph:
    """Tests for the knowledge graph."""

    @pytest.fixture
    def temp_knowledge_dir(self, tmp_path):
        """Create a temporary directory for knowledge data."""
        knowledge_dir = tmp_path / "knowledge"
        knowledge_dir.mkdir(parents=True)
        return knowledge_dir

    @pytest.fixture
    def mock_kg_dirs(self, temp_knowledge_dir, monkeypatch):
        """Mock the knowledge graph directories."""
        from lib import shared_memory

        memory_dir = temp_knowledge_dir.parent / "memory"
        memory_dir.mkdir(exist_ok=True)
        (memory_dir / "shared").mkdir(exist_ok=True)
        monkeypatch.setattr(shared_memory, "MEMORY_DIR", memory_dir)
        monkeypatch.setattr(shared_memory, "SHARED_MEMORY_DIR", memory_dir / "shared")
        monkeypatch.setattr(shared_memory, "KNOWLEDGE_GRAPH_DIR", temp_knowledge_dir)
        return temp_knowledge_dir

    def test_add_decision(self, mock_kg_dirs):
        """Test adding a decision to the knowledge graph."""
        from lib.shared_memory import KnowledgeGraph

        kg = KnowledgeGraph(story_key="test-story")
        decision = kg.add_decision(
            agent="ARCHITECT",
            topic="database",
            decision="Use PostgreSQL",
            context={"reason": "ACID compliance"},
        )

        assert decision.agent == "ARCHITECT"
        assert decision.topic == "database"
        assert decision.decision == "Use PostgreSQL"
        assert decision.status == "active"

    def test_query_knowledge(self, mock_kg_dirs):
        """Test querying the knowledge graph."""
        from lib.shared_memory import KnowledgeGraph

        kg = KnowledgeGraph(story_key="test-story")
        kg.add_decision("ARCHITECT", "authentication", "Use JWT tokens")
        kg.add_decision("ARCHITECT", "database", "Use PostgreSQL")

        result = kg.query("What authentication approach was decided?")

        assert result is not None
        assert "JWT" in result["decision"]
        assert result["agent"] == "ARCHITECT"

    def test_supersede_decision(self, mock_kg_dirs):
        """Test superseding a decision."""
        from lib.shared_memory import KnowledgeGraph

        kg = KnowledgeGraph(story_key="test-story")
        old = kg.add_decision("ARCHITECT", "cache", "Use Redis")
        new = kg.add_decision("ARCHITECT", "cache", "Use Memcached", supersedes=old.id)

        assert kg.decisions[old.id].status == "superseded"
        assert kg.decisions[new.id].status == "active"

    def test_add_handoff(self, mock_kg_dirs):
        """Test adding a handoff summary."""
        from lib.shared_memory import KnowledgeGraph

        kg = KnowledgeGraph(story_key="test-story")
        handoff = kg.add_handoff(
            from_agent="SM",
            to_agent="DEV",
            story_key="test-story",
            summary="Story context created",
            key_decisions=["Use existing patterns"],
            watch_out_for=["Rate limiting"],
        )

        assert handoff.from_agent == "SM"
        assert handoff.to_agent == "DEV"
        assert len(handoff.key_decisions) == 1

    def test_handoff_to_markdown(self, mock_kg_dirs):
        """Test converting handoff to markdown."""
        from lib.shared_memory import KnowledgeGraph

        kg = KnowledgeGraph(story_key="test-story")
        handoff = kg.add_handoff(
            from_agent="SM",
            to_agent="DEV",
            story_key="test-story",
            summary="Story ready",
            next_steps=["Implement feature", "Write tests"],
        )

        markdown = handoff.to_markdown()

        assert "## Handoff: SM -> DEV" in markdown
        assert "Story ready" in markdown
        assert "Implement feature" in markdown


# ============================================================================
# Agent Router Tests
# ============================================================================


class TestAgentRouter:
    """Tests for the agent router."""

    def test_analyze_bugfix_task(self):
        """Test analyzing a bugfix task."""
        from lib.agent_router import AgentRouter, TaskType

        router = AgentRouter()
        analysis = router.analyze_task("Fix login authentication bug")

        assert analysis.task_type == TaskType.BUGFIX
        assert len(analysis.detected_patterns) > 0

    def test_analyze_security_task(self):
        """Test analyzing a security-related task."""
        from lib.agent_router import AgentRouter, TaskType

        router = AgentRouter()
        analysis = router.analyze_task("Fix SQL injection vulnerability in user input")

        assert analysis.task_type == TaskType.SECURITY

    def test_analyze_feature_task(self):
        """Test analyzing a feature task."""
        from lib.agent_router import AgentRouter, TaskType

        router = AgentRouter()
        # Use a task description without "profile" which triggers performance detection
        analysis = router.analyze_task("Add user settings page with photo upload")

        # Default to FEATURE if no specific patterns match
        assert analysis.task_type in [TaskType.FEATURE, TaskType.DOCUMENTATION]

    def test_route_simple_bugfix(self):
        """Test routing a simple bugfix."""
        from lib.agent_router import AgentRouter

        router = AgentRouter()
        result = router.route("Fix typo in button label")

        assert "MAINTAINER" in result.agents or "DEV" in result.agents
        assert result.workflow in ["sequential", "single"]

    def test_route_complex_security(self):
        """Test routing a complex security task."""
        from lib.agent_router import AgentRouter

        router = AgentRouter()
        result = router.route("Critical security vulnerability in authentication system")

        assert "SECURITY" in result.agents or "REVIEWER" in result.agents

    def test_force_agents_override(self):
        """Test forcing specific agents."""
        from lib.agent_router import AgentRouter

        router = AgentRouter()
        result = router.route("Any task", force_agents=["DEV", "REVIEWER"])

        assert result.agents == ["DEV", "REVIEWER"]
        assert "Manual agent selection override" in result.reasoning

    def test_explain_routing(self):
        """Test routing explanation generation."""
        from lib.agent_router import AgentRouter

        router = AgentRouter()
        result = router.route("Refactor payment service")
        explanation = router.explain_routing(result)

        assert "Task Analysis" in explanation
        assert "Recommended Agents" in explanation
        assert "Workflow" in explanation


# ============================================================================
# Agent Handoff Tests
# ============================================================================


class TestAgentHandoff:
    """Tests for the agent handoff system."""

    @pytest.fixture
    def mock_handoff_dirs(self, tmp_path, monkeypatch):
        """Mock directories for handoff testing."""
        from lib import shared_memory

        memory_dir = tmp_path / "memory"
        memory_dir.mkdir(parents=True)
        (memory_dir / "shared").mkdir()
        (memory_dir / "knowledge").mkdir()
        monkeypatch.setattr(shared_memory, "MEMORY_DIR", memory_dir)
        monkeypatch.setattr(shared_memory, "SHARED_MEMORY_DIR", memory_dir / "shared")
        monkeypatch.setattr(shared_memory, "KNOWLEDGE_GRAPH_DIR", memory_dir / "knowledge")
        return memory_dir

    def test_generate_handoff(self, mock_handoff_dirs):
        """Test generating a handoff."""
        from lib.agent_handoff import HandoffGenerator

        generator = HandoffGenerator(story_key="test-story")
        handoff = generator.generate(
            from_agent="SM", to_agent="DEV", work_summary="Created story context"
        )

        assert handoff.from_agent == "SM"
        assert handoff.to_agent == "DEV"
        assert "Created story context" in handoff.summary

    def test_work_tracker(self, mock_handoff_dirs):
        """Test work tracking for handoff generation."""
        from lib.agent_handoff import WorkTracker

        tracker = WorkTracker(story_key="test-story", agent="DEV")
        tracker.record_decision("approach", "Use REST API")
        tracker.record_warning("Watch out for rate limits")

        handoff = tracker.generate_handoff("REVIEWER", "Implementation complete")

        assert len(handoff.key_decisions) >= 1
        assert len(handoff.watch_out_for) >= 1

    def test_generate_context_for_agent(self, mock_handoff_dirs):
        """Test context generation for an agent."""
        from lib.agent_handoff import HandoffGenerator, create_handoff

        # Create a handoff first
        create_handoff("SM", "DEV", "test-story", "Ready for development")

        generator = HandoffGenerator(story_key="test-story")
        context = generator.generate_context_for_agent("DEV")

        assert "Context for DEV" in context


# ============================================================================
# Swarm Orchestrator Tests
# ============================================================================


class TestSwarmOrchestrator:
    """Tests for the swarm orchestrator."""

    @pytest.fixture
    def mock_swarm_env(self, tmp_path, monkeypatch):
        """Mock environment for swarm testing."""
        from lib import shared_memory

        memory_dir = tmp_path / "memory"
        memory_dir.mkdir(parents=True)
        (memory_dir / "shared").mkdir()
        (memory_dir / "knowledge").mkdir()
        monkeypatch.setattr(shared_memory, "MEMORY_DIR", memory_dir)
        monkeypatch.setattr(shared_memory, "SHARED_MEMORY_DIR", memory_dir / "shared")
        monkeypatch.setattr(shared_memory, "KNOWLEDGE_GRAPH_DIR", memory_dir / "knowledge")
        return memory_dir

    def test_swarm_config_defaults(self):
        """Test swarm configuration defaults (adversarial mode)."""
        from lib.swarm_orchestrator import ConsensusType, SwarmConfig

        config = SwarmConfig()

        assert config.max_iterations == 3  # Limited rounds for diminishing returns
        assert config.consensus_type == ConsensusType.MAJORITY  # Adversarial default
        assert config.budget_limit_usd == 10.0  # Budget for debate

    def test_swarm_config_custom(self):
        """Test custom swarm configuration."""
        from lib.swarm_orchestrator import ConsensusType, SwarmConfig

        config = SwarmConfig(
            max_iterations=5, consensus_type=ConsensusType.UNANIMOUS, parallel_execution=True
        )

        assert config.max_iterations == 5
        assert config.consensus_type == ConsensusType.UNANIMOUS
        assert config.parallel_execution is True

    def test_extract_issues(self, mock_swarm_env):
        """Test issue extraction from response."""
        from lib.swarm_orchestrator import SwarmOrchestrator

        orchestrator = SwarmOrchestrator("test-story")
        content = """
        Here's my review:
        - Issue: Missing input validation
        -  No error handling for edge cases
        - Problem: Security vulnerability in auth
        """

        issues = orchestrator._extract_issues(content)

        assert len(issues) >= 2

    def test_extract_approvals(self, mock_swarm_env):
        """Test approval extraction from response."""
        from lib.swarm_orchestrator import SwarmOrchestrator

        orchestrator = SwarmOrchestrator("test-story")
        content = """
        LGTM! The implementation looks good.
         Code quality is excellent
        Approved for merge.
        """

        approvals = orchestrator._extract_approvals(content)

        assert len(approvals) >= 1

    def test_determine_vote_approve(self, mock_swarm_env):
        """Test vote determination for approval."""
        from lib.swarm_orchestrator import SwarmOrchestrator

        orchestrator = SwarmOrchestrator("test-story")

        vote = orchestrator._determine_vote("LGTM! Looks good to me.", [], ["approved"])
        assert vote == "approve"

    def test_determine_vote_reject(self, mock_swarm_env):
        """Test vote determination for rejection."""
        from lib.swarm_orchestrator import SwarmOrchestrator

        orchestrator = SwarmOrchestrator("test-story")

        vote = orchestrator._determine_vote(
            "Needs work before merge.", ["Missing tests", "No validation"], []
        )
        assert vote == "reject"

    def test_check_consensus_unanimous(self, mock_swarm_env):
        """Test unanimous consensus check."""
        from lib.swarm_orchestrator import (
            AgentResponse,
            ConsensusType,
            SwarmConfig,
            SwarmOrchestrator,
        )

        config = SwarmConfig(consensus_type=ConsensusType.UNANIMOUS)
        orchestrator = SwarmOrchestrator("test-story", config)

        responses = [
            AgentResponse("DEV", "opus", "", "", 0, vote="approve"),
            AgentResponse("REVIEWER", "opus", "", "", 0, vote="approve"),
        ]

        assert orchestrator._check_consensus(responses) is True

        responses[1].vote = "reject"
        assert orchestrator._check_consensus(responses) is False

    def test_check_consensus_reviewer_approval(self, mock_swarm_env):
        """Test reviewer approval consensus."""
        from lib.swarm_orchestrator import (
            AgentResponse,
            ConsensusType,
            SwarmConfig,
            SwarmOrchestrator,
        )

        config = SwarmConfig(consensus_type=ConsensusType.REVIEWER_APPROVAL)
        orchestrator = SwarmOrchestrator("test-story", config)

        responses = [
            AgentResponse("DEV", "opus", "", "", 0, vote="approve"),
            AgentResponse("REVIEWER", "opus", "", "", 0, vote="approve"),
        ]

        assert orchestrator._check_consensus(responses) is True

        responses[1].vote = "reject"
        assert orchestrator._check_consensus(responses) is False


# ============================================================================
# Integration Tests
# ============================================================================


class TestCollaborationIntegration:
    """Integration tests for the collaboration system."""

    @pytest.fixture
    def mock_full_env(self, tmp_path, monkeypatch):
        """Full mock environment for integration testing."""
        from lib import shared_memory

        memory_dir = tmp_path / "memory"
        memory_dir.mkdir(parents=True)
        (memory_dir / "shared").mkdir()
        (memory_dir / "knowledge").mkdir()
        monkeypatch.setattr(shared_memory, "MEMORY_DIR", memory_dir)
        monkeypatch.setattr(shared_memory, "SHARED_MEMORY_DIR", memory_dir / "shared")
        monkeypatch.setattr(shared_memory, "KNOWLEDGE_GRAPH_DIR", memory_dir / "knowledge")
        return memory_dir

    def test_full_workflow_simulation(self, mock_full_env):
        """Test a simulated full workflow."""
        from lib.agent_handoff import HandoffGenerator
        from lib.agent_router import AgentRouter
        from lib.shared_memory import get_knowledge_graph, get_shared_memory

        story_key = "integration-test"

        # 1. Route the task
        router = AgentRouter()
        result = router.route("Implement user authentication")

        assert len(result.agents) >= 1

        # 2. Create shared memory entries
        memory = get_shared_memory(story_key)
        memory.add("SM", "Story context created", tags=["context"])

        # 3. Record decisions
        kg = get_knowledge_graph(story_key)
        kg.add_decision("ARCHITECT", "auth-method", "Use JWT")

        # 4. Create handoffs
        handoff_gen = HandoffGenerator(story_key)
        handoff = handoff_gen.generate(
            from_agent="SM", to_agent="DEV", work_summary="Ready for implementation"
        )

        # 5. Verify context is available
        context = handoff_gen.generate_context_for_agent("DEV")

        assert "DEV" in context
        assert len(memory.entries) >= 1
        assert len(kg.decisions) >= 1

    def test_knowledge_query_across_agents(self, mock_full_env):
        """Test that knowledge is queryable across agents."""
        from lib.shared_memory import query_knowledge, record_decision

        story_key = "cross-agent-test"

        # Architect makes a decision
        record_decision("ARCHITECT", "database", "Use PostgreSQL", story_key)
        record_decision("ARCHITECT", "cache", "Use Redis", story_key)

        # DEV can query it
        result = query_knowledge("What database was chosen?", story_key)

        assert result is not None
        assert "PostgreSQL" in result["decision"]
        assert result["agent"] == "ARCHITECT"


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
