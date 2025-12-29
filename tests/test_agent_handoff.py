"""
Comprehensive unit tests for agent_handoff.py

Tests the agent handoff functionality including:
- Data classes (FileChange, AgentWorkSummary)
- Handoff templates
- Handoff generation
- Context extraction
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure imports work
sys.path.insert(0, str(Path(__file__).parent.parent / "tooling" / "scripts" / "lib"))

from lib.agent_handoff import (
    HANDOFF_TEMPLATES,
    AgentWorkSummary,
    FileChange,
    HandoffGenerator,
)


class TestFileChange:
    """Tests for FileChange dataclass."""

    def test_minimal_file_change(self):
        """Test creating minimal file change."""
        change = FileChange(path="src/app.py", status="modified")
        assert change.path == "src/app.py"
        assert change.status == "modified"
        assert change.additions == 0
        assert change.deletions == 0

    def test_full_file_change(self):
        """Test creating full file change."""
        change = FileChange(path="tests/test_app.py", status="added", additions=50, deletions=10)
        assert change.additions == 50
        assert change.deletions == 10

    def test_file_change_to_dict(self):
        """Test converting file change to dictionary."""
        change = FileChange(path="src/module.py", status="modified", additions=25, deletions=5)
        result = change.to_dict()
        assert isinstance(result, dict)
        assert result["path"] == "src/module.py"
        assert result["status"] == "modified"
        assert result["additions"] == 25
        assert result["deletions"] == 5


class TestAgentWorkSummary:
    """Tests for AgentWorkSummary dataclass."""

    def test_minimal_summary(self):
        """Test creating minimal summary."""
        summary = AgentWorkSummary(
            agent="DEV",
            story_key="test-1",
            start_time="2024-12-21T10:00:00",
            end_time="2024-12-21T11:00:00",
            description="Implemented feature",
        )
        assert summary.agent == "DEV"
        assert summary.story_key == "test-1"
        assert summary.files_changed == []
        assert summary.decisions_made == []

    def test_full_summary(self):
        """Test creating full summary."""
        file_change = FileChange(path="app.py", status="modified")
        summary = AgentWorkSummary(
            agent="DEV",
            story_key="test-1",
            start_time="2024-12-21T10:00:00",
            end_time="2024-12-21T11:00:00",
            description="Implemented feature",
            files_changed=[file_change],
            decisions_made=["Use decorator pattern"],
            blockers_encountered=["Missing API key"],
            blockers_resolved=["Added API key"],
            warnings=["Memory usage high"],
            questions_for_next=["Should we add caching?"],
            artifacts_created=["docs/design.md"],
        )
        assert len(summary.files_changed) == 1
        assert len(summary.decisions_made) == 1
        assert len(summary.blockers_encountered) == 1

    def test_summary_to_dict(self):
        """Test converting summary to dictionary."""
        summary = AgentWorkSummary(
            agent="REVIEWER",
            story_key="test-2",
            start_time="2024-12-21T10:00:00",
            end_time="2024-12-21T10:30:00",
            description="Code review",
        )
        result = summary.to_dict()
        assert isinstance(result, dict)
        assert result["agent"] == "REVIEWER"
        assert result["story_key"] == "test-2"
        assert result["files_changed"] == []

    def test_summary_to_dict_with_files(self):
        """Test summary to_dict includes file changes."""
        file_change = FileChange(path="app.py", status="modified", additions=10)
        summary = AgentWorkSummary(
            agent="DEV",
            story_key="test-1",
            start_time="2024-12-21T10:00:00",
            end_time="2024-12-21T11:00:00",
            description="Work",
            files_changed=[file_change],
        )
        result = summary.to_dict()
        assert len(result["files_changed"]) == 1
        assert result["files_changed"][0]["path"] == "app.py"


class TestHandoffTemplates:
    """Tests for HANDOFF_TEMPLATES."""

    def test_sm_to_dev_template(self):
        """Test SM to DEV handoff template exists."""
        template = HANDOFF_TEMPLATES.get(("SM", "DEV"))
        assert template is not None
        assert "focus_areas" in template
        assert "expected_questions" in template

    def test_dev_to_reviewer_template(self):
        """Test DEV to REVIEWER handoff template exists."""
        template = HANDOFF_TEMPLATES.get(("DEV", "REVIEWER"))
        assert template is not None
        assert len(template["focus_areas"]) > 0

    def test_reviewer_to_dev_template(self):
        """Test REVIEWER to DEV handoff template exists."""
        template = HANDOFF_TEMPLATES.get(("REVIEWER", "DEV"))
        assert template is not None

    def test_architect_to_dev_template(self):
        """Test ARCHITECT to DEV handoff template exists."""
        template = HANDOFF_TEMPLATES.get(("ARCHITECT", "DEV"))
        assert template is not None

    def test_ba_to_dev_template(self):
        """Test BA to DEV handoff template exists."""
        template = HANDOFF_TEMPLATES.get(("BA", "DEV"))
        assert template is not None


class TestHandoffGenerator:
    """Tests for HandoffGenerator class."""

    @pytest.fixture
    def mock_dependencies(self):
        """Mock external dependencies."""
        with (
            patch("lib.agent_handoff.get_knowledge_graph") as mock_kg,
            patch("lib.agent_handoff.get_shared_memory") as mock_sm,
        ):
            mock_kg_instance = MagicMock()
            mock_sm_instance = MagicMock()

            mock_kg.return_value = mock_kg_instance
            mock_sm.return_value = mock_sm_instance

            # Mock knowledge graph methods
            mock_kg_instance.get_decisions_by_agent.return_value = []
            mock_kg_instance.add_handoff.return_value = MagicMock()
            mock_kg_instance.get_latest_handoff.return_value = None
            mock_kg_instance.decisions = {}

            # Mock shared memory methods
            mock_sm_instance.get_recent.return_value = []

            yield {
                "knowledge_graph": mock_kg,
                "shared_memory": mock_sm,
                "kg_instance": mock_kg_instance,
                "sm_instance": mock_sm_instance,
            }

    def test_generator_creation(self, mock_dependencies):
        """Test creating a generator."""
        generator = HandoffGenerator(story_key="test-1")
        assert generator.story_key == "test-1"
        assert generator.project_root is not None

    def test_generator_with_custom_project_root(self, mock_dependencies):
        """Test creating generator with custom project root."""
        custom_root = Path("/custom/path")
        generator = HandoffGenerator(story_key="test-1", project_root=custom_root)
        assert generator.project_root == custom_root

    def test_extract_warnings_from_log(self, mock_dependencies):
        """Test extracting warnings from log content."""
        generator = HandoffGenerator(story_key="test-1")

        log_content = """
        Processing file...
        [WARNING] Memory usage is high
        WARNING: Rate limit approaching
        Note: This is a note
        Done.
        """

        warnings = generator.extract_warnings_from_log(log_content)
        assert len(warnings) >= 2
        assert any("Memory usage" in w for w in warnings)
        assert any("Rate limit" in w for w in warnings)

    def test_extract_warnings_empty_log(self, mock_dependencies):
        """Test extracting warnings from empty log."""
        generator = HandoffGenerator(story_key="test-1")
        warnings = generator.extract_warnings_from_log("")
        assert warnings == []

    def test_extract_warnings_no_warnings(self, mock_dependencies):
        """Test extracting warnings when none present."""
        generator = HandoffGenerator(story_key="test-1")
        log_content = "Everything completed successfully."
        warnings = generator.extract_warnings_from_log(log_content)
        assert len(warnings) == 0

    def test_generate_handoff(self, mock_dependencies):
        """Test generating a handoff."""
        generator = HandoffGenerator(story_key="test-1")

        # Mock the add_handoff to return a proper object
        mock_handoff = MagicMock()
        mock_dependencies["kg_instance"].add_handoff.return_value = mock_handoff

        handoff = generator.generate(
            from_agent="SM", to_agent="DEV", work_summary="Created story context"
        )

        assert handoff is not None
        # Verify add_handoff was called
        mock_dependencies["kg_instance"].add_handoff.assert_called_once()

    def test_generate_handoff_with_files(self, mock_dependencies):
        """Test generating handoff with file changes."""
        generator = HandoffGenerator(story_key="test-1")

        mock_handoff = MagicMock()
        mock_dependencies["kg_instance"].add_handoff.return_value = mock_handoff

        files = [
            FileChange(path="src/app.py", status="modified", additions=50),
            FileChange(path="tests/test_app.py", status="added", additions=100),
        ]

        handoff = generator.generate(
            from_agent="DEV",
            to_agent="REVIEWER",
            work_summary="Implemented feature",
            files_changed=files,
        )

        # Verify files were included
        call_kwargs = mock_dependencies["kg_instance"].add_handoff.call_args[1]
        assert len(call_kwargs["files_touched"]) == 2

    def test_generate_handoff_with_decisions(self, mock_dependencies):
        """Test generating handoff with decisions."""
        generator = HandoffGenerator(story_key="test-1")

        mock_handoff = MagicMock()
        mock_dependencies["kg_instance"].add_handoff.return_value = mock_handoff

        handoff = generator.generate(
            from_agent="ARCHITECT",
            to_agent="DEV",
            work_summary="Designed system",
            decisions_made=["Use microservices", "PostgreSQL for DB"],
        )

        call_kwargs = mock_dependencies["kg_instance"].add_handoff.call_args[1]
        assert len(call_kwargs["key_decisions"]) == 2

    def test_generate_handoff_records_in_shared_memory(self, mock_dependencies):
        """Test handoff is recorded in shared memory."""
        generator = HandoffGenerator(story_key="test-1")

        mock_handoff = MagicMock()
        mock_dependencies["kg_instance"].add_handoff.return_value = mock_handoff

        generator.generate(from_agent="SM", to_agent="DEV", work_summary="Context ready")

        mock_dependencies["sm_instance"].add.assert_called_once()
        call_kwargs = mock_dependencies["sm_instance"].add.call_args[1]
        assert call_kwargs["agent"] == "SM"
        assert "DEV" in call_kwargs["content"]

    def test_generate_next_steps_for_dev(self, mock_dependencies):
        """Test generating next steps for DEV."""
        generator = HandoffGenerator(story_key="test-1")

        files = [FileChange(path="context.md", status="added")]
        steps = generator._generate_next_steps("SM", "DEV", files, {})

        assert len(steps) > 0
        assert any("acceptance criteria" in s.lower() for s in steps)
        assert any("implement" in s.lower() for s in steps)

    def test_generate_next_steps_for_reviewer(self, mock_dependencies):
        """Test generating next steps for REVIEWER."""
        generator = HandoffGenerator(story_key="test-1")

        files = [
            FileChange(path="app.py", status="modified"),
            FileChange(path="test_app.py", status="added"),
        ]
        steps = generator._generate_next_steps("DEV", "REVIEWER", files, {})

        assert len(steps) > 0
        assert any("review" in s.lower() for s in steps)

    def test_generate_next_steps_for_architect(self, mock_dependencies):
        """Test generating next steps for ARCHITECT."""
        generator = HandoffGenerator(story_key="test-1")

        steps = generator._generate_next_steps("SM", "ARCHITECT", [], {})

        assert len(steps) > 0
        assert any("design" in s.lower() or "architect" in s.lower() for s in steps)

    def test_generate_next_steps_for_sm(self, mock_dependencies):
        """Test generating next steps for SM."""
        generator = HandoffGenerator(story_key="test-1")

        steps = generator._generate_next_steps("DEV", "SM", [], {})

        assert len(steps) > 0
        assert any("review" in s.lower() or "status" in s.lower() for s in steps)

    def test_get_latest_handoff_for_agent(self, mock_dependencies):
        """Test getting latest handoff for an agent."""
        generator = HandoffGenerator(story_key="test-1")

        mock_handoff = MagicMock()
        mock_dependencies["kg_instance"].get_latest_handoff.return_value = mock_handoff

        result = generator.get_latest_handoff_for("DEV")

        assert result == mock_handoff
        mock_dependencies["kg_instance"].get_latest_handoff.assert_called_with("DEV")

    def test_generate_context_for_agent(self, mock_dependencies):
        """Test generating context for an agent."""
        generator = HandoffGenerator(story_key="test-1")

        # No handoff, no memory
        mock_dependencies["kg_instance"].get_latest_handoff.return_value = None
        mock_dependencies["sm_instance"].get_recent.return_value = []
        mock_dependencies["kg_instance"].decisions = {}

        context = generator.generate_context_for_agent("DEV")

        assert "Context for DEV" in context

    def test_generate_context_with_handoff(self, mock_dependencies):
        """Test generating context with handoff."""
        generator = HandoffGenerator(story_key="test-1")

        mock_handoff = MagicMock()
        mock_handoff.to_markdown.return_value = "## Handoff content"
        mock_dependencies["kg_instance"].get_latest_handoff.return_value = mock_handoff
        mock_dependencies["sm_instance"].get_recent.return_value = []
        mock_dependencies["kg_instance"].decisions = {}

        context = generator.generate_context_for_agent("DEV")

        assert "Handoff" in context

    def test_generate_context_with_memory(self, mock_dependencies):
        """Test generating context with shared memory."""
        generator = HandoffGenerator(story_key="test-1")

        mock_entry = MagicMock()
        mock_entry.agent = "SM"
        mock_entry.content = "Story ready"

        mock_dependencies["kg_instance"].get_latest_handoff.return_value = None
        mock_dependencies["sm_instance"].get_recent.return_value = [mock_entry]
        mock_dependencies["kg_instance"].decisions = {}

        context = generator.generate_context_for_agent("DEV")

        assert "Team Activity" in context
        assert "SM" in context

    @patch("subprocess.run")
    def test_get_git_changes(self, mock_run, mock_dependencies):
        """Test getting git changes."""
        generator = HandoffGenerator(story_key="test-1")

        mock_run.return_value = MagicMock(stdout="10\t5\tsrc/app.py\n20\t0\ttests/test_app.py\n")

        changes = generator.get_git_changes()

        assert len(changes) == 2
        assert changes[0].path == "src/app.py"
        assert changes[0].additions == 10
        assert changes[0].deletions == 5

    @patch("subprocess.run")
    def test_get_git_changes_with_since(self, mock_run, mock_dependencies):
        """Test getting git changes since specific commit."""
        generator = HandoffGenerator(story_key="test-1")

        mock_run.return_value = MagicMock(stdout="5\t2\tmodule.py\n")

        changes = generator.get_git_changes(since_commit="abc123")

        # Verify git diff was called with the commit
        call_args = mock_run.call_args[0][0]
        assert "abc123" in call_args

    @patch("subprocess.run")
    def test_get_git_changes_error(self, mock_run, mock_dependencies):
        """Test git changes returns empty on error."""
        generator = HandoffGenerator(story_key="test-1")

        mock_run.side_effect = Exception("Git error")

        changes = generator.get_git_changes()
        assert changes == []

    @patch("subprocess.run")
    def test_get_staged_changes(self, mock_run, mock_dependencies):
        """Test getting staged git changes."""
        generator = HandoffGenerator(story_key="test-1")

        mock_run.return_value = MagicMock(stdout="15\t3\tstaged_file.py\n")

        changes = generator.get_staged_changes()

        assert len(changes) == 1
        assert changes[0].path == "staged_file.py"
        assert changes[0].status == "staged"

    @patch("subprocess.run")
    def test_get_staged_changes_error(self, mock_run, mock_dependencies):
        """Test staged changes returns empty on error."""
        generator = HandoffGenerator(story_key="test-1")

        mock_run.side_effect = Exception("Git error")

        changes = generator.get_staged_changes()
        assert changes == []

    def test_extract_decisions_from_memory(self, mock_dependencies):
        """Test extracting decisions from knowledge graph."""
        generator = HandoffGenerator(story_key="test-1")

        mock_decision = MagicMock()
        mock_decision.topic = "Architecture"
        mock_decision.decision = "Use microservices"

        mock_dependencies["kg_instance"].get_decisions_by_agent.return_value = [mock_decision]

        decisions = generator.extract_decisions_from_memory("ARCHITECT")

        assert len(decisions) == 1
        assert "Architecture" in decisions[0]
        assert "microservices" in decisions[0]

    def test_file_change_status_determination(self, mock_dependencies):
        """Test file change status is correctly determined."""
        # Test added (only additions)
        change = FileChange(path="new.py", status="added", additions=50, deletions=0)
        assert change.status == "added"

        # Test deleted (only deletions)
        change = FileChange(path="old.py", status="deleted", additions=0, deletions=30)
        assert change.status == "deleted"

        # Test modified (both)
        change = FileChange(path="updated.py", status="modified", additions=20, deletions=10)
        assert change.status == "modified"
