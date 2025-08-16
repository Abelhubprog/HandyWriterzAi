"""Autonomy V2 baseline tables

Revision ID: 20250813_autonomy_v2_baseline
Revises: railway_20250123
Create Date: 2025-08-13 04:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250813_autonomy_v2_baseline'
down_revision = 'railway_20250123'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ensure pgvector extension exists (no-op on SQLite)
    try:
        op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    except Exception:
        # Ignore if not supported
        pass

    # autonomy_checkpoints
    op.create_table(
        'autonomy_checkpoints',
        sa.Column('run_id', sa.String(length=64), primary_key=True, nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()) if op.get_bind().dialect.name != 'sqlite' else sa.JSON(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # autonomy_episodic_logs
    op.create_table(
        'autonomy_episodic_logs',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('run_id', sa.String(length=64), nullable=False, index=True),
        sa.Column('step_id', sa.String(length=64), nullable=True),
        sa.Column('role', sa.String(length=32), nullable=True),
        sa.Column('content', postgresql.JSONB(astext_type=sa.Text()) if op.get_bind().dialect.name != 'sqlite' else sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    op.create_index('ix_autonomy_episodic_logs_run_created', 'autonomy_episodic_logs', ['run_id', 'created_at'])

    # autonomy_semantic_notes
    # Use VECTOR(1536) when available; otherwise fallback to JSON array for portability
    dialect = op.get_bind().dialect.name
    if dialect == 'postgresql':
        op.create_table(
            'autonomy_semantic_notes',
            sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
            sa.Column('run_id', sa.String(length=64), nullable=False, index=True),
            sa.Column('note', sa.Text(), nullable=False),
            sa.Column('embedding', sa.dialects.postgresql.ARRAY(sa.Float), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
        )
    else:
        op.create_table(
            'autonomy_semantic_notes',
            sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
            sa.Column('run_id', sa.String(length=64), nullable=False, index=True),
            sa.Column('note', sa.Text(), nullable=False),
            sa.Column('embedding', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
        )
    op.create_index('ix_autonomy_semantic_notes_run_created', 'autonomy_semantic_notes', ['run_id', 'created_at'])

    # autonomy_job_queue
    op.create_table(
        'autonomy_job_queue',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('run_id', sa.String(length=64), nullable=False, index=True),
        sa.Column('user_id', sa.String(length=255), nullable=True, index=True),
        sa.Column('journey', sa.String(length=64), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('state', sa.String(length=32), nullable=False, server_default='queued'),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('locked_by', sa.String(length=64), nullable=True),
        sa.Column('locked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()) if op.get_bind().dialect.name != 'sqlite' else sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    op.create_index('ix_autonomy_job_queue_state_priority', 'autonomy_job_queue', ['state', 'priority'])

    # autonomy_turnitin_cycles
    op.create_table(
        'autonomy_turnitin_cycles',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('run_id', sa.String(length=64), nullable=False, index=True),
        sa.Column('artifact_id', sa.String(length=64), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='pending'),
        sa.Column('target_similarity', sa.Float(), nullable=True),
        sa.Column('observed_similarity', sa.Float(), nullable=True),
        sa.Column('report_path', sa.Text(), nullable=True),
        sa.Column('human_uploader_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    op.create_index('ix_autonomy_turnitin_cycles_run_created', 'autonomy_turnitin_cycles', ['run_id', 'created_at'])


def downgrade() -> None:
    op.drop_index('ix_autonomy_turnitin_cycles_run_created', table_name='autonomy_turnitin_cycles')
    op.drop_table('autonomy_turnitin_cycles')

    op.drop_index('ix_autonomy_job_queue_state_priority', table_name='autonomy_job_queue')
    op.drop_table('autonomy_job_queue')

    op.drop_index('ix_autonomy_semantic_notes_run_created', table_name='autonomy_semantic_notes')
    op.drop_table('autonomy_semantic_notes')

    op.drop_index('ix_autonomy_episodic_logs_run_created', table_name='autonomy_episodic_logs')
    op.drop_table('autonomy_episodic_logs')

    op.drop_table('autonomy_checkpoints')

