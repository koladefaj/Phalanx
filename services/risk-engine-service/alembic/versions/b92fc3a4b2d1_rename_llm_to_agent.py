"""rename_llm_to_agent

Revision ID: b92fc3a4b2d1
Revises: aee18c6aad26
Create Date: 2026-04-21 16:47:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b92fc3a4b2d1'
down_revision: Union[str, Sequence[str], None] = 'aee18c6aad26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename llm columns to agent columns."""
    op.alter_column('risk_results', 'llm_summary', new_column_name='agent_summary')
    op.alter_column('risk_results', 'llm_risk_factors', new_column_name='agent_risk_factors')
    op.alter_column('risk_results', 'llm_recommendation', new_column_name='agent_recommendation')
    op.alter_column('risk_results', 'llm_confidence', new_column_name='agent_confidence')
    op.alter_column('risk_results', 'llm_fallback_used', new_column_name='agent_fallback_used')
    op.alter_column('risk_results', 'llm_model', new_column_name='agent_model')
    op.alter_column('risk_results', 'llm_latency_ms', new_column_name='agent_latency_ms')


def downgrade() -> None:
    """Rename agent columns back to llm columns."""
    op.alter_column('risk_results', 'agent_summary', new_column_name='llm_summary')
    op.alter_column('risk_results', 'agent_risk_factors', new_column_name='llm_risk_factors')
    op.alter_column('risk_results', 'agent_recommendation', new_column_name='llm_recommendation')
    op.alter_column('risk_results', 'agent_confidence', new_column_name='llm_confidence')
    op.alter_column('risk_results', 'agent_fallback_used', new_column_name='llm_fallback_used')
    op.alter_column('risk_results', 'agent_model', new_column_name='llm_model')
    op.alter_column('risk_results', 'agent_latency_ms', new_column_name='llm_latency_ms')
