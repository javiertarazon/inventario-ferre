"""add allocation group to daily sales closure allocations

Revision ID: d4a8f6b2c913
Revises: b17f2c6d91aa
Create Date: 2026-03-07 12:35:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4a8f6b2c913'
down_revision = 'b17f2c6d91aa'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'daily_sales_closure_allocations',
        sa.Column('allocation_group', sa.String(length=30), nullable=True),
    )


def downgrade():
    op.drop_column('daily_sales_closure_allocations', 'allocation_group')
