# file: src/flask/src/flask/cli.py:405-437
# asked: {"lines": [436, 437], "branches": [[423, 425]]}
# gained: {"lines": [436, 437], "branches": [[423, 425]]}

import pytest
import click
from flask.cli import AppGroup
from flask import Flask

class TestAppGroup:
    def test_command_with_appcontext_false(self):
        """Test that command decorator with with_appcontext=False does not wrap function"""
        group = AppGroup('test')
        
        @group.command('test-cmd', with_appcontext=False)
        def test_cmd():
            return "command executed"
        
        # Verify the command was added to the group
        assert 'test-cmd' in group.commands
        # The command should not be wrapped with with_appcontext
        cmd = group.commands['test-cmd']
        assert cmd.callback.__name__ == 'test_cmd'
    
    def test_group_method_sets_cls_parameter(self):
        """Test that group method sets cls parameter to AppGroup"""
        group = AppGroup('parent')
        
        # Create a subgroup using the group method
        @group.group('subgroup')
        def subgroup():
            pass
        
        # Verify the subgroup was created with AppGroup class
        assert 'subgroup' in group.commands
        subgroup_cmd = group.commands['subgroup']
        assert isinstance(subgroup_cmd, AppGroup)
    
    def test_group_method_preserves_existing_cls(self):
        """Test that group method preserves existing cls parameter"""
        group = AppGroup('parent')
        
        # Create a subgroup with explicit cls parameter
        @group.group('subgroup', cls=click.Group)
        def subgroup():
            pass
        
        # Verify the subgroup uses the explicitly provided class
        assert 'subgroup' in group.commands
        subgroup_cmd = group.commands['subgroup']
        assert isinstance(subgroup_cmd, click.Group)
        assert not isinstance(subgroup_cmd, AppGroup)
