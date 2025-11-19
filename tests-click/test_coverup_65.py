# file: src/click/src/click/core.py:73-90
# asked: {"lines": [73, 74, 76, 77, 79, 80, 81, 82, 85, 86, 87, 90], "branches": [[76, 77], [76, 79], [79, 80], [79, 85]]}
# gained: {"lines": [73, 74, 76, 77, 79, 80, 81, 82, 85, 86, 87, 90], "branches": [[76, 77], [76, 79], [79, 80], [79, 85]]}

import pytest
import click
from click.core import _check_nested_chain, Group, Command


class TestCheckNestedChain:
    
    def test_check_nested_chain_with_non_chain_base_command(self):
        """Test that _check_nested_chain returns early when base_command.chain is False."""
        base_command = Group("base")
        cmd = Group("subgroup")
        
        # Should return without raising
        _check_nested_chain(base_command, "subgroup", cmd)
    
    def test_check_nested_chain_with_non_group_cmd(self):
        """Test that _check_nested_chain returns early when cmd is not a Group."""
        base_command = Group("base", chain=True)
        cmd = Command("subcommand")
        
        # Should return without raising
        _check_nested_chain(base_command, "subcommand", cmd)
    
    def test_check_nested_chain_register_true(self):
        """Test that _check_nested_chain raises RuntimeError with register=True message."""
        base_command = Group("base", chain=True)
        cmd = Group("subgroup")
        
        with pytest.raises(RuntimeError) as exc_info:
            _check_nested_chain(base_command, "subgroup", cmd, register=True)
        
        expected_message = (
            "It is not possible to add the group 'subgroup' to another"
            " group 'base' that is in chain mode."
        )
        assert str(exc_info.value) == expected_message
    
    def test_check_nested_chain_register_false(self):
        """Test that _check_nested_chain raises RuntimeError with register=False message."""
        base_command = Group("base", chain=True)
        cmd = Group("subgroup")
        
        with pytest.raises(RuntimeError) as exc_info:
            _check_nested_chain(base_command, "subgroup", cmd, register=False)
        
        expected_message = (
            "Found the group 'subgroup' as subcommand to another group "
            " 'base' that is in chain mode. This is not supported."
        )
        assert str(exc_info.value) == expected_message
