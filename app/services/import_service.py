"""
Import Service - Business logic for importing inventory from files.
"""
import pandas as pd
from typing import Dict, Any, List, Tuple
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename
import os

from app.models import Product
from app.services import ProductService
from app.utils.exceptions import ValidationError, BusinessLogicError
from app.extensions import db


class ImportService:
    """Service for importing inventory data from Excel/CSV files."""
    
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
    
    def __init__(self):
        """Initialize import service."""
        self.product_service = ProductService()
    
    def allowed_file(self, filename: str) -> bool:
        """
        Check if file extension is allowed.
        
        Args:
            filename: Name of the file
            
        Returns:
            True if extension is allowed
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def import_from_file(self, file, user_id: int) -> Dict[str, Any]:
        """
        Import products from Excel or CSV file.
        
        Args:
            file: File object from request
            user_id: ID of user performing import
            
        Returns:
            Dictionary with import results
            
        Raises:
            ValidationError: If file format is invalid
            BusinessLogicError: If import fails
        """
        if not file or file.filename == '':
            raise ValidationError('No se seleccionó ningún archivo')
        
        if not self.allowed_file(file.filename):
            raise ValidationError('Formato de archivo no permitido. Use XLSX, XLS o CSV')
        
        try:
            # Save file temporarily
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Read file based on extension
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath, header=1)  # Skip first row (headers)
            
            # Process data
            results = self._process_dataframe(df, user_id)
            
            # Clean up temporary file
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return results
            
        except pd.errors.EmptyDataError:
            raise ValidationError('El archivo está vacío')
        except Exception as e:
            current_app.logger.error(f"Error importing file: {str(e)}")
            raise BusinessLogicError(f'Error al importar archivo: {str(e)}')
    
    def _process_dataframe(self, df: pd.DataFrame, user_id: int) -> Dict[str, Any]:
        """
        Process dataframe and create/update products.
        
        Args:
            df: Pandas dataframe with product data
            user_id: ID of user performing import
            
        Returns:
            Dictionary with import statistics
        """
        created = 0
        updated = 0
        errors = []
        
        # Expected columns (flexible matching)
        codigo_col = self._find_column(df, ['codigo', 'code', 'código'])
        desc_col = self._find_column(df, ['descripcion', 'description', 'descripción', 'producto'])
        stock_col = self._find_column(df, ['stock', 'cantidad', 'existencia', 'inv.final'])
        price_col = self._find_column(df, ['precio', 'price', 'precio_dolares', 'costo unitario'])
        
        if not all([codigo_col, desc_col]):
            raise ValidationError('El archivo debe contener al menos columnas de Código y Descripción')
        
        for index, row in df.iterrows():
            try:
                # Skip empty rows
                if pd.isna(row[codigo_col]) or str(row[codigo_col]).strip() == '':
                    continue
                
                codigo = str(row[codigo_col]).strip()
                descripcion = str(row[desc_col]).strip() if not pd.isna(row[desc_col]) else codigo
                
                # Get optional fields
                stock = int(row[stock_col]) if stock_col and not pd.isna(row[stock_col]) else 0
                precio = float(row[price_col]) if price_col and not pd.isna(row[price_col]) else 0.0
                
                # Check if product exists
                existing_product = Product.query.filter_by(codigo=codigo, deleted_at=None).first()
                
                if existing_product:
                    # Update existing product
                    data = {
                        'descripcion': descripcion,
                        'stock': stock,
                        'precio_dolares': precio if precio > 0 else existing_product.precio_dolares
                    }
                    self.product_service.update_product(existing_product.id, data, user_id)
                    updated += 1
                else:
                    # Create new product
                    data = {
                        'codigo': codigo,
                        'descripcion': descripcion,
                        'stock': stock,
                        'precio_dolares': precio if precio > 0 else 1.0,
                        'factor_ajuste': 1.0
                    }
                    self.product_service.create_product(data, user_id)
                    created += 1
                    
            except Exception as e:
                errors.append(f"Fila {index + 2}: {str(e)}")
                current_app.logger.warning(f"Error processing row {index}: {str(e)}")
        
        return {
            'created': created,
            'updated': updated,
            'errors': errors,
            'total_processed': created + updated
        }
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> str:
        """
        Find column name from list of possible names (case-insensitive).
        
        Args:
            df: Pandas dataframe
            possible_names: List of possible column names
            
        Returns:
            Actual column name or None
        """
        df_columns_lower = {col.lower(): col for col in df.columns}
        
        for name in possible_names:
            if name.lower() in df_columns_lower:
                return df_columns_lower[name.lower()]
        
        return None
    
    def export_inventory_report(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Generate inventory report in Art 177 format with prices in Bolivares.
        
        Args:
            start_date: Start date for report
            end_date: End date for report
            
        Returns:
            Pandas dataframe with formatted report
        """
        from app.models import Movement, ExchangeRate
        
        # Get current exchange rate
        current_rate = ExchangeRate.get_current_rate()
        exchange_rate = float(current_rate.rate) if current_rate else 36.50
        
        # Get all products
        products = Product.query.filter_by(deleted_at=None).order_by(Product.codigo).all()
        
        report_data = []
        
        for product in products:
            # Get movements in date range
            movements = Movement.query.filter(
                Movement.producto_id == product.id,
                Movement.fecha >= start_date,
                Movement.fecha <= end_date,
                Movement.deleted_at == None
            ).all()
            
            # Calculate initial stock (stock before start_date)
            initial_movements = Movement.query.filter(
                Movement.producto_id == product.id,
                Movement.fecha < start_date,
                Movement.deleted_at == None
            ).all()
            
            initial_stock = 0
            for mov in initial_movements:
                if mov.tipo == 'entrada':
                    initial_stock += mov.cantidad
                elif mov.tipo == 'salida':
                    initial_stock -= mov.cantidad
            
            # Calculate entries and exits
            entries_qty = sum(m.cantidad for m in movements if m.tipo == 'entrada')
            exits_qty = sum(m.cantidad for m in movements if m.tipo == 'salida')
            
            # Calculate price in Bolivares with adjustment factor
            precio_bs = float(product.precio_dolares) * exchange_rate * float(product.factor_ajuste)
            
            # Calculate amounts in Bolivares
            initial_amount = initial_stock * precio_bs
            entries_amount = entries_qty * precio_bs
            exits_amount = exits_qty * precio_bs
            final_stock = initial_stock + entries_qty - exits_qty
            final_amount = final_stock * precio_bs
            
            report_data.append({
                'Código': product.codigo,
                'Descripción': product.descripcion,
                'Unidad de Medida': 'UND',
                'Existencia Inicial - Cantidad': initial_stock,
                'Existencia Inicial - Costo Unitario (Bs)': round(precio_bs, 2),
                'Existencia Inicial - Monto (Bs)': round(initial_amount, 2),
                'Entradas - Cantidad': entries_qty,
                'Entradas - Costo Unitario (Bs)': round(precio_bs, 2),
                'Entradas - Monto (Bs)': round(entries_amount, 2),
                'Salidas - Cantidad': exits_qty,
                'Salidas - Costo Unitario (Bs)': round(precio_bs, 2),
                'Salidas - Monto (Bs)': round(exits_amount, 2),
                'Autoconsumos - Cantidad': 0,
                'Autoconsumos - Costo Unitario (Bs)': 0,
                'Autoconsumos - Monto (Bs)': 0,
                'Retiro - Cantidad': 0,
                'Retiro - Costo Unitario (Bs)': 0,
                'Retiro - Monto (Bs)': 0,
                'Inv.final - Cantidad': final_stock,
                'Inv.final - Costo Unitario (Bs)': round(precio_bs, 2),
                'Inv.final - Monto (Bs)': round(final_amount, 2)
            })
        
        return pd.DataFrame(report_data)
