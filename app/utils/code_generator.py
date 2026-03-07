"""
Code Generator utility for automatic product code generation.
"""
import re
from typing import Optional
from app.models import Product, ItemGroup
from app.extensions import db


class CodeGenerator:
    """Generate product codes based on category and description."""
    
    # Mapping of category names to code prefixes
    CATEGORY_PREFIXES = {
        'Electricidad': 'E',
        'Plomeria': 'P',
        'Albañileria': 'A',
        'Carpinteria': 'C',
        'Herreria': 'H',
        'Tornilleria': 'T',
        'Miselaneos': 'M'
    }
    
    @staticmethod
    def clean_word(word: str) -> str:
        """
        Clean word by removing special characters and accents.
        
        Args:
            word: Word to clean
            
        Returns:
            Cleaned word in uppercase
        """
        # Remove accents
        replacements = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N'
        }
        
        for old, new in replacements.items():
            word = word.replace(old, new)
        
        # Remove special characters, keep only letters and numbers
        word = re.sub(r'[^a-zA-Z0-9]', '', word)
        
        return word.upper()
    
    @staticmethod
    def get_description_initials(description: str) -> str:
        """
        Get initials from the first two words of description.
        
        Args:
            description: Product description
            
        Returns:
            Two-letter code from first two words (e.g., "MC" from "Martillo Carpintero")
        """
        # Split description into words
        words = description.strip().split()

        # Clean words and keep only valid tokens
        cleaned_words = [CodeGenerator.clean_word(w) for w in words]
        cleaned_words = [w for w in cleaned_words if w]

        # Prefer initials from words that start with letters (avoid numeric initials like "3").
        alpha_words = [w for w in cleaned_words if w[0].isalpha()]

        if len(alpha_words) >= 2:
            return f"{alpha_words[0][0]}{alpha_words[1][0]}"

        if len(alpha_words) == 1:
            return f"{alpha_words[0][0]}X"

        if len(cleaned_words) >= 2:
            first = cleaned_words[0][0] if cleaned_words[0][0].isalpha() else 'X'
            second = cleaned_words[1][0] if cleaned_words[1][0].isalpha() else 'X'
            return f"{first}{second}"

        if len(cleaned_words) == 1:
            first = cleaned_words[0][0] if cleaned_words[0][0].isalpha() else 'X'
            return f"{first}X"

        return "XX"
    
    @staticmethod
    def get_next_sequence(category_prefix: str, description_initials: str) -> int:
        """
        Get next sequence number for a given prefix and initials.
        
        Args:
            category_prefix: Category prefix (E, P, A, etc.)
            description_initials: Description initials (SO, CO, etc.)
            
        Returns:
            Next sequence number
        """
        # Build pattern to search for existing codes
        pattern = f"{category_prefix}-{description_initials}-%"
        
        # Find all products with similar codes
        existing_products = Product.query.filter(
            Product.codigo.like(pattern),
            Product.deleted_at == None
        ).all()
        
        if not existing_products:
            return 1

        # Extract used sequence numbers (2-digit only)
        used_sequences = set()
        for product in existing_products:
            # Extract number from code (e.g., "E-SO-03" -> 3)
            parts = product.codigo.split('-')
            if len(parts) == 3:
                try:
                    sequence = int(parts[2])
                    if 1 <= sequence <= 99:
                        used_sequences.add(sequence)
                except ValueError:
                    continue

        for sequence in range(1, 100):
            if sequence not in used_sequences:
                return sequence

        raise ValueError(f"No hay correlativos disponibles para {category_prefix}-{description_initials}")
    
    @staticmethod
    def generate_code(category_name: str, description: str) -> str:
        """
        Generate product code based on category and description.
        
        Format: {CATEGORY_PREFIX}-{INITIALS}-{SEQUENCE}
        Example: E-SO-01 (Electricidad - Socates ...)
        
        Args:
            category_name: Name of the category
            description: Product description
            
        Returns:
            Generated product code
        """
        # Get category prefix
        category_prefix = CodeGenerator.CATEGORY_PREFIXES.get(category_name, 'X')
        
        # Get description initials from first two words.
        description_initials = CodeGenerator.get_description_initials(description)

        # Get next sequence number (1..99)
        sequence = CodeGenerator.get_next_sequence(category_prefix, description_initials)

        return f"{category_prefix}-{description_initials}-{sequence:02d}"
    
    @staticmethod
    def generate_code_from_item_group_id(item_group_id: int, description: str) -> str:
        """
        Generate product code based on item group ID and description.
        
        Args:
            item_group_id: ID of the item group (category)
            description: Product description
            
        Returns:
            Generated product code
        """
        # Get item group
        item_group = ItemGroup.query.get(item_group_id)
        
        if not item_group:
            # Default to 'X' if category not found
            return CodeGenerator.generate_code('Unknown', description)
        
        return CodeGenerator.generate_code(item_group.name, description)
