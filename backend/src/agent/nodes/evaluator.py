import asyncio
import json
from typing import Dict, Any, List

from ..base import BaseNode
from ..handywriterz_state import HandyWriterzState
from src.services.llm_service import get_all_llm_clients

class EvaluatorNode(BaseNode):
    """
    A sophisticated node that uses a multi-model consensus approach to evaluate
    the generated draft against a detailed academic rubric.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.llm_clients = get_all_llm_clients()
        self.evaluation_criteria = {
            "Academic_Rigor": 0.25,
            "Content_Quality": 0.20,
            "Structure_Organization": 0.15,
            "Citation_Excellence": 0.15,
            "Writing_Quality": 0.15,
            "Innovation_Impact": 0.10,
        }

    def _create_evaluation_prompt(self, draft: str) -> str:
        """Creates a detailed prompt for the evaluation models."""
        return f"""
        You are an expert academic evaluator. Your task is to provide a rigorous, unbiased evaluation of the following academic draft.

        **Draft to Evaluate:**
        ---
        {draft[:15000]}
        ---

        **Evaluation Criteria:**
        Please provide a score from 0 to 100 for each of the following criteria.

        1.  **Academic_Rigor:**
            -   Methodological Soundness
            -   Evidence Quality
            -   Analytical Depth
            -   Critical Thinking

        2.  **Content_Quality:**
            -   Thesis Clarity
            -   Argument Strength
            -   Evidence Integration
            -   Original Contribution

        3.  **Structure_Organization:**
            -   Logical Flow
            -   Section Balance
            -   Transition Quality

        4.  **Citation_Excellence:**
            -   Citation Style Accuracy
            -   Source Credibility
            -   Reference Completeness

        5.  **Writing_Quality:**
            -   Academic Tone
            -   Clarity and Precision
            -   Grammar and Syntax

        6.  **Innovation_Impact:**
            -   Novel Insights
            -   Interdisciplinary Integration
            -   Practical Applications

        **Output Format:**
        You MUST return a single, valid JSON object with keys corresponding to the criteria above (e.g., "Academic_Rigor", "Content_Quality"). The value for each key should be the score (0-100). Do not include any other text or explanations.
        """

    async def execute(self, state: HandyWriterzState) -> Dict[str, Any]:
        """
        Executes the multi-model evaluation process.
        """
        self.logger.info("⚖️ Executing Multi-Model EvaluatorNode")
        draft_content = state.get("generated_content")

        if not draft_content:
            self.logger.warning("EvaluatorNode: Missing draft_content, skipping.")
            return {"evaluation_score": 0, "evaluation_report": "Draft content was not provided."}

        evaluation_prompt = self._create_evaluation_prompt(draft_content)

        # --- Multi-Model Evaluation ---
        evaluation_tasks = []
        for client in self.llm_clients.values():
            evaluation_tasks.append(client.generate(evaluation_prompt, max_tokens=1000, is_json=True))
        
        responses = await asyncio.gather(*evaluation_tasks, return_exceptions=True)

        # --- Consensus Building ---
        valid_evaluations = []
        for i, res in enumerate(responses):
            if not isinstance(res, Exception):
                try:
                    valid_evaluations.append(json.loads(res))
                except json.JSONDecodeError:
                    self.logger.warning(f"Model {list(self.llm_clients.keys())[i]} produced invalid JSON for evaluation.")

        if not valid_evaluations:
            self.logger.error("All evaluation models failed to produce valid JSON.")
            return {"evaluation_score": 0, "evaluation_report": "Evaluation failed due to model errors."}

        # --- Weighted Score Calculation ---
        final_scores = {key: 0 for key in self.evaluation_criteria}
        for eval_result in valid_evaluations:
            for key in self.evaluation_criteria:
                final_scores[key] += eval_result.get(key, 0)
        
        # Average the scores
        for key in final_scores:
            final_scores[key] /= len(valid_evaluations)

        # Calculate the final weighted score
        weighted_score = sum(final_scores[key] * weight for key, weight in self.evaluation_criteria.items())

        # --- Generate Evaluation Report ---
        evaluation_report = self._generate_evaluation_report(final_scores)
        
        # Determine if the write-up is complete
        is_complete = weighted_score >= 85.0

        return {
            "evaluation_results": final_scores,
            "evaluation_score": weighted_score,
            "evaluation_report": evaluation_report,
            "is_complete": is_complete,
        }

    def _generate_evaluation_report(self, scores: Dict[str, float]) -> str:
        """Generates a summary report of the evaluation."""
        report = "Evaluation Summary:\n\n"
        for criterion, score in scores.items():
            report += f"- {criterion.replace('_', ' ')}: {score:.1f}/100\n"
        
        strengths = [criterion for criterion, score in scores.items() if score >= 85]
        weaknesses = [criterion for criterion, score in scores.items() if score < 75]

        if strengths:
            report += "\n**Strengths:**\n"
            for s in strengths:
                report += f"- Strong performance in {s.replace('_', ' ')}.\n"
        
        if weaknesses:
            report += "\n**Areas for Improvement:**\n"
            for w in weaknesses:
                report += f"- Consider refining the {w.replace('_', ' ')}.\n"
        
        return report
