"""
Comprehensive unit tests for errors.py

Tests the error handling functionality including:
- Error classes and codes
- Error context formatting
- Error message templates
- Error reporter
- Logging helpers
"""

import pytest
import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

# Ensure imports work
sys.path.insert(0, str(Path(__file__).parent.parent / "tooling" / "scripts" / "lib"))

from lib.errors import (
    ErrorCode,
    ErrorContext,
    CostTrackingError,
    ConfigurationError,
    SessionError,
    BudgetError,
    CalculationError,
    ERROR_MESSAGES,
    create_error,
    format_error_for_user,
    handle_error,
    wrap_errors,
    ErrorReporter,
    log_debug,
    log_info,
    log_warning,
    log_error,
    log_success,
    set_verbose,
    is_verbose,
)


class TestErrorCode:
    """Tests for ErrorCode enum."""

    def test_config_error_codes(self):
        """Test configuration error codes are in 1xx range."""
        assert ErrorCode.CONFIG_NOT_FOUND.value == 101
        assert ErrorCode.CONFIG_PARSE_ERROR.value == 102
        assert ErrorCode.CONFIG_INVALID_VALUE.value == 103

    def test_file_error_codes(self):
        """Test file error codes are in 2xx range."""
        assert ErrorCode.FILE_NOT_FOUND.value == 201
        assert ErrorCode.FILE_READ_ERROR.value == 202
        assert ErrorCode.FILE_WRITE_ERROR.value == 203
        assert ErrorCode.DIRECTORY_NOT_FOUND.value == 204
        assert ErrorCode.PERMISSION_DENIED.value == 205

    def test_session_error_codes(self):
        """Test session error codes are in 3xx range."""
        assert ErrorCode.SESSION_NOT_FOUND.value == 301
        assert ErrorCode.SESSION_CORRUPTED.value == 302
        assert ErrorCode.SESSION_SAVE_FAILED.value == 303

    def test_budget_error_codes(self):
        """Test budget error codes are in 4xx range."""
        assert ErrorCode.BUDGET_EXCEEDED.value == 401
        assert ErrorCode.BUDGET_INVALID.value == 402

    def test_calculation_error_codes(self):
        """Test calculation error codes are in 5xx range."""
        assert ErrorCode.UNKNOWN_MODEL.value == 501
        assert ErrorCode.INVALID_TOKENS.value == 502
        assert ErrorCode.CALCULATION_ERROR.value == 503

    def test_general_error_codes(self):
        """Test general error codes."""
        assert ErrorCode.UNKNOWN_ERROR.value == 999


class TestErrorContext:
    """Tests for ErrorContext dataclass."""

    def test_minimal_context(self):
        """Test creating context with minimal data."""
        context = ErrorContext(operation="test operation")
        assert context.operation == "test operation"
        assert context.file_path is None
        assert context.model is None
        assert context.agent is None

    def test_full_context(self):
        """Test creating context with all fields."""
        context = ErrorContext(
            operation="calculate cost",
            file_path=Path("/tmp/session.json"),
            model="opus",
            agent="DEV",
            tokens={"input": 1000, "output": 500},
            budget=15.00,
            additional={"extra": "data"}
        )
        assert context.operation == "calculate cost"
        assert context.file_path == Path("/tmp/session.json")
        assert context.model == "opus"
        assert context.agent == "DEV"
        assert context.tokens == {"input": 1000, "output": 500}
        assert context.budget == 15.00
        assert context.additional == {"extra": "data"}


class TestCostTrackingError:
    """Tests for CostTrackingError exception class."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = CostTrackingError("Test error message")
        assert "Test error message" in str(error)
        assert error.code == ErrorCode.UNKNOWN_ERROR

    def test_error_with_code(self):
        """Test error with specific code."""
        error = CostTrackingError(
            "Budget exceeded",
            code=ErrorCode.BUDGET_EXCEEDED
        )
        assert error.code == ErrorCode.BUDGET_EXCEEDED
        assert "BUDGET_EXCEEDED" in str(error)

    def test_error_with_context(self):
        """Test error with context information."""
        context = ErrorContext(
            operation="logging usage",
            model="opus",
            agent="DEV"
        )
        error = CostTrackingError(
            "Error during logging",
            code=ErrorCode.CALCULATION_ERROR,
            context=context
        )
        formatted = error.format_message()
        assert "logging usage" in formatted
        assert "opus" in formatted
        assert "DEV" in formatted

    def test_error_with_file_path_context(self):
        """Test error with file path in context."""
        context = ErrorContext(
            operation="reading config",
            file_path=Path("/tmp/config.json")
        )
        error = CostTrackingError(
            "Config error",
            context=context
        )
        formatted = error.format_message()
        assert "config.json" in formatted

    def test_error_with_suggestion(self):
        """Test error with suggestion."""
        error = CostTrackingError(
            "File not found",
            suggestion="Check the file path and try again"
        )
        formatted = error.format_message()
        assert "Suggestion" in formatted
        assert "Check the file path" in formatted

    def test_error_with_cause(self):
        """Test error with underlying cause."""
        original = ValueError("Invalid value")
        error = CostTrackingError(
            "Processing failed",
            cause=original
        )
        formatted = error.format_message()
        assert "Caused by" in formatted
        assert "ValueError" in formatted


class TestSpecificErrorClasses:
    """Tests for specific error subclasses."""

    def test_configuration_error(self):
        """Test ConfigurationError is a CostTrackingError."""
        error = ConfigurationError("Config issue")
        assert isinstance(error, CostTrackingError)

    def test_session_error(self):
        """Test SessionError is a CostTrackingError."""
        error = SessionError("Session issue")
        assert isinstance(error, CostTrackingError)

    def test_budget_error(self):
        """Test BudgetError is a CostTrackingError."""
        error = BudgetError("Budget issue")
        assert isinstance(error, CostTrackingError)

    def test_calculation_error(self):
        """Test CalculationError is a CostTrackingError."""
        error = CalculationError("Calculation issue")
        assert isinstance(error, CostTrackingError)


class TestErrorMessages:
    """Tests for ERROR_MESSAGES templates."""

    def test_all_error_codes_have_messages(self):
        """Test that common error codes have message templates."""
        important_codes = [
            ErrorCode.CONFIG_NOT_FOUND,
            ErrorCode.FILE_NOT_FOUND,
            ErrorCode.SESSION_NOT_FOUND,
            ErrorCode.BUDGET_EXCEEDED,
            ErrorCode.UNKNOWN_MODEL,
        ]
        for code in important_codes:
            assert code in ERROR_MESSAGES
            assert "message" in ERROR_MESSAGES[code]

    def test_messages_have_suggestions(self):
        """Test that error messages include suggestions."""
        for code, template in ERROR_MESSAGES.items():
            assert "message" in template
            # Most should have suggestions
            if code != ErrorCode.UNKNOWN_ERROR:
                assert "suggestion" in template


class TestCreateError:
    """Tests for create_error factory function."""

    def test_create_config_error(self):
        """Test creating configuration error."""
        error = create_error(ErrorCode.CONFIG_NOT_FOUND)
        assert isinstance(error, ConfigurationError)
        assert error.code == ErrorCode.CONFIG_NOT_FOUND

    def test_create_session_error(self):
        """Test creating session error."""
        error = create_error(ErrorCode.SESSION_NOT_FOUND)
        assert isinstance(error, SessionError)
        assert error.code == ErrorCode.SESSION_NOT_FOUND

    def test_create_budget_error(self):
        """Test creating budget error."""
        error = create_error(ErrorCode.BUDGET_EXCEEDED)
        assert isinstance(error, BudgetError)
        assert error.code == ErrorCode.BUDGET_EXCEEDED

    def test_create_calculation_error(self):
        """Test creating calculation error."""
        error = create_error(ErrorCode.UNKNOWN_MODEL)
        assert isinstance(error, CalculationError)
        assert error.code == ErrorCode.UNKNOWN_MODEL

    def test_create_error_with_context(self):
        """Test creating error with context."""
        context = ErrorContext(operation="test", model="opus")
        error = create_error(ErrorCode.UNKNOWN_MODEL, context=context)
        assert error.context == context

    def test_create_error_with_custom_message(self):
        """Test creating error with custom message."""
        error = create_error(
            ErrorCode.FILE_NOT_FOUND,
            custom_message="Custom file error"
        )
        assert "Custom file error" in str(error)

    def test_create_error_with_cause(self):
        """Test creating error with cause."""
        original = IOError("Disk error")
        error = create_error(ErrorCode.FILE_WRITE_ERROR, cause=original)
        assert error.cause == original

    def test_create_general_error(self):
        """Test creating general error for unknown codes."""
        error = create_error(ErrorCode.UNKNOWN_ERROR)
        assert isinstance(error, CostTrackingError)


class TestFormatErrorForUser:
    """Tests for format_error_for_user function."""

    def test_format_cost_tracking_error(self):
        """Test formatting a CostTrackingError."""
        error = CostTrackingError("Test error", code=ErrorCode.BUDGET_EXCEEDED)
        formatted = format_error_for_user(error)
        assert "Error Occurred" in formatted
        assert "BUDGET_EXCEEDED" in formatted

    def test_format_generic_exception(self):
        """Test formatting a generic exception."""
        error = ValueError("Invalid value")
        formatted = format_error_for_user(error)
        assert "Error Occurred" in formatted
        assert "ValueError" in formatted

    def test_format_with_verbose(self):
        """Test formatting with verbose mode."""
        error = ValueError("Test error")
        formatted = format_error_for_user(error, verbose=True)
        assert "Stack Trace" in formatted


class TestHandleError:
    """Tests for handle_error function."""

    def test_handle_generic_file_not_found(self, capsys):
        """Test handling FileNotFoundError."""
        error = FileNotFoundError("test.txt")
        handle_error(error, context="loading file")
        captured = capsys.readouterr()
        assert "FILE_NOT_FOUND" in captured.err

    def test_handle_permission_error(self, capsys):
        """Test handling PermissionError."""
        error = PermissionError("Access denied")
        handle_error(error, context="writing file")
        captured = capsys.readouterr()
        assert "PERMISSION_DENIED" in captured.err

    def test_handle_json_decode_error(self, capsys):
        """Test handling JSONDecodeError."""
        error = json.JSONDecodeError("Expecting value", "doc", 0)
        handle_error(error, context="parsing config")
        captured = capsys.readouterr()
        assert "CONFIG_PARSE_ERROR" in captured.err

    def test_handle_cost_tracking_error(self, capsys):
        """Test handling CostTrackingError directly."""
        error = CostTrackingError("Custom error", code=ErrorCode.BUDGET_EXCEEDED)
        handle_error(error, context="budget check")
        captured = capsys.readouterr()
        assert "BUDGET_EXCEEDED" in captured.err

    def test_handle_error_exit(self):
        """Test handle_error with exit_on_error."""
        error = ValueError("Fatal error")
        with pytest.raises(SystemExit) as exc_info:
            handle_error(error, exit_on_error=True)
        assert exc_info.value.code == 1


class TestWrapErrors:
    """Tests for wrap_errors decorator."""

    def test_wrap_successful_function(self):
        """Test decorator with successful function."""
        @wrap_errors("test operation")
        def successful_func():
            return "success"

        result = successful_func()
        assert result == "success"

    def test_wrap_failing_function(self):
        """Test decorator with failing function."""
        @wrap_errors("failing operation")
        def failing_func():
            raise ValueError("Something went wrong")

        with pytest.raises(CostTrackingError) as exc_info:
            failing_func()
        assert "Something went wrong" in str(exc_info.value)

    def test_wrap_preserves_cost_tracking_error(self):
        """Test decorator preserves CostTrackingError."""
        @wrap_errors("wrapped operation")
        def func_with_cost_error():
            raise BudgetError("Budget exceeded")

        with pytest.raises(BudgetError):
            func_with_cost_error()


class TestErrorReporter:
    """Tests for ErrorReporter class."""

    def test_empty_reporter(self):
        """Test empty reporter."""
        reporter = ErrorReporter()
        assert not reporter.has_errors()
        assert not reporter.has_warnings()

    def test_add_error(self):
        """Test adding errors."""
        reporter = ErrorReporter()
        reporter.add_error(ValueError("Test"), "context1")
        assert reporter.has_errors()
        assert len(reporter.errors) == 1

    def test_add_warning(self):
        """Test adding warnings."""
        reporter = ErrorReporter()
        reporter.add_warning("Warning message", "context1")
        assert reporter.has_warnings()
        assert len(reporter.warnings) == 1

    def test_format_report(self):
        """Test formatting report."""
        reporter = ErrorReporter()
        reporter.add_error(ValueError("Error 1"), "ctx1")
        reporter.add_error(TypeError("Error 2"), "ctx2")
        reporter.add_warning("Warning 1", "ctx3")

        report = reporter.format_report()
        assert "2 Error(s)" in report
        assert "1 Warning(s)" in report
        assert "Error 1" in report
        assert "Warning 1" in report

    def test_print_report(self, capsys):
        """Test printing report."""
        reporter = ErrorReporter()
        reporter.add_error(ValueError("Test error"), "test")
        reporter.print_report()

        captured = capsys.readouterr()
        assert "Error(s)" in captured.err

    def test_clear_reporter(self):
        """Test clearing reporter."""
        reporter = ErrorReporter()
        reporter.add_error(ValueError("Error"), "ctx")
        reporter.add_warning("Warning", "ctx")
        reporter.clear()

        assert not reporter.has_errors()
        assert not reporter.has_warnings()


class TestLoggingHelpers:
    """Tests for logging helper functions."""

    def test_log_info(self, capsys):
        """Test log_info output."""
        log_info("Test info message")
        captured = capsys.readouterr()
        assert "Test info message" in captured.out
        assert "ℹ️" in captured.out

    def test_log_warning(self, capsys):
        """Test log_warning output."""
        log_warning("Test warning message")
        captured = capsys.readouterr()
        assert "Test warning message" in captured.err
        assert "⚠️" in captured.err

    def test_log_error(self, capsys):
        """Test log_error output."""
        log_error("Test error message")
        captured = capsys.readouterr()
        assert "Test error message" in captured.err
        assert "❌" in captured.err

    def test_log_success(self, capsys):
        """Test log_success output."""
        log_success("Test success message")
        captured = capsys.readouterr()
        assert "Test success message" in captured.out
        assert "✅" in captured.out

    def test_log_debug_verbose_off(self, capsys):
        """Test log_debug with verbose mode off."""
        set_verbose(False)
        log_debug("Debug message")
        captured = capsys.readouterr()
        assert "Debug message" not in captured.err

    def test_log_debug_verbose_on(self, capsys):
        """Test log_debug with verbose mode on."""
        set_verbose(True)
        log_debug("Debug message", key="value")
        captured = capsys.readouterr()
        assert "Debug message" in captured.err
        assert "key=value" in captured.err
        set_verbose(False)  # Reset

    def test_verbose_mode_toggle(self):
        """Test verbose mode toggle."""
        assert not is_verbose()
        set_verbose(True)
        assert is_verbose()
        set_verbose(False)
        assert not is_verbose()
