"""Revolutionary database connection and session management for HandyWriterz."""

import os
import logging
from typing import Generator, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from .models import Base, User, Conversation, Document

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Revolutionary database manager with sophisticated connection handling."""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        # Handle different database URL formats
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)
        
        # Create synchronous engine
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create asynchronous engine for async operations (only for PostgreSQL)
        if "sqlite" not in self.database_url:
            async_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://")
            self.async_engine = create_async_engine(async_url, echo=False)
            self.AsyncSessionLocal = async_sessionmaker(
                self.async_engine, class_=AsyncSession, expire_on_commit=False
            )
        else:
            # SQLite doesn't support async operations well
            self.async_engine = None
            self.AsyncSessionLocal = None
        
        # Initialize database
        self._init_database()
    
    def _create_engine(self) -> Engine:
        """Create SQLAlchemy engine with optimized settings."""
        engine_kwargs = {
            "echo": os.getenv("DB_ECHO", "false").lower() == "true",
            "pool_pre_ping": True,
        }
        
        # For SQLite (development/testing)
        if "sqlite" in self.database_url:
            engine_kwargs.update({
                "poolclass": StaticPool,
                "connect_args": {"check_same_thread": False}
            })
        else:
            # PostgreSQL specific settings
            engine_kwargs.update({
                "pool_recycle": 3600,  # Recycle connections every hour
                "pool_size": 10,
                "max_overflow": 20,
            })
        
        return create_engine(self.database_url, **engine_kwargs)
    
    def _init_database(self):
        """Initialize database tables and indexes."""
        try:
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
            
            # Create additional indexes for performance
            self._create_performance_indexes()
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _create_performance_indexes(self):
        """Create additional performance indexes."""
        try:
            with self.engine.connect() as conn:
                # Create composite indexes for common queries
                if "sqlite" not in self.database_url:
                    # PostgreSQL specific indexes
                    conn.execute("""
                        CREATE INDEX IF NOT EXISTS idx_conversations_user_status
                        ON conversations(user_id, workflow_status);
                    """)
                    
                    conn.execute("""
                        CREATE INDEX IF NOT EXISTS idx_documents_user_created
                        ON documents(user_id, created_at DESC);
                    """)
                    
                    conn.execute("""
                        CREATE INDEX IF NOT EXISTS idx_source_cache_url_hash
                        ON source_cache(MD5(url));
                    """)
                    
                    conn.execute("""
                        CREATE INDEX IF NOT EXISTS idx_system_metrics_time_category
                        ON system_metrics(recorded_at DESC, metric_category);
                    """)
                else:
                    # SQLite compatible indexes
                    conn.execute("""
                        CREATE INDEX IF NOT EXISTS idx_conversations_user_status
                        ON conversations(user_id, workflow_status);
                    """)
                    
                    conn.execute("""
                        CREATE INDEX IF NOT EXISTS idx_documents_user_created
                        ON documents(user_id, created_at);
                    """)
                    
                    conn.execute("""
                        CREATE INDEX IF NOT EXISTS idx_system_metrics_time_category
                        ON system_metrics(recorded_at, metric_category);
                    """)
                
                conn.commit()
                logger.info("Performance indexes created successfully")
                
        except Exception as e:
            logger.warning(f"Could not create performance indexes: {e}")
    
    def get_db_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup."""
        db = self.SessionLocal()
        try:
            yield db
        except Exception as e:
            db.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            db.close()
    
    @contextmanager
    def get_db_context(self) -> Generator[Session, None, None]:
        """Context manager for database sessions."""
        db = self.SessionLocal()
        try:
            yield db
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Database context error: {e}")
            raise
        finally:
            db.close()
    
    async def get_async_session(self) -> AsyncSession:
        """Get async database session."""
        if self.AsyncSessionLocal is None:
            raise NotImplementedError("Async sessions not supported with SQLite")
        return self.AsyncSessionLocal()
    
    @contextmanager
    async def get_async_context(self) -> Generator[AsyncSession, None, None]:
        """Async context manager for database sessions."""
        if self.AsyncSessionLocal is None:
            raise NotImplementedError("Async sessions not supported with SQLite")
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Async database context error: {e}")
                raise
    
    def health_check(self) -> bool:
        """Check database connection health."""
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def async_health_check(self) -> bool:
        """Async database health check."""
        if self.async_engine is None:
            # For SQLite, just return the sync health check
            return self.health_check()
        try:
            async with self.async_engine.connect() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Async database health check failed: {e}")
            return False
    
    def close(self):
        """Close database connections."""
        try:
            self.engine.dispose()
            if self.async_engine:
                asyncio.create_task(self.async_engine.dispose())
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")


class UserRepository:
    """Revolutionary user repository with sophisticated user management."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_user(self, wallet_address: str, **kwargs) -> User:
        """Create a new user with comprehensive profiling."""
        with self.db_manager.get_db_context() as db:
            # Check if user already exists
            existing_user = db.query(User).filter(User.wallet_address == wallet_address).first()
            if existing_user:
                return existing_user
            
            user = User(
                wallet_address=wallet_address,
                **kwargs
            )
            db.add(user)
            db.flush()  # Get the ID
            
            logger.info(f"Created new user: {user.id}")
            return user
    
    def get_user_by_wallet(self, wallet_address: str) -> Optional[User]:
        """Get user by wallet address."""
        with self.db_manager.get_db_context() as db:
            return db.query(User).filter(User.wallet_address == wallet_address).first()
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        with self.db_manager.get_db_context() as db:
            return db.query(User).filter(User.id == user_id).first()
    
    def update_user_stats(self, user_id: str, **kwargs):
        """Update user statistics and metrics."""
        with self.db_manager.get_db_context() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                logger.info(f"Updated user stats for: {user_id}")


class ConversationRepository:
    """Revolutionary conversation repository with workflow state management."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_conversation(self, user_id: str, user_params: dict, **kwargs) -> Conversation:
        """Create a new conversation with initial parameters."""
        with self.db_manager.get_db_context() as db:
            conversation = Conversation(
                user_id=user_id,
                user_params=user_params,
                **kwargs
            )
            db.add(conversation)
            db.flush()
            
            logger.info(f"Created conversation: {conversation.id}")
            return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID."""
        with self.db_manager.get_db_context() as db:
            return db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    def update_conversation_state(self, conversation_id: str, **kwargs):
        """Update conversation workflow state."""
        with self.db_manager.get_db_context() as db:
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation:
                for key, value in kwargs.items():
                    if hasattr(conversation, key):
                        setattr(conversation, key, value)
                logger.debug(f"Updated conversation state: {conversation_id}")
    
    def get_user_conversations(self, user_id: str, limit: int = 50):
        """Get user's conversations."""
        with self.db_manager.get_db_context() as db:
            return db.query(Conversation)\
                    .filter(Conversation.user_id == user_id)\
                    .order_by(Conversation.created_at.desc())\
                    .limit(limit)\
                    .all()


class DocumentRepository:
    """Revolutionary document repository with comprehensive academic metadata."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_document(self, user_id: str, conversation_id: str, **kwargs) -> Document:
        """Create a new document with comprehensive metadata."""
        with self.db_manager.get_db_context() as db:
            document = Document(
                user_id=user_id,
                conversation_id=conversation_id,
                **kwargs
            )
            db.add(document)
            db.flush()
            
            logger.info(f"Created document: {document.id}")
            return document
    
    def get_document(self, document_id: str) -> Optional[Document]:
        """Get document by ID."""
        with self.db_manager.get_db_context() as db:
            return db.query(Document).filter(Document.id == document_id).first()
    
    def update_document(self, document_id: str, **kwargs):
        """Update document with new data."""
        with self.db_manager.get_db_context() as db:
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                for key, value in kwargs.items():
                    if hasattr(document, key):
                        setattr(document, key, value)
                logger.debug(f"Updated document: {document_id}")
    
    def get_user_documents(self, user_id: str, limit: int = 50):
        """Get user's documents."""
        with self.db_manager.get_db_context() as db:
            return db.query(Document)\
                    .filter(Document.user_id == user_id)\
                    .order_by(Document.created_at.desc())\
                    .limit(limit)\
                    .all()
    
    def get_by_conversation_and_type(self, conversation_id: str, document_type: str) -> Optional[Document]:
        """Get document by conversation ID and document type."""
        with self.db_manager.get_db_context() as db:
            return db.query(Document)\
                    .filter(Document.conversation_id == conversation_id)\
                    .filter(Document.document_type == document_type)\
                    .first()
    
    def get_conversation_documents(self, conversation_id: str) -> list[Document]:
        """Get all documents for a conversation."""
        with self.db_manager.get_db_context() as db:
            return db.query(Document)\
                    .filter(Document.conversation_id == conversation_id)\
                    .order_by(Document.created_at.desc())\
                    .all()


# Singleton instances - lazy initialization
_db_manager = None
_user_repo = None
_conversation_repo = None
_document_repo = None

def get_db_manager():
    """Get or create database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

def get_user_repo():
    """Get or create user repository instance."""
    global _user_repo
    if _user_repo is None:
        _user_repo = UserRepository(get_db_manager())
    return _user_repo

def get_conversation_repo():
    """Get or create conversation repository instance."""
    global _conversation_repo
    if _conversation_repo is None:
        _conversation_repo = ConversationRepository(get_db_manager())
    return _conversation_repo

def get_document_repo():
    """Get or create document repository instance."""
    global _document_repo
    if _document_repo is None:
        _document_repo = DocumentRepository(get_db_manager())
    return _document_repo

# For backward compatibility
db_manager = property(lambda self: get_db_manager())
user_repo = property(lambda self: get_user_repo())
conversation_repo = property(lambda self: get_conversation_repo())
document_repo = property(lambda self: get_document_repo())


# Dependency injection for FastAPI
def get_database() -> Generator[Session, None, None]:
    """Dependency for FastAPI route handlers."""
    yield from get_db_manager().get_db_session()


def get_user_repository() -> UserRepository:
    """Get user repository instance."""
    return get_user_repo()


def get_conversation_repository() -> ConversationRepository:
    """Get conversation repository instance."""
    return get_conversation_repo()


def get_document_repository() -> DocumentRepository:
    """Get document repository instance."""
    return get_document_repo()