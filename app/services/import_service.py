"""
Import Service - Business logic for importing inventory from files.
"""
import pandas as pd
from typing import Dict, Any, List, Tuple
from datetime import datetime
from decimal import Decimal
from flask import current_app
from werkzeug.utils import secure_filename
import os
import re
import unicodedata

from app.models import Product, ItemGroup, Proveedor
from app.models.daily_sales_closure import DailySalesClosure
from app.services.product_service import ProductService
from app.services.purchase_invoice_service import PurchaseInvoiceService
from app.services.daily_sales_closure_service import DailySalesClosureService
from app.utils.exceptions import ValidationError, BusinessLogicError
from app.utils.code_generator import CodeGenerator
from app.extensions import db


class ImportService:
    """Service for importing inventory data from Excel/CSV files."""
    
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
    CODE_PATTERN = re.compile(r'^[A-Z]-[A-Z]{2}-\d{2}$')
    
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
            filename, filepath = self._save_temp_file(file)
            df = self._read_dataframe(filepath, filename, header=2)
            
            # Process data
            results = self._process_dataframe(df, user_id)
            
            # Clean up temporary file
            self._cleanup_temp_file(filepath)
            
            return results
            
        except pd.errors.EmptyDataError:
            raise ValidationError('El archivo está vacío')
        except Exception as e:
            current_app.logger.error(f"Error importing file: {str(e)}")
            raise BusinessLogicError(f'Error al importar archivo: {str(e)}')

    def import_purchase_invoices_from_file(self, file, user_id: int) -> Dict[str, Any]:
        """Import supplier purchase invoices from CSV/Excel and register stock entries."""
        if not file or file.filename == '':
            raise ValidationError('No se seleccionó ningún archivo')

        if not self.allowed_file(file.filename):
            raise ValidationError('Formato de archivo no permitido. Use XLSX, XLS o CSV')

        try:
            filename, filepath = self._save_temp_file(file)
            df = self._read_dataframe(filepath, filename, header=0)
            results = self._process_purchase_invoices_dataframe(df, user_id)
            self._cleanup_temp_file(filepath)
            return results
        except pd.errors.EmptyDataError:
            raise ValidationError('El archivo está vacío')
        except Exception as e:
            current_app.logger.error(f"Error importing purchase invoices: {str(e)}")
            raise BusinessLogicError(f'Error al importar facturas de compra: {str(e)}')

    def import_daily_sales_closures_from_file(self, file, user_id: int) -> Dict[str, Any]:
        """Import daily closure totals and generate estimated exit movements."""
        if not file or file.filename == '':
            raise ValidationError('No se seleccionó ningún archivo')

        if not self.allowed_file(file.filename):
            raise ValidationError('Formato de archivo no permitido. Use XLSX, XLS o CSV')

        try:
            filename, filepath = self._save_temp_file(file)
            df = self._read_dataframe(filepath, filename, header=0)
            results = self._process_daily_closures_dataframe(df, user_id, filename)
            self._cleanup_temp_file(filepath)
            return results
        except pd.errors.EmptyDataError:
            raise ValidationError('El archivo está vacío')
        except Exception as e:
            current_app.logger.error(f"Error importing daily closures: {str(e)}")
            raise BusinessLogicError(f'Error al importar cierres diarios: {str(e)}')
    
    def _process_dataframe(self, df: pd.DataFrame, user_id: int) -> Dict[str, Any]:
        """
        Process dataframe and create/update products with automatic code generation.
        
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
        desc_col = self._find_column(df, ['descripcion', 'description', 'descripción', 'producto', 'descripcion del articulo'])
        stock_col = self._find_column(df, ['stock', 'cantidad', 'existencia', 'inv.final', 'cantidad unid/kg'])
        price_col = self._find_column(df, ['precio', 'price', 'precio_dolares', 'costo unitario', 'precio venta $'])
        category_col = self._find_column(df, ['categoria', 'category', 'categoría', 'item_group'])
        
        if not desc_col:
            raise ValidationError('El archivo debe contener al menos una columna de Descripción')
        
        # Get all categories for mapping
        categories = {cat.name: cat for cat in ItemGroup.query.filter_by(deleted_at=None).all()}
        existing_products = Product.query.filter_by(deleted_at=None).all()
        existing_by_description = {}
        for product in existing_products:
            description_key = self._normalize_description(product.descripcion)
            category_key = product.item_group_id
            existing_by_description[(description_key, category_key)] = product
        
        for index, row in df.iterrows():
            try:
                # Skip empty rows
                if pd.isna(row[desc_col]) or str(row[desc_col]).strip() == '':
                    continue
                
                descripcion = str(row[desc_col]).strip()
                descripcion_key = self._normalize_description(descripcion)
                
                # Get category
                item_group = None
                if category_col and not pd.isna(row[category_col]):
                    category_name = str(row[category_col]).strip()
                    item_group = categories.get(category_name)
                    
                    if not item_group:
                        errors.append(f"Fila {index + 2}: Categoría '{category_name}' no encontrada")
                        continue

                # Reuse existing product by description (and category when available)
                # to avoid creating duplicates on repeated imports.
                existing_by_description_product = existing_by_description.get(
                    (descripcion_key, item_group.id if item_group else None)
                )
                
                # Generate code automatically if category is provided
                if existing_by_description_product:
                    codigo = existing_by_description_product.codigo
                elif item_group:
                    codigo = CodeGenerator.generate_code(item_group.name, descripcion)
                elif codigo_col and not pd.isna(row[codigo_col]):
                    # Use provided code only if it matches expected format.
                    codigo_candidate = str(row[codigo_col]).strip().upper()
                    if self.CODE_PATTERN.match(codigo_candidate):
                        codigo = codigo_candidate
                    else:
                        codigo = CodeGenerator.generate_code('Unknown', descripcion)
                else:
                    codigo = CodeGenerator.generate_code('Unknown', descripcion)
                
                # Get optional fields
                stock = int(row[stock_col]) if stock_col and not pd.isna(row[stock_col]) else 0
                precio = float(row[price_col]) if price_col and not pd.isna(row[price_col]) else 0.0
                
                # Check if product exists by code
                existing_product = existing_by_description_product or Product.query.filter_by(
                    codigo=codigo,
                    deleted_at=None
                ).first()
                
                if existing_product:
                    # Update existing product
                    data = {
                        'descripcion': descripcion,
                        'stock': stock,
                        'precio_dolares': precio if precio > 0 else existing_product.precio_dolares,
                        'item_group_id': item_group.id if item_group else existing_product.item_group_id
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
                        'factor_ajuste': 1.0,
                        'item_group_id': item_group.id if item_group else None
                    }
                    created_product = self.product_service.create_product(data, user_id)
                    existing_by_description[(descripcion_key, item_group.id if item_group else None)] = created_product
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

    def _normalize_description(self, description: str) -> str:
        """Normalize description for duplicate detection during imports."""
        return ' '.join((description or '').strip().split()).upper()

    def _normalize_column_token(self, value: str) -> str:
        """Normalize column labels for flexible matching across CSV/Excel sources."""
        normalized = unicodedata.normalize('NFKD', str(value or '').strip())
        ascii_value = normalized.encode('ascii', 'ignore').decode('ascii')
        compact = re.sub(r'[^a-z0-9]+', ' ', ascii_value.lower()).strip()
        return re.sub(r'\s+', ' ', compact)
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> str:
        """
        Find column name from list of possible names (case-insensitive).
        
        Args:
            df: Pandas dataframe
            possible_names: List of possible column names
            
        Returns:
            Actual column name or None
        """
        df_columns_lower = {self._normalize_column_token(col): col for col in df.columns}
        
        for name in possible_names:
            normalized_name = self._normalize_column_token(name)
            if normalized_name in df_columns_lower:
                return df_columns_lower[normalized_name]
        
        return None

    def _save_temp_file(self, file) -> Tuple[str, str]:
        """Persist uploaded file in the configured uploads folder."""
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filename, filepath

    def _read_dataframe(self, filepath: str, filename: str, header: int = 0) -> pd.DataFrame:
        """Read a CSV/XLS/XLSX file into a dataframe."""
        if filename.lower().endswith('.csv'):
            return pd.read_csv(filepath)
        return pd.read_excel(filepath, header=header)

    def _cleanup_temp_file(self, filepath: str) -> None:
        """Delete temporary uploaded file if it still exists."""
        if os.path.exists(filepath):
            os.remove(filepath)

    def _process_purchase_invoices_dataframe(self, df: pd.DataFrame, user_id: int) -> Dict[str, Any]:
        """Convert tabular purchase rows into supplier invoices with inventory impact."""
        supplier_col = self._find_column(df, ['proveedor', 'supplier', 'supplier name', 'nombre proveedor'])
        invoice_number_col = self._find_column(df, ['numero factura', 'nro factura', 'factura', 'invoice number'])
        invoice_date_col = self._find_column(df, ['fecha factura', 'invoice date', 'fecha'])
        product_id_col = self._find_column(df, ['product id', 'producto id'])
        code_col = self._find_column(df, ['codigo', 'code', 'codigo producto'])
        description_col = self._find_column(df, ['descripcion', 'description', 'producto', 'descripcion producto'])
        quantity_col = self._find_column(df, ['cantidad', 'quantity'])
        unit_price_col = self._find_column(df, ['precio unitario', 'unit price', 'unitario', 'costo unitario'])
        subtotal_col = self._find_column(df, ['subtotal', 'sub total'])
        taxable_base_col = self._find_column(df, ['base imponible', 'taxable base'])
        tax_col = self._find_column(df, ['iva', 'impuesto', 'tax amount'])
        total_col = self._find_column(df, ['total', 'monto total'])
        notes_col = self._find_column(df, ['observaciones', 'notas', 'notes'])

        missing_fields = []
        if not supplier_col:
            missing_fields.append('Proveedor')
        if not invoice_number_col:
            missing_fields.append('Número de factura')
        if not invoice_date_col:
            missing_fields.append('Fecha de factura')
        if not quantity_col:
            missing_fields.append('Cantidad')
        if not unit_price_col:
            missing_fields.append('Precio unitario')
        if not any([product_id_col, code_col, description_col]):
            missing_fields.append('Producto (ID, código o descripción)')

        if missing_fields:
            raise ValidationError(
                'Faltan columnas requeridas para facturas de compra: ' + ', '.join(missing_fields)
            )

        created = 0
        items_processed = 0
        errors = []
        grouped_invoices: Dict[Tuple[str, str], Dict[str, Any]] = {}
        purchase_service = PurchaseInvoiceService()
        suppliers_cache: Dict[str, Proveedor] = {}

        products_by_id = {str(product.id): product for product in Product.query.filter_by(deleted_at=None).all()}
        products_by_code = {
            self._normalize_column_token(product.codigo): product
            for product in Product.query.filter_by(deleted_at=None).all()
            if product.codigo
        }
        products_by_description = {
            self._normalize_description(product.descripcion): product
            for product in Product.query.filter_by(deleted_at=None).all()
            if product.descripcion
        }

        for index, row in df.iterrows():
            try:
                supplier_name = str(row[supplier_col]).strip() if not pd.isna(row[supplier_col]) else ''
                invoice_number = str(row[invoice_number_col]).strip() if not pd.isna(row[invoice_number_col]) else ''
                invoice_date = str(row[invoice_date_col]).strip() if not pd.isna(row[invoice_date_col]) else ''

                if not supplier_name or not invoice_number or not invoice_date:
                    raise ValidationError('Proveedor, número y fecha de factura son obligatorios')

                product = self._resolve_import_product(
                    row=row,
                    product_id_col=product_id_col,
                    code_col=code_col,
                    description_col=description_col,
                    products_by_id=products_by_id,
                    products_by_code=products_by_code,
                    products_by_description=products_by_description,
                )

                supplier = self._get_or_create_import_supplier(supplier_name, user_id, suppliers_cache)
                quantity = self._parse_import_int(row[quantity_col], 'cantidad')
                unit_price = self._parse_import_decimal(row[unit_price_col], 'precio unitario')
                line_subtotal = self._parse_import_decimal(
                    row[subtotal_col] if subtotal_col and not pd.isna(row[subtotal_col]) else unit_price * quantity,
                    'subtotal'
                )
                taxable_base = self._parse_import_decimal(
                    row[taxable_base_col] if taxable_base_col and not pd.isna(row[taxable_base_col]) else line_subtotal,
                    'base imponible'
                )
                tax_amount = self._parse_import_decimal(
                    row[tax_col] if tax_col and not pd.isna(row[tax_col]) else Decimal('0'),
                    'iva'
                )
                total_amount = self._parse_import_decimal(
                    row[total_col] if total_col and not pd.isna(row[total_col]) else taxable_base + tax_amount,
                    'total'
                )

                group_key = (str(supplier.id), invoice_number.upper())
                invoice_group = grouped_invoices.setdefault(
                    group_key,
                    {
                        'supplier_id': supplier.id,
                        'invoice_number': invoice_number,
                        'invoice_date': invoice_date,
                        'taxable_base_usd': Decimal('0'),
                        'tax_amount_usd': Decimal('0'),
                        'total_usd': Decimal('0'),
                        'notes': None,
                        'items': [],
                    },
                )

                invoice_group['taxable_base_usd'] += taxable_base
                invoice_group['tax_amount_usd'] += tax_amount
                invoice_group['total_usd'] += total_amount

                if notes_col and not pd.isna(row[notes_col]) and not invoice_group['notes']:
                    invoice_group['notes'] = str(row[notes_col]).strip() or None

                invoice_group['items'].append({
                    'product_id': product.id,
                    'quantity': quantity,
                    'unit_price_usd': unit_price,
                    'line_subtotal_usd': line_subtotal,
                    'description': product.descripcion,
                })
                items_processed += 1
            except Exception as e:
                errors.append(f'Fila {index + 2}: {str(e)}')
                current_app.logger.warning(f'Error processing purchase invoice row {index}: {str(e)}')

        for invoice_data in grouped_invoices.values():
            try:
                purchase_service.create_purchase_invoice(invoice_data, user_id)
                created += 1
            except Exception as e:
                errors.append(
                    f"Factura {invoice_data['invoice_number']} proveedor {invoice_data['supplier_id']}: {str(e)}"
                )
                current_app.logger.warning(
                    'Error creating purchase invoice %s: %s',
                    invoice_data['invoice_number'],
                    str(e),
                )

        return {
            'created': created,
            'items_processed': items_processed,
            'errors': errors,
            'total_processed': created,
        }

    def _process_daily_closures_dataframe(self, df: pd.DataFrame, user_id: int, source_file_name: str) -> Dict[str, Any]:
        """Read daily closure rows and delegate estimated output generation."""
        date_col = self._find_column(df, ['fecha', 'fecha cierre', 'closure date'])
        total_col = self._find_column(df, ['total usd', 'ventas usd', 'total', 'monto total'])
        invoiced_amount_col = self._find_column(df, ['con factura', 'facturado', 'ventas facturadas'])
        non_invoiced_amount_col = self._find_column(df, ['sin factura', 'no facturado', 'ventas no facturadas'])
        invoiced_share_col = self._find_column(df, ['porcentaje facturado', 'share factura'])
        non_invoiced_share_col = self._find_column(df, ['porcentaje no facturado', 'share no factura'])
        notes_col = self._find_column(df, ['observaciones', 'notas', 'notes'])

        missing_fields = []
        if not date_col:
            missing_fields.append('Fecha')
        if not total_col and not (invoiced_amount_col and non_invoiced_amount_col):
            missing_fields.append('Total USD o columnas Con factura/Sin factura')
        if missing_fields:
            raise ValidationError('Faltan columnas requeridas para cierres diarios: ' + ', '.join(missing_fields))

        created = 0
        errors = []
        closure_service = DailySalesClosureService()

        for index, row in df.iterrows():
            try:
                closure_date = str(row[date_col]).strip() if not pd.isna(row[date_col]) else ''
                if not closure_date:
                    raise ValidationError('La fecha del cierre es requerida')

                total_amount = None
                if total_col and not pd.isna(row[total_col]):
                    total_amount = self._parse_import_decimal(row[total_col], 'total usd')

                invoiced_amount = None
                non_invoiced_amount = None
                if invoiced_amount_col and not pd.isna(row[invoiced_amount_col]):
                    invoiced_amount = self._parse_import_decimal(row[invoiced_amount_col], 'con factura')
                if non_invoiced_amount_col and not pd.isna(row[non_invoiced_amount_col]):
                    non_invoiced_amount = self._parse_import_decimal(row[non_invoiced_amount_col], 'sin factura')

                invoiced_share = None
                non_invoiced_share = None
                if invoiced_share_col and not pd.isna(row[invoiced_share_col]):
                    invoiced_share = self._normalize_share_value(row[invoiced_share_col])
                if non_invoiced_share_col and not pd.isna(row[non_invoiced_share_col]):
                    non_invoiced_share = self._normalize_share_value(row[non_invoiced_share_col])

                payload = {
                    'closure_date': closure_date,
                    'notes': str(row[notes_col]).strip() if notes_col and not pd.isna(row[notes_col]) else None,
                    'source_file_name': source_file_name,
                }

                if total_amount is not None:
                    payload['total_sales_usd'] = total_amount
                if invoiced_amount is not None:
                    payload['invoiced_sales_usd'] = invoiced_amount
                if non_invoiced_amount is not None:
                    payload['non_invoiced_sales_usd'] = non_invoiced_amount
                if invoiced_share is not None:
                    payload['invoiced_share'] = invoiced_share
                if non_invoiced_share is not None:
                    payload['non_invoiced_share'] = non_invoiced_share

                closure_service.create_closure(payload, user_id)
                created += 1
            except Exception as e:
                errors.append(f'Fila {index + 2}: {str(e)}')
                current_app.logger.warning(f'Error processing daily closure row {index}: {str(e)}')

        return {
            'created': created,
            'errors': errors,
            'total_processed': created,
        }

    def _get_or_create_import_supplier(self, supplier_name: str, user_id: int, cache: Dict[str, Proveedor]) -> Proveedor:
        """Find an existing supplier by name or create a minimal one for imports."""
        cache_key = self._normalize_description(supplier_name)
        cached = cache.get(cache_key)
        if cached:
            return cached

        supplier = Proveedor.query.filter(
            Proveedor.deleted_at.is_(None),
            db.func.upper(Proveedor.nombre) == cache_key,
        ).first()
        if not supplier:
            supplier = Proveedor(
                nombre=supplier_name,
                created_by=user_id,
                updated_by=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.session.add(supplier)
            db.session.commit()

        cache[cache_key] = supplier
        return supplier

    def _resolve_import_product(
        self,
        row,
        product_id_col: str,
        code_col: str,
        description_col: str,
        products_by_id: Dict[str, Product],
        products_by_code: Dict[str, Product],
        products_by_description: Dict[str, Product],
    ) -> Product:
        """Resolve the target product from a purchase import row."""
        if product_id_col and not pd.isna(row[product_id_col]):
            product_id_key = str(int(row[product_id_col]))
            if product_id_key in products_by_id:
                return products_by_id[product_id_key]

        if code_col and not pd.isna(row[code_col]):
            code_key = self._normalize_column_token(str(row[code_col]))
            if code_key in products_by_code:
                return products_by_code[code_key]

        if description_col and not pd.isna(row[description_col]):
            description_key = self._normalize_description(str(row[description_col]))
            if description_key in products_by_description:
                return products_by_description[description_key]

        raise ValidationError('No se pudo identificar el producto de la fila')

    def _parse_import_int(self, value: Any, field_name: str) -> int:
        """Parse integer values from flexible import formats."""
        try:
            parsed = int(float(value))
        except (TypeError, ValueError):
            raise ValidationError(f'El campo {field_name} debe ser entero')
        if parsed <= 0:
            raise ValidationError(f'El campo {field_name} debe ser mayor que cero')
        return parsed

    def _parse_import_decimal(self, value: Any, field_name: str) -> Decimal:
        """Parse decimal values from imports supporting localized separators."""
        if isinstance(value, Decimal):
            return value.quantize(Decimal('0.0001'))

        raw = str(value).strip().replace(' ', '')
        if not raw:
            raise ValidationError(f'El campo {field_name} es requerido')

        if ',' in raw and '.' in raw:
            raw = raw.replace('.', '').replace(',', '.')
        elif ',' in raw:
            raw = raw.replace(',', '.')

        try:
            return Decimal(raw).quantize(Decimal('0.0001'))
        except Exception:
            raise ValidationError(f'El campo {field_name} debe ser numérico')

    def _normalize_share_value(self, value: Any) -> Decimal:
        """Normalize percentage values like 60, 0.6 or 60% into decimal share."""
        raw = str(value).strip().replace('%', '')
        parsed = self._parse_import_decimal(raw, 'porcentaje')
        if parsed > Decimal('1'):
            parsed = (parsed / Decimal('100')).quantize(Decimal('0.0001'))
        return parsed
    
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
