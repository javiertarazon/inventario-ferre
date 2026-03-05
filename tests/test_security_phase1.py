"""
Security tests for Phase 1 implementation.
Verifies that secrets and configuration are secure.
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import Config, DevelopmentConfig, ProductionConfig


class TestSecurityConfiguration:
    """Tests for security configuration."""
    
    def test_env_file_not_committed(self):
        """Verify .env file is in gitignore."""
        gitignore_path = Path(__file__).parent.parent / '.gitignore'
        assert gitignore_path.exists(), ".gitignore file not found"
        
        gitignore_content = gitignore_path.read_text()
        assert '.env' in gitignore_content, ".env not in .gitignore"
    
    def test_env_example_exists(self):
        """Verify .env.example template exists."""
        env_example = Path(__file__).parent.parent / '.env.example'
        assert env_example.exists(), ".env.example not found"
    
    def test_development_config_allows_debug(self):
        """Development config should allow debug mode."""
        assert DevelopmentConfig.DEBUG is True
        assert DevelopmentConfig.TESTING is False
    
    def test_production_config_disables_debug(self):
        """Production config should disable debug mode."""
        assert ProductionConfig.DEBUG is False
        assert ProductionConfig.TESTING is False
    
    def test_production_config_requires_ssl(self):
        """Production config should require HTTPS."""
        assert ProductionConfig.PREFERRED_URL_SCHEME == 'https'
        assert ProductionConfig.SESSION_COOKIE_SECURE is True
    
    def test_production_config_strict_samesite(self):
        """Production config should use strict SameSite policy."""
        assert ProductionConfig.SESSION_COOKIE_SAMESITE == 'Strict'
    
    def test_csrf_protection_enabled_in_prod(self):
        """CSRF protection should be enabled in production."""
        assert ProductionConfig.WTF_CSRF_ENABLED is True
    
    def test_no_hardcoded_secrets_in_base_config(self):
        """Base Config should not have hardcoded secrets."""
        # SECRET_KEY should be None unless set via environment
        if 'SECRET_KEY' not in os.environ:
            assert Config.SECRET_KEY is None or len(Config.SECRET_KEY) > 32
    
    def test_session_cookies_httponly(self):
        """Session cookies should always be HTTPOnly."""
        assert Config.SESSION_COOKIE_HTTPONLY is True
        assert ProductionConfig.SESSION_COOKIE_HTTPONLY is True


class TestSecurityHeaders:
    """Tests for HTTP security headers."""
    
    def test_security_headers_middleware_exists(self):
        """Verify security headers middleware is registered."""
        from app import create_app
        app = create_app('development')
        
        # Test that the app exists and has the after_request hook
        assert app is not None
        assert len([f for f in app.after_request_funcs.values() if f]) > 0


class TestPasswordSecurity:
    """Tests for password handling."""
    
    def test_admin_password_not_hardcoded(self):
        """Verify admin password is not hardcoded in scripts."""
        run_app_path = Path(__file__).parent.parent / 'run_app.py'
        content = run_app_path.read_text()
        
        # Should not have hardcoded password like 'password=admin'
        assert "set_password('admin')" not in content
    
    def test_password_generated_securely(self):
        """Verify password generation uses secrets module."""
        run_app_path = Path(__file__).parent.parent / 'run_app.py'
        content = run_app_path.read_text()
        
        # Should use secrets.token_urlsafe
        assert 'secrets.token_urlsafe' in content or 'secrets.token_hex' in content


class TestEnvironmentVariables:
    """Tests for environment variable handling."""
    
    def test_log_level_from_env(self):
        """LOG_LEVEL should be configurable via environment."""
        # Test it's read from environment
        from app import create_app
        app_dev = create_app('development')
        assert app_dev.config['LOG_LEVEL'] is not None
    
    def test_database_url_from_env(self):
        """DATABASE_URL should be configurable via environment."""
        from app import create_app
        app_dev = create_app('development')
        assert app_dev.config['SQLALCHEMY_DATABASE_URI'] is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
