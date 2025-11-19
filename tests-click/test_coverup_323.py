# file: src/click/src/click/core.py:845-852
# asked: {"lines": [845, 852], "branches": []}
# gained: {"lines": [845, 852], "branches": []}

import pytest
from click.core import Context, ParameterSource

class MockCommand:
    def __init__(self):
        self.allow_extra_args = False
        self.allow_interspersed_args = True
        self.ignore_unknown_options = False

def test_context_set_parameter_source():
    """Test that set_parameter_source correctly stores parameter sources."""
    command = MockCommand()
    ctx = Context(command=command)
    
    # Test setting a parameter source
    ctx.set_parameter_source("test_param", ParameterSource.COMMANDLINE)
    assert ctx.get_parameter_source("test_param") == ParameterSource.COMMANDLINE
    
    # Test updating an existing parameter source
    ctx.set_parameter_source("test_param", ParameterSource.ENVIRONMENT)
    assert ctx.get_parameter_source("test_param") == ParameterSource.ENVIRONMENT
    
    # Test setting multiple different parameters
    ctx.set_parameter_source("param1", ParameterSource.DEFAULT)
    ctx.set_parameter_source("param2", ParameterSource.PROMPT)
    ctx.set_parameter_source("param3", ParameterSource.DEFAULT_MAP)
    
    assert ctx.get_parameter_source("param1") == ParameterSource.DEFAULT
    assert ctx.get_parameter_source("param2") == ParameterSource.PROMPT
    assert ctx.get_parameter_source("param3") == ParameterSource.DEFAULT_MAP
    
    # Test that non-existent parameter returns None
    assert ctx.get_parameter_source("non_existent") is None
