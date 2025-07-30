import asyncio
from opentelemetry import trace

tracer = trace.get_tracer(__name__)
from typing import Dict, Any

from src.agent.base import BaseNode
from ...agent.handywriterz_state import HandyWriterzState
from utils.chartify import create_chart_svg
from src.services.llm_service import get_llm_client

class Derivatives(BaseNode):
    """
    A node that generates derivative content from the final draft,
    such as slide bullets and charts.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.llm_client = get_llm_client(model_preference="flash") # Use a fast model

    async def execute(self, state: HandyWriterzState) -> Dict[str, Any]:
        """
        Generates slide bullets and charts from the final draft.
        """
        with tracer.start_as_current_span("derivatives_node") as span:
            span.set_attribute("document_length", len(state.get("final_draft_content", "")))
            print("🎨 Executing Derivatives Node")
        final_draft = state.get("final_draft_content")

        if not final_draft:
            print("⚠️ Derivatives: Missing final_draft, skipping.")
            return {}

        try:
            # Generate slide bullets and charts in parallel
            slide_bullets, chart_svg = await asyncio.gather(
                self._generate_slide_bullets(final_draft),
                self._generate_charts(final_draft)
            )

            print("✅ Successfully generated derivatives")
            return {
                "slide_bullets": slide_bullets,
                "charts_svg": chart_svg,
            }

        except Exception as e:
            print(f"❌ Derivatives Error: {e}")
            return {
                "slide_bullets": None,
                "charts_svg": None,
            }

    async def _generate_slide_bullets(self, text: str) -> str:
        """Generates slide bullets from the text using an LLM."""
        prompt = f"""
        Given the following academic text, extract the key points and present them as a concise list of slide bullets.
        Each bullet point should be a short, impactful statement.
        Do not exceed 10 bullet points.

        Text:
        ---
        {text[:4000]}
        ---

        Slide Bullets:
        """
        try:
            response = await self.llm_client.generate(prompt, max_tokens=500)
            return response
        except Exception as e:
            print(f"Failed to generate slide bullets: {e}")
            return ""

    async def _generate_charts(self, text: str) -> str:
        """Generates charts from the text using the chartify utility."""
        try:
            # This is a simplified call; a real implementation would
            # extract structured data from the text first.
            chart_svg = create_chart_svg(text)
            return chart_svg
        except Exception as e:
            print(f"Failed to generate charts: {e}")
            return ""