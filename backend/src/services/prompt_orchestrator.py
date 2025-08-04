"""
Advanced System Prompt Orchestrator
Provides policy-driven, composable prompt assembly for multi-use-case orchestration.
"""

import os
import yaml
import json
import hashlib
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel, Field, validator
from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)


class CostLevel(str, Enum):
    """Budget levels for prompt optimization."""
    BUDGET = "budget"
    STANDARD = "standard"
    PREMIUM = "premium"


class AcademicLevel(str, Enum):
    """Academic levels for content targeting."""
    UNDERGRADUATE = "undergraduate"
    GRADUATE = "graduate"
    DOCTORAL = "doctoral"
    PROFESSIONAL = "professional"


class CitationStyle(str, Enum):
    """Supported citation styles."""
    APA = "apa"
    MLA = "mla"
    HARVARD = "harvard"
    CHICAGO = "chicago"
    IEEE = "ieee"


class UseCase(str, Enum):
    """Supported use cases for prompt orchestration."""
    GENERAL = "general"
    DISSERTATION = "dissertation"
    THESIS = "thesis"
    RESEARCH_PAPER = "research_paper"
    REVIEW_ARTICLE = "review_article"
    CASE_STUDY = "case_study"
    METHODOLOGY_WRITER = "methodology_writer"
    LITERATURE_REVIEW = "literature_review"
    SLIDE_GENERATOR = "slide_generator"
    CODING_HELPER = "coding_helper"


@dataclass
class EvidenceSnippet:
    """Evidence snippet with citation metadata."""
    text: str
    citation: str
    source_url: Optional[str] = None
    confidence_score: float = 1.0
    snippet_id: Optional[str] = None


@dataclass
class UserParams:
    """User parameters for prompt customization."""
    citation_style: CitationStyle = CitationStyle.APA
    word_count_target: Optional[int] = None
    academic_level: AcademicLevel = AcademicLevel.GRADUATE
    deadline_sensitivity: bool = False
    file_ids: List[str] = field(default_factory=list)
    custom_instructions: Optional[str] = None


class ModelHints(BaseModel):
    """Model selection hints for different agent roles."""
    planner: Optional[str] = "claude-3-5-sonnet-20241022"
    researcher: List[str] = ["perplexity-sonar", "gemini-2.0-flash-exp"]
    writer: Optional[str] = "gpt-4o"
    evaluator: Optional[str] = "claude-3-5-sonnet-20241022"
    temperature_range: tuple = (0.1, 0.7)
    top_p_range: tuple = (0.8, 0.95)


class QualityMetrics(BaseModel):
    """Quality thresholds for evaluation."""
    coherence_threshold: float = 0.85
    citation_count_min: int = 10
    evidence_coverage_threshold: float = 0.8
    originality_threshold: float = 0.85
    accuracy_threshold: float = 0.9


class SafetyRules(BaseModel):
    """Safety and compliance rules."""
    verify_citations: bool = True
    never_fabricate: bool = True
    disclose_uncertainties: bool = True
    redact_pii: bool = True
    require_evidence_grounding: bool = True
    plagiarism_check: bool = True


class RefusalPolicy(BaseModel):
    """Refusal and clarification policies."""
    refuse_illegal: bool = True
    refuse_unethical: bool = True
    refuse_harmful: bool = True
    ask_clarifying_questions: bool = True
    max_clarification_attempts: int = 3


class OutputContract(BaseModel):
    """Expected output structure and format."""
    format_type: str = "markdown"  # markdown, json, structured
    sections: List[str] = []
    required_fields: List[str] = []
    json_schema: Optional[Dict[str, Any]] = None
    word_count_tolerance: float = 0.1  # ±10%
    citation_requirements: Dict[str, Any] = {}


class SSESchema(BaseModel):
    """SSE events to emit during processing."""
    planning_events: List[str] = ["planning_started", "sections_defined"]
    research_events: List[str] = ["search_progress", "sources_verified"]
    writing_events: List[str] = ["writing_progress", "section_completed"]
    evaluation_events: List[str] = ["evaluation_scores", "quality_check"]
    completion_events: List[str] = ["plagiarism_check_progress", "done"]


class UseCasePolicy(BaseModel):
    """Complete policy definition for a use case."""
    id: str
    name: str
    description: str
    target_audience: str = "academic"
    objectives: List[str] = []
    constraints: List[str] = []
    safety_rules: SafetyRules = SafetyRules()
    sources_policy: Dict[str, Any] = {}
    formatting: Dict[str, Any] = {}
    quality_metrics: QualityMetrics = QualityMetrics()
    refusal_policy: RefusalPolicy = RefusalPolicy()
    model_hints: ModelHints = ModelHints()
    sse_schema: SSESchema = SSESchema()
    output_contract: OutputContract = OutputContract()
    test_prompts: List[str] = []


class PromptPolicies(BaseModel):
    """Root configuration for all prompt policies."""
    version: str = "1.0"
    global_defaults: UseCasePolicy
    use_cases: Dict[str, UseCasePolicy] = {}
    
    @validator('use_cases')
    def validate_use_cases(cls, v):
        required_cases = [case.value for case in UseCase]
        missing = [case for case in required_cases if case not in v]
        if missing:
            logger.warning(f"Missing use case policies: {missing}")
        return v


@dataclass
class PromptAssemblyResult:
    """Result of prompt assembly process."""
    system_prompt: str
    developer_prompt: str
    output_contract: OutputContract
    metadata: Dict[str, Any]
    prompt_id: str
    policy_version: str
    token_estimate: int
    model_hints: ModelHints


class PromptOrchestrator:
    """
    Advanced prompt orchestrator for multi-use-case systems.
    Assembles production-grade system prompts from policies and templates.
    """
    
    def __init__(
        self,
        policies_path: str = "src/config/prompt_policies.yaml",
        templates_path: str = "src/prompts/templates"
    ):
        self.policies_path = policies_path
        self.templates_path = templates_path
        self.policies: Optional[PromptPolicies] = None
        self.jinja_env: Optional[Environment] = None
        
        self._initialize()
    
    def _initialize(self):
        """Initialize the orchestrator with policies and templates."""
        try:
            self._load_policies()
            self._setup_jinja_environment()
            logger.info("✅ PromptOrchestrator initialized successfully")
        except Exception as e:
            logger.error(f"❌ PromptOrchestrator initialization failed: {e}")
            raise
    
    def _load_policies(self):
        """Load and validate prompt policies from YAML."""
        try:
            if not os.path.exists(self.policies_path):
                logger.warning(f"⚠️  Policies file not found: {self.policies_path}")
                self._create_default_policies()
                return
            
            with open(self.policies_path, 'r', encoding='utf-8') as f:
                policy_data = yaml.safe_load(f)
            
            self.policies = PromptPolicies(**policy_data)
            logger.info(f"✅ Loaded {len(self.policies.use_cases)} use case policies")
            
        except Exception as e:
            logger.error(f"❌ Failed to load policies: {e}")
            self._create_default_policies()
    
    def _create_default_policies(self):
        """Create minimal default policies as fallback."""
        logger.info("Creating default prompt policies")
        
        default_policy = UseCasePolicy(
            id="general",
            name="General Assistant",
            description="Intelligent general-purpose assistant with clarify-plan-execute workflow",
            objectives=[
                "Clarify ambiguous requests with specific questions",
                "Propose structured approach and confirm with user",
                "Execute tasks with evidence-based reasoning",
                "Summarize results and suggest next steps"
            ],
            constraints=[
                "Cost-aware and concise unless long-form requested",
                "Verify information before stating as fact",
                "Acknowledge limitations and uncertainties"
            ]
        )
        
        self.policies = PromptPolicies(
            global_defaults=default_policy,
            use_cases={"general": default_policy}
        )
    
    def _setup_jinja_environment(self):
        """Setup Jinja2 environment for template rendering."""
        try:
            if not os.path.exists(self.templates_path):
                os.makedirs(self.templates_path, exist_ok=True)
                logger.info(f"Created templates directory: {self.templates_path}")
            
            self.jinja_env = Environment(
                loader=FileSystemLoader(self.templates_path),
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True
            )
            
            # Add custom filters
            self.jinja_env.filters['join_with_and'] = self._join_with_and
            self.jinja_env.filters['format_citations'] = self._format_citations
            
        except Exception as e:
            logger.error(f"❌ Failed to setup Jinja environment: {e}")
            raise
    
    def _join_with_and(self, items: List[str]) -> str:
        """Custom Jinja filter to join list with 'and'."""
        if not items:
            return ""
        if len(items) == 1:
            return items[0]
        if len(items) == 2:
            return f"{items[0]} and {items[1]}"
        return f"{', '.join(items[:-1])}, and {items[-1]}"
    
    def _format_citations(self, snippets: List[EvidenceSnippet], style: str = "apa") -> str:
        """Format evidence snippets according to citation style."""
        if not snippets:
            return "No evidence available."
        
        formatted = []
        for i, snippet in enumerate(snippets[:10], 1):  # Limit to top 10
            formatted.append(f"{i}. {snippet.text} ({snippet.citation})")
        
        return "\n".join(formatted)
    
    def get_policy(self, use_case: str) -> UseCasePolicy:
        """Get policy for specific use case, falling back to general."""
        if not self.policies:
            raise ValueError("Policies not loaded")
        
        # Try exact match first
        if use_case in self.policies.use_cases:
            return self.policies.use_cases[use_case]
        
        # Try case-insensitive match
        for key, policy in self.policies.use_cases.items():
            if key.lower() == use_case.lower():
                return policy
        
        # Fall back to general or global defaults
        if "general" in self.policies.use_cases:
            logger.info(f"Using general policy for unknown use case: {use_case}")
            return self.policies.use_cases["general"]
        
        logger.warning(f"Using global defaults for use case: {use_case}")
        return self.policies.global_defaults
    
    def assemble_prompt(
        self,
        use_case: str,
        user_params: UserParams,
        memory_summary: Optional[str] = None,
        evidence_snippets: List[EvidenceSnippet] = None,
        budget_level: CostLevel = CostLevel.STANDARD,
        custom_context: Optional[Dict[str, Any]] = None
    ) -> PromptAssemblyResult:
        """
        Assemble complete system prompt from policy and context.
        
        Args:
            use_case: Target use case identifier
            user_params: User-provided parameters
            memory_summary: Conversation memory summary
            evidence_snippets: Verified evidence snippets
            budget_level: Cost optimization level
            custom_context: Additional template context
            
        Returns:
            Complete prompt assembly result with metadata
        """
        try:
            assembly_start_time = time.time()
            
            # Get policy for use case
            policy = self.get_policy(use_case)
            
            # Apply budget constraints
            evidence_snippets = self._apply_budget_constraints(
                evidence_snippets or [], budget_level
            )
            
            # Build template context
            context = self._build_template_context(
                policy, user_params, memory_summary, evidence_snippets, custom_context
            )
            
            # Assemble prompt components
            system_prompt = self._assemble_system_prompt(policy, context)
            developer_prompt = self._assemble_developer_prompt(policy, context)
            
            # Calculate metadata
            prompt_content = f"{system_prompt}\n{developer_prompt}"
            prompt_id = self._generate_prompt_id(prompt_content, policy.id)
            token_estimate = self._estimate_tokens(prompt_content)
            
            result = PromptAssemblyResult(
                system_prompt=system_prompt,
                developer_prompt=developer_prompt,
                output_contract=policy.output_contract,
                metadata={
                    "use_case": use_case,
                    "policy_id": policy.id,
                    "budget_level": budget_level.value,
                    "evidence_count": len(evidence_snippets),
                    "user_params": user_params.__dict__,
                    "has_memory": bool(memory_summary),
                    "token_estimate": token_estimate,
                    "assembly_start_time": assembly_start_time,
                    "quality_metrics": policy.quality_metrics.dict()
                },
                prompt_id=prompt_id,
                policy_version=self.policies.version,
                token_estimate=token_estimate,
                model_hints=policy.model_hints
            )
            
            # Log assembly (with redaction)
            self._log_prompt_assembly(result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Prompt assembly failed for {use_case}: {e}")
            raise
    
    def _apply_budget_constraints(
        self, 
        evidence_snippets: List[EvidenceSnippet], 
        budget_level: CostLevel
    ) -> List[EvidenceSnippet]:
        """Apply budget-based constraints to evidence and context."""
        limits = {
            CostLevel.BUDGET: 5,
            CostLevel.STANDARD: 10,
            CostLevel.PREMIUM: 20
        }
        
        max_snippets = limits.get(budget_level, 10)
        
        # Sort by confidence score and truncate
        sorted_snippets = sorted(
            evidence_snippets, 
            key=lambda x: x.confidence_score, 
            reverse=True
        )
        
        return sorted_snippets[:max_snippets]
    
    def _build_template_context(
        self,
        policy: UseCasePolicy,
        user_params: UserParams,
        memory_summary: Optional[str],
        evidence_snippets: List[EvidenceSnippet],
        custom_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build comprehensive template context."""
        context = {
            # Policy data
            "use_case": policy.id,
            "use_case_name": policy.name,
            "description": policy.description,
            "objectives": policy.objectives,
            "constraints": policy.constraints,
            "safety_rules": policy.safety_rules.dict(),
            "quality_metrics": policy.quality_metrics.dict(),
            
            # User parameters
            "citation_style": user_params.citation_style.value,
            "word_count_target": user_params.word_count_target,
            "academic_level": user_params.academic_level.value,
            "custom_instructions": user_params.custom_instructions,
            
            # Context data
            "memory_summary": memory_summary or "No previous conversation context.",
            "evidence_snippets": evidence_snippets,
            "evidence_count": len(evidence_snippets),
            
            # Output formatting
            "sections": policy.output_contract.sections,
            "format_type": policy.output_contract.format_type,
            "required_fields": policy.output_contract.required_fields,
            
            # Model hints
            "model_hints": policy.model_hints.dict(),
            
            # Utility functions
            "has_evidence": len(evidence_snippets) > 0,
            "has_files": len(user_params.file_ids) > 0,
            "is_long_form": user_params.word_count_target and user_params.word_count_target > 2000
        }
        
        # Merge custom context
        if custom_context:
            context.update(custom_context)
        
        return context
    
    def _assemble_system_prompt(self, policy: UseCasePolicy, context: Dict[str, Any]) -> str:
        """Assemble system prompt from templates."""
        try:
            components = []
            
            # Header (persona, mission, values)
            if self._template_exists("header.jinja"):
                header = self.jinja_env.get_template("header.jinja").render(**context)
                components.append(header)
            
            # Safety and compliance
            if self._template_exists("safety.jinja"):
                safety = self.jinja_env.get_template("safety.jinja").render(**context)
                components.append(safety)
            
            # Use case specific content
            use_case_template = f"usecase_{policy.id}.jinja"
            if self._template_exists(use_case_template):
                use_case_content = self.jinja_env.get_template(use_case_template).render(**context)
                components.append(use_case_content)
            else:
                # Fallback to general template
                if self._template_exists("usecase_general.jinja"):
                    general_content = self.jinja_env.get_template("usecase_general.jinja").render(**context)
                    components.append(general_content)
            
            return "\n\n".join(filter(None, components))
            
        except Exception as e:
            logger.error(f"❌ System prompt assembly failed: {e}")
            return self._create_fallback_system_prompt(policy, context)
    
    def _assemble_developer_prompt(self, policy: UseCasePolicy, context: Dict[str, Any]) -> str:
        """Assemble developer instructions prompt."""
        try:
            components = []
            
            # Tool contracts
            if self._template_exists("tools_contracts.jinja"):
                tools = self.jinja_env.get_template("tools_contracts.jinja").render(**context)
                components.append(tools)
            
            # Output contract
            output_template = f"output_contract_{policy.id}.jinja"
            if self._template_exists(output_template):
                output_contract = self.jinja_env.get_template(output_template).render(**context)
                components.append(output_contract)
            elif self._template_exists("output_contract_general.jinja"):
                output_contract = self.jinja_env.get_template("output_contract_general.jinja").render(**context)
                components.append(output_contract)
            
            # Memory and evidence context
            if context.get("memory_summary") or context.get("evidence_snippets"):
                memory_context = self._format_memory_context(context)
                components.append(memory_context)
            
            return "\n\n".join(filter(None, components))
            
        except Exception as e:
            logger.error(f"❌ Developer prompt assembly failed: {e}")
            return self._create_fallback_developer_prompt(policy, context)
    
    def _template_exists(self, template_name: str) -> bool:
        """Check if template file exists."""
        template_path = os.path.join(self.templates_path, template_name)
        return os.path.exists(template_path)
    
    def _format_memory_context(self, context: Dict[str, Any]) -> str:
        """Format memory and evidence context section."""
        parts = []
        
        if context.get("memory_summary"):
            parts.append(f"## Conversation Context\n{context['memory_summary']}")
        
        if context.get("evidence_snippets"):
            evidence_text = self._format_citations(
                context["evidence_snippets"], 
                context.get("citation_style", "apa")
            )
            parts.append(f"## Evidence Base\n{evidence_text}")
        
        return "\n\n".join(parts)
    
    def _create_fallback_system_prompt(self, policy: UseCasePolicy, context: Dict[str, Any]) -> str:
        """Create minimal fallback system prompt."""
        return f"""You are HandyWriterz, an advanced academic research and writing system.

Mission: Produce high-quality, evidence-grounded work that meets academic standards.

Use Case: {policy.name}
Objectives: {'; '.join(policy.objectives)}
Constraints: {'; '.join(policy.constraints)}

Safety Rules:
- Never fabricate citations or sources
- Verify information before presenting as fact
- Acknowledge limitations and uncertainties
- Respect privacy and redact PII when appropriate

Quality Standards:
- Coherence threshold: {policy.quality_metrics.coherence_threshold}
- Minimum citations: {policy.quality_metrics.citation_count_min}
- Evidence coverage: {policy.quality_metrics.evidence_coverage_threshold}
"""
    
    def _create_fallback_developer_prompt(self, policy: UseCasePolicy, context: Dict[str, Any]) -> str:
        """Create minimal fallback developer prompt."""
        return f"""## Development Instructions

Output Format: {policy.output_contract.format_type}
Required Sections: {', '.join(policy.output_contract.sections)}

## Tool Usage
Use available tools in sequence: plan → search → verify → write → evaluate

## Context
{context.get('memory_summary', 'No conversation context available.')}

## Evidence Base
{len(context.get('evidence_snippets', []))} evidence snippets available for reference.
"""
    
    def _generate_prompt_id(self, prompt_content: str, policy_id: str) -> str:
        """Generate unique prompt ID for tracking."""
        content_hash = hashlib.sha256(prompt_content.encode()).hexdigest()[:12]
        return f"{policy_id}_{content_hash}"
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars ≈ 1 token)."""
        return len(text) // 4
    
    def _log_prompt_assembly(self, result: PromptAssemblyResult):
        """Log prompt assembly with comprehensive observability and appropriate redactions."""
        import json
        
        # Redact sensitive content for logging
        redacted_system = self._redact_for_logging(result.system_prompt)
        redacted_developer = self._redact_for_logging(result.developer_prompt)
        
        # Comprehensive observability data
        observability_data = {
            "event": "prompt_assembly_completed",
            "timestamp": time.time(),
            "prompt_metadata": {
                "prompt_id": result.prompt_id,
                "policy_version": result.policy_version,
                "use_case": result.metadata.get("use_case"),
                "token_estimate": result.token_estimate,
                "assembly_duration_ms": int((time.time() - result.metadata.get("assembly_start_time", time.time())) * 1000)
            },
            "content_metrics": {
                "system_prompt_length": len(result.system_prompt),
                "developer_prompt_length": len(result.developer_prompt),
                "total_prompt_length": len(result.system_prompt) + len(result.developer_prompt),
                "evidence_count": result.metadata.get("evidence_count", 0),
                "has_memory": result.metadata.get("has_memory", False),
                "has_files": len(result.metadata.get("user_params", {}).get("file_ids", [])) > 0
            },
            "configuration": {
                "budget_level": result.metadata.get("budget_level"),
                "model_hints": {
                    "planner": result.model_hints.planner,
                    "writer": result.model_hints.writer,
                    "evaluator": result.model_hints.evaluator,
                    "researcher_count": len(result.model_hints.researcher)
                },
                "output_format": result.output_contract.format_type,
                "sections_count": len(result.output_contract.sections),
                "required_fields_count": len(result.output_contract.required_fields)
            },
            "quality_thresholds": {
                "coherence_threshold": getattr(result.metadata.get("quality_metrics", {}), "coherence_threshold", None),
                "citation_count_min": getattr(result.metadata.get("quality_metrics", {}), "citation_count_min", None),
                "evidence_coverage_threshold": getattr(result.metadata.get("quality_metrics", {}), "evidence_coverage_threshold", None)
            }
        }
        
        # Structured logging for different verbosity levels
        logger.info(f"🎯 Prompt Assembly Complete", extra={
            "prompt_id": result.prompt_id,
            "use_case": result.metadata.get("use_case"),
            "token_estimate": result.token_estimate,
            "evidence_count": result.metadata.get("evidence_count", 0),
            "observability": observability_data
        })
        
        # Debug-level detailed logging
        logger.debug(f"📋 System Prompt Preview: {redacted_system[:200]}...")
        logger.debug(f"🔧 Developer Prompt Preview: {redacted_developer[:200]}...")
        logger.debug(f"📊 Full Assembly Data: {json.dumps(observability_data, indent=2)}")
        
        # Performance monitoring
        if result.token_estimate > 8000:
            logger.warning(f"⚠️ Large prompt detected: {result.token_estimate} tokens for {result.metadata.get('use_case')}")
        
        # Quality monitoring alerts
        evidence_count = result.metadata.get("evidence_count", 0)
        if evidence_count == 0 and result.metadata.get("use_case") in ["dissertation", "thesis", "research_paper"]:
            logger.warning(f"⚠️ No evidence provided for academic use case: {result.metadata.get('use_case')}")
        
        # Export observability data for external monitoring systems
        self._export_observability_metrics(observability_data)
    
    def _export_observability_metrics(self, observability_data: Dict[str, Any]):
        """Export observability metrics to external monitoring systems."""
        try:
            # Check for observability integrations
            otel_enabled = os.getenv("OTEL_ENABLED", "false").lower() == "true"
            
            if otel_enabled:
                # OpenTelemetry integration (if available)
                try:
                    from opentelemetry import trace, metrics
                    
                    tracer = trace.get_tracer(__name__)
                    meter = metrics.get_meter(__name__)
                    
                    # Create span for prompt assembly
                    with tracer.start_as_current_span("prompt_assembly") as span:
                        span.set_attribute("prompt.id", observability_data["prompt_metadata"]["prompt_id"])
                        span.set_attribute("prompt.use_case", observability_data["prompt_metadata"]["use_case"])
                        span.set_attribute("prompt.token_estimate", observability_data["prompt_metadata"]["token_estimate"])
                        span.set_attribute("prompt.evidence_count", observability_data["content_metrics"]["evidence_count"])
                    
                    # Record metrics
                    prompt_assembly_counter = meter.create_counter("prompt_assemblies_total")
                    prompt_assembly_counter.add(1, {
                        "use_case": observability_data["prompt_metadata"]["use_case"],
                        "budget_level": observability_data["configuration"]["budget_level"]
                    })
                    
                    token_histogram = meter.create_histogram("prompt_token_estimate")
                    token_histogram.record(observability_data["prompt_metadata"]["token_estimate"], {
                        "use_case": observability_data["prompt_metadata"]["use_case"]
                    })
                    
                except ImportError:
                    logger.debug("OpenTelemetry not available for observability export")
            
            # Redis metrics export for dashboard
            redis_metrics_enabled = os.getenv("REDIS_METRICS_ENABLED", "false").lower() == "true"
            
            if redis_metrics_enabled:
                try:
                    import redis
                    redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
                    
                    # Store prompt assembly metrics in Redis
                    metrics_key = f"prompt_metrics:{observability_data['prompt_metadata']['use_case']}"
                    redis_client.hincrby(metrics_key, "total_assemblies", 1)
                    redis_client.hincrby(metrics_key, "total_tokens", observability_data["prompt_metadata"]["token_estimate"])
                    redis_client.expire(metrics_key, 86400)  # 24 hour TTL
                    
                    # Daily metrics rollup
                    from datetime import datetime
                    daily_key = f"prompt_daily:{datetime.now().strftime('%Y-%m-%d')}"
                    redis_client.hincrby(daily_key, "assemblies", 1)
                    redis_client.hincrby(daily_key, "tokens", observability_data["prompt_metadata"]["token_estimate"])
                    redis_client.expire(daily_key, 7 * 86400)  # 7 day TTL
                    
                except Exception as e:
                    logger.debug(f"Redis metrics export failed: {e}")
            
        except Exception as e:
            logger.debug(f"Observability export failed: {e}")  # Don't fail prompt assembly for observability issues
    
    def _redact_for_logging(self, text: str) -> str:
        """Enterprise-grade PII detection and redaction for production logging."""
        import re
        import hashlib
        
        redacted = text
        redaction_metadata = {"redacted_count": 0, "redaction_types": []}
        
        # Enterprise-grade redaction patterns with contextual awareness
        redaction_patterns = [
            # API Keys and Tokens (various formats)
            {
                "pattern": r'\b(?:sk-|pk_|rk_|xapp_|ya29\.|AIza|AKIA|eyJ)[A-Za-z0-9_\-\.]{20,}',
                "replacement": lambda m: f"[REDACTED_API_KEY:{hashlib.sha256(m.group().encode()).hexdigest()[:8]}]",
                "type": "api_key"
            },
            # JWT Tokens
            {
                "pattern": r'\beyJ[A-Za-z0-9_\-]+\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+',
                "replacement": lambda m: f"[REDACTED_JWT:{hashlib.sha256(m.group().encode()).hexdigest()[:8]}]",
                "type": "jwt_token"
            },
            # Email addresses with domain preservation for analytics
            {
                "pattern": r'\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b',
                "replacement": lambda m: f"[REDACTED_EMAIL@{m.group(1)}]",
                "type": "email"
            },
            # Credit card numbers (various formats)
            {
                "pattern": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
                "replacement": "[REDACTED_CC_****]",
                "type": "credit_card"
            },
            # Social Security Numbers
            {
                "pattern": r'\b\d{3}-\d{2}-\d{4}\b',
                "replacement": "[REDACTED_SSN_***]",
                "type": "ssn"
            },
            # Phone numbers (international formats)
            {
                "pattern": r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
                "replacement": "[REDACTED_PHONE_***]",
                "type": "phone"
            },
            # IP addresses (but preserve localhost and private ranges indicators)
            {
                "pattern": r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
                "replacement": lambda m: self._redact_ip_address(m.group()),
                "type": "ip_address"
            },
            # URLs with sensitive paths
            {
                "pattern": r'https?://[^\s/$.?#].[^\s]*(?:/(?:api|admin|private|secure|auth|token|key)[^\s]*)',
                "replacement": lambda m: self._redact_sensitive_url(m.group()),
                "type": "sensitive_url"
            },
            # Database connection strings
            {
                "pattern": r'(?:postgres|mysql|mongodb|redis)://[^@\s]+:[^@\s]+@[^\s/]+',
                "replacement": "[REDACTED_DB_CONNECTION]",
                "type": "db_connection"
            },
            # AWS/Cloud resource identifiers
            {
                "pattern": r'\b(?:arn:aws:|i-[0-9a-f]{8,17}|vol-[0-9a-f]{8,17}|subnet-[0-9a-f]{8,17})\S*',
                "replacement": lambda m: f"[REDACTED_AWS_RESOURCE:{m.group()[:20]}...]",
                "type": "aws_resource"
            },
            # Personal names in structured contexts
            {
                "pattern": r'(?:name|author|user)[\s\'"]*:[\s\'"]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
                "replacement": lambda m: m.group().replace(m.group(1), "[REDACTED_NAME]"),
                "type": "personal_name"
            },
            # Addresses (basic pattern)
            {
                "pattern": r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln)\b',
                "replacement": "[REDACTED_ADDRESS]",
                "type": "address"
            }
        ]
        
        # Apply redaction patterns with metadata tracking
        for pattern_config in redaction_patterns:
            pattern = pattern_config["pattern"]
            replacement = pattern_config["replacement"]
            redaction_type = pattern_config["type"]
            
            if callable(replacement):
                def replace_func(match):
                    redaction_metadata["redacted_count"] += 1
                    if redaction_type not in redaction_metadata["redaction_types"]:
                        redaction_metadata["redaction_types"].append(redaction_type)
                    return replacement(match)
                redacted = re.sub(pattern, replace_func, redacted, flags=re.IGNORECASE)
            else:
                matches = re.findall(pattern, redacted, flags=re.IGNORECASE)
                if matches:
                    redaction_metadata["redacted_count"] += len(matches)
                    if redaction_type not in redaction_metadata["redaction_types"]:
                        redaction_metadata["redaction_types"].append(redaction_type)
                    redacted = re.sub(pattern, replacement, redacted, flags=re.IGNORECASE)
        
        # Log redaction metadata for security monitoring
        if redaction_metadata["redacted_count"] > 0:
            logger.info(f"🔒 Enterprise redaction applied: {redaction_metadata['redacted_count']} items of types {redaction_metadata['redaction_types']}")
        
        # Final sanitization pass - remove any remaining high-entropy strings
        redacted = self._final_entropy_check(redacted)
        
        return redacted
    
    def _redact_ip_address(self, ip: str) -> str:
        """Redact IP addresses while preserving network context."""
        # Preserve localhost and private network indicators
        if ip.startswith('127.') or ip.startswith('192.168.') or ip.startswith('10.'):
            return f"[REDACTED_PRIVATE_IP_{ip.split('.')[0]}.*.*.*]"
        elif ip.startswith('172.'):
            second_octet = int(ip.split('.')[1])
            if 16 <= second_octet <= 31:
                return "[REDACTED_PRIVATE_IP_172.*.*.*]"
        return "[REDACTED_PUBLIC_IP_*.*.*.*]"
    
    def _redact_sensitive_url(self, url: str) -> str:
        """Redact URLs while preserving domain and general structure."""
        import urllib.parse
        try:
            parsed = urllib.parse.urlparse(url)
            return f"[REDACTED_SENSITIVE_URL:{parsed.scheme}://{parsed.netloc}/***]"
        except:
            return "[REDACTED_SENSITIVE_URL]"
    
    def _final_entropy_check(self, text: str) -> str:
        """Final entropy-based check for missed secrets."""
        import re
        import math
        
        # Find high-entropy alphanumeric strings that might be secrets
        high_entropy_pattern = r'\b[A-Za-z0-9]{16,}\b'
        
        def entropy_check(match):
            string = match.group()
            # Calculate Shannon entropy
            if len(string) < 16:
                return string
                
            entropy = 0
            for char in set(string):
                p = string.count(char) / len(string)
                entropy -= p * math.log2(p)
            
            # High entropy threshold (adjust based on false positive rate)
            if entropy > 4.5:  # Typical random strings have entropy > 4.5
                return f"[REDACTED_HIGH_ENTROPY:{hashlib.sha256(string.encode()).hexdigest()[:8]}]"
            return string
        
        return re.sub(high_entropy_pattern, entropy_check, text)
    
    def reload_policies(self):
        """Reload policies from configuration file."""
        logger.info("🔄 Reloading prompt policies")
        self._load_policies()
    
    def validate_policies(self) -> Dict[str, Any]:
        """Validate loaded policies and return validation report."""
        if not self.policies:
            return {"valid": False, "error": "No policies loaded"}
        
        validation_report = {
            "valid": True,
            "version": self.policies.version,
            "use_cases_count": len(self.policies.use_cases),
            "missing_templates": [],
            "warnings": []
        }
        
        # Check for required templates
        required_templates = ["header.jinja", "safety.jinja", "tools_contracts.jinja"]
        for template in required_templates:
            if not self._template_exists(template):
                validation_report["missing_templates"].append(template)
        
        # Check use case templates
        for use_case_id in self.policies.use_cases.keys():
            template_name = f"usecase_{use_case_id}.jinja"
            if not self._template_exists(template_name):
                validation_report["warnings"].append(f"Missing template: {template_name}")
        
        if validation_report["missing_templates"]:
            validation_report["valid"] = False
        
        return validation_report


# Global orchestrator instance
_orchestrator: Optional[PromptOrchestrator] = None


def get_prompt_orchestrator() -> PromptOrchestrator:
    """Get global prompt orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = PromptOrchestrator()
    return _orchestrator


def reload_prompt_policies():
    """Reload prompt policies from configuration."""
    global _orchestrator
    if _orchestrator is not None:
        _orchestrator.reload_policies()
    else:
        _orchestrator = PromptOrchestrator()