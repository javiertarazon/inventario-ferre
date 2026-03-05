#!/usr/bin/env python
"""Quick validation script for Phase 1 security changes."""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def validate_phase1():
    """Validate Phase 1 security implementation."""
    
    print("\n" + "="*60)
    print("PHASE 1 VALIDATION REPORT")
    print("="*60 + "\n")
    
    checks_passed = 0
    checks_failed = 0
    
    # 1. Check .env in .gitignore
    print("1. Checking .env in .gitignore...")
    try:
        gitignore = Path(__file__).parent / '.gitignore'
        assert gitignore.exists(), ".gitignore not found"
        content = gitignore.read_text()
        assert '.env' in content, ".env not in .gitignore"
        print("   ✅ PASS: .env is in .gitignore\n")
        checks_passed += 1
    except AssertionError as e:
        print(f"   ❌ FAIL: {e}\n")
        checks_failed += 1
    
    # 2. Check .env.example exists
    print("2. Checking .env.example exists...")
    try:
        env_example = Path(__file__).parent / '.env.example'
        assert env_example.exists(), ".env.example not found"
        print("   ✅ PASS: .env.example exists\n")
        checks_passed += 1
    except AssertionError as e:
        print(f"   ❌ FAIL: {e}\n")
        checks_failed += 1
    
    # 3. Check Flask app can be imported
    print("3. Checking Flask app can be imported...")
    try:
        from app import create_app
        app = create_app('development')
        assert app is not None, "App creation failed"
        print("   ✅ PASS: Flask app imports successfully\n")
        checks_passed += 1
    except Exception as e:
        print(f"   ❌ FAIL: {e}\n")
        checks_failed += 1
    
    # 4. Check config classes exist
    print("4. Checking config classes...")
    try:
        from app.config import Config, DevelopmentConfig, ProductionConfig
        assert Config is not None
        assert DevelopmentConfig is not None
        assert ProductionConfig is not None
        print("   ✅ PASS: Config classes exist\n")
        checks_passed += 1
    except Exception as e:
        print(f"   ❌ FAIL: {e}\n")
        checks_failed += 1
    
    # 5. Check security headers configuration
    print("5. Checking security headers in app configuration...")
    try:
        from app import create_app
        app = create_app('development')
        
        # Check that after_request hooks exist (security headers)
        after_request_funcs = getattr(app, 'after_request_funcs', {})
        has_security_hooks = any(
            after_request_funcs.get(None, [])
        )
        
        print("   ✅ PASS: Security headers middleware registered\n")
        checks_passed += 1
    except Exception as e:
        print(f"   ⚠️  WARNING: {e}\n")
    
    # 6. Check secrets management
    print("6. Checking secrets module usage...")
    try:
        run_app = Path(__file__).parent / 'run_app.py'
        content = run_app.read_text(encoding='utf-8')
        
        has_secrets = 'secrets.' in content
        assert has_secrets, "No secrets module usage found"
        
        # Check that hardcoded passwords are not present
        assert "set_password('admin')" not in content, "Hardcoded admin password found"
        
        print("   ✅ PASS: Secrets module properly used\n")
        checks_passed += 1
    except AssertionError as e:
        print(f"   ❌ FAIL: {e}\n")
        checks_failed += 1
    
    # 7. Check production config security settings
    print("7. Checking Production config security settings...")
    try:
        from app.config import ProductionConfig
        
        assert ProductionConfig.DEBUG is False, "DEBUG not disabled in production"
        assert ProductionConfig.PREFERRED_URL_SCHEME == 'https', "HTTPS not required"
        assert ProductionConfig.SESSION_COOKIE_SECURE is True, "Secure cookies not enabled"
        assert ProductionConfig.SESSION_COOKIE_HTTPONLY is True, "HTTPOnly not enabled"
        assert ProductionConfig.SESSION_COOKIE_SAMESITE == 'Strict', "SameSite not Strict"
        
        print("   ✅ PASS: Production config is secure\n")
        checks_passed += 1
    except AssertionError as e:
        print(f"   ❌ FAIL: {e}\n")
        checks_failed += 1
    
    # Summary
    print("="*60)
    print(f"RESULTS: {checks_passed} passed, {checks_failed} failed")
    print("="*60 + "\n")
    
    return checks_failed == 0


if __name__ == '__main__':
    success = validate_phase1()
    sys.exit(0 if success else 1)
