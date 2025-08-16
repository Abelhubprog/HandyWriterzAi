"""
HandyWriterz State Management for LangGraph Workflow
Comprehensive state tracking for multi-agent academic writing system.
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from langchain_core.messages import BaseMessage


class DocumentType(Enum):
    """Supported document types."""
    ESSAY = "essay"
    REPORT = "report"
    DISSERTATION = "dissertation"
    CASE_STUDY = "case_study"
    LITERATURE_REVIEW = "literature_review"
    RESEARCH_PAPER = "research_paper"
    THESIS = "thesis"


class CitationStyle(Enum):
    """Supported citation styles."""
    HARVARD = "Harvard"
    APA = "APA"
    MLA = "MLA"
    CHICAGO = "Chicago"
    VANCOUVER = "Vancouver"
    IEEE = "IEEE"


class AcademicField(Enum):
    """Academic fields and subjects."""
    HEALTH_SOCIAL_CARE = "health-social-care"
    NURSING = "nursing"
    MEDICINE = "medicine"
    LAW = "law"
    BUSINESS = "business"
    EDUCATION = "education"
    PSYCHOLOGY = "psychology"
    ENGINEERING = "engineering"
    COMPUTER_SCIENCE = "computer-science"
    LITERATURE = "literature"
    HISTORY = "history"
    SOCIOLOGY = "sociology"
    ECONOMICS = "economics"
    ENVIRONMENTAL_SCIENCE = "environmental-science"
    POLITICAL_SCIENCE = "political-science"


class Region(Enum):
    """Academic regions with different standards."""
    UK = "UK"
    US = "US"
    AUSTRALIA = "AU"
    CANADA = "CA"
    EUROPE = "EU"


class WorkflowStatus(Enum):
    """Workflow execution status."""
    INITIATED = "initiated"
    PLANNING = "planning"
    RESEARCHING = "researching"
    FILTERING = "filtering"
    WRITING = "writing"
    EVALUATING = "evaluating"
    TURNITIN_CHECK = "turnitin_check"
    REVISING = "revising"
    FORMATTING = "formatting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class UserParams:
    """User parameters for academic writing request."""
    word_count: int
    document_type: Union[DocumentType, str] = DocumentType.ESSAY
    citation_style: Union[CitationStyle, str] = CitationStyle.HARVARD
    academic_field: Union[AcademicField, str] = AcademicField.BUSINESS
    region: Union[Region, str] = Region.UK
    academic_level: str = "undergraduate"
    deadline: Optional[str] = None
    special_instructions: Optional[str] = None

    def __post_init__(self):
        """Convert string values to enums if needed."""
        if isinstance(self.document_type, str):
            try:
                self.document_type = DocumentType(self.document_type.lower().replace(' ', '_'))
            except ValueError:
                self.document_type = DocumentType.ESSAY

        if isinstance(self.citation_style, str):
            try:
                self.citation_style = CitationStyle(self.citation_style.title())
            except ValueError:
                self.citation_style = CitationStyle.HARVARD

        if isinstance(self.academic_field, str):
            try:
                self.academic_field = AcademicField(self.academic_field.lower().replace(' ', '-'))
            except ValueError:
                self.academic_field = AcademicField.BUSINESS

        if isinstance(self.region, str):
            try:
                self.region = Region(self.region.upper())
            except ValueError:
                self.region = Region.UK

    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "word_count": self.word_count,
            "document_type": self.document_type.value if isinstance(self.document_type, DocumentType) else self.document_type,
            "citation_style": self.citation_style.value if isinstance(self.citation_style, CitationStyle) else self.citation_style,
            "academic_field": self.academic_field.value if isinstance(self.academic_field, AcademicField) else self.academic_field,
            "region": self.region.value if isinstance(self.region, Region) else self.region,
            "academic_level": self.academic_level,
            "deadline": self.deadline,
            "special_instructions": self.special_instructions
        }


@dataclass
class HandyWriterzState:
    """Comprehensive state for HandyWriterz workflow."""

    # Core Identifiers
    conversation_id: str
    user_id: str = ""
    wallet_address: Optional[str] = None

    # Messages and Communication
    messages: List[BaseMessage] = field(default_factory=list)

    # User Parameters
    user_params: Dict[str, Any] = field(default_factory=dict)

    # Document Management
    uploaded_docs: List[Dict[str, Any]] = field(default_factory=list)
    uploaded_files: List[Dict[str, Any]] = field(default_factory=list)

    # Planning and Structure
    outline: Optional[Dict[str, Any]] = None
    research_agenda: List[str] = field(default_factory=list)

    # Research Results
    search_queries: List[str] = field(default_factory=list)
    raw_search_results: List[Dict[str, Any]] = field(default_factory=list)
    filtered_sources: List[Dict[str, Any]] = field(default_factory=list)
    verified_sources: List[Dict[str, Any]] = field(default_factory=list)

    # Writing Content
    draft_content: Optional[str] = None
    current_draft: Optional[str] = None
    revision_count: int = 0

    # Quality Assurance
    evaluation_results: List[Dict[str, Any]] = field(default_factory=list)
    evaluation_score: Optional[float] = None

    # Turnitin Integration
    turnitin_reports: List[Dict[str, Any]] = field(default_factory=list)
    turnitin_passed: bool = False

    # Final Output
    formatted_document: Optional[str] = None
    learning_outcomes_report: Optional[Dict[str, Any]] = None
    download_urls: Dict[str, str] = field(default_factory=dict)

    # Workflow Management
    current_node: Optional[str] = None
    workflow_status: Union[WorkflowStatus, str] = WorkflowStatus.INITIATED
    error_message: Optional[str] = None
    retry_count: int = 0
    max_iterations: int = 5

    # Advanced Features
    enable_tutor_review: bool = False
    enable_swarm_intelligence: bool = True

    # Timing and Performance
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    processing_metrics: Dict[str, Any] = field(default_factory=dict)

    # Authentication and Payment
    auth_token: Optional[str] = None
    payment_transaction_id: Optional[str] = None
    credits_used: int = 0
    # Prompt orchestration metadata (optional)
    prompt_metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize state after creation."""
        if isinstance(self.workflow_status, str):
            try:
                self.workflow_status = WorkflowStatus(self.workflow_status.lower())
            except ValueError:
                self.workflow_status = WorkflowStatus.INITIATED

        if self.start_time is None:
            import time
            self.start_time = time.time()

    def update_status(self, status: Union[WorkflowStatus, str], node: Optional[str] = None):
        """Update workflow status and current node."""
        if isinstance(status, str):
            try:
                status = WorkflowStatus(status.lower())
            except ValueError:
                status = WorkflowStatus.INITIATED

        self.workflow_status = status
        if node:
            self.current_node = node

    def add_message(self, message: BaseMessage):
        """Add a message to the conversation."""
        self.messages.append(message)

    def add_search_result(self, result: Dict[str, Any]):
        """Add a search result."""
        self.raw_search_results.append(result)

    def add_verified_source(self, source: Dict[str, Any]):
        """Add a verified source."""
        self.verified_sources.append(source)

    def add_evaluation_result(self, result: Dict[str, Any]):
        """Add an evaluation result."""
        self.evaluation_results.append(result)

    def set_error(self, error_message: str):
        """Set error status."""
        self.error_message = error_message
        self.workflow_status = WorkflowStatus.FAILED

    def increment_retry(self):
        """Increment retry count."""
        self.retry_count += 1

    def can_retry(self) -> bool:
        """Check if can retry."""
        return self.retry_count < self.max_iterations

    def get_user_params_object(self) -> UserParams:
        """Get UserParams object from dict."""
        return UserParams(**self.user_params)

    def is_complete(self) -> bool:
        """Check if workflow is complete."""
        return self.workflow_status == WorkflowStatus.COMPLETED

    def is_failed(self) -> bool:
        """Check if workflow has failed."""
        return self.workflow_status == WorkflowStatus.FAILED

    def get_progress_percentage(self) -> float:
        """Calculate progress percentage."""
        status_progress = {
            WorkflowStatus.INITIATED: 5.0,
            WorkflowStatus.PLANNING: 15.0,
            WorkflowStatus.RESEARCHING: 35.0,
            WorkflowStatus.FILTERING: 50.0,
            WorkflowStatus.WRITING: 70.0,
            WorkflowStatus.EVALUATING: 85.0,
            WorkflowStatus.TURNITIN_CHECK: 90.0,
            WorkflowStatus.REVISING: 95.0,
            WorkflowStatus.FORMATTING: 98.0,
            WorkflowStatus.COMPLETED: 100.0,
            WorkflowStatus.FAILED: 0.0,
            WorkflowStatus.CANCELLED: 0.0
        }
        return status_progress.get(self.workflow_status, 0.0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization."""
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "wallet_address": self.wallet_address,
            "user_params": self.user_params,
            "workflow_status": self.workflow_status.value if isinstance(self.workflow_status, WorkflowStatus) else self.workflow_status,
            "current_node": self.current_node,
            "progress_percentage": self.get_progress_percentage(),
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "turnitin_passed": self.turnitin_passed,
            "credits_used": self.credits_used,
            "download_urls": self.download_urls,
            "prompt_metadata": self.prompt_metadata
        }
