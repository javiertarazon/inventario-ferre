#!/usr/bin/env python
"""
Script para generar secrets seguros para la aplicación.
Uso: python scripts/generate_secrets.py
"""

import secrets
import string
import sys

def generate_secret_key(length=32):
    """Generate a cryptographically secure secret key."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    # Exclude problematic characters for shell
    safe_chars = string.ascii_letters + string.digits + '_-'
    return ''.join(secrets.choice(safe_chars) for _ in range(length))

def main():
    """Generate and display secure secrets."""
    print("\n" + "="*70)
    print("GENERADOR DE SECRETS SEGUROS PARA FERRETERÍA INVENTARIO")
    print("="*70 + "\n")
    
    secret_key = generate_secret_key(43)
    jwt_key = generate_secret_key(43)
    
    print("Añade estos valores a tu archivo .env:\n")
    print(f"SECRET_KEY={secret_key}")
    print(f"JWT_SECRET_KEY={jwt_key}\n")
    
    print("="*70)
    print("⚠️  IMPORTANTE:")
    print("   - Guarda estos valores en lugar seguro")
    print("   - Usa diferentes valores para cada ambiente (dev, staging, prod)")
    print("   - Nunca compartas estos valores")
    print("   - Cambia los secrets cada cierto tiempo")
    print("="*70 + "\n")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
