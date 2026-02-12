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
        Get initials from first two words of description.
        
        Args:
            description: Product description
            
        Returns:
            Two-letter code from description (e.g., "SO-PO" from "Socates Porcelana")
        """
        # Split description into words
        words = description.strip().split()
        
        # Filter out very short words (prepositions, articles)
        meaningful_words = [w for w in words if len(w) > 2]
        
        # If we don't have enough meaningful words, use all words
        if len(meaningful_words) < 2:
            meaningful_words = words
        
        # Get first two words
        first_word = meaningful_words[0] if len(meaningful_words) > 0 else 'XX'
        second_word = meaningful_words[1] if len(meaningful_words) > 1 else 'XX'
        
        # Clean and get first 2 letters of each word
        first_initials = CodeGenerator.clean_word(first_word)[:2].ljust(2, 'X')
        second_initials = CodeGenerator.clean_word(second_word)[:2].ljust(2, 'X')
        
        return f"{first_initials}-{second_initials}"
    
    @staticmethod
    def get_next_sequence(category_prefix: str, description_initials: str) -> int:
        """
        Get next sequence number for a given prefix and initials.
        
        Args:
            category_prefix: Category prefix (E, P, A, etc.)
            description_initials: Description initials (SO-PO, CO-GA, etc.)
            
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
        
        # Extract sequence numbers
        max_sequence = 0
        for product in existing_products:
            # Extract number from code (e.g., "E-SO-PO-03" -> 3)
            parts = product.codigo.split('-')
            if len(parts) >= 4:
                try:
                    sequence = int(parts[3])
                    max_sequence = max(max_sequence, sequence)
                except ValueError:
                    continue
        
        return max_sequence + 1
    
    @staticmethod
    def generate_code(category_name: str, description: str) -> str:
        """
        Generate product code based on category and description.
        
        Format: {CATEGORY_PREFIX}-{FIRST_WORD_INITIALS}-{SECOND_WORD_INITIALS}-{SEQUENCE}
        Example: E-SO-PO-01 (Electricidad - Socates Porcelana)
        
        Args:
            category_name: Name of the category
            description: Product description
            
        Returns:
            Generated product code
        """
        # Get category prefix
        category_prefix = CodeGenerator.CATEGORY_PREFIXES.get(category_name, 'X')
        
        # Get description initials
        description_initials = CodeGenerator.get_description_initials(description)
        
        # Get next sequence number
        sequence = CodeGenerator.get_next_sequence(category_prefix, description_initials)
        
        # Build code
        code = f"{category_prefix}-{description_initials}-{sequence:02d}"
        
        return code
    
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
