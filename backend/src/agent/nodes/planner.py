"""Planner node for creating comprehensive outlines and research agendas."""

from typing import Dict, Any, List

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from ..base import BaseNode, UserParams
from ..handywriterz_state import HandyWriterzState
from src.services.llm_service import get_llm_client


class OutlineSection(BaseModel):
    """Represents a section in the document outline."""
    title: str
    description: str
    word_allocation: int
    key_points: List[str]
    subsections: List['OutlineSection'] = Field(default_factory=list)


class PlannerOutput(BaseModel):
    """Structured output from the planner node."""
    outline: List[OutlineSection]
    research_agenda: List[str]
    estimated_complexity: str
    recommended_sources: int
    writing_approach: str


class PlannerNode(BaseNode):
    """Creates comprehensive outlines and research agendas for academic writing."""

    def __init__(self):
        super().__init__("planner", timeout_seconds=120.0, max_retries=2)

    async def execute(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute the planning process."""
        try:
            # Extract context and parameters
            user_params = UserParams(**state.get("user_params", {}))
            uploaded_docs = state.get("uploaded_docs", [])
            user_prompt = self._extract_user_prompt(state)

            self._broadcast_progress(state, "Analyzing requirements...", 20.0)

            # Create comprehensive outline
            outline_result = await self._create_outline(user_prompt, user_params, uploaded_docs)

            self._broadcast_progress(state, "Generating research agenda...", 60.0)

            # Generate detailed research agenda
            research_agenda = await self._create_research_agenda(outline_result, user_params)

            self._broadcast_progress(state, "Finalizing plan...", 90.0)

            # Structure the output
            planning_result = {
                "outline": outline_result.outline,
                "research_agenda": research_agenda,
                "estimated_complexity": outline_result.estimated_complexity,
                "recommended_sources": outline_result.recommended_sources,
                "writing_approach": outline_result.writing_approach,
                "planning_complete": True
            }

            self._broadcast_progress(state, "Planning completed successfully", 100.0)

            return planning_result

        except Exception as e:
            self.logger.error(f"Planning failed: {e}")
            raise

    def _extract_user_prompt(self, state: HandyWriterzState) -> str:
        """Extract the main user prompt from messages."""
        messages = state.get("messages", [])
        if not messages:
            raise ValueError("No user prompt provided")

        # Get the last human message
        for message in reversed(messages):
            if hasattr(message, 'type') and message.type == 'human':
                return message.content

        raise ValueError("No user prompt found in messages")

    async def _create_outline(
        self,
        user_prompt: str,
        user_params: UserParams,
        uploaded_docs: List[Dict[str, Any]]
    ) -> PlannerOutput:
        """Create a comprehensive outline using the appropriate LLM."""
        try:
            llm = get_llm_client("planning", "opus")  # Use Claude 3 Opus for planning via named policy
            structured_llm = llm.with_structured_output(PlannerOutput)

            # Create context from uploaded documents
            context_text = self._create_context_summary(uploaded_docs)

            prompt = self._build_planning_prompt(user_prompt, user_params, context_text)

            result = await structured_llm.ainvoke(prompt)
            return result

        except Exception as e:
            self.logger.error(f"Outline creation failed: {e}")
            raise

    def _create_context_summary(self, uploaded_docs: List[Dict[str, Any]]) -> str:
        """Create a summary of uploaded documents for context."""
        if not uploaded_docs:
            return "No additional context documents provided."

        context_parts = []
        for doc in uploaded_docs[:5]:  # Limit to first 5 docs to avoid token overflow
            content = doc.get("content", "")[:1000]  # Truncate to 1000 chars
            file_name = doc.get("metadata", {}).get("file_name", "Unknown")
            context_parts.append(f"Document: {file_name}\nContent: {content}...\n")

        return "\n---\n".join(context_parts)

    def _build_planning_prompt(self, user_prompt: str, user_params: UserParams, context: str) -> str:
        """Build the comprehensive planning prompt."""
        return f"""
You are an expert academic writing planner with extensive experience in {user_params.field}.
Create a comprehensive plan for a {user_params.writeup_type} based on the user's request.

**User Request:**
{user_prompt}

**Writing Parameters:**
- Word Count: {user_params.word_count} words
- Academic Field: {user_params.field}
- Document Type: {user_params.writeup_type}
- Citation Style: {user_params.citation_style}
- Region: {user_params.region}
- Maximum Source Age: {user_params.source_age_years} years

**Context Documents:**
{context}

**Instructions:**

1. **Outline Creation:**
   - Create a detailed hierarchical outline with precise word allocations
   - Each section should have 3-5 key points to address
   - Ensure total word allocation matches target ({user_params.word_count} words)
   - Include introduction, main body sections, and conclusion
   - For dissertations/research papers, include methodology if applicable

2. **Research Requirements:**
   - Generate specific, targeted research queries
   - Focus on academic sources from reputable journals
   - Ensure queries cover all outline sections comprehensively
   - Consider {user_params.region} context and standards
   - Target {user_params.target_sources} high-quality sources

3. **Academic Standards:**
   - Ensure outline meets {user_params.region} academic standards
   - Consider learning outcomes typical for {user_params.field}
   - Include critical analysis and evaluation components
   - Plan for proper argumentation structure

4. **Complexity Assessment:**
   - Rate complexity as "Basic", "Intermediate", or "Advanced"
   - Consider depth of analysis required
   - Account for source integration needs

Return a structured plan that will guide high-quality academic writing.
"""

    async def _create_research_agenda(self, outline_result: PlannerOutput, user_params: UserParams) -> List[str]:
        """Create detailed research agenda based on the outline."""
        try:
            research_queries = []

            # Extract research needs from each outline section
            for section in outline_result.outline:
                section_queries = await self._generate_section_queries(section, user_params)
                research_queries.extend(section_queries)

            # Add general field-specific queries
            field_queries = self._generate_field_specific_queries(user_params)
            research_queries.extend(field_queries)

            # Remove duplicates and prioritize
            unique_queries = list(dict.fromkeys(research_queries))

            # Limit to reasonable number of queries
            max_queries = min(20, user_params.target_sources * 2)
            return unique_queries[:max_queries]

        except Exception as e:
            self.logger.error(f"Research agenda creation failed: {e}")
            raise

    async def _generate_section_queries(self, section: OutlineSection, user_params: UserParams) -> List[str]:
        """Generate research queries for a specific outline section."""
        queries = []

        # Base query for the section
        base_query = f"{section.title} {user_params.field}"
        queries.append(base_query)

        # Queries for key points
        for point in section.key_points[:3]:  # Limit to top 3 points
            point_query = f"{point} {user_params.field} research"
            queries.append(point_query)

        # Regional context query if relevant
        if user_params.region and user_params.region != "general":
            regional_query = f"{section.title} {user_params.region} context {user_params.field}"
            queries.append(regional_query)

        return queries

    def _generate_field_specific_queries(self, user_params: UserParams) -> List[str]:
        """Generate field-specific research queries."""
        field_mapping = {
            "adult nursing": [
                "adult nursing best practices evidence",
                "patient care adult nursing interventions",
                "nursing theory adult care applications"
            ],
            "mental health nursing": [
                "mental health nursing interventions evidence",
                "psychiatric nursing care models",
                "mental health recovery approaches"
            ],
            "law": [
                "legal precedents case law analysis",
                "statutory interpretation principles",
                "judicial decision making"
            ],
            "social work": [
                "social work intervention effectiveness",
                "community social work practice",
                "social work theory application"
            ],
            "health and social care": [
                "integrated health social care delivery",
                "health social care policy implementation",
                "multidisciplinary care approaches"
            ]
        }

        return field_mapping.get(user_params.field.lower(), [
            f"{user_params.field} current research",
            f"{user_params.field} theoretical frameworks",
            f"{user_params.field} evidence based practice"
        ])

    def _validate_outline(self, outline: List[OutlineSection], target_words: int) -> bool:
        """Validate that outline word allocation is reasonable."""
        total_allocated = sum(section.word_allocation for section in outline)

        # Allow 10% variance
        tolerance = 0.1
        min_words = target_words * (1 - tolerance)
        max_words = target_words * (1 + tolerance)

        return min_words <= total_allocated <= max_words
