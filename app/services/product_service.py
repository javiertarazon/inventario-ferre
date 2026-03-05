"""
Product Service - Business logic for product management.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from app.models import Product, Supplier
from app.repositories import ProductRepository, SupplierRepository
from app.services.validation_service import ValidationService
from app.utils.exceptions import ValidationError, NotFoundError, DatabaseError, BusinessLogicError
from app.extensions import db


class ProductService:
    """Service for managing product business logic."""
    
    def __init__(self):
        """Initialize product service with dependencies."""
        self.product_repo = ProductRepository()
        self.supplier_repo = SupplierRepository()
        self.validation_service = ValidationService()
    
    def create_product(self, data: Dict[str, Any], user_id: int) -> Product:
        """
        Create new product with validation.
        
        Args:
            data: Product data dictionary
            user_id: ID of user creating the product
            
        Returns:
            Created product instance
            
        Raises:
            ValidationError: If data validation fails
            DatabaseError: If database operation fails
        """
        try:
            # Validate product data
            validated_data = self.validation_service.validate_product_data(data)
            
            # Generate product code if not provided
            if 'codigo' not in validated_data or not validated_data['codigo']:
                validated_data['codigo'] = self._generate_product_code(
                    validated_data.get('rubro', 'A'),
                    validated_data.get('iniciales', 'XX')
                )
            
            # Check if product code already exists
            existing = self.product_repo.get_by_codigo(validated_data['codigo'])
            if existing and existing.deleted_at is None:
                raise ValidationError(
                    f"Ya existe un producto con el código {validated_data['codigo']}",
                    field='codigo'
                )
            
            # Set audit fields
            validated_data['created_by'] = user_id
            validated_data['updated_by'] = user_id
            validated_data['created_at'] = datetime.utcnow()
            validated_data['updated_at'] = datetime.utcnow()
            
            # Create product
            product = Product(**validated_data)
            created_product = self.product_repo.create(product)
            
            current_app.logger.info(
                f"Product created: {created_product.codigo} by user {user_id}"
            )
            
            return created_product
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error creating product: {str(e)}")
            raise DatabaseError("Error al crear el producto", original_error=e)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error creating product: {str(e)}")
            raise BusinessLogicError(f"Error inesperado al crear el producto: {str(e)}")
    
    def update_product(self, product_id: int, data: Dict[str, Any], user_id: int) -> Product:
        """
        Update existing product with validation.
        
        Args:
            product_id: ID of product to update
            data: Updated product data
            user_id: ID of user updating the product
            
        Returns:
            Updated product instance
            
        Raises:
            NotFoundError: If product not found
            ValidationError: If data validation fails
            DatabaseError: If database operation fails
        """
        try:
            # Get existing product
            product = self.product_repo.get_by_id(product_id)
            if not product or product.deleted_at is not None:
                raise NotFoundError("Product", product_id)
            
            # Validate update data
            validated_data = self.validation_service.validate_product_data(data, is_update=True)
            
            # Check if codigo is being changed and if new code exists
            if 'codigo' in validated_data and validated_data['codigo'] != product.codigo:
                existing = self.product_repo.get_by_codigo(validated_data['codigo'])
                if existing and existing.id != product_id and existing.deleted_at is None:
                    raise ValidationError(
                        f"Ya existe un producto con el código {validated_data['codigo']}",
                        field='codigo'
                    )
            
            # Update fields
            for key, value in validated_data.items():
                if hasattr(product, key):
                    setattr(product, key, value)
            
            # Set audit fields
            product.updated_by = user_id
            product.updated_at = datetime.utcnow()
            
            # Save changes
            updated_product = self.product_repo.update(product)
            
            # Refresh to load relationships
            db.session.refresh(updated_product)
            
            current_app.logger.info(
                f"Product updated: {updated_product.codigo} by user {user_id}"
            )
            
            return updated_product
            
        except (NotFoundError, ValidationError):
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error updating product: {str(e)}")
            raise DatabaseError("Error al actualizar el producto", original_error=e)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error updating product: {str(e)}")
            raise BusinessLogicError(f"Error inesperado al actualizar el producto: {str(e)}")
    
    def delete_product(self, product_id: int, user_id: int) -> bool:
        """
        Soft delete product.
        
        Args:
            product_id: ID of product to delete
            user_id: ID of user deleting the product
            
        Returns:
            True if deletion successful
            
        Raises:
            NotFoundError: If product not found
            DatabaseError: If database operation fails
        """
        try:
            # Get existing product
            product = self.product_repo.get_by_id(product_id)
            if not product or product.deleted_at is not None:
                raise NotFoundError("Product", product_id)
            
            # Soft delete
            product.deleted_at = datetime.utcnow()
            product.updated_by = user_id
            product.updated_at = datetime.utcnow()
            
            self.product_repo.update(product)
            
            current_app.logger.info(
                f"Product soft deleted: {product.codigo} by user {user_id}"
            )
            
            return True
            
        except NotFoundError:
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error deleting product: {str(e)}")
            raise DatabaseError("Error al eliminar el producto", original_error=e)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error deleting product: {str(e)}")
            raise BusinessLogicError(f"Error inesperado al eliminar el producto: {str(e)}")
    
    def get_product(self, product_id: int) -> Optional[Product]:
        """
        Get product by ID.
        
        Args:
            product_id: ID of product to retrieve
            
        Returns:
            Product instance or None if not found
        """
        product = self.product_repo.get_by_id(product_id)
        if product and product.deleted_at is None:
            return product
        return None
    
    def get_product_by_codigo(self, codigo: str) -> Optional[Product]:
        """
        Get product by codigo.
        
        Args:
            codigo: Product code
            
        Returns:
            Product instance or None if not found
        """
        product = self.product_repo.get_by_codigo(codigo)
        if product and product.deleted_at is None:
            return product
        return None
    
    def search_products(
        self,
        query: str = '',
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Search products with pagination.
        
        Performs full-text search across product names, descriptions,
        and codes with optional filtering and pagination support.
        
        Args:
            query: Search query string (searches product name, description, code)
            filters: Optional dictionary of additional filters (e.g., category_id, supplier_id)
            page: Page number for pagination (starting from 1)
            per_page: Number of items to return per page (default 20)
            
        Returns:
            Dictionary containing:
                - items: List of Product objects matching the search
                - total: Total count of matching products
                - pages: Total number of pages
                - current_page: Current page number
                - per_page: Items per page used
                
        Raises:
            BusinessLogicError: If search operation fails
        """
        try:
            # Validate pagination
            page, per_page = self.validation_service.validate_pagination(page, per_page)
            
            # Search products
            return self.product_repo.search_products(
                query=query,
                filters=filters or {},
                page=page,
                per_page=per_page
            )
            
        except Exception as e:
            current_app.logger.error(f"Error searching products: {str(e)}")
            raise BusinessLogicError(f"Error al buscar productos: {str(e)}")
    
    def get_low_stock_products(
        self,
        threshold: int = 10,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Get products with stock levels below threshold (inventory alert).
        
        Returns paginated list of products where current stock is less than
        the specified threshold, useful for inventory management and ordering.
        
        Args:
            threshold: Stock level threshold - products below this will be returned (default 10)
            page: Page number for pagination (starting from 1)
            per_page: Number of items to return per page (default 20)
            
        Returns:
            Dictionary containing:
                - items: List of Product objects with low stock
                - total: Total count of low stock products
                - pages: Total number of pages
                - current_page: Current page number
                - per_page: Items per page used
                
        Raises:
            BusinessLogicError: If query fails
        """
        try:
            return self.product_repo.get_low_stock_products(
                threshold=threshold,
                page=page,
                per_page=per_page
            )
        except Exception as e:
            current_app.logger.error(f"Error getting low stock products: {str(e)}")
            raise BusinessLogicError(f"Error al obtener productos con bajo stock: {str(e)}")
    
    def _generate_product_code(self, rubro: str, iniciales: str) -> str:
        """
        Generate unique product code.
        
        Args:
            rubro: Product category (1 character)
            iniciales: Product initials (2 characters)
            
        Returns:
            Generated product code in format X-XX-NN
        """
        # Get next number for this rubro-iniciales combination
        prefix = f"{rubro}-{iniciales}"
        
        # Find highest number for this prefix
        products = Product.query.filter(
            Product.codigo.like(f"{prefix}-%")
        ).all()
        
        max_num = 0
        for product in products:
            try:
                parts = product.codigo.split('-')
                if len(parts) == 3:
                    num = int(parts[2])
                    if num > max_num:
                        max_num = num
            except (ValueError, IndexError):
                continue
        
        # Generate next code
        next_num = max_num + 1
        return f"{prefix}-{next_num:02d}"

    def get_products_by_category(
        self,
        category_id: int,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Get all products in a specific category with pagination.
        
        Retrieves all active products that belong to the specified item group/category,
        excluding soft-deleted products.
        
        Args:
            category_id: ID of the item group/category to filter by
            page: Page number for pagination (starting from 1)
            per_page: Number of items to return per page (default 20)
            
        Returns:
            Dictionary containing:
                - items: List of Product objects in the category
                - total: Total count of products in category
                - pages: Total number of pages
                - current_page: Current page number
                - per_page: Items per page used
                
        Raises:
            DatabaseError: If database query fails
        """
        try:
            return self.product_repo.get_by_category(category_id, page=page, per_page=per_page)
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error getting products by category: {str(e)}")
            raise DatabaseError(f"Error al obtener productos por categoría: {str(e)}")
    
    def get_all_products(self) -> List[Product]:
        """
        Get all active products without pagination.
        
        Returns all products that are not soft-deleted. Use with caution
        on large datasets as no pagination is applied.
        
        Returns:
            List of all active Product objects
            
        Raises:
            DatabaseError: If database query fails
        """
        try:
            return self.product_repo.get_all_list()
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error getting all products: {str(e)}")
            raise DatabaseError(f"Error al obtener productos: {str(e)}")
