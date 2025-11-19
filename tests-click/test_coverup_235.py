# file: src/click/src/click/types.py:431-434
# asked: {"lines": [431, 432, 433, 434], "branches": []}
# gained: {"lines": [431, 432, 433, 434], "branches": []}

import pytest
from click.types import DateTime

class TestDateTime:
    def test_to_info_dict_includes_formats(self):
        """Test that to_info_dict includes the formats attribute."""
        # Create a DateTime instance with custom formats
        custom_formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']
        dt_type = DateTime(formats=custom_formats)
        
        # Call to_info_dict and verify it includes formats
        info_dict = dt_type.to_info_dict()
        
        # Assert that the formats are included in the info_dict
        assert 'formats' in info_dict
        assert info_dict['formats'] == custom_formats
    
    def test_to_info_dict_with_default_formats(self):
        """Test that to_info_dict includes default formats when no custom formats provided."""
        # Create a DateTime instance with default formats
        dt_type = DateTime()
        
        # Call to_info_dict and verify it includes default formats
        info_dict = dt_type.to_info_dict()
        
        # Assert that the formats are included in the info_dict
        assert 'formats' in info_dict
        assert info_dict['formats'] == ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']
