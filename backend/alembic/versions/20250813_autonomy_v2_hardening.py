"""Autonomy V2 hardening: idempotent HITL + indexes

Revision ID: 20250813_autonomy_v2_hardening
Revises: 20250813_autonomy_v2_baseline
Create Date: 2025-08-13 05:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '20250813_autonomy_v2_hardening'
down_revision = '20250813_autonomy_v2_baseline'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add resume_job_id to autonomy_turnitin_cycles
    try:
        op.add_column('autonomy_turnitin_cycles', sa.Column('resume_job_id', sa.BigInteger(), nullable=True))
    except Exception:
        pass

    # Add simple status constraint if supported
    try:
        op.create_check_constraint(
            'ck_autonomy_turnitin_cycles_status',
            'autonomy_turnitin_cycles',
            "status in ('awaiting_report','report_ready','accepted','rejected')"
        )
    except Exception:
        pass

    # Indexes for performance
    try:
        op.create_index('ix_autonomy_episodic_logs_run_created', 'autonomy_episodic_logs', ['run_id', 'created_at'])
    except Exception:
        pass
    try:
        op.create_index('ix_autonomy_job_queue_state_sched', 'autonomy_job_queue', ['state', 'scheduled_at'])
    except Exception:
        pass
    try:
        op.create_index('ix_autonomy_checkpoints_run', 'autonomy_checkpoints', ['run_id'])
    except Exception:
        pass


def downgrade() -> None:
    try:
        op.drop_index('ix_autonomy_checkpoints_run', table_name='autonomy_checkpoints')
    except Exception:
        pass
    try:
        op.drop_index('ix_autonomy_job_queue_state_sched', table_name='autonomy_job_queue')
    except Exception:
        pass
    try:
        op.drop_index('ix_autonomy_episodic_logs_run_created', table_name='autonomy_episodic_logs')
    except Exception:
        pass
    try:
        op.drop_constraint('ck_autonomy_turnitin_cycles_status', 'autonomy_turnitin_cycles', type_='check')
    except Exception:
        pass
    try:
        op.drop_column('autonomy_turnitin_cycles', 'resume_job_id')
    except Exception:
        pass

