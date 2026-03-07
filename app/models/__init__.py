"""
Models package initialization.
"""

from app.models.user import User
from app.models.product import Product
from app.models.supplier import Proveedor
from app.models.movement import Movimiento
from app.models.audit_log import AuditLog
from app.models.backup_metadata import BackupMetadata
from app.models.item_group import ItemGroup
from app.models.customer import Customer
from app.models.sales_order import SalesOrder, SalesOrderItem
from app.models.exchange_rate import ExchangeRate
from app.models.company_settings import CompanySettings
from app.models.purchase_invoice import PurchaseInvoice, PurchaseInvoiceItem
from app.models.daily_sales_closure import DailySalesClosure, DailySalesClosureAllocation

# Aliases for English names
Supplier = Proveedor
Movement = Movimiento

__all__ = [
    'User',
    'Product',
    'Proveedor',
    'Supplier',
    'Movimiento',
    'Movement',
    'AuditLog',
    'BackupMetadata',
    'ItemGroup',
    'Customer',
    'SalesOrder',
    'SalesOrderItem',
    'ExchangeRate',
    'CompanySettings',
    'PurchaseInvoice',
    'PurchaseInvoiceItem',
    'DailySalesClosure',
    'DailySalesClosureAllocation',
]

