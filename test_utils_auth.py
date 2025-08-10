import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import os

from utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    ADMIN_TOKEN
)

class TestPasswordHashing:
    """Test cases for password hashing and verification"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert hashed != password  # Should be different from original
        assert len(hashed) > 0  # Should not be empty
        assert hashed.startswith("$2b$")  # bcrypt hash format
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "correct_password"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_hash_same_password_different_hashes(self):
        """Test that same password produces different hashes (salt)"""
        password = "same_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2  # Should be different due to salt
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

class TestTokenCreation:
    """Test cases for JWT token creation"""
    
    def test_create_access_token(self):
        """Test access token creation"""
        data = {"role": "patient", "user_id": 123}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify token
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["role"] == "patient"
        assert decoded["user_id"] == 123
        assert decoded["type"] == "access"
        assert "exp" in decoded
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        data = {"role": "doctor", "user_id": 456}
        token = create_refresh_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify token
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["role"] == "doctor"
        assert decoded["user_id"] == 456
        assert decoded["type"] == "refresh"
    
    def test_create_token_with_custom_expiry(self):
        """Test token creation with custom expiry"""
        data = {"role": "admin", "user_id": 1}
        custom_expiry = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=custom_expiry)
        
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        # Should expire in approximately 60 minutes
        time_diff = exp_time - now
        assert 59 <= time_diff.total_seconds() / 60 <= 61
    
    def test_token_expiration_time(self):
        """Test that tokens have correct expiration times"""
        data = {"role": "patient", "user_id": 123}
        
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)
        
        access_decoded = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        refresh_decoded = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        access_exp = datetime.fromtimestamp(access_decoded["exp"], tz=timezone.utc)
        refresh_exp = datetime.fromtimestamp(refresh_decoded["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        # Access token should expire in ~30 minutes
        access_diff = (access_exp - now).total_seconds() / 60
        assert ACCESS_TOKEN_EXPIRE_MINUTES - 1 <= access_diff <= ACCESS_TOKEN_EXPIRE_MINUTES + 1
        
        # Refresh token should expire much later
        refresh_diff = (refresh_exp - now).total_seconds() / 60
        assert refresh_diff > access_diff

class TestTokenDecoding:
    """Test cases for JWT token decoding"""
    
    def test_decode_valid_token(self):
        """Test decoding a valid token"""
        data = {"role": "patient", "user_id": 123, "type": "access"}
        token = create_access_token({"role": "patient", "user_id": 123})
        
        decoded = decode_token(token)
        assert decoded is not None
        assert decoded["role"] == "patient"
        assert decoded["user_id"] == 123
        assert decoded["type"] == "access"
    
    def test_decode_invalid_token(self):
        """Test decoding an invalid token"""
        invalid_token = "invalid.token.here"
        decoded = decode_token(invalid_token)
        assert decoded is None
    
    def test_decode_expired_token(self):
        """Test decoding an expired token"""
        # Create token that expires immediately
        data = {"role": "patient", "user_id": 123}
        expired_token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        decoded = decode_token(expired_token)
        assert decoded is None
    
    def test_decode_malformed_token(self):
        """Test decoding a malformed token"""
        malformed_tokens = [
            "",
            "not.a.token",
            "header.payload",  # Missing signature
            "too.many.parts.here.invalid"
        ]
        
        for token in malformed_tokens:
            decoded = decode_token(token)
            assert decoded is None

class TestGetCurrentUser:
    """Test cases for get_current_user function"""
    
    def test_get_current_user_valid_access_token(self):
        """Test getting current user with valid access token"""
        data = {"role": "patient", "user_id": 123}
        token = create_access_token(data)
        
        result = get_current_user(token, expected_type="access")
        assert result is not None
        assert result == ("patient", 123)
    
    def test_get_current_user_valid_refresh_token(self):
        """Test getting current user with valid refresh token"""
        data = {"role": "doctor", "user_id": 456}
        token = create_refresh_token(data)
        
        result = get_current_user(token, expected_type="refresh")
        assert result is not None
        assert result == ("doctor", 456)
    
    def test_get_current_user_wrong_token_type(self):
        """Test getting current user with wrong token type"""
        data = {"role": "patient", "user_id": 123}
        access_token = create_access_token(data)
        
        # Try to use access token as refresh token
        result = get_current_user(access_token, expected_type="refresh")
        assert result is None
    
    def test_get_current_user_no_type_check(self):
        """Test getting current user without type checking"""
        data = {"role": "admin", "user_id": 1}
        token = create_access_token(data)
        
        result = get_current_user(token)  # No expected_type
        assert result is not None
        assert result == ("admin", 1)
    
    def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token"""
        invalid_token = "invalid.token.here"
        result = get_current_user(invalid_token)
        assert result is None
    
    def test_get_current_user_missing_claims(self):
        """Test getting current user with token missing required claims"""
        # Create token with missing claims
        incomplete_data = {"role": "patient"}  # Missing user_id
        token = jwt.encode(incomplete_data, SECRET_KEY, algorithm=ALGORITHM)
        
        result = get_current_user(token)
        assert result is None

class TestAuthConfiguration:
    """Test cases for authentication configuration"""
    
    def test_secret_key_exists(self):
        """Test that SECRET_KEY is set"""
        assert SECRET_KEY is not None
        assert len(SECRET_KEY) > 0
        assert SECRET_KEY != "change-me"  # Should be changed in production
    
    def test_algorithm_is_hs256(self):
        """Test that algorithm is HS256"""
        assert ALGORITHM == "HS256"
    
    def test_token_expire_times_are_positive(self):
        """Test that token expiration times are positive integers"""
        assert isinstance(ACCESS_TOKEN_EXPIRE_MINUTES, int)
        assert ACCESS_TOKEN_EXPIRE_MINUTES > 0
        assert isinstance(REFRESH_TOKEN_EXPIRE_MINUTES, int)
        assert REFRESH_TOKEN_EXPIRE_MINUTES > 0
        assert REFRESH_TOKEN_EXPIRE_MINUTES > ACCESS_TOKEN_EXPIRE_MINUTES
    
    def test_admin_token_exists(self):
        """Test that ADMIN_TOKEN is set"""
        assert ADMIN_TOKEN is not None
        assert len(ADMIN_TOKEN) > 0
        assert ADMIN_TOKEN != "admin-change-me"  # Should be changed in production

class TestTokenSecurity:
    """Test cases for token security features"""
    
    def test_tokens_are_different_for_same_data(self):
        """Test that tokens created at different times are different"""
        data = {"role": "patient", "user_id": 123}
        
        token1 = create_access_token(data)
        # Small delay to ensure different timestamps
        import time
        time.sleep(0.001)
        token2 = create_access_token(data)
        
        assert token1 != token2  # Should be different due to timestamp
    
    def test_token_cannot_be_modified(self):
        """Test that modified tokens are rejected"""
        data = {"role": "patient", "user_id": 123}
        token = create_access_token(data)
        
        # Try to modify the token
        parts = token.split('.')
        if len(parts) == 3:
            # Modify the payload
            modified_token = parts[0] + '.modified_payload.' + parts[2]
            decoded = decode_token(modified_token)
            assert decoded is None
    
    def test_different_secret_key_fails(self):
        """Test that tokens created with different secret key fail"""
        data = {"role": "patient", "user_id": 123}
        
        # Create token with different secret
        different_secret = "different_secret_key"
        fake_token = jwt.encode(data, different_secret, algorithm=ALGORITHM)
        
        # Should fail to decode with correct secret
        decoded = decode_token(fake_token)
        assert decoded is None

if __name__ == "__main__":
    pytest.main([__file__])
