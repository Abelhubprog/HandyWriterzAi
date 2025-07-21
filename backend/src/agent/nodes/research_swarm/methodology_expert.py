"""
Methodology Expert Agent for HandyWriterz Research Swarm.

This micro-agent analyzes and evaluates research methodologies from
academic papers, ensuring the generated content is methodologically sound.
"""

from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from ...base import BaseNode
from ...handywriterz_state import HandyWriterzState

class MethodologyExpertAgent(BaseNode):
    """
    A specialized agent for analyzing and evaluating research methodologies.
    """

    def __init__(self):
        super().__init__(name="MethodologyExpertAgent")
        self.llm = None  # Initialize lazily to avoid startup failures

    async def execute(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the methodology analysis.
        """
        # Lazy initialization of LLM
        if self.llm is None:
            try:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenAI LLM: {e}")
                return {"methodology_analysis": {"status": "error", "message": "LLM initialization failed"}}
        
        self.logger.info("Initiating methodology analysis.")
        self._broadcast_progress(state, "Analyzing research methodologies...")

        # For this example, we'll assume that the state contains a list of
        # abstracts or paper excerpts to analyze.
        papers = state.get("arxiv_results", [])
        if not papers:
            return {"methodology_analysis": {}}

        analysis_results = []
        for paper in papers:
            analysis = await self._analyze_paper_methodology(paper)
            analysis_results.append(analysis)

        self.logger.info("Methodology analysis complete.")
        self._broadcast_progress(state, "Completed analysis of research methodologies.")

        return {"methodology_analysis": analysis_results}

    async def _analyze_paper_methodology(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes the methodology of a single paper using an LLM.
        """
        prompt = f"""
        Analyze the research methodology described in the following academic paper abstract:

        Title: {paper.get('title', '')}
        Abstract: {paper.get('summary', '')}

        Please provide a brief analysis of the methodology, including:
        1.  The type of methodology used (e.g., qualitative, quantitative, mixed-methods).
        2.  Any specific techniques or approaches mentioned.
        3.  Potential strengths of the methodology.
        4.  Potential limitations or weaknesses.

        Provide your analysis in a structured format.
        """
        try:
            response = await self.llm.ainvoke(prompt)
            # A more robust implementation would parse the response into a
            # structured Pydantic model.
            return {"paper_title": paper.get("title"), "analysis": response.content}
        except Exception as e:
            self.logger.error(f"LLM call failed during methodology analysis: {e}")
            return {"paper_title": paper.get("title"), "analysis": "Could not analyze methodology."}

methodology_expert_agent_node = MethodologyExpertAgent()
