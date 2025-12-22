"""
Comprehensive unit tests for pair_programming.py

Tests the pair programming functionality including:
- Data classes (CodeChunk, ReviewFeedback, PairExchange, etc.)
- Feedback parsing
- Chunk parsing
- Session configuration
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

# Ensure imports work
sys.path.insert(0, str(Path(__file__).parent.parent / "tooling" / "scripts" / "lib"))

from lib.pair_programming import (
    ChunkType,
    FeedbackType,
    CodeChunk,
    ReviewFeedback,
    PairExchange,
    PairSessionResult,
    PairConfig,
    PairSession,
)


class TestChunkType:
    """Tests for ChunkType enum."""

    def test_all_chunk_types(self):
        """Test all chunk types are defined."""
        types = [
            ChunkType.DESIGN,
            ChunkType.IMPLEMENTATION,
            ChunkType.TEST,
            ChunkType.REFACTOR,
            ChunkType.FIX,
            ChunkType.DOCUMENTATION,
        ]
        for t in types:
            assert t.value is not None

    def test_chunk_type_values(self):
        """Test chunk type values."""
        assert ChunkType.DESIGN.value == "design"
        assert ChunkType.IMPLEMENTATION.value == "implementation"
        assert ChunkType.TEST.value == "test"


class TestFeedbackType:
    """Tests for FeedbackType enum."""

    def test_all_feedback_types(self):
        """Test all feedback types are defined."""
        types = [
            FeedbackType.APPROVE,
            FeedbackType.MINOR,
            FeedbackType.MAJOR,
            FeedbackType.BLOCKING,
            FeedbackType.QUESTION,
        ]
        for t in types:
            assert t.value is not None

    def test_feedback_type_values(self):
        """Test feedback type values."""
        assert FeedbackType.APPROVE.value == "approve"
        assert FeedbackType.BLOCKING.value == "blocking"


class TestCodeChunk:
    """Tests for CodeChunk dataclass."""

    def test_minimal_chunk(self):
        """Test creating minimal chunk."""
        chunk = CodeChunk(
            chunk_id="chunk_001",
            chunk_type=ChunkType.IMPLEMENTATION,
            description="Test chunk",
            content="def test(): pass"
        )
        assert chunk.chunk_id == "chunk_001"
        assert chunk.file_path is None
        assert chunk.line_range is None

    def test_full_chunk(self):
        """Test creating full chunk."""
        chunk = CodeChunk(
            chunk_id="chunk_002",
            chunk_type=ChunkType.TEST,
            description="Test function",
            content="def test_func(): assert True",
            file_path="tests/test_module.py",
            line_range=(10, 20)
        )
        assert chunk.file_path == "tests/test_module.py"
        assert chunk.line_range == (10, 20)

    def test_chunk_to_dict(self):
        """Test converting chunk to dictionary."""
        chunk = CodeChunk(
            chunk_id="chunk_001",
            chunk_type=ChunkType.IMPLEMENTATION,
            description="Test",
            content="code here"
        )
        result = chunk.to_dict()
        assert isinstance(result, dict)
        assert result["chunk_id"] == "chunk_001"
        assert result["chunk_type"] == "implementation"

    def test_chunk_to_dict_truncates_long_content(self):
        """Test chunk to_dict truncates long content."""
        long_content = "x" * 1000
        chunk = CodeChunk(
            chunk_id="chunk_001",
            chunk_type=ChunkType.IMPLEMENTATION,
            description="Test",
            content=long_content
        )
        result = chunk.to_dict()
        assert len(result["content"]) < 600
        assert result["content"].endswith("...")


class TestReviewFeedback:
    """Tests for ReviewFeedback dataclass."""

    def test_minimal_feedback(self):
        """Test creating minimal feedback."""
        feedback = ReviewFeedback(
            chunk_id="chunk_001",
            feedback_type=FeedbackType.APPROVE,
            comments=["Looks good"]
        )
        assert feedback.chunk_id == "chunk_001"
        assert feedback.approved is False
        assert feedback.must_fix == []

    def test_full_feedback(self):
        """Test creating full feedback."""
        feedback = ReviewFeedback(
            chunk_id="chunk_001",
            feedback_type=FeedbackType.MAJOR,
            comments=["Review comment"],
            suggestions=["Consider X"],
            must_fix=["Fix Y"],
            nice_to_have=["Maybe Z"],
            approved=False
        )
        assert len(feedback.comments) == 1
        assert len(feedback.must_fix) == 1

    def test_feedback_to_dict(self):
        """Test converting feedback to dictionary."""
        feedback = ReviewFeedback(
            chunk_id="chunk_001",
            feedback_type=FeedbackType.MINOR,
            comments=["Minor issue"]
        )
        result = feedback.to_dict()
        assert isinstance(result, dict)
        assert result["feedback_type"] == "minor"

    def test_has_blocking_issues_major(self):
        """Test has_blocking_issues with major feedback."""
        feedback = ReviewFeedback(
            chunk_id="chunk_001",
            feedback_type=FeedbackType.MAJOR,
            comments=["Major issue"]
        )
        assert feedback.has_blocking_issues()

    def test_has_blocking_issues_blocking(self):
        """Test has_blocking_issues with blocking feedback."""
        feedback = ReviewFeedback(
            chunk_id="chunk_001",
            feedback_type=FeedbackType.BLOCKING,
            comments=["Critical issue"]
        )
        assert feedback.has_blocking_issues()

    def test_has_blocking_issues_minor(self):
        """Test has_blocking_issues with minor feedback."""
        feedback = ReviewFeedback(
            chunk_id="chunk_001",
            feedback_type=FeedbackType.MINOR,
            comments=["Small issue"]
        )
        assert not feedback.has_blocking_issues()

    def test_has_blocking_issues_approve(self):
        """Test has_blocking_issues with approve feedback."""
        feedback = ReviewFeedback(
            chunk_id="chunk_001",
            feedback_type=FeedbackType.APPROVE,
            comments=["LGTM"]
        )
        assert not feedback.has_blocking_issues()


class TestPairExchange:
    """Tests for PairExchange dataclass."""

    def test_minimal_exchange(self):
        """Test creating minimal exchange."""
        chunk = CodeChunk(
            chunk_id="chunk_001",
            chunk_type=ChunkType.IMPLEMENTATION,
            description="Test",
            content="code"
        )
        exchange = PairExchange(exchange_id=1, chunk=chunk)
        assert exchange.exchange_id == 1
        assert exchange.feedback is None
        assert not exchange.resolved

    def test_full_exchange(self):
        """Test creating full exchange."""
        chunk = CodeChunk(
            chunk_id="chunk_001",
            chunk_type=ChunkType.IMPLEMENTATION,
            description="Test",
            content="code"
        )
        feedback = ReviewFeedback(
            chunk_id="chunk_001",
            feedback_type=FeedbackType.APPROVE,
            comments=["Good"]
        )
        revision = CodeChunk(
            chunk_id="chunk_001_r1",
            chunk_type=ChunkType.FIX,
            description="Revision",
            content="fixed code"
        )
        exchange = PairExchange(
            exchange_id=1,
            chunk=chunk,
            feedback=feedback,
            revision=revision,
            resolved=True
        )
        assert exchange.resolved
        assert exchange.feedback is not None
        assert exchange.revision is not None

    def test_exchange_to_dict(self):
        """Test converting exchange to dictionary."""
        chunk = CodeChunk(
            chunk_id="chunk_001",
            chunk_type=ChunkType.IMPLEMENTATION,
            description="Test",
            content="code"
        )
        exchange = PairExchange(exchange_id=1, chunk=chunk)
        result = exchange.to_dict()
        assert isinstance(result, dict)
        assert result["exchange_id"] == 1
        assert result["chunk"] is not None


class TestPairSessionResult:
    """Tests for PairSessionResult dataclass."""

    def test_create_result(self):
        """Test creating session result."""
        result = PairSessionResult(
            story_key="test-1",
            task="Implement feature",
            exchanges=[],
            final_code="final implementation",
            files_created=["file1.py"],
            files_modified=["file2.py"],
            total_chunks=5,
            total_revisions=2,
            approval_rate=0.8,
            start_time="2024-12-21T10:00:00",
            end_time="2024-12-21T10:30:00"
        )
        assert result.story_key == "test-1"
        assert result.total_chunks == 5

    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = PairSessionResult(
            story_key="test-1",
            task="Test task",
            exchanges=[],
            final_code="code",
            files_created=[],
            files_modified=[],
            total_chunks=1,
            total_revisions=0,
            approval_rate=1.0,
            start_time="2024-12-21T10:00:00",
            end_time="2024-12-21T10:01:00"
        )
        d = result.to_dict()
        assert d["story_key"] == "test-1"
        assert d["approval_rate"] == 1.0

    def test_result_to_dict_truncates_final_code(self):
        """Test result to_dict truncates long final code."""
        long_code = "x" * 2000
        result = PairSessionResult(
            story_key="test-1",
            task="Test task",
            exchanges=[],
            final_code=long_code,
            files_created=[],
            files_modified=[],
            total_chunks=1,
            total_revisions=0,
            approval_rate=1.0,
            start_time="2024-12-21T10:00:00",
            end_time="2024-12-21T10:01:00"
        )
        d = result.to_dict()
        assert len(d["final_code"]) == 1000

    def test_result_to_summary(self):
        """Test generating summary."""
        result = PairSessionResult(
            story_key="test-1",
            task="Implement feature X",
            exchanges=[],
            final_code="code",
            files_created=["new_file.py"],
            files_modified=["existing.py"],
            total_chunks=5,
            total_revisions=2,
            approval_rate=0.75,
            start_time="2024-12-21T10:00:00",
            end_time="2024-12-21T10:30:00"
        )
        summary = result.to_summary()
        assert "test-1" in summary
        assert "Implement feature X" in summary
        assert "new_file.py" in summary
        assert "existing.py" in summary
        assert "75%" in summary


class TestPairConfig:
    """Tests for PairConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = PairConfig()
        assert config.max_revisions_per_chunk == 3
        assert config.timeout_seconds == 180
        assert config.verbose
        assert config.auto_apply_fixes
        assert config.chunk_size_hint == "medium"
        assert config.reviewer_model == "opus"
        assert config.dev_model == "opus"

    def test_custom_config(self):
        """Test custom configuration."""
        config = PairConfig(
            max_revisions_per_chunk=5,
            timeout_seconds=300,
            verbose=False,
            dev_model="sonnet"
        )
        assert config.max_revisions_per_chunk == 5
        assert config.timeout_seconds == 300
        assert not config.verbose
        assert config.dev_model == "sonnet"

    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = PairConfig(max_revisions_per_chunk=4)
        d = config.to_dict()
        assert d["max_revisions_per_chunk"] == 4
        assert "timeout_seconds" in d


class TestPairSession:
    """Tests for PairSession class."""

    @pytest.fixture
    def mock_dependencies(self):
        """Mock external dependencies."""
        with patch('lib.pair_programming.get_shared_memory') as mock_sm, \
             patch('lib.pair_programming.get_knowledge_graph') as mock_kg:

            mock_sm.return_value = MagicMock()
            mock_kg.return_value = MagicMock()

            yield {
                'shared_memory': mock_sm,
                'knowledge_graph': mock_kg,
            }

    def test_session_creation(self, mock_dependencies):
        """Test creating a session."""
        session = PairSession(story_key="test-1", task="Implement feature")
        assert session.story_key == "test-1"
        assert session.task == "Implement feature"
        assert session.chunk_counter == 0
        assert session.exchange_counter == 0

    def test_session_with_config(self, mock_dependencies):
        """Test creating session with config."""
        config = PairConfig(verbose=False, max_revisions_per_chunk=5)
        session = PairSession(story_key="test-1", task="Task", config=config)
        assert not session.config.verbose
        assert session.config.max_revisions_per_chunk == 5

    def test_generate_chunk_id(self, mock_dependencies):
        """Test generating chunk IDs."""
        session = PairSession(story_key="test-1", task="Task")
        id1 = session._generate_chunk_id()
        id2 = session._generate_chunk_id()
        assert id1 == "chunk_001"
        assert id2 == "chunk_002"

    def test_parse_dev_output_implementation(self, mock_dependencies):
        """Test parsing DEV output as implementation."""
        session = PairSession(story_key="test-1", task="Task")
        
        output = """# Implementing the login function

File: src/auth.py

```python
def login(username, password):
    return authenticate(username, password)
```
"""
        chunk = session._parse_dev_output(output)
        assert chunk.chunk_type == ChunkType.IMPLEMENTATION
        assert chunk.file_path == "src/auth.py"
        assert "login" in chunk.content

    def test_parse_dev_output_test(self, mock_dependencies):
        """Test parsing DEV output as test."""
        session = PairSession(story_key="test-1", task="Task")
        
        output = """# Test for login function

```python
def test_login():
    assert login("user", "pass") == True
```
"""
        chunk = session._parse_dev_output(output)
        assert chunk.chunk_type == ChunkType.TEST

    def test_parse_dev_output_refactor(self, mock_dependencies):
        """Test parsing DEV output as refactor."""
        session = PairSession(story_key="test-1", task="Task")
        
        output = """# Refactoring the authentication module

```python
class AuthService:
    pass
```
"""
        chunk = session._parse_dev_output(output)
        assert chunk.chunk_type == ChunkType.REFACTOR

    def test_parse_dev_output_fix(self, mock_dependencies):
        """Test parsing DEV output as fix."""
        session = PairSession(story_key="test-1", task="Task")
        
        output = """# Bug fix for login error

```python
def login(user, pwd):
    if not user:
        raise ValueError("User required")
```
"""
        chunk = session._parse_dev_output(output)
        assert chunk.chunk_type == ChunkType.FIX

    def test_parse_reviewer_output_approve(self, mock_dependencies):
        """Test parsing REVIEWER output as approve."""
        session = PairSession(story_key="test-1", task="Task")
        
        output = """LGTM! The implementation looks good.
- Clean code
- Good structure
"""
        feedback = session._parse_reviewer_output(output, "chunk_001")
        assert feedback.feedback_type == FeedbackType.APPROVE
        assert feedback.approved

    def test_parse_reviewer_output_blocking(self, mock_dependencies):
        """Test parsing REVIEWER output as blocking."""
        session = PairSession(story_key="test-1", task="Task")
        
        output = """BLOCKING issue found!
Cannot proceed until this is fixed.
- Critical security vulnerability
"""
        feedback = session._parse_reviewer_output(output, "chunk_001")
        assert feedback.feedback_type == FeedbackType.BLOCKING
        assert not feedback.approved

    def test_parse_reviewer_output_major(self, mock_dependencies):
        """Test parsing REVIEWER output as major."""
        session = PairSession(story_key="test-1", task="Task")
        
        output = """Major issues found that must fix:
- Missing error handling
- No input validation
"""
        feedback = session._parse_reviewer_output(output, "chunk_001")
        assert feedback.feedback_type == FeedbackType.MAJOR

    def test_parse_reviewer_output_minor(self, mock_dependencies):
        """Test parsing REVIEWER output as minor."""
        session = PairSession(story_key="test-1", task="Task")
        
        output = """Minor nitpick:
- Could use a better variable name
"""
        feedback = session._parse_reviewer_output(output, "chunk_001")
        assert feedback.feedback_type == FeedbackType.MINOR

    def test_parse_reviewer_output_question(self, mock_dependencies):
        """Test parsing REVIEWER output as question."""
        session = PairSession(story_key="test-1", task="Task")
        
        output = """I have a question about this approach.
Can you clarify why you chose this pattern?
It's unclear to me.
"""
        feedback = session._parse_reviewer_output(output, "chunk_001")
        assert feedback.feedback_type == FeedbackType.QUESTION

    def test_parse_reviewer_extracts_must_fix(self, mock_dependencies):
        """Test extracting must-fix issues."""
        session = PairSession(story_key="test-1", task="Task")
        
        output = """Must fix:
- Add error handling
- Validate inputs
"""
        feedback = session._parse_reviewer_output(output, "chunk_001")
        assert len(feedback.must_fix) >= 1

    def test_log_verbose(self, mock_dependencies, capsys):
        """Test logging in verbose mode."""
        config = PairConfig(verbose=True)
        session = PairSession(story_key="test-1", task="Task", config=config)
        
        session._log("Test message", "DEV")
        captured = capsys.readouterr()
        assert "Test message" in captured.out
        assert "DEV" in captured.out

    def test_log_silent(self, mock_dependencies, capsys):
        """Test logging in silent mode."""
        config = PairConfig(verbose=False)
        session = PairSession(story_key="test-1", task="Task", config=config)
        
        session._log("Test message", "DEV")
        captured = capsys.readouterr()
        assert "Test message" not in captured.out

    def test_build_dev_prompt_initial(self, mock_dependencies):
        """Test building initial DEV prompt."""
        session = PairSession(story_key="test-1", task="Task")
        
        prompt = session._build_dev_prompt(
            task_part="Implement login",
            context="Auth module context",
            previous_feedback=None
        )
        assert "PAIR PROGRAMMING" in prompt
        assert "Implement login" in prompt
        assert "Auth module context" in prompt

    def test_build_dev_prompt_with_feedback(self, mock_dependencies):
        """Test building DEV prompt with feedback."""
        session = PairSession(story_key="test-1", task="Task")
        
        feedback = ReviewFeedback(
            chunk_id="chunk_001",
            feedback_type=FeedbackType.MAJOR,
            comments=["Fix error handling"],
            suggestions=["Use try-except"],
            must_fix=["Add validation"]
        )
        
        prompt = session._build_dev_prompt(
            task_part="Continue implementation",
            context="Context",
            previous_feedback=feedback
        )
        assert "Add validation" in prompt
        assert "Use try-except" in prompt

    def test_build_reviewer_prompt(self, mock_dependencies):
        """Test building REVIEWER prompt."""
        session = PairSession(story_key="test-1", task="Task")
        
        chunk = CodeChunk(
            chunk_id="chunk_001",
            chunk_type=ChunkType.IMPLEMENTATION,
            description="Login function",
            content="def login(): pass",
            file_path="auth.py"
        )
        
        prompt = session._build_reviewer_prompt(
            chunk=chunk,
            accumulated_code="previous code here"
        )
        assert "PAIR PROGRAMMING" in prompt
        assert "Login function" in prompt
        assert "implementation" in prompt
        assert "auth.py" in prompt
