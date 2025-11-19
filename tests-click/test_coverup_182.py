# file: src/click/src/click/core.py:2866-2883
# asked: {"lines": [2866, 2871, 2872, 2873, 2874, 2875, 2879, 2880, 2881, 2883], "branches": []}
# gained: {"lines": [2866, 2871, 2872, 2873, 2874, 2875, 2879, 2880, 2881, 2883], "branches": []}

import pytest
import click
from click._utils import UNSET


class TestOptionToInfoDict:
    """Test cases for Option.to_info_dict method to achieve full coverage."""
    
    def test_to_info_dict_with_flag_value_unset(self):
        """Test to_info_dict when flag_value is UNSET."""
        # Create an option where flag_value remains UNSET
        # This happens when is_flag=False and flag_value is not explicitly set
        option = click.Option(['--test'], is_flag=False)
        info_dict = option.to_info_dict()
        
        assert info_dict['name'] == 'test'
        assert info_dict['help'] is None
        assert info_dict['prompt'] is None
        assert info_dict['is_flag'] is False
        assert info_dict['flag_value'] is None  # Should be None when flag_value is UNSET
        assert info_dict['count'] is False
        assert info_dict['hidden'] is False
    
    def test_to_info_dict_with_flag_value_set(self):
        """Test to_info_dict when flag_value is explicitly set."""
        option = click.Option(['--test'], is_flag=True, flag_value='custom_value')
        info_dict = option.to_info_dict()
        
        assert info_dict['name'] == 'test'
        assert info_dict['help'] is None
        assert info_dict['prompt'] is None
        assert info_dict['is_flag'] is True
        assert info_dict['flag_value'] == 'custom_value'  # Should be the custom value
        assert info_dict['count'] is False
        assert info_dict['hidden'] is False
    
    def test_to_info_dict_with_prompt(self):
        """Test to_info_dict with prompt set."""
        option = click.Option(['--name'], prompt='Enter name')
        info_dict = option.to_info_dict()
        
        assert info_dict['name'] == 'name'
        assert info_dict['help'] is None
        assert info_dict['prompt'] == 'Enter name'
        assert info_dict['is_flag'] is False
        assert info_dict['flag_value'] is None
        assert info_dict['count'] is False
        assert info_dict['hidden'] is False
    
    def test_to_info_dict_with_help(self):
        """Test to_info_dict with help text."""
        option = click.Option(['--verbose'], help='Enable verbose output')
        info_dict = option.to_info_dict()
        
        assert info_dict['name'] == 'verbose'
        assert info_dict['help'] == 'Enable verbose output'
        assert info_dict['prompt'] is None
        assert info_dict['is_flag'] is False
        assert info_dict['flag_value'] is None
        assert info_dict['count'] is False
        assert info_dict['hidden'] is False
    
    def test_to_info_dict_with_count(self):
        """Test to_info_dict with count enabled."""
        option = click.Option(['-v'], count=True)
        info_dict = option.to_info_dict()
        
        assert info_dict['name'] == 'v'
        assert info_dict['help'] is None
        assert info_dict['prompt'] is None
        assert info_dict['is_flag'] is False
        assert info_dict['flag_value'] is None
        assert info_dict['count'] is True
        assert info_dict['hidden'] is False
    
    def test_to_info_dict_with_hidden(self):
        """Test to_info_dict with hidden enabled."""
        option = click.Option(['--secret'], hidden=True)
        info_dict = option.to_info_dict()
        
        assert info_dict['name'] == 'secret'
        assert info_dict['help'] is None
        assert info_dict['prompt'] is None
        assert info_dict['is_flag'] is False
        assert info_dict['flag_value'] is None
        assert info_dict['count'] is False
        assert info_dict['hidden'] is True
    
    def test_to_info_dict_comprehensive(self):
        """Test to_info_dict with multiple attributes set."""
        option = click.Option(
            ['--config'], 
            help='Configuration file',
            prompt='Enter config path',
            is_flag=True,
            flag_value='/etc/config.yaml',
            count=False,
            hidden=True
        )
        info_dict = option.to_info_dict()
        
        assert info_dict['name'] == 'config'
        assert info_dict['help'] == 'Configuration file'
        assert info_dict['prompt'] == 'Enter config path'
        assert info_dict['is_flag'] is True
        assert info_dict['flag_value'] == '/etc/config.yaml'
        assert info_dict['count'] is False
        assert info_dict['hidden'] is True
