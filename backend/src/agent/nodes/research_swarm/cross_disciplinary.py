"""
Cross-Disciplinary Agent for HandyWriterz Research Swarm.

This micro-agent finds and synthesizes information from related academic
disciplines, fostering innovation and interdisciplinary insights.
"""

from typing import Dict, Any, List
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
import arxiv

from ...base import BaseNode
from ...handywriterz_state import HandyWriterzState

class CrossDisciplinaryAgent(BaseNode):
    """
    A specialized agent for cross-disciplinary research and synthesis.
    """

    def __init__(self):
        super().__init__(name="CrossDisciplinaryAgent")
        self.llm = None  # Initialize lazily
        self.arxiv_client = None  # Initialize lazily

    async def execute(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the cross-disciplinary research and synthesis.
        """
        # Lazy initialization
        if self.llm is None:
            try:
                self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
            except Exception as e:
                self.logger.warning(f"Failed to initialize LLM: {e}")
                return {"cross_disciplinary_analysis": {"status": "error", "message": "LLM unavailable"}}
        
        if self.arxiv_client is None:
            try:
                self.arxiv_client = arxiv.Client()
            except Exception as e:
                self.logger.warning(f"Failed to initialize arXiv client: {e}")
                return {"cross_disciplinary_analysis": {"status": "error", "message": "arXiv unavailable"}}
        self.logger.info("Initiating cross-disciplinary research.")
        self._broadcast_progress(state, "Exploring related academic disciplines...")

        related_fields = await self._identify_related_fields(state)
        if not related_fields:
            return {"cross_disciplinary_analysis": {}}

        self.logger.info(f"Identified related fields: {related_fields}")
        self._broadcast_progress(state, f"Identified related fields: {', '.join(related_fields)}")

        cross_disciplinary_results = {}
        for field in related_fields:
            results = await self._search_related_field(state, field)
            cross_disciplinary_results[field] = results

        synthesis = await self._synthesize_results(cross_disciplinary_results)

        return {
            "cross_disciplinary_analysis": {
                "related_fields": related_fields,
                "raw_results": cross_disciplinary_results,
                "synthesis": synthesis,
            }
        }

    async def _identify_related_fields(self, state: HandyWriterzState) -> List[str]:
        """
        Identifies related academic fields using an LLM.
        """
        user_params = state.get("user_params", {})
        field = user_params.get("field", "")
        prompt_text = state.get("messages", [{}])[-1].get("content", "")

        prompt = f"""
        Given the primary academic field "{field}" and the research topic "{prompt_text}",
        identify up to 3 related academic disciplines that might offer
        valuable alternative perspectives or complementary research.

        Return a simple comma-separated list of the identified fields.
        """
        try:
            response = await self.llm.ainvoke(prompt)
            return [f.strip() for f in response.content.split(",") if f.strip()]
        except Exception as e:
            self.logger.error(f"LLM call failed during related field identification: {e}")
            return []

    async def _search_related_field(self, state: HandyWriterzState, field: str) -> List[Dict[str, Any]]:
        """
        Searches for relevant literature in a related field.
        """
        prompt_text = state.get("messages", [{}])[-1].get("content", "")
        search_query = f"{field} AND ({prompt_text})"

        try:
            search = arxiv.Search(
                query=search_query,
                max_results=3,
                sort_by=arxiv.SortCriterion.Relevance
            )
            results = list(self.arxiv_client.results(search))
            return self._process_results(results)
        except Exception as e:
            self.logger.error(f"ArXiv search failed for related field {field}: {e}")
            return []

    def _process_results(self, results: List[arxiv.Result]) -> List[Dict[str, Any]]:
        """
        Processes the raw results from the arXiv API into a structured format.
        """
        processed = []
        for result in results:
            processed.append({
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "summary": result.summary,
                "pdf_url": result.pdf_url,
            })
        return processed

    async def _synthesize_results(self, results: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Synthesizes the findings from the cross-disciplinary research.
        """
        if not results:
            return "No cross-disciplinary findings."

        prompt = f"""
        Synthesize the key insights from the following cross-disciplinary research findings.
        Identify any common themes, contrasting perspectives, or novel connections
        that emerge from the combination of these different fields.

        {json.dumps(results, indent=2)}

        Provide a brief synthesis of the most important cross-disciplinary insights.
        """
        try:
            response = await self.llm.ainvoke(prompt)
            return response.content
        except Exception as e:
            self.logger.error(f"LLM call failed during synthesis: {e}")
            return "Could not synthesize cross-disciplinary findings."

cross_disciplinary_agent_node = CrossDisciplinaryAgent()
