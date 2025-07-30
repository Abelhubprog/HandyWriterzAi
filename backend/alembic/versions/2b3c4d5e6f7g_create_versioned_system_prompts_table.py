"""Create versioned system_prompts table

Revision ID: 2b3c4d5e6f7g
Revises: d2b13d0018af
Create Date: 2025-07-10 23:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b3c4d5e6f7g'
down_revision = 'd2b13d0018af'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Creates the system_prompts table with a composite primary key
    to support versioning of prompts for each stage.
    """
    op.create_table(
        'system_prompts',
        sa.Column('stage_id', sa.String(100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('template', sa.Text(), nullable=False),
        sa.Column('updated', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('stage_id', 'version', name='pk_system_prompts')
    )
    op.create_index(op.f('ix_system_prompts_stage_id'), 'system_prompts', ['stage_id'], unique=False)


def downgrade() -> None:
    """Removes the system_prompts table."""
    op.drop_index(op.f('ix_system_prompts_stage_id'), table_name='system_prompts')
    op.drop_table('system_prompts')