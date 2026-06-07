"""add client_id to transactions

Revision ID: rev_add_client_id
Revises: rev_1776546734
Create Date: 2026-06-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'rev_add_client_id'
down_revision: Union[str, None] = 'rev_1776546734'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'transactions',
        sa.Column(
            'client_id',
            sa.String(length=128),
            server_default='legacy',
            nullable=False,
        ),
    )
    op.create_index('ix_transactions_client_id', 'transactions', ['client_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_transactions_client_id', table_name='transactions')
    op.drop_column('transactions', 'client_id')
