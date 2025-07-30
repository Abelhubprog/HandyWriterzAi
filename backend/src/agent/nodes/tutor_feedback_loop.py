"""Tutor Feedback Loop node for continuous model fine-tuning."""

import time
import hashlib
from typing import Dict, Any, List
from langchain_core.runnables import RunnableConfig

from src.agent.base import BaseNode
from ...agent.handywriterz_state import HandyWriterzState


class TutorFeedbackLoopNode(BaseNode):
    """Processes tutor feedback to continuously improve writing suggestions."""
    
    def __init__(self):
        super().__init__("tutor_feedback_loop", timeout_seconds=30.0, max_retries=2)
    
    async def execute(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Process tutor feedback and update fine-tuning data."""
        try:
            tutor_feedback = state.get("tutor_feedback", {})
            current_draft = state.get("current_draft", "")
            user_params = state.get("user_params", {})
            
            if not tutor_feedback or not current_draft:
                return {"feedback_processed": False}
            
            # Extract learning patterns from feedback
            learning_patterns = self._extract_learning_patterns(tutor_feedback, current_draft, user_params)
            
            # Create fine-tuning examples
            training_examples = await self._create_training_examples(learning_patterns, current_draft, tutor_feedback)
            
            # Store for batch fine-tuning
            await self._store_training_data(training_examples, user_params)
            
            # Update prompt templates based on feedback
            updated_prompts = self._update_prompt_templates(tutor_feedback, user_params)
            
            # Generate improvement suggestions for current session
            immediate_improvements = self._generate_immediate_improvements(tutor_feedback)
            
            self._broadcast_progress(state, f"Processed feedback and created {len(training_examples)} training examples", 100.0)
            
            return {
                "feedback_processed": True,
                "learning_patterns": learning_patterns,
                "training_examples_count": len(training_examples),
                "updated_prompts": updated_prompts,
                "immediate_improvements": immediate_improvements
            }
            
        except Exception as e:
            self.logger.error(f"Tutor feedback processing failed: {e}")
            raise
    
    def _extract_learning_patterns(self, feedback: Dict, draft: str, user_params: Dict) -> Dict[str, Any]:
        """Extract patterns from tutor feedback for model learning."""
        patterns = {
            "writing_issues": [],
            "successful_elements": [],
            "field_specific_guidance": [],
            "common_mistakes": [],
            "improvement_suggestions": []
        }
        
        # Analyze feedback categories
        feedback_categories = feedback.get("categories", {})
        
        # Extract writing issues
        if "grammar" in feedback_categories:
            patterns["writing_issues"].extend(self._extract_grammar_patterns(feedback_categories["grammar"], draft))
        
        if "structure" in feedback_categories:
            patterns["writing_issues"].extend(self._extract_structure_patterns(feedback_categories["structure"], draft))
        
        if "citations" in feedback_categories:
            patterns["writing_issues"].extend(self._extract_citation_patterns(feedback_categories["citations"], draft))
        
        # Extract successful elements
        positive_feedback = feedback.get("positive_feedback", [])
        for item in positive_feedback:
            patterns["successful_elements"].append({
                "element": item.get("element", ""),
                "reason": item.get("reason", ""),
                "context": self._extract_context_around_element(draft, item.get("element", ""))
            })
        
        # Field-specific patterns
        field = user_params.get("field", "general")
        field_feedback = feedback.get("field_specific", {})
        if field_feedback:
            patterns["field_specific_guidance"] = self._extract_field_patterns(field_feedback, field)
        
        # Common mistakes identification
        mistakes = feedback.get("common_mistakes", [])
        for mistake in mistakes:
            patterns["common_mistakes"].append({
                "mistake_type": mistake.get("type", ""),
                "description": mistake.get("description", ""),
                "correction": mistake.get("correction", ""),
                "frequency": mistake.get("frequency", 1)
            })
        
        return patterns
    
    def _extract_grammar_patterns(self, grammar_feedback: Dict, draft: str) -> List[Dict]:
        """Extract grammar-related learning patterns."""
        patterns = []
        
        issues = grammar_feedback.get("issues", [])
        for issue in issues:
            patterns.append({
                "type": "grammar",
                "issue_type": issue.get("type", ""),
                "original_text": issue.get("original", ""),
                "corrected_text": issue.get("corrected", ""),
                "explanation": issue.get("explanation", ""),
                "confidence": issue.get("confidence", 0.8)
            })
        
        return patterns
    
    def _extract_structure_patterns(self, structure_feedback: Dict, draft: str) -> List[Dict]:
        """Extract structure-related learning patterns."""
        patterns = []
        
        issues = structure_feedback.get("issues", [])
        for issue in issues:
            patterns.append({
                "type": "structure",
                "issue_type": issue.get("type", ""),
                "paragraph_number": issue.get("paragraph", 0),
                "current_structure": issue.get("current", ""),
                "suggested_structure": issue.get("suggested", ""),
                "reasoning": issue.get("reasoning", "")
            })
        
        return patterns
    
    def _extract_citation_patterns(self, citation_feedback: Dict, draft: str) -> List[Dict]:
        """Extract citation-related learning patterns."""
        patterns = []
        
        issues = citation_feedback.get("issues", [])
        for issue in issues:
            patterns.append({
                "type": "citation",
                "issue_type": issue.get("type", ""),
                "current_citation": issue.get("current", ""),
                "corrected_citation": issue.get("corrected", ""),
                "style_guide": issue.get("style", "harvard"),
                "context": issue.get("context", "")
            })
        
        return patterns
    
    def _extract_context_around_element(self, draft: str, element: str) -> str:
        """Extract context around a successful element."""
        if not element or element not in draft:
            return ""
        
        # Find the sentence containing the element
        sentences = draft.split('.')
        for sentence in sentences:
            if element in sentence:
                return sentence.strip() + "."
        
        return ""
    
    def _extract_field_patterns(self, field_feedback: Dict, field: str) -> List[Dict]:
        """Extract field-specific learning patterns."""
        patterns = []
        
        # Field-specific terminology
        terminology = field_feedback.get("terminology", [])
        for term in terminology:
            patterns.append({
                "type": "terminology",
                "field": field,
                "term": term.get("term", ""),
                "usage": term.get("correct_usage", ""),
                "common_error": term.get("common_error", "")
            })
        
        # Field-specific writing style
        style_guidance = field_feedback.get("style", {})
        if style_guidance:
            patterns.append({
                "type": "style",
                "field": field,
                "guidance": style_guidance.get("guidance", ""),
                "examples": style_guidance.get("examples", [])
            })
        
        return patterns
    
    async def _create_training_examples(self, patterns: Dict, draft: str, feedback: Dict) -> List[Dict]:
        """Create training examples for model fine-tuning."""
        training_examples = []
        
        # Create examples from writing issues
        for issue in patterns.get("writing_issues", []):
            if issue.get("original_text") and issue.get("corrected_text"):
                training_examples.append({
                    "input": {
                        "text": issue["original_text"],
                        "context": "revise for " + issue.get("issue_type", "improvement"),
                        "field": feedback.get("field", "general")
                    },
                    "output": issue["corrected_text"],
                    "explanation": issue.get("explanation", ""),
                    "confidence": issue.get("confidence", 0.8),
                    "pattern_type": issue.get("type", "unknown")
                })
        
        # Create examples from successful elements
        for element in patterns.get("successful_elements", []):
            training_examples.append({
                "input": {
                    "context": "write similar to this successful example",
                    "example": element.get("context", ""),
                    "field": feedback.get("field", "general")
                },
                "output": element.get("element", ""),
                "explanation": element.get("reason", ""),
                "confidence": 0.9,
                "pattern_type": "positive_example"
            })
        
        # Create examples from field-specific patterns
        for pattern in patterns.get("field_specific_guidance", []):
            if pattern.get("type") == "terminology":
                training_examples.append({
                    "input": {
                        "text": pattern.get("common_error", ""),
                        "context": f"correct {pattern.get('field')} terminology",
                        "field": pattern.get("field", "general")
                    },
                    "output": pattern.get("usage", ""),
                    "explanation": f"Correct {pattern.get('field')} terminology usage",
                    "confidence": 0.85,
                    "pattern_type": "terminology"
                })
        
        return training_examples
    
    async def _store_training_data(self, training_examples: List[Dict], user_params: Dict):
        """Store training examples for batch fine-tuning."""
        # TODO(fill-secret): Implement database storage
        # For now, log the training data
        
        field = user_params.get("field", "general")
        user_id = user_params.get("user_id", "unknown")
        
        training_batch = {
            "user_id": user_id,
            "field": field,
            "timestamp": time.time(),
            "examples": training_examples,
            "batch_id": hashlib.md5(f"{user_id}{time.time()}".encode()).hexdigest()[:8]
        }
        
        self.logger.info(f"Storing training batch {training_batch['batch_id']} with {len(training_examples)} examples")
        
        # In production, this would be:
        # await database.store_training_batch(training_batch)
        # await ml_pipeline.queue_for_fine_tuning(training_batch['batch_id'])
    
    def _update_prompt_templates(self, feedback: Dict, user_params: Dict) -> Dict[str, str]:
        """Update prompt templates based on feedback patterns."""
        field = user_params.get("field", "general")
        updated_prompts = {}
        
        # Base writing prompt updates
        writing_improvements = []
        if feedback.get("grammar", {}).get("issues"):
            writing_improvements.append("Pay special attention to grammar and sentence structure.")
        
        if feedback.get("structure", {}).get("issues"):
            writing_improvements.append("Focus on clear paragraph structure and logical flow.")
        
        if feedback.get("citations", {}).get("issues"):
            writing_improvements.append("Ensure proper citation formatting and integration.")
        
        # Field-specific prompt adjustments
        field_guidance = feedback.get("field_specific", {})
        if field_guidance:
            terminology_notes = field_guidance.get("terminology", [])
            if terminology_notes:
                writing_improvements.append(f"Use appropriate {field} terminology and concepts.")
        
        # Create updated writer prompt
        if writing_improvements:
            updated_prompts["writer_prompt"] = self._create_enhanced_writer_prompt(
                field, writing_improvements
            )
        
        # Create updated evaluator prompt
        evaluation_focus = self._extract_evaluation_focus(feedback)
        if evaluation_focus:
            updated_prompts["evaluator_prompt"] = self._create_enhanced_evaluator_prompt(
                field, evaluation_focus
            )
        
        return updated_prompts
    
    def _create_enhanced_writer_prompt(self, field: str, improvements: List[str]) -> str:
        """Create enhanced writer prompt based on feedback."""
        base_prompt = f"""You are an expert academic writer specializing in {field}. 
        Based on recent tutor feedback, please pay special attention to the following:
        
        """
        
        for i, improvement in enumerate(improvements, 1):
            base_prompt += f"{i}. {improvement}\n"
        
        base_prompt += f"""
        
        Write content that demonstrates mastery of {field} concepts while addressing 
        these specific improvement areas. Ensure your writing is clear, well-structured, 
        and follows academic conventions.
        """
        
        return base_prompt
    
    def _create_enhanced_evaluator_prompt(self, field: str, focus_areas: List[str]) -> str:
        """Create enhanced evaluator prompt based on feedback."""
        base_prompt = f"""You are evaluating academic writing in {field}. 
        Based on recent tutor feedback patterns, focus your evaluation on:
        
        """
        
        for i, area in enumerate(focus_areas, 1):
            base_prompt += f"{i}. {area}\n"
        
        base_prompt += """
        
        Provide detailed feedback in these areas while maintaining overall quality assessment.
        """
        
        return base_prompt
    
    def _extract_evaluation_focus(self, feedback: Dict) -> List[str]:
        """Extract areas that need focused evaluation."""
        focus_areas = []
        
        # Check which areas had the most issues
        categories = feedback.get("categories", {})
        
        for category, data in categories.items():
            if isinstance(data, dict) and data.get("issues"):
                issue_count = len(data["issues"])
                if issue_count > 0:
                    focus_areas.append(f"{category.title()} quality and accuracy")
        
        # Add field-specific focus if needed
        if feedback.get("field_specific"):
            focus_areas.append("Field-specific terminology and concepts")
        
        return focus_areas
    
    def _generate_immediate_improvements(self, feedback: Dict) -> List[Dict[str, Any]]:
        """Generate immediate improvement suggestions for current session."""
        improvements = []
        
        # High-priority improvements from feedback
        categories = feedback.get("categories", {})
        
        for category, data in categories.items():
            if isinstance(data, dict) and data.get("issues"):
                for issue in data["issues"][:3]:  # Top 3 issues per category
                    improvements.append({
                        "category": category,
                        "type": issue.get("type", ""),
                        "description": issue.get("explanation", ""),
                        "priority": self._calculate_priority(issue),
                        "suggested_action": self._suggest_action(issue)
                    })
        
        # Sort by priority
        improvements.sort(key=lambda x: x["priority"], reverse=True)
        
        return improvements[:10]  # Top 10 improvements
    
    def _calculate_priority(self, issue: Dict) -> float:
        """Calculate priority score for an issue."""
        base_priority = 0.5
        
        # Boost priority based on issue type
        high_priority_types = ["grammar", "citation", "structure"]
        if issue.get("type") in high_priority_types:
            base_priority += 0.3
        
        # Boost priority based on confidence
        confidence = issue.get("confidence", 0.5)
        base_priority += confidence * 0.2
        
        return min(1.0, base_priority)
    
    def _suggest_action(self, issue: Dict) -> str:
        """Suggest specific action for addressing an issue."""
        issue_type = issue.get("type", "")
        
        actions = {
            "grammar": "Review sentence structure and verb tenses",
            "citation": "Check citation format against style guide",
            "structure": "Reorganize paragraphs for better flow",
            "terminology": "Verify field-specific term usage",
            "clarity": "Simplify complex sentences for better readability"
        }
        
        return actions.get(issue_type, "Review and revise based on feedback")