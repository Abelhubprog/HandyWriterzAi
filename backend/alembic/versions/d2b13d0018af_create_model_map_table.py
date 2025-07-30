"""create_model_map_table

Revision ID: d2b13d0018af
Revises: 
Create Date: 2025-07-10 16:29:57.298641

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2b13d0018af'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DROP TABLE IF EXISTS model_map")
    op.create_table(
        'model_map',
        sa.Column('stage_id', sa.Text(), primary_key=True),
        sa.Column('model_name', sa.Text(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    with op.batch_alter_table('model_map', schema=None) as batch_op:
        batch_op.create_check_constraint(
            "ck_model_map_stage_id",
            "stage_id IN ('INTENT', 'PLAN', 'SEARCH-A', 'SEARCH-B', 'SEARCH-C', 'EVIDENCE', 'WRITE', 'REWRITE', 'QA-1', 'QA-2', 'QA-3')"
        )

    op.bulk_insert(
        sa.table('model_map', sa.column('stage_id', sa.Text), sa.column('model_name', sa.Text)),
        [
            {'stage_id': 'INTENT', 'model_name': 'gemini-2.5-pro'},
            {'stage_id': 'PLAN', 'model_name': 'gemini-pro'},
            {'stage_id': 'SEARCH-A', 'model_name': 'gemini-pro-web-tool'},
            {'stage_id': 'SEARCH-B', 'model_name': 'grok-4-web'},
            {'stage_id': 'SEARCH-C', 'model_name': 'openai-o3-browser'},
            {'stage_id': 'EVIDENCE', 'model_name': 'gemini-pro-function-call'},
            {'stage_id': 'WRITE', 'model_name': 'gemini-pro'},
            {'stage_id': 'REWRITE', 'model_name': 'openai-o3'},
            {'stage_id': 'QA-1', 'model_name': 'gemini-pro'},
            {'stage_id': 'QA-2', 'model_name': 'grok-4'},
            {'stage_id': 'QA-3', 'model_name': 'openai-o3'},
        ]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('model_map')
