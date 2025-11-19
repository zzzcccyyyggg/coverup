# file: src/click/src/click/types.py:730-751
# asked: {"lines": [730, 731, 733, 736, 738, 739, 741, 743, 744, 745, 746, 747, 750, 751], "branches": [[738, 739], [738, 741]]}
# gained: {"lines": [730, 731, 733, 736, 738, 739, 741, 743, 744, 745, 746, 747, 750, 751], "branches": [[738, 739], [738, 741]]}

import pytest
import uuid
from click.types import UUIDParameterType
from click.core import Context, Parameter
from click.exceptions import BadParameter


class TestUUIDParameterType:
    """Test cases for UUIDParameterType to achieve full coverage."""
    
    def test_convert_with_uuid_object(self):
        """Test convert method when value is already a UUID object."""
        uuid_type = UUIDParameterType()
        test_uuid = uuid.uuid4()
        
        result = uuid_type.convert(test_uuid, None, None)
        
        assert result == test_uuid
    
    def test_convert_with_valid_uuid_string(self):
        """Test convert method with a valid UUID string."""
        uuid_type = UUIDParameterType()
        test_uuid = uuid.uuid4()
        uuid_string = str(test_uuid)
        
        result = uuid_type.convert(uuid_string, None, None)
        
        assert result == test_uuid
    
    def test_convert_with_valid_uuid_string_with_whitespace(self):
        """Test convert method with a valid UUID string that has whitespace."""
        uuid_type = UUIDParameterType()
        test_uuid = uuid.uuid4()
        uuid_string = f"  {test_uuid}  "
        
        result = uuid_type.convert(uuid_string, None, None)
        
        assert result == test_uuid
    
    def test_convert_with_invalid_uuid_string(self):
        """Test convert method with an invalid UUID string."""
        uuid_type = UUIDParameterType()
        invalid_uuid = "not-a-valid-uuid"
        
        with pytest.raises(BadParameter) as exc_info:
            uuid_type.convert(invalid_uuid, None, None)
        
        assert "not-a-valid-uuid" in str(exc_info.value)
        assert "is not a valid UUID" in str(exc_info.value)
    
    def test_repr(self):
        """Test __repr__ method returns 'UUID'."""
        uuid_type = UUIDParameterType()
        
        result = repr(uuid_type)
        
        assert result == "UUID"
