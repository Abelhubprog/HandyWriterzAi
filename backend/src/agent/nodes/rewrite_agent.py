import logging
import os
from typing import Dict, Any, List

from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph
from langgraph.graph import END
from langgraph.types import Send
from langchain_core.runnables import RunnableConfig

from src.agent.handywriterz_state import HandyWriterzState, WorkflowStatus
from src.config import get_settings
from src.prompts.templates.rewrite_prompts import REWRITE_INSTRUCTIONS

logger = logging.getLogger(__name__)

class RewriteAgent:
    """
    Agent responsible for iteratively rewriting sections of a document based on human feedback (highlights).
    """

    def __init__(self):
        settings = get_settings()
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_pro_model, # Or a specific rewrite model
            temperature=0.7,
            max_retries=2,
            api_key=os.getenv("GEMINI_API_KEY"),
        )

    async def rewrite_document(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Rewrites the current draft based on highlighted sections provided by human feedback.
        """
        logger.info(f"🔄 RewriteAgent: Starting rewrite for conversation {state.conversation_id}")

        current_draft = state.current_draft
        highlighted_sections = state.get("highlighted_sections", []) # Get from state

        if not current_draft:
            logger.warning("RewriteAgent: No current draft found to rewrite.")
            return {"workflow_status": WorkflowStatus.FAILED, "error_message": "No draft to rewrite."}

        if not highlighted_sections:
            logger.info("RewriteAgent: No highlighted sections provided. Skipping rewrite.")
            return {"current_draft": current_draft, "workflow_status": WorkflowStatus.WRITING} # Return original draft

        # Construct the prompt for the LLM
        highlight_feedback = "\n".join([
            f"- Section: '{section.get('text', '')}' (Type: {section.get('type', 'unknown')})"
            for section in highlighted_sections
        ])

        prompt = REWRITE_INSTRUCTIONS.format(
            current_draft=current_draft,
            highlighted_feedback=highlight_feedback
        )

        messages = [
            HumanMessage(content=prompt)
        ]

        try:
            response = await self.llm.invoke(messages)
            revised_draft = response.content

            logger.info(f"✅ RewriteAgent: Document rewritten for conversation {state.conversation_id}")

            # Increment revision count
            new_revision_count = state.revision_count + 1

            # Update state with new draft and increment revision count
            return {
                "current_draft": revised_draft,
                "revision_count": new_revision_count,
                "workflow_status": WorkflowStatus.REVISING, # Indicate it's in a revision loop
                "messages": state.messages + [AIMessage(content=revised_draft)] # Add AI response to messages
            }

        except Exception as e:
            logger.error(f"❌ RewriteAgent: Error during rewrite for {state.conversation_id}: {e}")
            return {"workflow_status": WorkflowStatus.FAILED, "error_message": f"Rewrite failed: {e}"}

# Helper function to get the agent instance
def get_rewrite_agent() -> RewriteAgent:
    return RewriteAgent()
