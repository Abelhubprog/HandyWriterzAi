import json
from typing import Dict, Any, List

from ..base import BaseNode
from ..handywriterz_state import HandyWriterzState
from src.services.llm_service import get_llm_client, get_all_llm_clients
from src.utils.file_utils import get_file_summary

class EnhancedUserIntentAgent(BaseNode):
    """
    A sophisticated agent that performs deep semantic analysis of the user's request,
    integrates context from uploaded files, and uses a multi-model consensus approach
    to determine the precise user intent and workflow requirements.
    """

    def __init__(self, name: str):
        super().__init__(name)
        # Get clients for all major models for multi-model analysis
        self.llm_clients = get_all_llm_clients()
        self.primary_client = self.llm_clients.get("claude", get_llm_client()) # Default to Claude for reasoning

    def _create_system_prompt(self, user_prompt: str, file_summaries: List[str]) -> str:
        """Creates a detailed system prompt for intent analysis."""
        return f"""
        You are an expert academic workflow analyzer. Your task is to perform a deep semantic analysis of a user's request to determine their precise intent for an academic writing task.

        **User's Core Request:**
        "{user_prompt}"

        **Context from Uploaded Files:**
        {file_summaries if file_summaries else "No files uploaded."}

        **Your Analysis Must Include:**

        1.  **Primary Intent Classification:**
            -   `document_type`: (e.g., 'doctoral_dissertation', 'research_paper', 'literature_review')
            -   `subject_area`: (e.g., 'interdisciplinary_ai_law_healthcare', 'psychology', 'business')
            -   `academic_rigor`: (e.g., 'publication_ready', 'undergraduate', 'phd_level')
            -   `methodology`: (e.g., 'systematic_review_with_analysis', 'qualitative_analysis')
            -   `integration_complexity`: (e.g., 'expert_multimodal', 'text_only', 'heavy_data_integration')

        2.  **Technical Requirements Extraction:**
            -   `word_count`: (e.g., {{"target": 8500, "range": [8000, 10000]}})
            -   `citation_style`: (e.g., 'harvard', 'apa', 'mla')
            -   `source_count`: (e.g., {{"minimum": 40, "target": 50}})
            -   `originality_threshold`: (e.g., 90.0)
            -   `quality_threshold`: (e.g., 87.0)

        3.  **File Utilization Strategy:**
            -   `research_papers`: (e.g., 'evidence_foundation', 'background_context')
            -   `audio_content`: (e.g., 'expert_testimony_integration', 'primary_data_source')
            -   `video_content`: (e.g., 'visual_evidence_support', 'lecture_summary')
            -   `data_files`: (e.g., 'statistical_analysis_inclusion', 'economic_modeling')

        4.  **Workflow Recommendations:**
            -   `activate_swarm_intelligence`: (boolean) - True for complex, interdisciplinary, or high-stakes tasks.
            -   `deploy_all_research_agents`: (boolean) - True if extensive research is required.
            -   `enable_deep_quality_assurance`: (boolean) - True for high academic rigor.
            -   `generate_supplementary_content`: (boolean) - True if user asks for slides, infographics, etc.

        5.  **Clarification Assessment:**
            -   `clarity_score`: A score from 0.0 to 100.0 indicating how clear the user's request is.
            -   `ambiguity_detected`: A list of any ambiguous terms or requirements.
            -   `missing_information`: A list of critical information that is missing.
            -   `clarification_needed`: (boolean) - True if clarity_score is below 85.0 or critical information is missing.
            -   `clarifying_questions`: A list of specific questions to ask the user if clarification is needed.

        **Output Format:**
        You MUST return a single, valid JSON object containing all the fields described above. Do not include any other text or explanations.
        """

    async def execute(self, state: HandyWriterzState) -> Dict[str, Any]:
        """
        Executes the multi-model intent analysis.
        """
        print("🔎 Executing EnhancedUserIntentAgent with multi-model analysis")
        prompt = state.get("messages", [])[-1].content
        uploaded_files = state.get("uploaded_files", [])

        # Generate summaries for uploaded files
        file_summaries = [get_file_summary(file) for file in uploaded_files]

        system_prompt = self._create_system_prompt(prompt, file_summaries)

        # --- Multi-Model Analysis ---
        analysis_tasks = []
        for model_name, client in self.llm_clients.items():
            analysis_tasks.append(client.generate(system_prompt, max_tokens=1500, is_json=True))
        
        responses = await asyncio.gather(*analysis_tasks, return_exceptions=True)

        # --- Consensus Building ---
        valid_analyses = []
        for i, res in enumerate(responses):
            if not isinstance(res, Exception):
                try:
                    valid_analyses.append(json.loads(res))
                except json.JSONDecodeError:
                    print(f"⚠️ Warning: Model {list(self.llm_clients.keys())[i]} produced invalid JSON.")
        
        if not valid_analyses:
            # Critical failure, fallback to asking for clarification
            return {
                "intent_analysis_result": {},
                "clarification_needed": True,
                "clarifying_questions": ["I had trouble understanding the request. Could you please rephrase or provide more specific details about your academic task?"]
            }

        # Simple consensus: merge dictionaries, letting later ones overwrite earlier ones.
        # A more complex system could vote on each field.
        final_analysis = {}
        for analysis in valid_analyses:
            final_analysis.update(analysis)

        # Final validation and decision
        clarification_needed = final_analysis.get("clarification_needed", False)
        if final_analysis.get("clarity_score", 100.0) < 85.0:
            clarification_needed = True
        if not final_analysis.get("primary_intent", {}).get("document_type"):
            clarification_needed = True
            final_analysis["clarifying_questions"] = final_analysis.get("clarifying_questions", []) + ["What type of document do you need (e.g., essay, research paper, dissertation)?"]

        return {
            "intent_analysis_result": final_analysis,
            "clarification_needed": clarification_needed,
            "clarifying_questions": final_analysis.get("clarifying_questions", [])
        }
