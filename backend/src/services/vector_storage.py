"""
Revolutionary Vector Storage Service with pgvector integration.
Production-ready semantic search and vector similarity for academic sources.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime

from db.database import DatabaseManager, db_manager

logger = logging.getLogger(__name__)

# Extended base for vector models
VectorBase = declarative_base()


class VectorDocument(VectorBase):
    """Vector storage model for semantic search of academic documents."""
    __tablename__ = "vector_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(String(255), nullable=False, index=True)  # References source in main DB
    conversation_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Content and metadata
    title = Column(String(1000), nullable=False)
    abstract = Column(Text, nullable=True)
    content_preview = Column(Text, nullable=True)  # First 500 chars
    authors = Column(String(500), nullable=True)
    publication_year = Column(Integer, nullable=True)
    academic_field = Column(String(100), nullable=True)

    # Vector embeddings (1536 dimensions for OpenAI embeddings)
    title_embedding = Column(Vector(1536), nullable=True)
    abstract_embedding = Column(Vector(1536), nullable=True)
    content_embedding = Column(Vector(1536), nullable=True)

    # Quality metrics
    credibility_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class VectorEvidenceMap(VectorBase):
    """Vector storage for evidence mapping and hover card data."""
    __tablename__ = "vector_evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    source_id = Column(String(255), nullable=False, index=True)

    # Evidence content
    evidence_text = Column(Text, nullable=False)
    evidence_type = Column(String(50), nullable=True)  # systematic_review, experimental, etc.
    key_insights = Column(Text, nullable=True)

    # Vector embedding for semantic matching
    evidence_embedding = Column(Vector(1536), nullable=True)

    # Quality metrics
    evidence_quality_score = Column(Float, nullable=True)
    academic_indicators = Column(String(500), nullable=True)  # Comma-separated

    # Positioning data
    paragraph_position = Column(Integer, nullable=True)
    relevance_score = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Chunk(VectorBase):
    """Vector storage model for file chunks."""
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String(255), nullable=False)
    chunk = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class RevolutionaryVectorStorage:
    """Production-ready vector storage service with advanced semantic search."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.embedding_dimension = 1536  # OpenAI embedding dimension
        self._initialize_pgvector()
        self._setup_vector_tables()

    def _initialize_pgvector(self):
        """Initialize pgvector extension in PostgreSQL."""
        try:
            with self.db_manager.get_db_context() as db:
                # Enable pgvector extension
                db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                logger.info("pgvector extension enabled successfully")
        except Exception as e:
            logger.error(f"Failed to initialize pgvector: {e}")
            raise

    def _setup_vector_tables(self):
        """Setup vector tables and indexes."""
        try:
            # Create vector tables
            VectorBase.metadata.create_all(bind=self.db_manager.engine)

            # Create vector indexes for performance
            with self.db_manager.get_db_context() as db:

                # Create HNSW indexes for fast similarity search
                db.execute(text("""
                    CREATE INDEX IF NOT EXISTS vector_documents_title_embedding_idx
                    ON vector_documents USING hnsw (title_embedding vector_cosine_ops)
                """))

                db.execute(text("""
                    CREATE INDEX IF NOT EXISTS vector_documents_abstract_embedding_idx
                    ON vector_documents USING hnsw (abstract_embedding vector_cosine_ops)
                """))

                db.execute(text("""
                    CREATE INDEX IF NOT EXISTS vector_documents_content_embedding_idx
                    ON vector_documents USING hnsw (content_embedding vector_cosine_ops)
                """))

                db.execute(text("""
                    CREATE INDEX IF NOT EXISTS vector_evidence_embedding_idx
                    ON vector_evidence USING hnsw (evidence_embedding vector_cosine_ops)
                """))

                # Create composite indexes for filtered searches
                db.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_vector_docs_field_year
                    ON vector_documents(academic_field, publication_year DESC)
                """))

                db.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_vector_evidence_conversation
                    ON vector_evidence(conversation_id, evidence_quality_score DESC)
                """))

                db.execute(text("""
                    CREATE INDEX IF NOT EXISTS chunks_embedding_idx
                    ON chunks USING hnsw (embedding vector_cosine_ops)
                """))

                logger.info("Vector indexes created successfully")

        except Exception as e:
            logger.error(f"Failed to setup vector tables: {e}")
            raise

    async def store_chunks(self, file_name: str, chunks: List[str], embeddings: List[List[float]], user_id: Optional[str] = None) -> List[str]:
        """Store file chunks with their embeddings, associating with a user if provided."""
        try:
            stored_ids = []
            with self.db_manager.get_db_context() as db:
                for chunk_text, embedding in zip(chunks, embeddings):
                    chunk = Chunk(
                        file_name=file_name,
                        chunk=chunk_text,
                        embedding=embedding,
                        user_id=user_id
                    )
                    db.add(chunk)
                    db.flush()
                    stored_ids.append(str(chunk.id))
            logger.info(f"Stored {len(stored_ids)} chunks for file {file_name}")
            return stored_ids
        except Exception as e:
            logger.error(f"Failed to store chunks: {e}")
            raise

    async def retrieve_chunks(self, query_embedding: List[float], k: int = 10, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve chunks using vector similarity search, optionally filtering by user."""
        try:
            with self.db_manager.get_db_context() as db:
                query = db.query(
                    Chunk,
                    (1 - Chunk.embedding.cosine_distance(query_embedding)).label("similarity")
                )
                if user_id:
                    query = query.filter(Chunk.user_id == user_id)

                results = query.order_by(
                    (1 - Chunk.embedding.cosine_distance(query_embedding)).desc()
                ).limit(k).all()

                return [
                    {
                        "chunk": row.Chunk.chunk,
                        "file_name": row.Chunk.file_name,
                        "similarity": row.similarity
                    }
                    for row in results
                ]
        except Exception as e:
            logger.error(f"Failed to retrieve chunks: {e}")
            raise

    async def store_document_vectors(
        self,
        source_data: Dict[str, Any],
        embeddings: Dict[str, List[float]],
        conversation_id: Optional[str] = None
    ) -> str:
        """Store document with vector embeddings."""
        try:
            with self.db_manager.get_db_context() as db:

                vector_doc = VectorDocument(
                    source_id=source_data.get("id", str(uuid.uuid4())),
                    conversation_id=uuid.UUID(conversation_id) if conversation_id else None,
                    title=source_data.get("title", ""),
                    abstract=source_data.get("abstract", ""),
                    content_preview=source_data.get("content", "")[:500] if source_data.get("content") else None,
                    authors=", ".join(source_data.get("authors", [])),
                    publication_year=self._extract_year(source_data.get("publication_date")),
                    academic_field=source_data.get("academic_field"),
                    title_embedding=embeddings.get("title_embedding"),
                    abstract_embedding=embeddings.get("abstract_embedding"),
                    content_embedding=embeddings.get("content_embedding"),
                    credibility_score=source_data.get("credibility_score"),
                    relevance_score=source_data.get("relevance_score")
                )

                db.add(vector_doc)
                db.flush()

                logger.info(f"Stored vector document: {vector_doc.id}")
                return str(vector_doc.id)

        except Exception as e:
            logger.error(f"Failed to store document vectors: {e}")
            raise

    async def store_private_document_chunks(
        self,
        document_id: str,
        user_id: str,
        chunks: List[str],
        embeddings: List[List[float]]
    ) -> List[str]:
        """Stores private document chunks with their embeddings."""
        from db.models import PrivateChunk
        try:
            stored_ids = []
            with self.db_manager.get_db_context() as db:
                for chunk_text, embedding in zip(chunks, embeddings):
                    private_chunk = PrivateChunk(
                        document_id=uuid.UUID(document_id),
                        user_id=uuid.UUID(user_id),
                        chunk_text=chunk_text,
                        embedding=embedding
                    )
                    db.add(private_chunk)
                    db.flush()
                    stored_ids.append(str(private_chunk.id))
            logger.info(f"Stored {len(stored_ids)} private chunks for document {document_id}")
            return stored_ids
        except Exception as e:
            logger.error(f"Failed to store private document chunks: {e}")
            raise

    async def store_evidence_vectors(
        self,
        conversation_id: str,
        evidence_data: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> List[str]:
        """Store evidence with vector embeddings."""
        try:
            stored_ids = []

            with self.db_manager.get_db_context() as db:

                for evidence, embedding in zip(evidence_data, embeddings):
                    vector_evidence = VectorEvidenceMap(
                        conversation_id=uuid.UUID(conversation_id),
                        source_id=evidence.get("source_id", ""),
                        evidence_text=evidence.get("text", ""),
                        evidence_type=evidence.get("evidence_type"),
                        key_insights="; ".join(evidence.get("key_insights", [])),
                        evidence_embedding=embedding,
                        evidence_quality_score=evidence.get("relevance_score"),
                        academic_indicators=", ".join(evidence.get("academic_indicators", [])),
                        paragraph_position=evidence.get("position"),
                        relevance_score=evidence.get("relevance_score")
                    )

                    db.add(vector_evidence)
                    db.flush()
                    stored_ids.append(str(vector_evidence.id))

                logger.info(f"Stored {len(stored_ids)} evidence vectors for conversation {conversation_id}")
                return stored_ids

        except Exception as e:
            logger.error(f"Failed to store evidence vectors: {e}")
            raise

    async def semantic_search_documents(
        self,
        query_embedding: List[float],
        limit: int = 10,
        academic_field: Optional[str] = None,
        min_credibility: float = 0.6,
        year_range: Optional[Tuple[int, int]] = None,
        user_id: Optional[str] = None # For accessing private documents
    ) -> List[Dict[str, Any]]:
        """Perform semantic search on documents using vector similarity."""
        from db.models import PrivateChunk
        try:
            with self.db_manager.get_db_context() as db:

                # Public search
                public_query = db.query(
                    VectorDocument,
                    (1 - VectorDocument.content_embedding.cosine_distance(query_embedding)).label("similarity")
                ).filter(
                    VectorDocument.credibility_score >= min_credibility
                )
                if academic_field:
                    public_query = public_query.filter(VectorDocument.academic_field == academic_field)
                if year_range:
                    public_query = public_query.filter(VectorDocument.publication_year.between(*year_range))

                public_results = public_query.order_by(
                    (1 - VectorDocument.content_embedding.cosine_distance(query_embedding)).desc()
                ).limit(limit).all()

                search_results = [
                    {
                        "id": str(doc.id), "source_id": doc.source_id, "title": doc.title,
                        "abstract": doc.abstract, "authors": doc.authors,
                        "publication_year": doc.publication_year, "academic_field": doc.academic_field,
                        "credibility_score": doc.credibility_score, "semantic_similarity": sim,
                        "access_class": "public"
                    }
                    for doc, sim in public_results
                ]

                # Private search if user_id is provided
                if user_id:
                    private_query = db.query(
                        PrivateChunk,
                        (1 - PrivateChunk.embedding.cosine_distance(query_embedding)).label("similarity")
                    ).filter(PrivateChunk.user_id == uuid.UUID(user_id))

                    private_results = private_query.order_by(
                        (1 - PrivateChunk.embedding.cosine_distance(query_embedding)).desc()
                    ).limit(limit).all()

                    search_results.extend([
                        {
                            "id": str(chunk.id), "source_id": str(chunk.document_id), "title": "Private Document",
                            "abstract": chunk.chunk_text[:200], "authors": ["You"],
                            "publication_year": datetime.now().year, "academic_field": "private",
                            "credibility_score": 1.0, "semantic_similarity": sim,
                            "access_class": "private"
                        }
                        for chunk, sim in private_results
                    ])

                # Sort combined results and take top N
                search_results.sort(key=lambda x: x["semantic_similarity"], reverse=True)

                logger.info(f"Semantic search returned {len(search_results[:limit])} documents")
                return search_results[:limit]

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            raise

    async def find_similar_evidence(
        self,
        query_embedding: List[float],
        conversation_id: Optional[str] = None,
        evidence_type: Optional[str] = None,
        min_quality: float = 0.7,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar evidence using vector similarity."""
        try:
            with self.db_manager.get_db_context() as db:

                query = db.query(
                    VectorEvidenceMap,
                    (1 - VectorEvidenceMap.evidence_embedding.cosine_distance(query_embedding)).label("similarity")
                ).filter(
                    VectorEvidenceMap.evidence_quality_score >= min_quality
                )

                # Apply optional filters
                if conversation_id:
                    query = query.filter(VectorEvidenceMap.conversation_id == uuid.UUID(conversation_id))

                if evidence_type:
                    query = query.filter(VectorEvidenceMap.evidence_type == evidence_type)

                results = query.order_by(
                    (1 - VectorEvidenceMap.evidence_embedding.cosine_distance(query_embedding)).desc()
                ).limit(limit).all()

                # Format results
                evidence_results = []
                for row in results:
                    evidence = row[0]
                    similarity = float(row[1]) if row[1] else 0.0

                    evidence_results.append({
                        "id": str(evidence.id),
                        "source_id": evidence.source_id,
                        "evidence_text": evidence.evidence_text,
                        "evidence_type": evidence.evidence_type,
                        "key_insights": evidence.key_insights,
                        "academic_indicators": evidence.academic_indicators,
                        "quality_score": evidence.evidence_quality_score,
                        "semantic_similarity": similarity
                    })

                logger.info(f"Found {len(evidence_results)} similar evidence pieces")
                return evidence_results

        except Exception as e:
            logger.error(f"Evidence similarity search failed: {e}")
            raise

    async def get_conversation_evidence(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all evidence for a specific conversation."""
        try:
            with self.db_manager.get_db_context() as db:

                evidence_list = db.query(VectorEvidenceMap).filter(
                    VectorEvidenceMap.conversation_id == uuid.UUID(conversation_id)
                ).order_by(VectorEvidenceMap.evidence_quality_score.desc()).all()

                results = []
                for evidence in evidence_list:
                    results.append({
                        "id": str(evidence.id),
                        "source_id": evidence.source_id,
                        "evidence_text": evidence.evidence_text,
                        "evidence_type": evidence.evidence_type,
                        "key_insights": evidence.key_insights,
                        "quality_score": evidence.evidence_quality_score,
                        "paragraph_position": evidence.paragraph_position
                    })

                return results

        except Exception as e:
            logger.error(f"Failed to get conversation evidence: {e}")
            raise

    async def cleanup_old_vectors(self, days_old: int = 30):
        """Clean up old vector data to save storage."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)

            with self.db_manager.get_db_context() as db:

                # Delete old documents
                deleted_docs = db.query(VectorDocument).filter(
                    VectorDocument.created_at < cutoff_date
                ).delete()

                # Delete old evidence
                deleted_evidence = db.query(VectorEvidenceMap).filter(
                    VectorEvidenceMap.created_at < cutoff_date
                ).delete()

                logger.info(f"Cleaned up {deleted_docs} old vector documents and {deleted_evidence} evidence entries")

        except Exception as e:
            logger.error(f"Vector cleanup failed: {e}")
            raise

    def _extract_year(self, date_string: Optional[str]) -> Optional[int]:
        """Extract year from date string."""
        if not date_string:
            return None

        try:
            # Try to extract 4-digit year
            import re
            year_match = re.search(r'\b(\d{4})\b', str(date_string))
            if year_match:
                year = int(year_match.group(1))
                if 1900 <= year <= 2030:  # Reasonable year range
                    return year
        except:
            pass

        return None


# Global vector storage instance
vector_storage = RevolutionaryVectorStorage(db_manager)


# Dependency injection for FastAPI
def get_vector_storage() -> RevolutionaryVectorStorage:
    """Get vector storage instance."""
    return vector_storage
