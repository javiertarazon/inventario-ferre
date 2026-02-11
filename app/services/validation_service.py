"""
Validation Service Module

This module provides centralized validation and sanitization for all user inputs.
Implements comprehensive validation rules for products, suppliers, movements, and file uploads.
"""

import re
from typing import Dict, Any, Optional, List
from decimal import Decimal, InvalidOperation
from datetime import datetime
import bleach
from werkzeug.datastructures import FileStorage

from app.utils.exceptions import ValidationError


class ValidationService:
    """
    Service for validating and sanitizing user inputs.
    
    Provides validation methods for:
    - Product data (codes, prices, stock)
    - Supplier data (RIF format, contact info)
    - Movement data (quantities, dates)
    - File uploads (type, size, content)
    - String sanitization (XSS prevention)
    """
    
    # Product code format: X-XX-XX (e.g., A-BC-01)
    PRODUCT_CODE_PATTERN = re.compile(r'^[A-Z]-[A-Z]{2}-\d{2}$')
    
    # Venezuelan RIF format: J-12345678-9 or V-12345678-9
    RIF_PATTERN = re.compile(r'^[JVEGP]-\d{8,9}-\d$')
    
    # Allowed file extensions for uploads
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
    
    # Maximum file size: 10MB
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Allowed HTML tags for sanitization (very restrictive)
    ALLOWED_TAGS = []
    ALLOWED_ATTRIBUTES = {}
    
    def __init__(self):
        """Initialize validation service."""
        pass
    
    def validate_product_data(self, data: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
        """Validate product data."""
        errors = []
        validated_data = {}
        
        # Validate codigo (optional for updates if not provided)
        codigo = data.get('codigo', '').strip()
        if codigo:
            codigo_result = self.validate_product_code(codigo)
            if codigo_result:
                errors.append(codigo_result)
            else:
                validated_data['codigo'] = codigo.upper()
        elif not is_update:
            # Codigo is optional for create (will be auto-generated)
            pass
        
        # Validate descripcion (optional for updates)
        descripcion = data.get('descripcion', '').strip()
        if descripcion:
            if len(descripcion) > 200:
                errors.append("La descripción no puede exceder 200 caracteres")
            else:
                validated_data['descripcion'] = self.sanitize_string(descripcion)
        elif not is_update:
            errors.append("La descripción del producto es requerida")
        
        # Validate stock
        stock = data.get('stock')
        if stock is None:
            validated_data['stock'] = 0
        else:
            try:
                stock_value = int(stock)
                if stock_value < 0:
                    errors.append("El stock no puede ser negativo")
                else:
                    validated_data['stock'] = stock_value
            except (ValueError, TypeError):
                errors.append("El stock debe ser un número entero válido")
        
        # Validate precio_dolares
        precio_dolares = data.get('precio_dolares')
        if precio_dolares is None:
            validated_data['precio_dolares'] = Decimal('0.00')
        else:
            try:
                precio_value = Decimal(str(precio_dolares))
                if precio_value < 0:
                    errors.append("El precio no puede ser negativo")
                else:
                    validated_data['precio_dolares'] = precio_value
            except (InvalidOperation, ValueError, TypeError):
                errors.append("El precio debe ser un número válido")
        
        # Validate factor_ajuste
        factor_ajuste = data.get('factor_ajuste')
        if factor_ajuste is None:
            validated_data['factor_ajuste'] = Decimal('1.00')
        else:
            try:
                factor_value = Decimal(str(factor_ajuste))
                if factor_value <= 0:
                    errors.append("El factor de ajuste debe ser mayor que cero")
                else:
                    validated_data['factor_ajuste'] = factor_value
            except (InvalidOperation, ValueError, TypeError):
                errors.append("El factor de ajuste debe ser un número válido")
        
        # Validate proveedor_id
        proveedor_id = data.get('proveedor_id')
        if proveedor_id is not None:
            try:
                validated_data['proveedor_id'] = int(proveedor_id)
            except (ValueError, TypeError):
                errors.append("El ID del proveedor debe ser un número entero válido")
        
        if errors:
            raise ValidationError("; ".join(errors))
        
        return validated_data

    def validate_supplier_data(self, data: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
        """Validate supplier data including Venezuelan RIF format."""
        errors = []
        validated_data = {}
        
        # Validate nombre (optional for updates)
        nombre = data.get('nombre', '').strip()
        if nombre:
            if len(nombre) > 200:
                errors.append("El nombre no puede exceder 200 caracteres")
            else:
                validated_data['nombre'] = self.sanitize_string(nombre)
        elif not is_update:
            errors.append("El nombre del proveedor es requerido")
        
        # Validate RIF (optional for updates)
        rif = data.get('rif', '').strip()
        if rif:
            rif_upper = rif.upper()
            if not self.RIF_PATTERN.match(rif_upper):
                errors.append("El formato del RIF es inválido. Debe ser: J-12345678-9 o V-12345678-9")
            else:
                validated_data['rif'] = rif_upper
        elif not is_update:
            errors.append("El RIF del proveedor es requerido")
        
        # Validate telefono
        telefono = data.get('telefono', '').strip()
        if telefono:
            if len(telefono) > 20:
                errors.append("El teléfono no puede exceder 20 caracteres")
            else:
                validated_data['telefono'] = self.sanitize_string(telefono)
        
        # Validate email
        email = data.get('email', '').strip()
        if email:
            if not self._validate_email(email):
                errors.append("El formato del email es inválido")
            elif len(email) > 255:
                errors.append("El email no puede exceder 255 caracteres")
            else:
                validated_data['email'] = email.lower()
        
        # Validate direccion
        direccion = data.get('direccion', '').strip()
        if direccion:
            if len(direccion) > 500:
                errors.append("La dirección no puede exceder 500 caracteres")
            else:
                validated_data['direccion'] = self.sanitize_string(direccion)
        
        if errors:
            raise ValidationError("; ".join(errors))
        
        return validated_data
    
    def validate_movement_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate movement data."""
        errors = []
        validated_data = {}
        
        # Validate producto_id
        producto_id = data.get('producto_id')
        if not producto_id:
            errors.append("El ID del producto es requerido")
        else:
            try:
                validated_data['producto_id'] = int(producto_id)
            except (ValueError, TypeError):
                errors.append("El ID del producto debe ser un número entero válido")
        
        # Validate tipo (accept both 'tipo' and 'tipo_movimiento' for compatibility)
        tipo = data.get('tipo') or data.get('tipo_movimiento', '').strip().upper()
        if not tipo:
            errors.append("El tipo de movimiento es requerido")
        elif tipo not in ['ENTRADA', 'SALIDA', 'AJUSTE']:
            errors.append("El tipo de movimiento debe ser: ENTRADA, SALIDA o AJUSTE")
        else:
            validated_data['tipo'] = tipo
        
        # Validate cantidad
        cantidad = data.get('cantidad')
        if cantidad is None:
            errors.append("La cantidad es requerida")
        else:
            try:
                cantidad_value = int(cantidad)
                if cantidad_value <= 0:
                    errors.append("La cantidad debe ser mayor que cero")
                else:
                    validated_data['cantidad'] = cantidad_value
            except (ValueError, TypeError):
                errors.append("La cantidad debe ser un número entero válido")
        
        # Validate fecha
        fecha = data.get('fecha')
        if fecha:
            if isinstance(fecha, str):
                try:
                    fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
                    validated_data['fecha'] = fecha_obj
                except ValueError:
                    errors.append("El formato de fecha es inválido. Use: YYYY-MM-DD")
            elif hasattr(fecha, 'date'):
                validated_data['fecha'] = fecha.date()
            else:
                validated_data['fecha'] = fecha
        
        # Validate descripcion (accept both 'descripcion' and 'motivo' for compatibility)
        descripcion = data.get('descripcion') or data.get('motivo', '').strip()
        if descripcion:
            if len(descripcion) > 500:
                errors.append("La descripción no puede exceder 500 caracteres")
            else:
                validated_data['descripcion'] = self.sanitize_string(descripcion)
        
        if errors:
            raise ValidationError("; ".join(errors))
        
        return validated_data

    def validate_file_upload(self, file: FileStorage) -> None:
        """Validate uploaded file (type, size, content)."""
        if not file:
            raise ValidationError("No se ha proporcionado ningún archivo")
        
        if not file.filename:
            raise ValidationError("El archivo no tiene nombre")
        
        # Check file extension
        if '.' not in file.filename:
            raise ValidationError("El archivo debe tener una extensión")
        
        extension = file.filename.rsplit('.', 1)[1].lower()
        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValidationError(
                f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > self.MAX_FILE_SIZE:
            max_mb = self.MAX_FILE_SIZE / (1024 * 1024)
            raise ValidationError(f"El archivo excede el tamaño máximo permitido de {max_mb}MB")
        
        if file_size == 0:
            raise ValidationError("El archivo está vacío")
    
    def sanitize_string(self, value: str) -> str:
        """Sanitize string input to prevent XSS attacks."""
        if not value:
            return value
        
        # Use bleach to remove all HTML tags and attributes
        sanitized = bleach.clean(
            value,
            tags=self.ALLOWED_TAGS,
            attributes=self.ALLOWED_ATTRIBUTES,
            strip=True
        )
        
        # Remove any remaining potentially dangerous characters
        sanitized = sanitized.replace('\x00', '')
        
        return sanitized.strip()
    
    def validate_product_code(self, code: str) -> Optional[str]:
        """Validate product code format (X-XX-XX)."""
        if not code:
            return "El código del producto es requerido"
        
        code_upper = code.upper().strip()
        
        if not self.PRODUCT_CODE_PATTERN.match(code_upper):
            return "El formato del código es inválido. Debe ser: X-XX-XX (ej: A-BC-01)"
        
        return None
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(email_pattern.match(email))
    
    def validate_date_range(self, start_date: Any, end_date: Any) -> tuple:
        """Validate and parse date range."""
        errors = []
        
        # Parse start_date
        if isinstance(start_date, str):
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                errors.append("El formato de fecha inicial es inválido. Use: YYYY-MM-DD")
        elif hasattr(start_date, 'date'):
            start_date = start_date.date()
        
        # Parse end_date
        if isinstance(end_date, str):
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                errors.append("El formato de fecha final es inválido. Use: YYYY-MM-DD")
        elif hasattr(end_date, 'date'):
            end_date = end_date.date()
        
        # Validate range
        if not errors and start_date > end_date:
            errors.append("La fecha inicial no puede ser posterior a la fecha final")
        
        if errors:
            raise ValidationError("; ".join(errors))
        
        return start_date, end_date
    
    def validate_pagination(self, page: Any, per_page: Any) -> tuple:
        """Validate pagination parameters."""
        errors = []
        
        try:
            page_int = int(page) if page else 1
            if page_int < 1:
                errors.append("El número de página debe ser mayor o igual a 1")
        except (ValueError, TypeError):
            errors.append("El número de página debe ser un entero válido")
            page_int = 1
        
        try:
            per_page_int = int(per_page) if per_page else 20
            if per_page_int < 1:
                errors.append("Los elementos por página deben ser mayor o igual a 1")
            elif per_page_int > 100:
                errors.append("Los elementos por página no pueden exceder 100")
        except (ValueError, TypeError):
            errors.append("Los elementos por página deben ser un entero válido")
            per_page_int = 20
        
        if errors:
            raise ValidationError("; ".join(errors))
        
        return page_int, per_page_int
