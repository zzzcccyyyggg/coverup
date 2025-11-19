# file: src/click/src/click/core.py:97-113
# asked: {"lines": [97, 98, 99, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113], "branches": [[105, 106], [105, 107], [107, 108], [107, 109], [111, 112], [111, 113]]}
# gained: {"lines": [97, 98, 99, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113], "branches": [[105, 106], [105, 107], [107, 108], [107, 109], [111, 112], [111, 113]]}

import pytest
from click.core import Context, Option, Command
from click.exceptions import BadParameter, UsageError
from click.core import augment_usage_errors


def test_augment_usage_errors_bad_parameter_no_ctx_no_param():
    """Test augment_usage_errors with BadParameter that has no ctx and no param provided."""
    command = Command("test")
    ctx = Context(command=command, info_name="test")
    param = Option(["--test"])
    
    with pytest.raises(BadParameter) as exc_info:
        with augment_usage_errors(ctx, param):
            raise BadParameter("test error")
    
    assert exc_info.value.ctx is ctx
    assert exc_info.value.param is param


def test_augment_usage_errors_bad_parameter_with_ctx_no_param():
    """Test augment_usage_errors with BadParameter that already has ctx but no param provided."""
    command = Command("test")
    ctx = Context(command=command, info_name="test")
    existing_ctx = Context(command=command, info_name="existing")
    param = Option(["--test"])
    
    with pytest.raises(BadParameter) as exc_info:
        with augment_usage_errors(ctx, param):
            e = BadParameter("test error", ctx=existing_ctx)
            raise e
    
    assert exc_info.value.ctx is existing_ctx  # Should not be overwritten
    assert exc_info.value.param is param  # Should be set


def test_augment_usage_errors_bad_parameter_no_ctx_with_param():
    """Test augment_usage_errors with BadParameter that has no ctx but already has param."""
    command = Command("test")
    ctx = Context(command=command, info_name="test")
    existing_param = Option(["--existing"])
    param = Option(["--test"])
    
    with pytest.raises(BadParameter) as exc_info:
        with augment_usage_errors(ctx, param):
            e = BadParameter("test error", param=existing_param)
            raise e
    
    assert exc_info.value.ctx is ctx  # Should be set
    assert exc_info.value.param is existing_param  # Should not be overwritten


def test_augment_usage_errors_usage_error_no_ctx():
    """Test augment_usage_errors with UsageError that has no ctx."""
    command = Command("test")
    ctx = Context(command=command, info_name="test")
    
    with pytest.raises(UsageError) as exc_info:
        with augment_usage_errors(ctx):
            raise UsageError("test error")
    
    assert exc_info.value.ctx is ctx


def test_augment_usage_errors_usage_error_with_ctx():
    """Test augment_usage_errors with UsageError that already has ctx."""
    command = Command("test")
    ctx = Context(command=command, info_name="test")
    existing_ctx = Context(command=command, info_name="existing")
    
    with pytest.raises(UsageError) as exc_info:
        with augment_usage_errors(ctx):
            e = UsageError("test error", ctx=existing_ctx)
            raise e
    
    assert exc_info.value.ctx is existing_ctx  # Should not be overwritten


def test_augment_usage_errors_no_exception():
    """Test augment_usage_errors when no exception is raised."""
    command = Command("test")
    ctx = Context(command=command, info_name="test")
    param = Option(["--test"])
    
    # Should not raise any exception
    with augment_usage_errors(ctx, param):
        pass


def test_augment_usage_errors_other_exception():
    """Test augment_usage_errors when a different exception is raised."""
    command = Command("test")
    ctx = Context(command=command, info_name="test")
    param = Option(["--test"])
    
    with pytest.raises(ValueError, match="other error"):
        with augment_usage_errors(ctx, param):
            raise ValueError("other error")
