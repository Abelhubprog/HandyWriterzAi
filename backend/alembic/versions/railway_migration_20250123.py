"""Railway PostgreSQL Migration for Chat Files

Revision ID: railway_20250123
Revises: 2b3c4d5e6f7g
Create Date: 2025-01-23 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'railway_20250123'
down_revision = '2b3c4d5e6f7g'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create tables required for Railway deployment with PostgreSQL and pgvector.
    """
    
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create chat_files table for file metadata
    op.create_table(
        'chat_files',
        sa.Column('file_id', sa.String(36), primary_key=True),  # UUID
        sa.Column('user_id', sa.String(255), nullable=False, index=True),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('file_path', sa.Text(), nullable=False),
        sa.Column('size', sa.BigInteger(), nullable=False),
        sa.Column('content_type', sa.String(100), nullable=False),
        sa.Column('context', sa.String(50), nullable=False, default='chat'),
        sa.Column('status', sa.String(20), nullable=False, default='uploaded'),
        sa.Column('chunk_count', sa.Integer(), nullable=True),
        sa.Column('embedding_count', sa.Integer(), nullable=True),
        sa.Column('processing_time', sa.Float(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True)
    )
    
    # Create indexes for chat_files
    op.create_index('idx_chat_files_user_context', 'chat_files', ['user_id', 'context'])
    op.create_index('idx_chat_files_status', 'chat_files', ['status'])
    op.create_index('idx_chat_files_uploaded_at', 'chat_files', ['uploaded_at'])
    
    # Create document_chunks table for vector storage
    op.create_table(
        'document_chunks',
        sa.Column('chunk_id', sa.String(36), primary_key=True),  # UUID
        sa.Column('file_id', sa.String(36), nullable=False, index=True),
        sa.Column('user_id', sa.String(255), nullable=False, index=True),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', postgresql.ARRAY(sa.Float), nullable=True),  # pgvector compatible
        sa.Column('token_count', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['file_id'], ['chat_files.file_id'], ondelete='CASCADE')
    )
    
    # Create indexes for document_chunks
    op.create_index('idx_document_chunks_file_user', 'document_chunks', ['file_id', 'user_id'])
    op.create_index('idx_document_chunks_user_created', 'document_chunks', ['user_id', 'created_at'])
    
    # Create user_memories table for user context storage
    op.create_table(
        'user_memories',
        sa.Column('user_id', sa.String(255), primary_key=True),
        sa.Column('fingerprint', sa.JSON(), nullable=False),
        sa.Column('preferences', sa.JSON(), nullable=True),
        sa.Column('context_summary', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Create chat_sessions table for session management
    op.create_table(
        'chat_sessions',
        sa.Column('session_id', sa.String(36), primary_key=True),  # UUID
        sa.Column('user_id', sa.String(255), nullable=False, index=True),
        sa.Column('trace_id', sa.String(36), nullable=True, index=True),
        sa.Column('mode', sa.String(50), nullable=False, default='chat'),
        sa.Column('status', sa.String(20), nullable=False, default='active'),
        sa.Column('file_ids', postgresql.ARRAY(sa.String), nullable=True),  # Associated files
        sa.Column('context_data', sa.JSON(), nullable=True),
        sa.Column('cost_usd', sa.Numeric(10, 4), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create indexes for chat_sessions
    op.create_index('idx_chat_sessions_user_status', 'chat_sessions', ['user_id', 'status'])
    op.create_index('idx_chat_sessions_trace_id', 'chat_sessions', ['trace_id'])
    op.create_index('idx_chat_sessions_created_at', 'chat_sessions', ['created_at'])


def downgrade() -> None:
    """
    Drop tables created for Railway deployment.
    """
    op.drop_table('chat_sessions')
    op.drop_table('user_memories')
    op.drop_table('document_chunks')
    op.drop_table('chat_files')
    
    # Note: We don't drop the pgvector extension as it might be used by other applications