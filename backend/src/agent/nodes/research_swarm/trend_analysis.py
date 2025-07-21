"""
Trend Analysis Agent for HandyWriterz Research Swarm.

This micro-agent identifies emerging trends and hot topics in a given
academic field by analyzing Google Trends data and recent arXiv pre-prints.
"""

from typing import Dict, Any, List
from langchain_core.runnables import RunnableConfig

# Optional imports - gracefully handle missing dependencies
try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    TrendReq = None

try:
    import arxiv
    ARXIV_AVAILABLE = True
except ImportError:
    ARXIV_AVAILABLE = False
    arxiv = None

from ...base import BaseNode, NodeError
from ...handywriterz_state import HandyWriterzState

class TrendAnalysisAgent(BaseNode):
    """
    A specialized agent for analyzing academic trends.
    """

    def __init__(self):
        super().__init__(name="TrendAnalysisAgent")
        if PYTRENDS_AVAILABLE:
            self.pytrends = TrendReq(hl='en-US', tz=360)
        else:
            self.pytrends = None
            
        if ARXIV_AVAILABLE:
            self.arxiv_client = arxiv.Client()
        else:
            self.arxiv_client = None

    async def execute(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the trend analysis.
        """
        self.logger.info("Initiating academic trend analysis.")
        self._broadcast_progress(state, "Analyzing academic trends...")

        # Check if required dependencies are available
        if not PYTRENDS_AVAILABLE and not ARXIV_AVAILABLE:
            self.logger.warning("Trend analysis dependencies not available, using fallback")
            return {"trend_analysis": {"status": "dependencies_missing", "fallback_trends": ["emerging AI", "sustainability", "digital transformation"]}}

        keywords = self._extract_keywords(state)
        if not keywords:
            raise NodeError("Could not extract keywords for trend analysis.", self.name)

        processed_trends = {"keywords": keywords, "trends": []}

        # Try Google Trends if available
        if PYTRENDS_AVAILABLE and self.pytrends:
            try:
                self.pytrends.build_payload(keywords, cat=0, timeframe='today 5-y', geo='', gprop='')
                interest_over_time = self.pytrends.interest_over_time()
                related_topics = self.pytrends.related_topics()
                processed_trends = self._process_trends(interest_over_time, related_topics)
                self.logger.info("Successfully retrieved Google Trends data.")
                self._broadcast_progress(state, "Analyzed Google Trends for key topics.")
            except Exception as e:
                self.logger.warning(f"Google Trends analysis failed: {e}")

        # Try arXiv if available
        if ARXIV_AVAILABLE and self.arxiv_client:
            try:
                # Add arXiv trends analysis here if needed
                pass
            except Exception as e:
                self.logger.warning(f"arXiv analysis failed: {e}")

        return {"trend_analysis": processed_trends}

    def _extract_keywords(self, state: HandyWriterzState) -> List[str]:
        """
        Extracts keywords for trend analysis from the user's request.
        """
        user_params = state.get("user_params", {})
        field = user_params.get("field", "")
        prompt = state.get("messages", [{}])[-1].get("content", "")

        # A more sophisticated implementation would use an LLM to extract
        # key concepts and topics.
        return [kw for kw in f"{field} {prompt}".split() if len(kw) > 3][:5]

    def _process_trends(self, interest_over_time, related_topics) -> Dict[str, Any]:
        """
        Processes the trend data into a structured format.
        """
        return {
            "interest_over_time": interest_over_time.to_dict(),
            "related_topics": {kw: topic.to_dict() for kw, topic in related_topics.items()},
        }

trend_analysis_agent_node = TrendAnalysisAgent()
