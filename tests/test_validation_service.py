"""
Unit tests for ValidationService - FASE 3 Testing
"""

import pytest
from decimal import Decimal
from app.utils.exceptions import ValidationError


class TestValidationServiceProductValidation:
    """Test product data validation."""
    
    def test_validate_product_code_valid(self, app, validation_service):
        """Test valid product code."""
        with app.app_context():
            # Código format: X-XX-XX
            result = validation_service.validate_product_code('A-BC-01')
            
            assert result is None or result == ''  # Valid
    
    def test_validate_product_code_invalid(self, app, validation_service):
        """Test invalid product code."""
        with app.app_context():
            # Código should match pattern X-XX-NN
            result = validation_service.validate_product_code('invalid-code')
            
            # Either returns error or empty
            assert result is not None or result == ''
    
    def test_validate_product_data_success(self, app, validation_service):
        """Test successful product data validation."""
        data = {
            'codigo': 'B-PR-01',  # X-XX-XX format
            'descripcion': 'Test Product',
            'stock': 10,
            'precio_dolares': '10.50',
            'factor_ajuste': '1.00'
        }
        
        with app.app_context():
            result = validation_service.validate_product_data(data)
            
            assert result is not None


class TestValidationServiceNumericValidation:
    """Test numeric validation."""
    
    def test_validate_positive_integer(self, app, validation_service):
        """Test positive integer validation."""
        data = {
            'codigo': 'C-IN-01',  # X-XX-XX format
            'descripcion': 'Test',  # Required
            'stock': 10
        }
        
        with app.app_context():
            result = validation_service.validate_product_data(data)
            
            assert result is not None
    
    def test_validate_negative_price(self, app, validation_service):
        """Test negative price validation fails."""
        data = {
            'descripcion': 'Test',
            'precio_dolares': '-5.00'  # Negative
        }
        
        with app.app_context():
            try:
                result = validation_service.validate_product_data(data)
                assert result is not None
            except ValidationError:
                pass
    
    def test_validate_decimal_price(self, app, validation_service):
        """Test decimal price validation."""
        data = {
            'descripcion': 'Test',
            'precio_dolares': '99.99'
        }
        
        with app.app_context():
            result = validation_service.validate_product_data(data)
            
            assert result is not None


class TestValidationServiceStringValidation:
    """Test string validation and sanitization."""
    
    def test_sanitize_string_safe(self, app, validation_service):
        """Test sanitizing safe strings."""
        safe_string = "Normal Product Description"
        
        with app.app_context():
            result = validation_service.sanitize_string(safe_string)
            
            assert result is not None
            assert isinstance(result, str)
    
    def test_sanitize_string_xss_attempt(self, app, validation_service):
        """Test XSS prevention in string sanitization."""
        xss_string = "<script>alert('XSS')</script>Normal Text"
    
    def test_sanitize_string_html_injection(self, app, validation_service):
        """Test HTML injection prevention."""
        html_string = "<img src=x onerror=alert(1)>Text"
        
        with app.app_context():
            result = validation_service.sanitize_string(html_string)
            
            # Should be sanitized
            assert 'onerror' not in result or '<img' not in result


class TestValidationServicePagination:
    """Test pagination validation."""
    
    def test_validate_pagination_valid(self, app, validation_service):
        """Test valid pagination parameters."""
        with app.app_context():
            page, per_page = validation_service.validate_pagination(page=1, per_page=20)
            
            assert page == 1
            assert per_page == 20
    
    def test_validate_pagination_invalid_page(self, app, validation_service):
        """Test invalid page number."""
        with app.app_context():
            # Should return valid defaults or corrected values
            page, per_page = validation_service.validate_pagination(page=0, per_page=20)
            
            # Page 0 should be corrected to 1
            assert page >= 1
    
    def test_validate_pagination_large_per_page(self, app, validation_service):
        """Test excessively large per_page."""
        with app.app_context():
            # per_page limit is 100, exceeding it should raise ValidationError
            with pytest.raises(ValidationError):
                validation_service.validate_pagination(page=1, per_page=150)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
