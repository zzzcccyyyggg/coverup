# file: src/click/src/click/core.py:143-166
# asked: {"lines": [143, 144, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166], "branches": []}
# gained: {"lines": [143, 144, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166], "branches": []}

import pytest
from click.core import ParameterSource


class TestParameterSource:
    """Test cases for ParameterSource enum to achieve full coverage."""
    
    def test_parameter_source_enum_members(self):
        """Test that all ParameterSource enum members are accessible and have correct values."""
        # Test COMMANDLINE member
        assert ParameterSource.COMMANDLINE is not None
        assert isinstance(ParameterSource.COMMANDLINE, ParameterSource)
        
        # Test ENVIRONMENT member  
        assert ParameterSource.ENVIRONMENT is not None
        assert isinstance(ParameterSource.ENVIRONMENT, ParameterSource)
        
        # Test DEFAULT member
        assert ParameterSource.DEFAULT is not None
        assert isinstance(ParameterSource.DEFAULT, ParameterSource)
        
        # Test DEFAULT_MAP member
        assert ParameterSource.DEFAULT_MAP is not None
        assert isinstance(ParameterSource.DEFAULT_MAP, ParameterSource)
        
        # Test PROMPT member
        assert ParameterSource.PROMPT is not None
        assert isinstance(ParameterSource.PROMPT, ParameterSource)
        
        # Verify all members are distinct
        members = list(ParameterSource)
        assert len(members) == 5
        assert len(set(members)) == 5
        
    def test_parameter_source_enum_iteration(self):
        """Test that ParameterSource enum can be iterated over."""
        members = list(ParameterSource)
        expected_members = [
            ParameterSource.COMMANDLINE,
            ParameterSource.ENVIRONMENT, 
            ParameterSource.DEFAULT,
            ParameterSource.DEFAULT_MAP,
            ParameterSource.PROMPT
        ]
        assert members == expected_members
        
    def test_parameter_source_enum_comparison(self):
        """Test comparison operations on ParameterSource enum members."""
        # Test equality
        assert ParameterSource.COMMANDLINE == ParameterSource.COMMANDLINE
        assert ParameterSource.ENVIRONMENT == ParameterSource.ENVIRONMENT
        assert ParameterSource.DEFAULT == ParameterSource.DEFAULT
        assert ParameterSource.DEFAULT_MAP == ParameterSource.DEFAULT_MAP
        assert ParameterSource.PROMPT == ParameterSource.PROMPT
        
        # Test inequality
        assert ParameterSource.COMMANDLINE != ParameterSource.ENVIRONMENT
        assert ParameterSource.DEFAULT != ParameterSource.DEFAULT_MAP
        
    def test_parameter_source_enum_string_representation(self):
        """Test string representation of ParameterSource enum members."""
        # Test repr
        assert repr(ParameterSource.COMMANDLINE) == '<ParameterSource.COMMANDLINE: 1>'
        assert repr(ParameterSource.ENVIRONMENT) == '<ParameterSource.ENVIRONMENT: 2>'
        assert repr(ParameterSource.DEFAULT) == '<ParameterSource.DEFAULT: 3>'
        assert repr(ParameterSource.DEFAULT_MAP) == '<ParameterSource.DEFAULT_MAP: 4>'
        assert repr(ParameterSource.PROMPT) == '<ParameterSource.PROMPT: 5>'
        
        # Test str
        assert str(ParameterSource.COMMANDLINE) == 'ParameterSource.COMMANDLINE'
        assert str(ParameterSource.ENVIRONMENT) == 'ParameterSource.ENVIRONMENT'
        assert str(ParameterSource.DEFAULT) == 'ParameterSource.DEFAULT'
        assert str(ParameterSource.DEFAULT_MAP) == 'ParameterSource.DEFAULT_MAP'
        assert str(ParameterSource.PROMPT) == 'ParameterSource.PROMPT'
        
    def test_parameter_source_enum_name_and_value(self):
        """Test name and value properties of ParameterSource enum members."""
        # Test names
        assert ParameterSource.COMMANDLINE.name == 'COMMANDLINE'
        assert ParameterSource.ENVIRONMENT.name == 'ENVIRONMENT'
        assert ParameterSource.DEFAULT.name == 'DEFAULT'
        assert ParameterSource.DEFAULT_MAP.name == 'DEFAULT_MAP'
        assert ParameterSource.PROMPT.name == 'PROMPT'
        
        # Test values (auto-generated sequential integers starting from 1)
        assert ParameterSource.COMMANDLINE.value == 1
        assert ParameterSource.ENVIRONMENT.value == 2
        assert ParameterSource.DEFAULT.value == 3
        assert ParameterSource.DEFAULT_MAP.value == 4
        assert ParameterSource.PROMPT.value == 5
