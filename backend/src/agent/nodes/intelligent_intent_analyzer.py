"""
Intelligent Intent Analyzer Agent - Advanced Clarification System
Analyzes user intent and asks intelligent clarifying questions when needed.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic

from src.agent.base import BaseNode, NodeError
from ...agent.handywriterz_state import HandyWriterzState
from src.prompts.system_prompts import secure_prompt_loader


class IntentClarity(Enum):
    """Intent clarity levels."""
    CRYSTAL_CLEAR = "crystal_clear"      # 90-100% clarity
    MOSTLY_CLEAR = "mostly_clear"        # 75-89% clarity
    PARTIALLY_CLEAR = "partially_clear"  # 50-74% clarity
    UNCLEAR = "unclear"                  # 25-49% clarity
    VERY_UNCLEAR = "very_unclear"        # 0-24% clarity


class QuestionType(Enum):
    """Types of clarifying questions."""
    SCOPE_DEFINITION = "scope_definition"
    REQUIREMENTS_CLARIFICATION = "requirements_clarification"
    ACADEMIC_STANDARDS = "academic_standards"
    FORMAT_PREFERENCES = "format_preferences"
    COMPLEXITY_LEVEL = "complexity_level"
    TIMELINE_CONSTRAINTS = "timeline_constraints"
    RESOURCE_AVAILABILITY = "resource_availability"


@dataclass
class ClarifyingQuestion:
    """A clarifying question with context."""
    question: str
    question_type: QuestionType
    importance: float  # 0-1 scale
    options: Optional[List[str]] = None
    explanation: Optional[str] = None
    required: bool = False


@dataclass
class IntentAnalysisResult:
    """Result of intelligent intent analysis."""
    clarity_level: IntentClarity
    clarity_score: float
    missing_information: List[str]
    clarifying_questions: List[ClarifyingQuestion]
    confidence_score: float
    should_proceed: bool
    recommendations: List[str]
    analysis_details: Dict[str, Any]


class IntelligentIntentAnalyzer(BaseNode):
    """
    Intelligent Intent Analyzer that understands user requirements and asks
    strategic clarifying questions to ensure optimal academic assistance.
    
    Features:
    - Advanced intent clarity assessment
    - Context-aware question generation
    - Academic requirement analysis
    - Strategic clarification workflows
    - Intent confidence scoring
    """
    
    def __init__(self):
        super().__init__(
            name="IntelligentIntentAnalyzer",
            timeout_seconds=90.0,
            max_retries=2
        )
        
        # Initialize Claude for sophisticated analysis
        self._initialize_claude_client()
        
        # Analysis configuration
        self.min_clarity_threshold = 0.75  # Minimum clarity to proceed
        self.max_questions_per_session = 5
        self.question_importance_threshold = 0.6
        
        # Academic requirement checklist
        self.academic_requirements_checklist = {
            "field": {
                "required": True,
                "default_available": False,
                "question_type": QuestionType.SCOPE_DEFINITION
            },
            "writeup_type": {
                "required": True,
                "default_available": False,
                "question_type": QuestionType.REQUIREMENTS_CLARIFICATION
            },
            "academic_level": {
                "required": True,
                "default_available": False,
                "question_type": QuestionType.ACADEMIC_STANDARDS
            },
            "word_count": {
                "required": True,
                "default_available": True,
                "question_type": QuestionType.SCOPE_DEFINITION
            },
            "citation_style": {
                "required": True,
                "default_available": True,
                "question_type": QuestionType.FORMAT_PREFERENCES
            },
            "research_depth": {
                "required": False,
                "default_available": False,
                "question_type": QuestionType.COMPLEXITY_LEVEL
            },
            "timeline": {
                "required": False,
                "default_available": False,
                "question_type": QuestionType.TIMELINE_CONSTRAINTS
            }
        }
    
    def _initialize_claude_client(self):
        """Initialize Claude client for advanced analysis."""
        try:
            self.claude_client = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=0.1,
                max_tokens=4000
            )
            self.logger.info("Claude client initialized for intent analysis")
        except Exception as e:
            self.logger.error(f"Claude client initialization failed: {e}")
            self.claude_client = None
    
    async def execute(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute intelligent intent analysis with strategic clarification.
        """
        start_time = time.time()
        analysis_id = f"intent_analysis_{int(start_time)}"
        
        try:
            self.logger.info("🤔 Intelligent Intent Analyzer: Analyzing user requirements")
            self._broadcast_progress(state, "Analyzing user intent and requirements", 5)
            
            if not self.claude_client:
                raise NodeError("Claude client not available for intent analysis", self.name)
            
            # Phase 1: Extract and sanitize user input
            user_input_analysis = await self._extract_user_input(state)
            self._broadcast_progress(state, "User input extracted and analyzed", 20)
            
            # Phase 2: Assess intent clarity
            clarity_assessment = await self._assess_intent_clarity(state, user_input_analysis)
            self._broadcast_progress(state, "Intent clarity assessed", 40)
            
            # Phase 3: Check academic requirements completeness
            requirements_analysis = await self._analyze_requirements_completeness(state, user_input_analysis)
            self._broadcast_progress(state, "Requirements completeness analyzed", 60)
            
            # Phase 4: Generate strategic clarifying questions
            clarifying_questions = await self._generate_clarifying_questions(state, clarity_assessment, requirements_analysis)
            self._broadcast_progress(state, "Clarifying questions generated", 80)
            
            # Phase 5: Make proceed/clarify decision
            final_decision = await self._make_proceed_decision(state, clarity_assessment, requirements_analysis, clarifying_questions)
            self._broadcast_progress(state, "Intent analysis complete", 95)
            
            # Compile comprehensive analysis result
            analysis_result = IntentAnalysisResult(
                clarity_level=clarity_assessment.get("clarity_level", IntentClarity.PARTIALLY_CLEAR),
                clarity_score=clarity_assessment.get("clarity_score", 0.6),
                missing_information=requirements_analysis.get("missing_requirements", []),
                clarifying_questions=clarifying_questions,
                confidence_score=final_decision.get("confidence_score", 0.7),
                should_proceed=final_decision.get("should_proceed", False),
                recommendations=final_decision.get("recommendations", []),
                analysis_details={
                    "user_input_analysis": user_input_analysis,
                    "clarity_assessment": clarity_assessment,
                    "requirements_analysis": requirements_analysis,
                    "processing_time": time.time() - start_time
                }
            )
            
            # Update state with analysis results
            state.update({
                "intent_analysis_result": asdict(analysis_result),
                "intent_clarity_score": analysis_result.clarity_score,
                "should_proceed": analysis_result.should_proceed,
                "clarifying_questions": [asdict(q) for q in analysis_result.clarifying_questions],
                "intent_analysis_complete": True
            })
            
            self._broadcast_progress(state, "🤔 Intelligent Intent Analysis Complete", 100)
            
            if analysis_result.should_proceed:
                self.logger.info(f"Intent analysis complete - proceeding with {analysis_result.clarity_score:.1%} clarity")
            else:
                self.logger.info(f"Intent analysis complete - clarification needed ({len(analysis_result.clarifying_questions)} questions)")
            
            return {
                "analysis_result": asdict(analysis_result),
                "processing_metrics": {
                    "execution_time": time.time() - start_time,
                    "clarity_score": analysis_result.clarity_score,
                    "questions_generated": len(analysis_result.clarifying_questions),
                    "should_proceed": analysis_result.should_proceed
                }
            }
            
        except Exception as e:
            self.logger.error(f"Intelligent intent analysis failed: {e}")
            self._broadcast_progress(state, f"Intent analysis failed: {str(e)}", error=True)
            raise NodeError(f"Intent analysis execution failed: {e}", self.name)
    
    async def _extract_user_input(self, state: HandyWriterzState) -> Dict[str, Any]:
        """Extract and analyze user input comprehensively."""
        user_messages = state.get("messages", [])
        user_params = state.get("user_params", {})
        uploaded_files = state.get("uploaded_files", [])
        
        # Extract user request
        user_request = ""
        if user_messages:
            for msg in reversed(user_messages):
                if hasattr(msg, 'content') and msg.content.strip():
                    user_request = msg.content
                    break
        
        # Sanitize inputs
        sanitized_request = secure_prompt_loader.security_manager.sanitize_input(user_request)
        sanitized_params = secure_prompt_loader.sanitize_user_params(user_params)
        
        # Analyze request complexity and detail
        request_analysis = {
            "user_request": sanitized_request,
            "request_length": len(sanitized_request),
            "request_complexity": self._assess_request_complexity(sanitized_request),
            "explicit_requirements": self._extract_explicit_requirements(sanitized_request),
            "implicit_indicators": self._extract_implicit_indicators(sanitized_request),
            "user_params": sanitized_params,
            "uploaded_files_count": len(uploaded_files),
            "has_context_files": len(uploaded_files) > 0
        }
        
        return request_analysis
    
    async def _assess_intent_clarity(self, state: HandyWriterzState, user_input_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the clarity of user intent using AI analysis."""
        user_request = user_input_analysis.get("user_request", "")
        user_params = user_input_analysis.get("user_params", {})
        
        # Get secure system prompt
        system_prompt = secure_prompt_loader.get_system_prompt("enhanced_user_intent", user_request)
        
        clarity_prompt = f"""
        TASK: Assess the clarity of this academic writing request.
        
        USER REQUEST: {user_request}
        
        PROVIDED PARAMETERS:
        - Field: {user_params.get('field', 'NOT PROVIDED')}
        - Document Type: {user_params.get('writeup_type', 'NOT PROVIDED')}
        - Word Count: {user_params.get('word_count', 'NOT PROVIDED')}
        - Citation Style: {user_params.get('citation_style', 'NOT PROVIDED')}
        
        CONTEXT ANALYSIS:
        - Request Length: {user_input_analysis.get('request_length', 0)} characters
        - Complexity Level: {user_input_analysis.get('request_complexity', 'unknown')}
        - Has Context Files: {user_input_analysis.get('has_context_files', False)}
        
        ASSESS INTENT CLARITY:
        
        1. CLARITY SCORING (0-100):
           - Request specificity and detail level
           - Academic requirements clarity
           - Scope and objectives definition
           - Success criteria visibility
           
        2. CLARITY LEVEL CLASSIFICATION:
           - crystal_clear (90-100): All requirements clear
           - mostly_clear (75-89): Minor clarification needed
           - partially_clear (50-74): Some important gaps
           - unclear (25-49): Major clarification needed
           - very_unclear (0-24): Extensive clarification required
           
        3. SPECIFIC CLARITY ASSESSMENT:
           - What is clearly stated
           - What is ambiguous or unclear
           - What is completely missing
           - Critical information gaps
           
        4. INTENT CONFIDENCE:
           - Confidence in understanding user needs (0-100)
           - Likelihood of successful completion
           - Risk factors and uncertainties
           
        Return comprehensive clarity assessment as structured JSON.
        """
        
        try:
            messages = [
                HumanMessage(content=system_prompt),
                HumanMessage(content=clarity_prompt)
            ]
            result = await self.claude_client.ainvoke(messages)
            clarity_data = self._parse_structured_response(result.content)
            
            # Extract and validate clarity score
            clarity_score = clarity_data.get("clarity_scoring", 60) / 100.0
            clarity_level = self._determine_clarity_level(clarity_score)
            
            clarity_assessment = {
                "clarity_score": clarity_score,
                "clarity_level": clarity_level,
                "clarity_details": clarity_data,
                "assessment_timestamp": datetime.utcnow().isoformat(),
                "confidence_level": clarity_data.get("intent_confidence", 70) / 100.0
            }
            
            return clarity_assessment
            
        except Exception as e:
            self.logger.error(f"Clarity assessment failed: {e}")
            return {
                "clarity_score": 0.5,
                "clarity_level": IntentClarity.PARTIALLY_CLEAR,
                "assessment_timestamp": datetime.utcnow().isoformat(),
                "confidence_level": 0.6,
                "fallback_used": True
            }
    
    async def _analyze_requirements_completeness(self, state: HandyWriterzState, 
                                               user_input_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze completeness of academic requirements."""
        user_params = user_input_analysis.get("user_params", {})
        user_request = user_input_analysis.get("user_request", "")
        
        missing_requirements = []
        available_requirements = []
        requirement_scores = {}
        
        for req_name, req_config in self.academic_requirements_checklist.items():
            # Check if requirement is provided
            param_value = user_params.get(req_name)
            is_provided = param_value and str(param_value).strip() and param_value != "general"
            
            # Check if it's inferrable from the request
            is_inferrable = self._can_infer_requirement(req_name, user_request)
            
            # Calculate requirement score
            if is_provided:
                requirement_scores[req_name] = 1.0
                available_requirements.append(req_name)
            elif is_inferrable:
                requirement_scores[req_name] = 0.7
                available_requirements.append(req_name)
            elif req_config["default_available"]:
                requirement_scores[req_name] = 0.5
                available_requirements.append(req_name)
            else:
                requirement_scores[req_name] = 0.0
                if req_config["required"]:
                    missing_requirements.append(req_name)
        
        # Calculate overall completeness
        total_score = sum(requirement_scores.values())
        max_possible = len(self.academic_requirements_checklist)
        completeness_score = total_score / max_possible if max_possible > 0 else 0
        
        requirements_analysis = {
            "missing_requirements": missing_requirements,
            "available_requirements": available_requirements,
            "requirement_scores": requirement_scores,
            "completeness_score": completeness_score,
            "critical_missing": [req for req in missing_requirements 
                               if self.academic_requirements_checklist[req]["required"]],
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
        return requirements_analysis
    
    async def _generate_clarifying_questions(self, state: HandyWriterzState,
                                           clarity_assessment: Dict[str, Any],
                                           requirements_analysis: Dict[str, Any]) -> List[ClarifyingQuestion]:
        """Generate strategic clarifying questions based on analysis."""
        questions = []
        
        missing_requirements = requirements_analysis.get("missing_requirements", [])
        clarity_score = clarity_assessment.get("clarity_score", 0.6)
        
        # Generate questions for missing critical requirements
        for req_name in missing_requirements:
            if req_name in self.academic_requirements_checklist:
                req_config = self.academic_requirements_checklist[req_name]
                question = self._create_requirement_question(req_name, req_config)
                if question:
                    questions.append(question)
        
        # Generate questions based on clarity issues
        clarity_details = clarity_assessment.get("clarity_details", {})
        unclear_aspects = clarity_details.get("unclear_aspects", [])
        
        for aspect in unclear_aspects[:3]:  # Limit to top 3 clarity issues
            question = self._create_clarity_question(aspect)
            if question:
                questions.append(question)
        
        # Sort by importance and limit total questions
        questions.sort(key=lambda q: q.importance, reverse=True)
        questions = questions[:self.max_questions_per_session]
        
        # Filter by importance threshold
        questions = [q for q in questions if q.importance >= self.question_importance_threshold]
        
        return questions
    
    async def _make_proceed_decision(self, state: HandyWriterzState,
                                   clarity_assessment: Dict[str, Any],
                                   requirements_analysis: Dict[str, Any],
                                   clarifying_questions: List[ClarifyingQuestion]) -> Dict[str, Any]:
        """Make decision on whether to proceed or ask for clarification."""
        clarity_score = clarity_assessment.get("clarity_score", 0.6)
        completeness_score = requirements_analysis.get("completeness_score", 0.6)
        critical_missing = requirements_analysis.get("critical_missing", [])
        
        # Calculate overall readiness score
        readiness_score = (clarity_score + completeness_score) / 2
        
        # Decision logic
        should_proceed = (
            readiness_score >= self.min_clarity_threshold and
            len(critical_missing) == 0 and
            len(clarifying_questions) <= 2
        )
        
        # Generate recommendations
        recommendations = []
        if not should_proceed:
            if len(critical_missing) > 0:
                recommendations.append("Critical academic requirements need clarification")
            if clarity_score < 0.7:
                recommendations.append("Request details need clarification for optimal assistance")
            if len(clarifying_questions) > 3:
                recommendations.append("Multiple aspects require clarification")
        else:
            recommendations.append("Requirements are sufficiently clear to proceed")
            if readiness_score > 0.9:
                recommendations.append("Excellent clarity - can provide optimal assistance")
        
        decision_result = {
            "should_proceed": should_proceed,
            "readiness_score": readiness_score,
            "confidence_score": min(clarity_score, completeness_score),
            "recommendations": recommendations,
            "decision_factors": {
                "clarity_sufficient": clarity_score >= self.min_clarity_threshold,
                "requirements_complete": len(critical_missing) == 0,
                "questions_manageable": len(clarifying_questions) <= 2
            },
            "decision_timestamp": datetime.utcnow().isoformat()
        }
        
        return decision_result
    
    # Helper methods
    
    def _assess_request_complexity(self, request: str) -> str:
        """Assess complexity of user request."""
        complexity_indicators = [
            len(request.split()) > 50,
            "analyze" in request.lower(),
            "compare" in request.lower(),
            "research" in request.lower(),
            "methodology" in request.lower()
        ]
        
        complexity_score = sum(complexity_indicators)
        
        if complexity_score >= 4:
            return "high"
        elif complexity_score >= 2:
            return "medium"
        else:
            return "low"
    
    def _extract_explicit_requirements(self, request: str) -> List[str]:
        """Extract explicitly stated requirements."""
        explicit_requirements = []
        request_lower = request.lower()
        
        requirement_patterns = {
            "word_count": ["words", "pages", "length"],
            "citation_style": ["apa", "mla", "harvard", "chicago", "citation"],
            "academic_level": ["undergraduate", "graduate", "phd", "masters"],
            "format": ["essay", "research paper", "dissertation", "thesis"]
        }
        
        for req_type, patterns in requirement_patterns.items():
            if any(pattern in request_lower for pattern in patterns):
                explicit_requirements.append(req_type)
        
        return explicit_requirements
    
    def _extract_implicit_indicators(self, request: str) -> List[str]:
        """Extract implicit indicators from request."""
        indicators = []
        request_lower = request.lower()
        
        if any(term in request_lower for term in ["research", "study", "analysis"]):
            indicators.append("research_focus")
        
        if any(term in request_lower for term in ["urgent", "deadline", "asap"]):
            indicators.append("time_sensitive")
        
        if any(term in request_lower for term in ["high quality", "excellent", "top grade"]):
            indicators.append("quality_focused")
        
        return indicators
    
    def _determine_clarity_level(self, clarity_score: float) -> IntentClarity:
        """Determine clarity level from score."""
        if clarity_score >= 0.9:
            return IntentClarity.CRYSTAL_CLEAR
        elif clarity_score >= 0.75:
            return IntentClarity.MOSTLY_CLEAR
        elif clarity_score >= 0.5:
            return IntentClarity.PARTIALLY_CLEAR
        elif clarity_score >= 0.25:
            return IntentClarity.UNCLEAR
        else:
            return IntentClarity.VERY_UNCLEAR
    
    def _can_infer_requirement(self, req_name: str, request: str) -> bool:
        """Check if requirement can be inferred from request."""
        request_lower = request.lower()
        
        inference_patterns = {
            "field": ["psychology", "business", "science", "literature", "history", "medicine"],
            "writeup_type": ["essay", "paper", "thesis", "dissertation", "report", "analysis"],
            "academic_level": ["university", "college", "graduate", "undergraduate", "phd"]
        }
        
        patterns = inference_patterns.get(req_name, [])
        return any(pattern in request_lower for pattern in patterns)
    
    def _create_requirement_question(self, req_name: str, req_config: Dict[str, Any]) -> Optional[ClarifyingQuestion]:
        """Create a question for missing requirement."""
        question_templates = {
            "field": ClarifyingQuestion(
                question="What academic field or subject area is your assignment in?",
                question_type=req_config["question_type"],
                importance=0.9,
                options=["Psychology", "Business", "Science", "Literature", "History", "Medicine", "Other"],
                explanation="This helps me provide field-specific guidance and appropriate academic standards.",
                required=True
            ),
            "writeup_type": ClarifyingQuestion(
                question="What type of academic document do you need help with?",
                question_type=req_config["question_type"],
                importance=0.9,
                options=["Essay", "Research Paper", "Thesis", "Dissertation", "Report", "Analysis", "Other"],
                explanation="Different document types have specific requirements and structures.",
                required=True
            ),
            "academic_level": ClarifyingQuestion(
                question="What is your academic level?",
                question_type=req_config["question_type"],
                importance=0.8,
                options=["High School", "Undergraduate", "Graduate", "PhD", "Professional"],
                explanation="This ensures appropriate complexity and academic standards.",
                required=True
            ),
            "research_depth": ClarifyingQuestion(
                question="How in-depth should the research be?",
                question_type=req_config["question_type"],
                importance=0.6,
                options=["Basic overview", "Moderate depth", "Comprehensive research", "Extensive analysis"],
                explanation="This helps determine the scope and number of sources needed."
            ),
            "timeline": ClarifyingQuestion(
                question="What is your timeline or deadline for this assignment?",
                question_type=req_config["question_type"],
                importance=0.5,
                options=["Within 24 hours", "Within a week", "Within a month", "No rush"],
                explanation="This helps prioritize and plan the assistance appropriately."
            )
        }
        
        return question_templates.get(req_name)
    
    def _create_clarity_question(self, unclear_aspect: str) -> Optional[ClarifyingQuestion]:
        """Create a question to clarify unclear aspects."""
        # This would be implemented based on specific unclear aspects
        # For now, return a generic clarification question
        return ClarifyingQuestion(
            question=f"Could you provide more details about {unclear_aspect}?",
            question_type=QuestionType.REQUIREMENTS_CLARIFICATION,
            importance=0.7,
            explanation="Additional details will help provide better assistance."
        )
    
    def _parse_structured_response(self, content: str) -> Dict[str, Any]:
        """Parse structured AI response with error handling."""
        try:
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            return json.loads(content)
        except json.JSONDecodeError:
            return {
                "clarity_scoring": 60,
                "intent_confidence": 70,
                "unclear_aspects": ["general_clarity"],
                "fallback_used": True
            }