# file: src/flask/src/flask/sessions.py:317-335
# asked: {"lines": [317, 318, 319, 321, 323, 324, 326, 327, 328, 329, 330, 331, 332, 333], "branches": [[318, 319], [318, 321], [323, 324], [323, 326]]}
# gained: {"lines": [317, 318, 319, 321, 323, 324, 326, 327, 328, 329, 330, 331, 332, 333], "branches": [[318, 319], [318, 321], [323, 324], [323, 326]]}

import pytest
from flask import Flask
from flask.sessions import SecureCookieSessionInterface
from itsdangerous import URLSafeTimedSerializer


class TestSecureCookieSessionInterfaceGetSigningSerializer:
    """Test cases for SecureCookieSessionInterface.get_signing_serializer method."""
    
    def test_get_signing_serializer_no_secret_key_returns_none(self):
        """Test that get_signing_serializer returns None when app has no secret_key."""
        app = Flask(__name__)
        app.secret_key = None
        interface = SecureCookieSessionInterface()
        
        result = interface.get_signing_serializer(app)
        
        assert result is None
    
    def test_get_signing_serializer_with_secret_key_no_fallbacks(self):
        """Test that get_signing_serializer returns serializer with only secret_key."""
        app = Flask(__name__)
        app.secret_key = "test_secret_key"
        app.config["SECRET_KEY_FALLBACKS"] = []
        interface = SecureCookieSessionInterface()
        
        result = interface.get_signing_serializer(app)
        
        assert isinstance(result, URLSafeTimedSerializer)
        assert result.secret_keys == [b"test_secret_key"]
        assert result.salt == b"cookie-session"  # URLSafeTimedSerializer converts to bytes
        assert result.serializer == interface.serializer
        assert result.signer_kwargs["key_derivation"] == interface.key_derivation
        assert result.signer_kwargs["digest_method"] == interface.digest_method
    
    def test_get_signing_serializer_with_secret_key_and_fallbacks(self):
        """Test that get_signing_serializer returns serializer with fallbacks and secret_key."""
        app = Flask(__name__)
        app.secret_key = "current_secret_key"
        app.config["SECRET_KEY_FALLBACKS"] = ["fallback1", "fallback2"]
        interface = SecureCookieSessionInterface()
        
        result = interface.get_signing_serializer(app)
        
        assert isinstance(result, URLSafeTimedSerializer)
        assert result.secret_keys == [b"fallback1", b"fallback2", b"current_secret_key"]
        assert result.salt == b"cookie-session"  # URLSafeTimedSerializer converts to bytes
        assert result.serializer == interface.serializer
        assert result.signer_kwargs["key_derivation"] == interface.key_derivation
        assert result.signer_kwargs["digest_method"] == interface.digest_method
    
    def test_get_signing_serializer_with_bytes_secret_key_and_fallbacks(self):
        """Test that get_signing_serializer works with bytes secret keys and fallbacks."""
        app = Flask(__name__)
        app.secret_key = b"current_secret_key_bytes"
        app.config["SECRET_KEY_FALLBACKS"] = [b"fallback1_bytes", b"fallback2_bytes"]
        interface = SecureCookieSessionInterface()
        
        result = interface.get_signing_serializer(app)
        
        assert isinstance(result, URLSafeTimedSerializer)
        assert result.secret_keys == [b"fallback1_bytes", b"fallback2_bytes", b"current_secret_key_bytes"]
        assert result.salt == b"cookie-session"  # URLSafeTimedSerializer converts to bytes
        assert result.serializer == interface.serializer
        assert result.signer_kwargs["key_derivation"] == interface.key_derivation
        assert result.signer_kwargs["digest_method"] == interface.digest_method
    
    def test_get_signing_serializer_with_mixed_string_bytes_keys(self):
        """Test that get_signing_serializer works with mixed string and bytes keys."""
        app = Flask(__name__)
        app.secret_key = "current_secret_string"
        app.config["SECRET_KEY_FALLBACKS"] = [b"fallback_bytes", "fallback_string"]
        interface = SecureCookieSessionInterface()
        
        result = interface.get_signing_serializer(app)
        
        assert isinstance(result, URLSafeTimedSerializer)
        assert result.secret_keys == [b"fallback_bytes", b"fallback_string", b"current_secret_string"]
        assert result.salt == b"cookie-session"  # URLSafeTimedSerializer converts to bytes
        assert result.serializer == interface.serializer
        assert result.signer_kwargs["key_derivation"] == interface.key_derivation
        assert result.signer_kwargs["digest_method"] == interface.digest_method
