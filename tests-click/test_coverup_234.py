# file: src/click/src/click/types.py:264-268
# asked: {"lines": [264, 265, 266, 267, 268], "branches": []}
# gained: {"lines": [264, 265, 266, 267, 268], "branches": []}

import pytest
from click.types import Choice


class TestChoiceToInfoDict:
    def test_to_info_dict_returns_expected_structure(self):
        """Test that to_info_dict returns the expected dictionary structure with choices and case_sensitive."""
        choices = ["option1", "option2", "option3"]
        case_sensitive = True
        choice_type = Choice(choices, case_sensitive)
        
        result = choice_type.to_info_dict()
        
        assert isinstance(result, dict)
        assert "choices" in result
        assert "case_sensitive" in result
        # The choices are stored as a tuple in the Choice class, so compare with tuple
        assert result["choices"] == tuple(choices)
        assert result["case_sensitive"] == case_sensitive
    
    def test_to_info_dict_with_case_insensitive(self):
        """Test to_info_dict with case insensitive configuration."""
        choices = ["A", "B", "C"]
        case_sensitive = False
        choice_type = Choice(choices, case_sensitive)
        
        result = choice_type.to_info_dict()
        
        assert result["choices"] == tuple(choices)
        assert result["case_sensitive"] == case_sensitive
    
    def test_to_info_dict_includes_parent_info(self):
        """Test that to_info_dict includes information from parent class."""
        choices = ["test1", "test2"]
        choice_type = Choice(choices)
        
        result = choice_type.to_info_dict()
        
        # Should include at least the basic structure from parent
        assert isinstance(result, dict)
        assert "choices" in result
        assert "case_sensitive" in result
        # The parent class should contribute additional fields
        assert len(result) >= 2
