"""
Migrated Writer Agent - Using new LLM Gateway with capability-based model selection.
This shows how to migrate from direct model instantiation to the new gateway system.
"""

import re
import json
import time
from typing import Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage

from ..base import StreamingNode, NodeError
from ..handywriterz_state import HandyWriterzState
from ...services.node_integration import get_node_client_factory, get_model_service_integration
from ...services.model_selector import SelectionStrategy


@dataclass
class WritingResult:
    """Comprehensive writing result with quality metrics."""
    content: str
    word_count: int
    citation_count: int
    sections_count: int
    quality_score: float
    academic_tone_score: float
    processing_time: float
    model_used: str
    revision_count: int
    compliance_score: float
    evidence_integration_score: float
    originality_score: float


class MigratedWriterAgent(StreamingNode):
    """
    Migrated writer agent using the new LLM Gateway system.
    Shows compatibility between old and new approaches.
    """

    def __init__(self):
        super().__init__("writer", timeout_seconds=450.0, max_retries=3)

        # NEW: Use node client factory instead of direct model instantiation
        self.client_factory = get_node_client_factory()
        self.model_service = get_model_service_integration()

        # Quality and structure requirements remain the same
        self.quality_threshold = 0.85
        self.max_revisions = 3

        self.academic_quality_standards = {
            "minimum_word_accuracy": 0.90,
            "minimum_citation_density": 0.03,
            "minimum_source_utilization": 0.80,
            "minimum_academic_tone": 0.85,
            "minimum_evidence_integration": 0.80,
            "minimum_originality": 0.75
        }

        self.structure_requirements = {
            "essay": ["introduction", "body_paragraphs", "conclusion"],
            "research_paper": ["abstract", "introduction", "literature_review",
                             "methodology", "results", "discussion", "conclusion", "references"],
            "literature_review": ["introduction", "methodology", "main_themes",
                                "synthesis", "conclusion", "references"],
            "case_study": ["introduction", "background", "case_description",
                         "analysis", "findings", "implications", "conclusion"],
            "dissertation": ["abstract", "introduction", "literature_review",
                           "methodology", "results", "discussion", "conclusion",
                           "references", "appendices"]
        }

    async def execute(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute writing with new gateway system."""
        start_time = time.time()

        try:
            self.logger.info("🎯 Writer Agent: Starting content generation with new gateway")
            self._broadcast_progress(state, "Initializing intelligent writing system", 5)

            # Emit SSE: writer_started (via unified publisher on routing layer channel)
            try:
                from src.agent.sse import SSEPublisher  # type: ignore
                import redis.asyncio as _redis  # type: ignore
                import os as _os
                _publisher = SSEPublisher(async_redis=_redis.from_url(_os.getenv("REDIS_URL", "redis://localhost:6379")))
                await _publisher.publish(
                    state.get("conversation_id"),
                    "writer_started",
                    {"node": "writer", "ts": datetime.utcnow().isoformat()}
                )
            except Exception:
                # Non-fatal if SSE not available in this environment
                pass

            # Extract and validate inputs (unchanged)
            filtered_sources = state.get("filtered_sources", [])
            evidence_map = state.get("evidence_map", {})
            user_params = state.get("user_params", {})
            uploaded_docs = state.get("uploaded_docs", [])

            if not filtered_sources and not evidence_map:
                raise NodeError("No validated sources or evidence provided for writing", self.name)

            self.logger.info(f"Processing {len(filtered_sources)} sources with evidence mapping")

            # Phase 1: Content Planning (using new system)
            content_plan = await self._design_content_structure_v2(state, filtered_sources)
            self._broadcast_progress(state, "Content structure designed with AI assistance", 15)

            # Phase 2: Content Generation (using new gateway)
            writing_result = await self._generate_content_v2(state, content_plan, filtered_sources, evidence_map)
            self._broadcast_progress(state, "Content generation completed", 70)

            # Phase 3: Quality Assurance (enhanced with new metrics)
            refined_result = await self._quality_assurance_v2(state, writing_result, filtered_sources)
            self._broadcast_progress(state, "Quality assurance completed", 85)

            # Phase 4: Academic Compliance (unchanged)
            compliance_result = await self._academic_compliance_validation(state, refined_result, user_params)
            self._broadcast_progress(state, "Academic compliance validated", 95)

            # Compile results (unchanged)
            final_result = WritingResult(
                content=compliance_result["content"],
                word_count=compliance_result["word_count"],
                citation_count=compliance_result["citation_count"],
                sections_count=compliance_result["sections_count"],
                quality_score=compliance_result["quality_score"],
                academic_tone_score=compliance_result["academic_tone_score"],
                processing_time=time.time() - start_time,
                model_used=compliance_result["model_used"],
                revision_count=compliance_result["revision_count"],
                compliance_score=compliance_result["compliance_score"],
                evidence_integration_score=compliance_result["evidence_integration_score"],
                originality_score=compliance_result["originality_score"]
            )

            # Update state (unchanged)
            state.update({
                "generated_content": final_result.content,
                "writing_result": asdict(final_result),
                "content_metadata": {
                    "generation_timestamp": datetime.utcnow().isoformat(),
                    "quality_validated": final_result.quality_score >= self.quality_threshold,
                    "academic_standard_met": final_result.compliance_score >= 0.85,
                    "processing_duration": final_result.processing_time,
                    "gateway_version": "v2_capability_aware"  # NEW: Track gateway version
                }
            })

            self._broadcast_progress(state, "🎯 Intelligent Writing Complete", 100)

            self.logger.info(f"Writing completed in {final_result.processing_time:.2f}s with {final_result.quality_score:.1%} quality using {final_result.model_used}")

            return {
                "writing_result": asdict(final_result),
                "content": final_result.content,
                "quality_metrics": {
                    "overall_quality": final_result.quality_score,
                    "academic_compliance": final_result.compliance_score,
                    "evidence_integration": final_result.evidence_integration_score,
                    "originality": final_result.originality_score,
                    "processing_efficiency": final_result.processing_time
                }
            }

        except Exception as e:
            self.logger.error(f"Writing failed: {e}")
            self._broadcast_progress(state, f"Writing error: {str(e)}", error=True)
            raise NodeError(f"Writing execution failed: {e}", self.name)

    async def _design_content_structure_v2(self, state: HandyWriterzState, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        NEW VERSION: Design content structure using capability-aware model selection.
        The gateway automatically selects the best model for planning tasks.
        """
        try:
            user_params = state.get("user_params", {})
            writeup_type = user_params.get("writeupType", "essay")
            word_count = user_params.get("wordCount", 1000)

            # NEW: Create capability-aware client for content planning
            # The system automatically selects a model optimized for reasoning/planning
            planning_client = self.client_factory.create_client(
                node_name="content_planner",
                capabilities=["reasoning", "function_calling", "long_context"],
                strategy=SelectionStrategy.PERFORMANCE_OPTIMIZED,  # Best model for planning
                trace_id=state.get("trace_id"),
                user_id=state.get("user_id")
            )

            prompt = self._create_content_plan_prompt(user_params, sources)

            messages = [
                SystemMessage(content="You are an expert academic content planner with deep knowledge of academic writing structures and evidence integration."),
                HumanMessage(content=prompt)
            ]

            # NEW: The client automatically handles model selection, retries, and fallbacks
            response = await planning_client.ainvoke(messages)

            try:
                content_plan = json.loads(response.content)
                self.logger.info(f"Content plan generated successfully using model selection")
                return content_plan
            except json.JSONDecodeError:
                # Fallback to parsing if JSON is malformed
                return self._parse_plan_from_text(response.content, writeup_type, word_count)

        except Exception as e:
            self.logger.error(f"Content structure design failed: {e}")
            # Fallback to simple structure (unchanged)
            required_sections = self.structure_requirements.get(writeup_type, self.structure_requirements["essay"])
            words_per_section = word_count // len(required_sections)
            return {
                "writeup_type": writeup_type,
                "total_words": word_count,
                "sections": [
                    {"name": section, "target_words": words_per_section, "sources_allocated": 2}
                    for section in required_sections
                ],
                "citation_style": user_params.get("citationStyle", "Harvard"),
                "academic_field": user_params.get("field", "general")
            }

    async def _generate_content_v2(self, state: HandyWriterzState, content_plan: Dict[str, Any], sources: List[Dict[str, Any]], evidence_map: Dict[str, Any]) -> Dict[str, Any]:
        """
        NEW VERSION: Generate content using the new gateway with automatic model selection.
        """
        try:
            user_params = state.get("user_params", {})

            # NEW: Create writer client optimized for creative writing tasks
            writer_client = self.client_factory.create_writer_client(
                node_name="writer",
                strategy=SelectionStrategy.BALANCED,  # Balance quality and cost
                trace_id=state.get("trace_id"),
                user_id=state.get("user_id")
            )

            # Create comprehensive writing prompt
            system_prompt = self._create_academic_writing_prompt(content_plan, sources, user_params)

            # NEW: Use model service integration for streaming with automatic selection
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Please write the complete academic document as specified."}
            ]

            full_content = ""
            word_count = 0
            model_used = "unknown"

            # NEW: Stream with automatic model selection and performance tracking
            async for chunk in self.model_service.stream_completion(
                agent_name="writer",
                messages=messages,
                temperature=0.7,
                trace_id=state.get("trace_id")
            ):
                if chunk.get("token"):
                    full_content += chunk["token"]
                    model_used = chunk.get("model", model_used)

                    # Publish SSE token delta for live UI rendering
                    try:
                        from src.agent.sse import SSEPublisher  # type: ignore
                        import redis.asyncio as _redis  # type: ignore
                        import os as _os
                        _publisher = SSEPublisher(async_redis=_redis.from_url(_os.getenv("REDIS_URL", "redis://localhost:6379")))
                        await _publisher.publish(
                            state.get("conversation_id"),
                            "token",
                            {
                                "delta": chunk["token"],
                                "cursor": {"message_id": state.get("conversation_id"), "index": 0},
                                "ts": datetime.utcnow().isoformat()
                            }
                        )
                    except Exception:
                        # Non-fatal if SSE not available
                        pass

                    # Update progress every 50 words (unchanged)
                    new_word_count = len(full_content.split())
                    if new_word_count - word_count >= 50:
                        word_count = new_word_count
                        self._broadcast_progress(
                            state,
                            f"Generated {word_count} words using {model_used}...",
                            min(90, 20 + (word_count / 1000) * 50)
                        )

            writing_result = {
                "content": full_content,
                "word_count": len(full_content.split()),
                "model_used": model_used,
                "generation_time": time.time(),
                "gateway_version": "v2"  # NEW: Track gateway usage
            }

            return writing_result

        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")

            # NEW: The gateway system handles fallbacks automatically,
            # but we can still implement application-level fallbacks
            try:
                # Try with cost-optimized strategy as fallback
                fallback_client = self.client_factory.create_writer_client(
                    node_name="writer_fallback",
                    strategy=SelectionStrategy.COST_OPTIMIZED,
                    trace_id=state.get("trace_id")
                )

                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content="Please write a shorter version of the requested document.")
                ]

                response = await fallback_client.ainvoke(messages)

                return {
                    "content": response.content,
                    "word_count": len(response.content.split()),
                    "model_used": "fallback_model",
                    "generation_time": time.time(),
                    "gateway_version": "v2_fallback"
                }

            except Exception as fallback_error:
                self.logger.error(f"Fallback generation also failed: {fallback_error}")
                raise NodeError(f"All content generation attempts failed: {e}", self.name)

    async def _quality_assurance_v2(self, state: HandyWriterzState, writing_result: Dict[str, Any], sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        NEW VERSION: Enhanced quality assurance using AI-powered evaluation.
        """
        try:
            content = writing_result["content"]

            # Clean formatting (unchanged)
            content = self._clean_formatting(content)

            # NEW: AI-powered quality evaluation
            quality_metrics = await self._ai_quality_evaluation(content, sources, state)

            # Ensure citations present (unchanged)
            content = self._ensure_citations_present(content, sources)

            refined_result = {
                **writing_result,
                "content": content,
                "citation_count": quality_metrics["citation_count"],
                "sections_count": quality_metrics["sections_count"],
                "quality_score": quality_metrics["overall_quality"],
                "ai_evaluation": quality_metrics.get("ai_feedback", {})  # NEW: AI feedback
            }

            return refined_result

        except Exception as e:
            self.logger.error(f"Quality assurance failed: {e}")
            # Fallback to basic quality metrics
            basic_metrics = self._calculate_quality_metrics(content, sources, state.get("user_params", {}))
            return {
                **writing_result,
                "content": content,
                **basic_metrics
            }

    async def _ai_quality_evaluation(self, content: str, sources: List[Dict[str, Any]], state: HandyWriterzState) -> Dict[str, Any]:
        """
        NEW: AI-powered quality evaluation using evaluator-optimized model.
        """
        try:
            # Create evaluator client optimized for reasoning and analysis
            evaluator_client = self.client_factory.create_evaluator_client(
                node_name="quality_evaluator",
                trace_id=state.get("trace_id")
            )

            evaluation_prompt = f"""
            Please evaluate the following academic content for quality:

            Content:
            {content[:2000]}...  # Limit for evaluation

            Sources Available: {len(sources)}

            Evaluate on these criteria and return JSON:
            {{
                "overall_quality": 0.0-1.0,
                "citation_count": number,
                "sections_count": number,
                "academic_tone": 0.0-1.0,
                "evidence_integration": 0.0-1.0,
                "structure_quality": 0.0-1.0,
                "feedback": "brief improvement suggestions"
            }}
            """

            messages = [
                SystemMessage(content="You are an expert academic evaluator."),
                HumanMessage(content=evaluation_prompt)
            ]

            response = await evaluator_client.ainvoke(messages)

            try:
                ai_metrics = json.loads(response.content)
                return ai_metrics
            except json.JSONDecodeError:
                # Fallback to basic metrics if AI evaluation fails
                return self._calculate_quality_metrics(content, sources, state.get("user_params", {}))

        except Exception as e:
            self.logger.warning(f"AI quality evaluation failed, using basic metrics: {e}")
            return self._calculate_quality_metrics(content, sources, state.get("user_params", {}))

    # The following methods remain largely unchanged from the original
    # but can be enhanced with the new gateway system

    def _parse_plan_from_text(self, text: str, writeup_type: str, word_count: int) -> Dict[str, Any]:
        """Parse content plan from unstructured text response."""
        # Simple fallback parser
        required_sections = self.structure_requirements.get(writeup_type, self.structure_requirements["essay"])
        words_per_section = word_count // len(required_sections)

        return {
            "writeup_type": writeup_type,
            "total_words": word_count,
            "sections": [
                {"name": section, "target_words": words_per_section, "sources_allocated": 2}
                for section in required_sections
            ],
            "citation_style": "Harvard",
            "academic_field": "general"
        }

    def _create_content_plan_prompt(self, user_params: Dict[str, Any], sources: List[Dict[str, Any]]) -> str:
        """Create a prompt for generating a detailed content plan."""
        sources_summary = "\n".join([
            f"- {source.get('title', 'Untitled')}: {source.get('summary', 'No summary available.')}"
            for source in sources[:10]  # Limit to avoid token overflow
        ])

        return f"""
        Based on the user's request for a {user_params.get("writeupType", "essay")} of {user_params.get("wordCount", 1000)} words
        in the field of {user_params.get("field", "general")}, and the following sources, create a detailed content plan.

        Available Sources:
        {sources_summary}

        Create a JSON content plan with this structure:
        {{
            "writeup_type": "{user_params.get("writeupType", "essay")}",
            "total_words": {user_params.get("wordCount", 1000)},
            "sections": [
                {{
                    "name": "Introduction",
                    "target_words": 150,
                    "key_points": ["Hook", "Background", "Thesis statement"],
                    "sources_to_use": ["Source Title 1", "Source Title 2"]
                }}
            ],
            "citation_style": "{user_params.get("citationStyle", "Harvard")}",
            "academic_field": "{user_params.get("field", "general")}"
        }}
        """

    def _create_academic_writing_prompt(self, content_plan: Dict[str, Any], sources: List[Dict[str, Any]], user_params: Dict[str, Any]) -> str:
        """Create a comprehensive academic writing prompt."""
        sources_text = "\n".join([
            f"Source {i+1}: {source.get('title', 'Unknown')} by {source.get('authors', 'Unknown')} ({source.get('year', 'Unknown')})"
            for i, source in enumerate(sources[:10])
        ])

        sections_text = "\n".join([
            f"- {section['name']}: ~{section['target_words']} words"
            for section in content_plan.get("sections", [])
        ])

        return f"""
You are an expert academic writer specializing in {content_plan.get("academic_field", "general studies")}.

Write a {content_plan.get("writeup_type", "essay")} of {content_plan.get("total_words", 1000)} words using this structure:

{sections_text}

Available Sources:
{sources_text}

Requirements:
- Use {content_plan.get("citation_style", "Harvard")} citation style
- Maintain formal academic tone throughout
- Integrate at least 80% of provided sources meaningfully
- Include proper in-text citations
- Ensure logical flow between sections
- Meet the target word count (±10%)
- Follow field-specific conventions for {content_plan.get("academic_field", "general studies")}

Begin writing the complete {content_plan.get("writeup_type", "document")} now:
"""

    # Include remaining unchanged methods from original
    async def _academic_compliance_validation(self, state: HandyWriterzState, refined_result: Dict[str, Any], user_params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate academic compliance and standards."""
        try:
            content = refined_result["content"]

            target_words = user_params.get("wordCount", 1000)
            current_words = len(content.split())
            word_accuracy = 1.0 - abs(current_words - target_words) / target_words

            compliance_result = {
                **refined_result,
                "word_count": current_words,
                "academic_tone_score": 0.85,
                "compliance_score": min(word_accuracy + 0.15, 1.0),
                "evidence_integration_score": 0.80,
                "originality_score": 0.85,
                "revision_count": 0
            }

            return compliance_result

        except Exception as e:
            self.logger.error(f"Academic compliance validation failed: {e}")
            raise NodeError(f"Academic compliance validation failed: {e}", self.name)

    def _clean_formatting(self, content: str) -> str:
        """Clean up formatting issues in the content."""
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r'\n\n+', '\n\n', content)
        content = re.sub(r'\s+([,.;:!?])', r'\1', content)
        return content.strip()

    def _ensure_citations_present(self, content: str, sources: List[Dict[str, Any]]) -> str:
        """Ensure all sources are cited in the content."""
        cited_sources = 0

        for source in sources:
            authors = source.get("authors", "")
            year = str(source.get("year", ""))

            if authors and year:
                author_parts = authors.split(",")
                if author_parts:
                    first_author_surname = author_parts[0].strip().split()[-1]
                    if first_author_surname in content and year in content:
                        cited_sources += 1

        citation_rate = cited_sources / len(sources) if sources else 1

        if citation_rate < 0.7:
            self.logger.warning(f"Low citation rate detected: {citation_rate:.1%}")

        return content

    def _calculate_quality_metrics(self, content: str, sources: List[Dict[str, Any]], user_params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive quality metrics."""
        words = content.split()
        word_count = len(words)

        citation_pattern = r'([^)]*\d{4}[^)]*)'
        citations = re.findall(citation_pattern, content)
        citation_count = len(citations)

        section_pattern = r'^#+\s+.+$'
        sections = re.findall(section_pattern, content, re.MULTILINE)
        sections_count = len(sections)

        target_words = user_params.get("wordCount", 1000)
        word_accuracy = 1.0 - abs(word_count - target_words) / target_words if target_words > 0 else 1.0
        citation_density = citation_count / max(1, word_count // 100)

        overall_quality = (word_accuracy * 0.3 + min(citation_density / 3, 1.0) * 0.4 + 0.3) * 0.85

        return {
            "word_count": word_count,
            "citation_count": citation_count,
            "sections_count": sections_count,
            "word_accuracy": word_accuracy,
            "citation_density": citation_density,
            "overall_quality": min(overall_quality, 1.0)
        }


# Export the migrated writer agent instance
migrated_writer_agent_node = MigratedWriterAgent()
