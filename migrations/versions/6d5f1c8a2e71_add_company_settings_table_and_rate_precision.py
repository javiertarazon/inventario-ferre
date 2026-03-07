"""add company settings table and exchange rate precision

Revision ID: 6d5f1c8a2e71
Revises: 0f5723c68fcb
Create Date: 2026-03-06 19:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d5f1c8a2e71'
down_revision = '0f5723c68fcb'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'company_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_name', sa.String(length=200), nullable=False),
        sa.Column('rif', sa.String(length=20), nullable=False),
        sa.Column('fiscal_address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(length=30), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    with op.batch_alter_table('exchange_rates', schema=None) as batch_op:
        batch_op.alter_column(
            'rate',
            existing_type=sa.Numeric(precision=10, scale=2),
            type_=sa.Numeric(precision=12, scale=4),
            existing_nullable=False,
        )


def downgrade():
    with op.batch_alter_table('exchange_rates', schema=None) as batch_op:
        batch_op.alter_column(
            'rate',
            existing_type=sa.Numeric(precision=12, scale=4),
            type_=sa.Numeric(precision=10, scale=2),
            existing_nullable=False,
        )

    op.drop_table('company_settings')