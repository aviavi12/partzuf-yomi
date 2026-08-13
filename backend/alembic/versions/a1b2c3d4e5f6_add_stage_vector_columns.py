"""add stage vector, causal chain, father/mother attributes, daily vector, temporal columns

Revision ID: a1b2c3d4e5f6
Revises: 362f8cc3cf8a
Create Date: 2026-08-13 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '362f8cc3cf8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('developmental_analyses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('stage_vector_json', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('causal_chain_json', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('father_attributes_json', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('mother_attributes_json', sa.Text(), nullable=True))

    with op.batch_alter_table('daily_summaries', schema=None) as batch_op:
        batch_op.add_column(sa.Column('daily_stage_vector_json', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('temporal_analysis_json', sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('daily_summaries', schema=None) as batch_op:
        batch_op.drop_column('temporal_analysis_json')
        batch_op.drop_column('daily_stage_vector_json')

    with op.batch_alter_table('developmental_analyses', schema=None) as batch_op:
        batch_op.drop_column('mother_attributes_json')
        batch_op.drop_column('father_attributes_json')
        batch_op.drop_column('causal_chain_json')
        batch_op.drop_column('stage_vector_json')
