"""add daily sales closures

Revision ID: b17f2c6d91aa
Revises: 9c0d1f4a7b22
Create Date: 2026-03-07 11:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b17f2c6d91aa'
down_revision = '9c0d1f4a7b22'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'daily_sales_closures',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('closure_date', sa.Date(), nullable=False),
        sa.Column('total_sales_usd', sa.Numeric(14, 4), nullable=False, server_default='0'),
        sa.Column('invoiced_share', sa.Numeric(5, 4), nullable=False, server_default='0.6000'),
        sa.Column('non_invoiced_share', sa.Numeric(5, 4), nullable=False, server_default='0.4000'),
        sa.Column('invoiced_sales_usd', sa.Numeric(14, 4), nullable=False, server_default='0'),
        sa.Column('non_invoiced_sales_usd', sa.Numeric(14, 4), nullable=False, server_default='0'),
        sa.Column('reconstructed_sales_usd', sa.Numeric(14, 4), nullable=False, server_default='0'),
        sa.Column('generated_exit_units', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('source_file_name', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('closure_date'),
    )
    op.create_index(op.f('ix_daily_sales_closures_closure_date'), 'daily_sales_closures', ['closure_date'], unique=False)

    op.create_table(
        'daily_sales_closure_allocations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('closure_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('movement_id', sa.Integer(), nullable=True),
        sa.Column('reference_unit_price_usd', sa.Numeric(12, 4), nullable=False),
        sa.Column('allocated_sales_usd', sa.Numeric(14, 4), nullable=False, server_default='0'),
        sa.Column('estimated_quantity', sa.Integer(), nullable=False),
        sa.Column('weighting_value_usd', sa.Numeric(14, 4), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint('allocated_sales_usd >= 0', name='check_daily_closure_alloc_sales_non_negative'),
        sa.CheckConstraint('estimated_quantity > 0', name='check_daily_closure_alloc_qty_positive'),
        sa.ForeignKeyConstraint(['closure_id'], ['daily_sales_closures.id']),
        sa.ForeignKeyConstraint(['movement_id'], ['movimientos.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_daily_sales_closure_allocations_closure_id'), 'daily_sales_closure_allocations', ['closure_id'], unique=False)
    op.create_index(op.f('ix_daily_sales_closure_allocations_product_id'), 'daily_sales_closure_allocations', ['product_id'], unique=False)
    op.create_index(op.f('ix_daily_sales_closure_allocations_movement_id'), 'daily_sales_closure_allocations', ['movement_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_daily_sales_closure_allocations_movement_id'), table_name='daily_sales_closure_allocations')
    op.drop_index(op.f('ix_daily_sales_closure_allocations_product_id'), table_name='daily_sales_closure_allocations')
    op.drop_index(op.f('ix_daily_sales_closure_allocations_closure_id'), table_name='daily_sales_closure_allocations')
    op.drop_table('daily_sales_closure_allocations')
    op.drop_index(op.f('ix_daily_sales_closures_closure_date'), table_name='daily_sales_closures')
    op.drop_table('daily_sales_closures')