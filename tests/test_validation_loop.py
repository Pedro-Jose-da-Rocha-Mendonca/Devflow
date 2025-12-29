#!/usr/bin/env python3
"""
Unit tests for validation_loop.py

Tests the three-tier validation system:
- Validation gates
- Loop context
- Validation results
- Gate execution
"""

import sys
from pathlib import Path
from unittest.mock import patch

# Add lib directory for imports
TESTS_DIR = Path(__file__).parent
PROJECT_ROOT = TESTS_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "tooling" / "scripts" / "lib"))

from validation_loop import (
    ALL_GATES,
    INTER_PHASE_GATES,
    POST_COMPLETION_GATES,
    PREFLIGHT_GATES,
    FailureAction,
    GateResult,
    LoopContext,
    ValidationGate,
    ValidationLoop,
    ValidationMemory,
    ValidationReport,
    ValidationResult,
)


class TestValidationResult:
    """Tests for ValidationResult enum."""

    def test_result_values(self):
        """Test validation result values."""
        assert ValidationResult.PASS.value == "pass"
        assert ValidationResult.WARN.value == "warn"
        assert ValidationResult.FAIL.value == "fail"
        assert ValidationResult.SKIP.value == "skip"
        assert ValidationResult.ERROR.value == "error"


class TestFailureAction:
    """Tests for FailureAction enum."""

    def test_action_values(self):
        """Test failure action values."""
        assert FailureAction.BLOCK.value == "block"
        assert FailureAction.WARN.value == "warn"
        assert FailureAction.RETRY.value == "retry"
        assert FailureAction.ESCALATE.value == "escalate"


class TestValidationGate:
    """Tests for ValidationGate dataclass."""

    def test_gate_creation(self):
        """Test creating a validation gate."""
        gate = ValidationGate(
            name="test_gate",
            validator=lambda ctx: True,
            description="Test gate",
            on_fail=FailureAction.WARN,
        )
        assert gate.name == "test_gate"
        assert gate.description == "Test gate"
        assert gate.on_fail == FailureAction.WARN
        assert gate.max_retries == 3
        assert gate.tier == 2

    def test_gate_string_on_fail(self):
        """Test that string on_fail is converted to FailureAction."""
        gate = ValidationGate(
            name="test_gate",
            validator=lambda ctx: True,
            on_fail="block",
        )
        assert gate.on_fail == FailureAction.BLOCK


class TestLoopContext:
    """Tests for LoopContext dataclass."""

    def test_context_creation(self):
        """Test creating a loop context."""
        ctx = LoopContext(
            story_key="test-story",
            iteration=1,
            max_iterations=3,
        )
        assert ctx.story_key == "test-story"
        assert ctx.iteration == 1
        assert ctx.max_iterations == 3
        assert ctx.accumulated_issues == []
        assert ctx.cost_so_far == 0.0

    def test_context_to_dict(self):
        """Test context serialization."""
        ctx = LoopContext(
            story_key="test-story",
            phase="preflight",
        )
        d = ctx.to_dict()
        assert d["story_key"] == "test-story"
        assert d["phase"] == "preflight"


class TestGateResult:
    """Tests for GateResult dataclass."""

    def test_result_creation(self):
        """Test creating a gate result."""
        result = GateResult(
            gate_name="test_gate",
            result=ValidationResult.PASS,
            message="Test passed",
            duration_ms=100.0,
        )
        assert result.gate_name == "test_gate"
        assert result.result == ValidationResult.PASS
        assert result.duration_ms == 100.0

    def test_result_to_dict(self):
        """Test result serialization."""
        result = GateResult(
            gate_name="test_gate",
            result=ValidationResult.FAIL,
            message="Test failed",
        )
        d = result.to_dict()
        assert d["gate_name"] == "test_gate"
        assert d["result"] == "fail"
        assert d["message"] == "Test failed"


class TestValidationReport:
    """Tests for ValidationReport dataclass."""

    def test_report_passed(self):
        """Test report with passing results."""
        gate_results = [
            GateResult("gate1", ValidationResult.PASS, "OK"),
            GateResult("gate2", ValidationResult.PASS, "OK"),
        ]
        report = ValidationReport(
            id="test_report",
            timestamp="2024-01-01T00:00:00",
            story_key="test-story",
            tier=1,
            gate_results=gate_results,
            overall_result=ValidationResult.PASS,
            total_duration_ms=200.0,
        )
        assert report.passed is True
        assert report.failed is False
        assert len(report.failures) == 0

    def test_report_failed(self):
        """Test report with failing results."""
        gate_results = [
            GateResult("gate1", ValidationResult.PASS, "OK"),
            GateResult("gate2", ValidationResult.FAIL, "Failed"),
        ]
        report = ValidationReport(
            id="test_report",
            timestamp="2024-01-01T00:00:00",
            story_key="test-story",
            tier=1,
            gate_results=gate_results,
            overall_result=ValidationResult.FAIL,
            total_duration_ms=200.0,
        )
        assert report.passed is False
        assert report.failed is True
        assert len(report.failures) == 1

    def test_report_warnings(self):
        """Test report with warnings."""
        gate_results = [
            GateResult("gate1", ValidationResult.PASS, "OK"),
            GateResult("gate2", ValidationResult.WARN, "Warning"),
        ]
        report = ValidationReport(
            id="test_report",
            timestamp="2024-01-01T00:00:00",
            story_key="test-story",
            tier=1,
            gate_results=gate_results,
            overall_result=ValidationResult.WARN,
            total_duration_ms=200.0,
        )
        assert report.passed is True
        assert len(report.warnings) == 1

    def test_report_to_summary(self):
        """Test report summary generation."""
        gate_results = [
            GateResult("gate1", ValidationResult.PASS, "OK"),
        ]
        report = ValidationReport(
            id="test_report",
            timestamp="2024-01-01T00:00:00",
            story_key="test-story",
            tier=1,
            gate_results=gate_results,
            overall_result=ValidationResult.PASS,
            total_duration_ms=200.0,
        )
        summary = report.to_summary()
        assert "PASS" in summary
        assert "test-story" in summary


class TestValidationLoop:
    """Tests for ValidationLoop class."""

    def test_loop_creation(self):
        """Test creating a validation loop."""
        gates = [
            ValidationGate("test", lambda ctx: True),
        ]
        loop = ValidationLoop(gates, story_key="test")
        assert len(loop.gates) == 1
        assert loop.story_key == "test"

    def test_run_passing_gate(self):
        """Test running a gate that passes."""
        gate = ValidationGate("passing", lambda ctx: True)
        loop = ValidationLoop([gate], story_key="test")
        ctx = LoopContext(story_key="test")

        result = loop.run_gate(gate, ctx)
        assert result.result == ValidationResult.PASS

    def test_run_failing_gate(self):
        """Test running a gate that fails."""
        gate = ValidationGate("failing", lambda ctx: False)
        loop = ValidationLoop([gate], story_key="test")
        ctx = LoopContext(story_key="test")

        result = loop.run_gate(gate, ctx)
        assert result.result == ValidationResult.FAIL

    def test_run_error_gate(self):
        """Test running a gate that raises an exception."""

        def error_validator(ctx):
            raise ValueError("Test error")

        gate = ValidationGate("error", error_validator)
        loop = ValidationLoop([gate], story_key="test")
        ctx = LoopContext(story_key="test")

        result = loop.run_gate(gate, ctx)
        assert result.result == ValidationResult.ERROR

    def test_run_gates_all_pass(self):
        """Test running all gates with all passing."""
        gates = [
            ValidationGate("gate1", lambda ctx: True, tier=1),
            ValidationGate("gate2", lambda ctx: True, tier=1),
        ]
        loop = ValidationLoop(gates, story_key="test")
        ctx = LoopContext(story_key="test")

        report = loop.run_gates(ctx, tier=1)
        assert report.passed is True
        assert report.overall_result == ValidationResult.PASS

    def test_run_gates_with_failure(self):
        """Test running gates with one failure."""
        gates = [
            ValidationGate("pass", lambda ctx: True, tier=1),
            ValidationGate("fail", lambda ctx: False, tier=1, on_fail=FailureAction.WARN),
        ]
        loop = ValidationLoop(gates, story_key="test")
        ctx = LoopContext(story_key="test")

        report = loop.run_gates(ctx, tier=1)
        assert report.overall_result == ValidationResult.FAIL

    def test_run_gates_blocking(self):
        """Test that blocking failure stops execution."""
        call_count = {"value": 0}

        def counting_validator(ctx):
            call_count["value"] += 1
            return False

        gates = [
            ValidationGate("block", counting_validator, tier=1, on_fail=FailureAction.BLOCK),
            ValidationGate("skip", counting_validator, tier=1),
        ]
        loop = ValidationLoop(gates, story_key="test")
        ctx = LoopContext(story_key="test")

        loop.run_gates(ctx, tier=1)
        # Only first gate should be called due to blocking
        assert call_count["value"] == 1

    def test_run_preflight(self):
        """Test running pre-flight validation."""
        gates = [ValidationGate("test", lambda ctx: True, tier=1)]
        loop = ValidationLoop(gates, story_key="test")
        ctx = LoopContext(story_key="test")

        report = loop.run_preflight(ctx)
        assert report.tier == 1

    def test_run_post_completion(self):
        """Test running post-completion validation."""
        gates = [ValidationGate("test", lambda ctx: True, tier=3)]
        loop = ValidationLoop(gates, story_key="test")
        ctx = LoopContext(story_key="test")

        report = loop.run_post_completion(ctx)
        assert report.tier == 3

    def test_auto_fix(self):
        """Test auto-fix functionality."""
        fix_called = {"value": False}

        def auto_fix(ctx):
            fix_called["value"] = True
            return True

        # First call fails, second (after fix) passes
        call_count = {"value": 0}

        def validator(ctx):
            call_count["value"] += 1
            return call_count["value"] > 1

        gate = ValidationGate(
            "fixable",
            validator,
            auto_fix=auto_fix,
            tier=1,
        )
        loop = ValidationLoop([gate], config={"auto_fix_enabled": True}, story_key="test")
        ctx = LoopContext(story_key="test")

        result = loop.run_gate(gate, ctx)
        assert fix_called["value"] is True
        assert result.auto_fixed is True
        assert result.result == ValidationResult.PASS


class TestPreDefinedGates:
    """Tests for pre-defined gate sets."""

    def test_preflight_gates_exist(self):
        """Test that pre-flight gates are defined."""
        assert len(PREFLIGHT_GATES) > 0
        for gate in PREFLIGHT_GATES:
            assert gate.tier == 1

    def test_inter_phase_gates_exist(self):
        """Test that inter-phase gates are defined."""
        assert len(INTER_PHASE_GATES) > 0
        for gate in INTER_PHASE_GATES:
            assert gate.tier == 2

    def test_post_completion_gates_exist(self):
        """Test that post-completion gates are defined."""
        assert len(POST_COMPLETION_GATES) > 0
        for gate in POST_COMPLETION_GATES:
            assert gate.tier == 3

    def test_all_gates_combined(self):
        """Test that ALL_GATES contains all tiers."""
        assert len(ALL_GATES) == len(PREFLIGHT_GATES) + len(INTER_PHASE_GATES) + len(
            POST_COMPLETION_GATES
        )


class TestValidationMemory:
    """Tests for ValidationMemory class."""

    def test_memory_creation(self):
        """Test creating validation memory."""
        memory = ValidationMemory(story_key="test")
        assert memory.story_key == "test"

    @patch("validation_loop.HAS_SHARED_MEMORY", False)
    def test_memory_without_shared_memory(self):
        """Test memory works without shared memory module."""
        memory = ValidationMemory(story_key="test")
        # Should not raise
        memory.record_validation(
            "test_gate",
            ValidationResult.PASS,
            LoopContext(story_key="test"),
        )

    def test_get_success_rate_empty(self):
        """Test success rate with no data."""
        memory = ValidationMemory(story_key="test")
        rate = memory.get_success_rate("nonexistent_gate")
        assert rate == 1.0  # Default to 100% when no data


class TestGetActionableFeedback:
    """Tests for actionable feedback extraction."""

    def test_feedback_from_failures(self):
        """Test extracting feedback from validation failures."""
        gates = [
            ValidationGate(
                "fail_gate",
                lambda ctx: False,
                on_fail=FailureAction.RETRY,
                retry_with_agent="DEV",
                tier=1,
            ),
        ]
        loop = ValidationLoop(gates, story_key="test")
        ctx = LoopContext(story_key="test")

        report = loop.run_gates(ctx, tier=1)
        feedback = loop.get_actionable_feedback(report)

        assert len(feedback["issues"]) == 1
        assert feedback["issues"][0]["gate"] == "fail_gate"
        assert "DEV" in feedback["suggestions"][0]
