"""add inventory entry date and purchase history

Revision ID: 9c0d1f4a7b22
Revises: 6d5f1c8a2e71
Create Date: 2026-03-06 21:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c0d1f4a7b22'
down_revision = '6d5f1c8a2e71'
branch_labels = None
depends_on = None


DEFAULT_DATE = '2024-08-01'


def upgrade():
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('inventory_entry_date', sa.Date(), nullable=True))

    op.execute(f"UPDATE products SET inventory_entry_date = '{DEFAULT_DATE}' WHERE inventory_entry_date IS NULL")

    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.alter_column('inventory_entry_date', nullable=False)

    op.create_table(
        'purchase_invoices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('supplier_id', sa.Integer(), nullable=False),
        sa.Column('invoice_number', sa.String(length=100), nullable=False),
        sa.Column('invoice_date', sa.Date(), nullable=False),
        sa.Column('currency_code', sa.String(length=10), nullable=False, server_default='USD'),
        sa.Column('exchange_rate_value', sa.Numeric(12, 4), nullable=True),
        sa.Column('subtotal_usd', sa.Numeric(14, 4), nullable=False, server_default='0'),
        sa.Column('taxable_base_usd', sa.Numeric(14, 4), nullable=False, server_default='0'),
        sa.Column('tax_amount_usd', sa.Numeric(14, 4), nullable=False, server_default='0'),
        sa.Column('total_usd', sa.Numeric(14, 4), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['supplier_id'], ['proveedores.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('supplier_id', 'invoice_number', name='uq_purchase_invoice_supplier_number'),
    )
    op.create_index(op.f('ix_purchase_invoices_invoice_date'), 'purchase_invoices', ['invoice_date'], unique=False)
    op.create_index(op.f('ix_purchase_invoices_supplier_id'), 'purchase_invoices', ['supplier_id'], unique=False)

    op.create_table(
        'purchase_invoice_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('description_snapshot', sa.String(length=200), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price_usd', sa.Numeric(12, 4), nullable=False),
        sa.Column('line_subtotal_usd', sa.Numeric(14, 4), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint('line_subtotal_usd >= 0', name='check_purchase_item_subtotal_non_negative'),
        sa.CheckConstraint('quantity > 0', name='check_purchase_item_quantity_positive'),
        sa.CheckConstraint('unit_price_usd >= 0', name='check_purchase_item_price_non_negative'),
        sa.ForeignKeyConstraint(['invoice_id'], ['purchase_invoices.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_purchase_invoice_items_invoice_id'), 'purchase_invoice_items', ['invoice_id'], unique=False)
    op.create_index(op.f('ix_purchase_invoice_items_product_id'), 'purchase_invoice_items', ['product_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_purchase_invoice_items_product_id'), table_name='purchase_invoice_items')
    op.drop_index(op.f('ix_purchase_invoice_items_invoice_id'), table_name='purchase_invoice_items')
    op.drop_table('purchase_invoice_items')

    op.drop_index(op.f('ix_purchase_invoices_supplier_id'), table_name='purchase_invoices')
    op.drop_index(op.f('ix_purchase_invoices_invoice_date'), table_name='purchase_invoices')
    op.drop_table('purchase_invoices')

    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_column('inventory_entry_date')