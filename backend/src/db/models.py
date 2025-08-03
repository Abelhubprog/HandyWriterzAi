"""Revolutionary SQLAlchemy models for HandyWriterz with comprehensive academic data structures."""

import uuid
from datetime import datetime
from typing import Dict, Any
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, Boolean, ForeignKey, LargeBinary, Enum as SQLEnum, BigInteger, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from enum import Enum


Base = declarative_base()


class UserType(Enum):
    """User type classification."""
    STUDENT = "student"
    TUTOR = "tutor"
    ADMIN = "admin"
    PREMIUM = "premium"


class WorkflowStatus(Enum):
    """Comprehensive workflow status tracking."""
    INITIATED = "initiated"
    PROCESSING = "processing"
    ANALYZING = "analyzing"
    SEARCHING = "searching"
    WRITING = "writing"
    EVALUATING = "evaluating"
    TURNITIN_CHECK = "turnitin_check"
    FORMATTING = "formatting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DocumentType(Enum):
    """Academic document type classification."""
    ESSAY = "essay"
    RESEARCH_PAPER = "research_paper"
    THESIS = "thesis"
    DISSERTATION = "dissertation"
    REPORT = "report"
    LITERATURE_REVIEW = "literature_review"
    CASE_STUDY = "case_study"
    COURSEWORK = "coursework"


class User(Base):
    """Revolutionary user model with comprehensive academic profiling."""
    __tablename__ = "users"

    # Core identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_address = Column(String(100), unique=True, nullable=False, index=True)
    dynamic_user_id = Column(String(100), unique=True, nullable=True, index=True)

    # Profile information
    email = Column(String(255), unique=True, nullable=True, index=True)
    username = Column(String(100), unique=True, nullable=True)
    full_name = Column(String(200), nullable=True)
    user_type = Column(SQLEnum(UserType), default=UserType.STUDENT, nullable=False)

    # Academic profile
    institution = Column(String(200), nullable=True)
    academic_level = Column(String(50), nullable=True)  # undergraduate, graduate, doctoral
    field_of_study = Column(String(100), nullable=True)
    preferred_citation_style = Column(String(50), default="harvard")

    # Usage analytics
    total_documents_created = Column(Integer, default=0)
    total_words_written = Column(Integer, default=0)
    average_quality_score = Column(Float, default=0.0)
    subscription_tier = Column(String(50), default="free")
    credits_remaining = Column(Integer, default=3)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    user_fingerprints = relationship("UserFingerprint", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary representation."""
        return {
            "id": str(self.id),
            "wallet_address": self.wallet_address,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "user_type": self.user_type.value if self.user_type else None,
            "institution": self.institution,
            "academic_level": self.academic_level,
            "field_of_study": self.field_of_study,
            "total_documents_created": self.total_documents_created,
            "average_quality_score": self.average_quality_score,
            "subscription_tier": self.subscription_tier,
            "credits_remaining": self.credits_remaining,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }


class Conversation(Base):
    """Revolutionary conversation model with comprehensive workflow tracking."""
    __tablename__ = "conversations"

    # Core identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Conversation metadata
    title = Column(String(500), nullable=True)
    workflow_status = Column(SQLEnum(WorkflowStatus), default=WorkflowStatus.INITIATED, nullable=False)

    # User parameters (from frontend)
    user_params = Column(JSON, nullable=False, default=dict)

    # Workflow state tracking
    current_node = Column(String(100), nullable=True)
    workflow_progress = Column(Float, default=0.0)  # 0.0 to 1.0
    retry_count = Column(Integer, default=0)

    # Revolutionary orchestration data
    orchestration_result = Column(JSON, nullable=True)
    workflow_intelligence = Column(JSON, nullable=True)

    # Research and content data
    research_agenda = Column(JSON, nullable=True)  # List of research questions
    outline = Column(JSON, nullable=True)  # Hierarchical outline

    # Search results from multiple agents
    search_results = Column(JSON, nullable=True)  # Aggregated from all search agents
    verified_sources = Column(JSON, nullable=True)  # After source filtering

    # Content progression
    current_draft = Column(Text, nullable=True)
    draft_history = Column(JSON, nullable=True)  # List of previous drafts

    # Advanced evaluation results
    evaluation_results = Column(JSON, nullable=True)  # Multi-model evaluation
    comprehensive_evaluation = Column(JSON, nullable=True)  # Revolutionary evaluation

    # Academic integrity analysis
    turnitin_results = Column(JSON, nullable=True)
    similarity_score = Column(Float, nullable=True)
    ai_detection_score = Column(Float, nullable=True)

    # Final outputs
    formatted_document = Column(JSON, nullable=True)  # Multiple formats
    quality_metrics = Column(JSON, nullable=True)

    # Performance metrics
    processing_duration = Column(Float, nullable=True)  # Total seconds
    tokens_used = Column(Integer, default=0)
    api_calls_made = Column(Integer, default=0)

    # Error handling
    error_message = Column(Text, nullable=True)
    failed_node = Column(String(100), nullable=True)
    recovery_attempts = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="conversations")
    documents = relationship("Document", back_populates="conversation", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary representation."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "workflow_status": self.workflow_status.value if self.workflow_status else None,
            "user_params": self.user_params,
            "current_node": self.current_node,
            "workflow_progress": self.workflow_progress,
            "research_agenda": self.research_agenda,
            "outline": self.outline,
            "current_draft": self.current_draft,
            "similarity_score": self.similarity_score,
            "ai_detection_score": self.ai_detection_score,
            "processing_duration": self.processing_duration,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class Document(Base):
    """Revolutionary document model with comprehensive academic metadata."""
    __tablename__ = "documents"

    # Core identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True)

    # Document metadata
    title = Column(String(500), nullable=False)
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    academic_field = Column(String(100), nullable=False)
    access_class = Column(String(50), default="public", nullable=False) # public or private

    # Content and formatting
    content_markdown = Column(Text, nullable=False)
    content_docx = Column(LargeBinary, nullable=True)
    content_pdf = Column(LargeBinary, nullable=True)
    content_html = Column(Text, nullable=True)

    # Academic specifications
    word_count = Column(Integer, nullable=False)
    target_word_count = Column(Integer, nullable=False)
    citation_style = Column(String(50), nullable=False)
    citation_count = Column(Integer, default=0)

    # Quality and assessment
    overall_quality_score = Column(Float, nullable=True)
    quality_breakdown = Column(JSON, nullable=True)
    evaluation_summary = Column(JSON, nullable=True)

    # Academic integrity
    similarity_percentage = Column(Float, nullable=True)
    ai_detection_percentage = Column(Float, nullable=True)
    turnitin_report = Column(JSON, nullable=True)

    # Learning outcomes
    learning_outcomes_coverage = Column(JSON, nullable=True)
    lo_mapping_report = Column(LargeBinary, nullable=True)  # PDF report

    # Source and citation analysis
    sources_used = Column(JSON, nullable=True)  # List of sources
    citation_quality_analysis = Column(JSON, nullable=True)
    bibliography = Column(Text, nullable=True)

    # Processing metadata
    generation_duration = Column(Float, nullable=True)
    revision_count = Column(Integer, default=0)
    processing_nodes_used = Column(JSON, nullable=True)  # List of agent nodes

    # File storage URLs (for cloud storage)
    docx_url = Column(String(500), nullable=True)
    pdf_url = Column(String(500), nullable=True)
    lo_report_url = Column(String(500), nullable=True)

    # Version control
    version_number = Column(String(20), default="1.0")
    parent_document_id = Column(UUID(as_uuid=True), nullable=True)  # For revisions

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="documents")
    conversation = relationship("Conversation", back_populates="documents")

    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary representation."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "conversation_id": str(self.conversation_id),
            "title": self.title,
            "document_type": self.document_type.value if self.document_type else None,
            "academic_field": self.academic_field,
            "word_count": self.word_count,
            "target_word_count": self.target_word_count,
            "citation_style": self.citation_style,
            "citation_count": self.citation_count,
            "overall_quality_score": self.overall_quality_score,
            "similarity_percentage": self.similarity_percentage,
            "ai_detection_percentage": self.ai_detection_percentage,
            "revision_count": self.revision_count,
            "version_number": self.version_number,
            "docx_url": self.docx_url,
            "pdf_url": self.pdf_url,
            "lo_report_url": self.lo_report_url,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class UserFingerprint(Base):
    """Revolutionary user fingerprint model for academic writing style analysis."""
    __tablename__ = "user_fingerprints"

    # Core identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Fingerprint metadata
    fingerprint_name = Column(String(200), nullable=False)
    academic_level = Column(String(50), nullable=False)
    field_of_study = Column(String(100), nullable=False)

    # Writing style characteristics
    style_characteristics = Column(JSON, nullable=False)  # Comprehensive style analysis
    vocabulary_profile = Column(JSON, nullable=False)  # Vocabulary patterns
    syntactic_patterns = Column(JSON, nullable=False)  # Sentence structure patterns
    argumentation_style = Column(JSON, nullable=False)  # Argument construction patterns

    # Academic writing metrics
    average_sentence_length = Column(Float, nullable=True)
    lexical_diversity = Column(Float, nullable=True)
    academic_sophistication = Column(Float, nullable=True)
    citation_patterns = Column(JSON, nullable=True)

    # Learning and adaptation
    documents_analyzed = Column(Integer, default=0)
    confidence_score = Column(Float, default=0.0)
    last_updated_from_document = Column(UUID(as_uuid=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="user_fingerprints")

    def to_dict(self) -> Dict[str, Any]:
        """Convert fingerprint to dictionary representation."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "fingerprint_name": self.fingerprint_name,
            "academic_level": self.academic_level,
            "field_of_study": self.field_of_study,
            "average_sentence_length": self.average_sentence_length,
            "lexical_diversity": self.lexical_diversity,
            "academic_sophistication": self.academic_sophistication,
            "documents_analyzed": self.documents_analyzed,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class SourceCache(Base):
    """Revolutionary source caching model for efficient research management."""
    __tablename__ = "source_cache"

    # Core identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Source identification
    url = Column(String(1000), nullable=False, index=True)
    title = Column(String(1000), nullable=False)
    authors = Column(JSON, nullable=True)  # List of authors

    # Content and metadata
    abstract = Column(Text, nullable=True)
    full_content = Column(Text, nullable=True)
    doi = Column(String(200), nullable=True, index=True)
    publication_year = Column(Integer, nullable=True)
    publication_venue = Column(String(500), nullable=True)

    # Quality assessment
    credibility_score = Column(Float, nullable=True)
    quality_analysis = Column(JSON, nullable=True)
    peer_review_status = Column(Boolean, default=False)

    # Usage analytics
    times_accessed = Column(Integer, default=0)
    last_accessed = Column(DateTime, nullable=True)
    search_keywords = Column(JSON, nullable=True)  # Keywords that found this source

    # Advanced analysis
    academic_field_tags = Column(JSON, nullable=True)
    methodology_tags = Column(JSON, nullable=True)
    theoretical_frameworks = Column(JSON, nullable=True)

    # Embeddings for similarity search
    content_embedding = Column(JSON, nullable=True)  # Vector embedding
    abstract_embedding = Column(JSON, nullable=True)  # Abstract embedding

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert source to dictionary representation."""
        return {
            "id": str(self.id),
            "url": self.url,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "doi": self.doi,
            "publication_year": self.publication_year,
            "publication_venue": self.publication_venue,
            "credibility_score": self.credibility_score,
            "peer_review_status": self.peer_review_status,
            "times_accessed": self.times_accessed,
            "academic_field_tags": self.academic_field_tags,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class SystemMetrics(Base):
    """Revolutionary system metrics for performance monitoring and optimization."""
    __tablename__ = "system_metrics"

    # Core identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Metric identification
    metric_name = Column(String(100), nullable=False, index=True)
    metric_category = Column(String(50), nullable=False, index=True)  # performance, quality, usage

    # Metric data
    metric_value = Column(Float, nullable=False)
    metric_metadata = Column(JSON, nullable=True)

    # Context
    node_name = Column(String(100), nullable=True)  # Which agent node
    conversation_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Aggregation period
    time_period = Column(String(20), nullable=True)  # hourly, daily, weekly
    aggregation_type = Column(String(20), nullable=True)  # avg, sum, max, min

    # Timestamps
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary representation."""
        return {
            "id": str(self.id),
            "metric_name": self.metric_name,
            "metric_category": self.metric_category,
            "metric_value": self.metric_value,
            "metric_metadata": self.metric_metadata,
            "node_name": self.node_name,
            "conversation_id": str(self.conversation_id) if self.conversation_id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None
        }

class ChunkStatus(Enum):
    """Status of a document chunk in the checking workflow."""
    OPEN = "open"
    CHECKING = "checking"
    NEEDS_EDIT = "needs_edit"
    DONE = "done"
    TELEGRAM_FAILED = "telegram_failed"

class PayoutStatus(Enum):
    """Status of a checker's payout."""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"

class Checker(Base):
    """Represents a human checker with KYC, wallet, etc."""
    __tablename__ = "checkers"
    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    wallet_address = Column(String(100), unique=True, nullable=False, index=True)
    whatsapp_number = Column(String(20), nullable=True)
    specialties = Column(ARRAY(String), nullable=True) # e.g., ['nursing', 'social_work']
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    submissions = relationship("Submission", back_populates="checker")
    payouts = relationship("CheckerPayout", back_populates="checker")

class DocLot(Base):
    """Represents a whole essay job, which is composed of multiple chunks."""
    __tablename__ = "doc_lots"
    id = Column(Integer, primary_key=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    status = Column(String(50), default="processing") # e.g., processing, needs_approval, completed
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document")
    chunks = relationship("DocChunk", back_populates="lot")

class DocChunk(Base):
    """Represents a 350-word slice of a document for Turnitin checking."""
    __tablename__ = "doc_chunks"
    id = Column(Integer, primary_key=True)
    lot_id = Column(Integer, ForeignKey("doc_lots.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content_markdown = Column(Text, nullable=False)
    s3_key = Column(String(500), nullable=False) # Path to the chunk file
    status = Column(SQLEnum(ChunkStatus), default=ChunkStatus.OPEN, nullable=False)

    checker_id = Column(Integer, ForeignKey("checkers.id"), nullable=True)
    claim_timestamp = Column(DateTime, nullable=True)

    current_version = Column(Integer, default=0)

    similarity_report_url = Column(String(500), nullable=True)
    ai_report_url = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lot = relationship("DocLot", back_populates="chunks")
    checker = relationship("Checker")
    submissions = relationship("Submission", back_populates="chunk")

class Submission(Base):
    """Represents a checker's submission of PDFs and flagged text."""
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True)
    chunk_id = Column(Integer, ForeignKey("doc_chunks.id"), nullable=False)
    checker_id = Column(Integer, ForeignKey("checkers.id"), nullable=False)
    version = Column(Integer, nullable=False) # Corresponds to chunk.current_version

    similarity_report_url = Column(String(500), nullable=False)
    ai_report_url = Column(String(500), nullable=False)
    flagged_json = Column(JSON, nullable=True) # {"flags": ["text1", "text2"]}

    created_at = Column(DateTime, default=datetime.utcnow)

    chunk = relationship("DocChunk", back_populates="submissions")
    checker = relationship("Checker", back_populates="submissions")

class CheckerPayout(Base):
    """Represents an amount of money owed to a checker for an approved chunk."""
    __tablename__ = "checker_payouts"
    id = Column(Integer, primary_key=True)
    checker_id = Column(Integer, ForeignKey("checkers.id"), nullable=False)
    chunk_id = Column(Integer, ForeignKey("doc_chunks.id"), nullable=False)
    amount_pence = Column(Integer, nullable=False)
    status = Column(SQLEnum(PayoutStatus), default=PayoutStatus.PENDING, nullable=False)
    transaction_hash = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)

    checker = relationship("Checker", back_populates="payouts")
    chunk = relationship("DocChunk")

class WalletEscrow(Base):
    """Stub table for on-chain escrow interactions."""
    __tablename__ = "wallet_escrows"
    id = Column(Integer, primary_key=True)
    tx_hash = Column(String(255), primary_key=True)
    checker_id = Column(Integer, ForeignKey("checkers.id"), nullable=False)
    amount = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False) # e.g., 'locked', 'released', 'refunded'
    created_at = Column(DateTime, default=datetime.utcnow)

class PrivateChunk(Base):
    """Stores chunks of private documents for vectorization."""
    __tablename__ = "private_chunks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True) # Or use a specific vector type
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document")
    user = relationship("User")

class StudyCircle(Base):
    """Represents a study circle for collaborative work."""
    __tablename__ = "study_circles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User")
    members = relationship("User", secondary="study_circle_members")
    documents = relationship("Document", secondary="study_circle_documents")

class StudyCircleMember(Base):
    """Association table for users and study circles."""
    __tablename__ = "study_circle_members"
    circle_id = Column(UUID(as_uuid=True), ForeignKey("study_circles.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)

class StudyCircleDocument(Base):
    """Association table for documents and study circles."""
    __tablename__ = "study_circle_documents"
    circle_id = Column(UUID(as_uuid=True), ForeignKey("study_circles.id"), primary_key=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), primary_key=True)


# -----------------------------
# HITL Turnitin Workbench Models
# -----------------------------

class WorkbenchUserRole(Enum):
    ADMIN = "admin"
    CHECKER = "checker"

class WorkbenchAssignmentStatus(Enum):
    QUEUED = "queued"
    ASSIGNED = "assigned"
    CHECKING = "checking"
    NEEDS_EDIT = "needs_edit"
    AWAITING_UPLOAD = "awaiting_upload"
    AWAITING_VERIFICATION = "awaiting_verification"
    VERIFIED = "verified"
    REJECTED = "rejected"
    CLOSED = "closed"
    ITERATION_PENDING_AI_REWRITE = "iteration_pending_ai_rewrite"
    ITERATION_PENDING_HUMAN_REVIEW = "iteration_pending_human_review"


class WorkbenchDeliveryChannel(Enum):
    TELEGRAM = "telegram"
    WORKBENCH = "workbench"


class WorkbenchSubmissionStatus(Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class WorkbenchArtifactType(Enum):
    SIMILARITY_REPORT_PDF = "similarity_report_pdf"
    AI_REPORT_PDF = "ai_report_pdf"
    MODIFIED_DOCX = "modified_docx"
    MODIFIED_PDF = "modified_pdf"
    RAW_CHUNK_PDF = "raw_chunk_pdf"
    ORIGINAL_DOCX_UPLOAD = "original_docx_upload"
    HIGHLIGHTED_IMAGE = "highlighted_image"
    OTHER = "other"


class WorkbenchUser(Base):
    """Represents a user specifically for the Workbench (admin or checker)."""
    __tablename__ = "workbench_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(SQLEnum(WorkbenchUserRole), default=WorkbenchUserRole.CHECKER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_workbench_users_username", "username"),
        Index("ix_workbench_users_email", "email"),
    )


class WorkbenchAssignment(Base):
    __tablename__ = "workbench_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    source_conversation_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    title = Column(Text, nullable=True)
    status = Column(SQLEnum(WorkbenchAssignmentStatus), default=WorkbenchAssignmentStatus.QUEUED, nullable=False, index=True)
    assigned_checker_id = Column(UUID(as_uuid=True), ForeignKey("workbench_users.id"), nullable=True, index=True) # FK to workbench_users
    delivery_channel = Column(SQLEnum(WorkbenchDeliveryChannel), default=WorkbenchDeliveryChannel.WORKBENCH, nullable=False)

    ai_metadata = Column(JSONB, nullable=True)
    requirements = Column(JSONB, nullable=True)
    telegram_message_ref = Column(JSONB, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    soft_deleted = Column(Boolean, default=False, nullable=False)

    # relationships
    user = relationship("User")
    assigned_checker = relationship("WorkbenchUser") # Relationship to WorkbenchUser
    submissions = relationship("WorkbenchSubmission", back_populates="assignment", cascade="all, delete-orphan")
    artifacts = relationship("WorkbenchArtifact", back_populates="assignment", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_workbench_assignments_tenant_created_desc", "tenant_id", "created_at"),
        Index("ix_workbench_assignments_status_created", "status", "created_at"),
        Index("ix_workbench_assignments_source_conversation", "source_conversation_id"),
    )


class WorkbenchSubmission(Base):
    __tablename__ = "workbench_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("workbench_assignments.id"), nullable=False, index=True)
    checker_id = Column(UUID(as_uuid=True), ForeignKey("workbench_users.id"), nullable=False, index=True) # FK to workbench_users

    # idempotency for flaky re-uploads
    submission_id = Column(String(255), unique=True, nullable=False)

    # human uploads (JSONB for structured metadata + file references)
    similarity_report = Column(JSONB, nullable=False)  # expected to contain url(s), score fields, etc.
    ai_report = Column(JSONB, nullable=False)          # expected to contain url(s), score fields, etc.
    modified_document = Column(JSONB, nullable=False)  # references to updated docx/pdf

    notes = Column(Text, nullable=True)
    highlighted_sections = Column(JSONB, nullable=True) # Data representing highlighted sections detected by vision system
    status = Column(SQLEnum(WorkbenchSubmissionStatus), default=WorkbenchSubmissionStatus.SUBMITTED, nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assignment = relationship("WorkbenchAssignment", back_populates="submissions")
    checker = relationship("WorkbenchUser") # Relationship to WorkbenchUser

    __table_args__ = (
        Index("ix_workbench_submissions_assignment_created_desc", "assignment_id", "created_at"),
        Index("ix_workbench_submissions_checker_created_desc", "checker_id", "created_at"),
        Index("ix_workbench_submissions_status_created", "status", "created_at"),
        UniqueConstraint("submission_id", name="uq_workbench_submissions_submission_id"),
    )


class WorkbenchArtifact(Base):
    __tablename__ = "workbench_artifacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("workbench_assignments.id"), nullable=True, index=True)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("workbench_submissions.id"), nullable=True, index=True)

    artifact_type = Column(SQLEnum(WorkbenchArtifactType), default=WorkbenchArtifactType.OTHER, nullable=False, index=True)
    storage_provider = Column(String(50), nullable=False)  # e.g., s3, supabase
    bucket = Column(String(255), nullable=True)
    object_key = Column(String(1024), nullable=False, index=True)

    size_bytes = Column(BigInteger, nullable=True)
    mime_type = Column(String(255), nullable=True)
    checksum_sha256 = Column(String(128), nullable=True, index=True)

    artifact_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    assignment = relationship("WorkbenchAssignment", back_populates="artifacts")
    submission = relationship("WorkbenchSubmission")

    __table_args__ = (
        Index("ix_workbench_artifacts_assignment_created_desc", "assignment_id", "created_at"),
        Index("ix_workbench_artifacts_submission_created_desc", "submission_id", "created_at"),
        Index("ix_workbench_artifacts_type_created_desc", "artifact_type", "created_at"),
    )


class WorkbenchSectionStatus(Base):
    __tablename__ = "workbench_section_status"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("workbench_assignments.id"), nullable=False, index=True)
    section_id = Column(String(255), nullable=False)  # deterministic chunk key or range id

    status = Column(SQLEnum(ChunkStatus), default=ChunkStatus.OPEN, nullable=False, index=True)
    evidence = Column(JSONB, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assignment = relationship("WorkbenchAssignment")

    __table_args__ = (
        UniqueConstraint("assignment_id", "section_id", name="uq_workbench_section_unique"),
        Index("ix_workbench_section_status_created_desc", "status", "created_at"),
    )
