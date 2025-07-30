"""Main LangGraph orchestration for HandyWriterz academic writing workflow."""

import os
from typing import Dict, Any, List

from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from .handywriterz_state import HandyWriterzState
from .nodes.user_intent import UserIntentNode
from .nodes.planner import PlannerNode
from .nodes.writer import revolutionary_writer_agent_node as WriterNode
from .nodes.memory_writer import MemoryWriter as MemoryWriterNode
from .nodes.memory_retriever import MemoryRetrieverNode

# Revolutionary new agents
from .nodes.master_orchestrator import MasterOrchestratorAgent
from .nodes.enhanced_user_intent import EnhancedUserIntentAgent

# Revolutionary sophisticated agents
from .nodes.evaluator import EvaluatorNode
from .nodes.turnitin_advanced import revolutionary_turnitin_node
from .nodes.formatter_advanced import revolutionary_formatter_node
from .nodes.fail_handler_advanced import revolutionary_fail_handler_node

# Revolutionary swarm intelligence agents
from .nodes.swarm_intelligence_coordinator import swarm_intelligence_coordinator_node
from .nodes.emergent_intelligence_engine import emergent_intelligence_engine_node

# EvidenceGuard nodes
from .nodes.search_crossref import SearchCrossRef
from .nodes.search_pmc import SearchPMC
from .nodes.search_ss import SearchSS
from .nodes.source_verifier import SourceVerifier
from .nodes.citation_audit import CitationAudit
from .nodes.source_filter import SourceFilterNode
from .nodes.source_fallback_controller import SourceFallbackController

# Production-ready AI search agents
from .nodes.search_gemini import GeminiSearchAgent
from .nodes.search_perplexity import PerplexitySearchAgent
from .nodes.search_o3 import O3SearchAgent
from .nodes.search_claude import ClaudeSearchAgent
# Note: Deepseek, Qwen, and Grok search agents are temporarily disabled
# Uncomment these imports when the agents are ready:
# from .nodes.search_deepseek import DeepseekSearchAgent
# from .nodes.search_qwen import QwenSearchAgent  
# from .nodes.search_grok import GrokSearchAgent
from .nodes.search_openai import OpenAISearchAgent
from .nodes.search_github import GitHubSearchAgent
from src.tools.github_tools import GitHubIssuesTool
from .nodes.aggregator import AggregatorNode
from .nodes.rag_summarizer import RAGSummarizerNode
from .nodes.search_scholar import ScholarSearchAgent
from .nodes.legislation_scraper import LegislationScraperAgent
from .nodes.prisma_filter import PRISMAFilterNode
from .nodes.synthesis import SynthesisNode
from .nodes.methodology_writer import MethodologyWriterNode
from src.tools.casp_appraisal_tool import CASPAppraisalTool
from src.tools.mermaid_diagram_tool import MermaidDiagramTool
from src.tools.gibbs_framework_tool import GibbsFrameworkTool
from src.tools.action_plan_template_tool import ActionPlanTemplateTool
from src.tools.case_study_framework_tool import CaseStudyFrameworkTool
from src.tools.cost_model_tool import CostModelTool

# Intelligent intent analysis
from .nodes.intelligent_intent_analyzer import IntelligentIntentAnalyzer
from src.config.model_config import get_model_config

load_dotenv()

# Validate required environment variables (disabled for demo startup)
required_env_vars = [
    "GEMINI_API_KEY",
    "PERPLEXITY_API_KEY", 
    "OPENAI_API_KEY",
    "DATABASE_URL",
    "REDIS_URL",
]

# Commented out for demo - agents will handle missing keys gracefully
# for var in required_env_vars:
#     if not os.getenv(var):
#         raise ValueError(f"Required environment variable {var} is not set")


class HandyWriterzOrchestrator:
    """Main orchestrator for the HandyWriterz academic writing workflow."""
    
    def __init__(self):
        # Revolutionary orchestration agents
        self.master_orchestrator = MasterOrchestratorAgent()
        self.enhanced_user_intent = EnhancedUserIntentAgent()
        
        # Existing workflow agents
        self.user_intent_node = UserIntentNode()
        self.planner_node = PlannerNode()
        self.writer_node = WriterNode()
        self.memory_writer_node = MemoryWriterNode()
        self.memory_retriever_node = MemoryRetrieverNode()
        
        # Revolutionary sophisticated agents
        self.evaluator_node = EvaluatorNode("evaluator")
        self.turnitin_loop_node = revolutionary_turnitin_node
        self.formatter_node = revolutionary_formatter_node
        self.fail_handler_node = revolutionary_fail_handler_node
        
        # Revolutionary swarm intelligence agents
        self.swarm_coordinator_node = swarm_intelligence_coordinator_node
        self.emergent_intelligence_node = emergent_intelligence_engine_node
        
        # EvidenceGuard agents
        self.search_crossref_node = SearchCrossRef()
        self.search_pmc_node = SearchPMC()
        self.search_ss_node = SearchSS()
        self.source_verifier_node = SourceVerifier()
        self.citation_audit_node = CitationAudit()
        self.source_filter_node = SourceFilterNode()
        self.source_fallback_controller_node = SourceFallbackController()
        
        # Production-ready AI search agents
        self.search_agents = {
            "gemini": GeminiSearchAgent(),
            "perplexity": PerplexitySearchAgent(),
            "o3": O3SearchAgent(),
            "claude": ClaudeSearchAgent(),
            "openai": OpenAISearchAgent(),
            "github": GitHubSearchAgent(),
        }
        
        # Dynamically initialize search nodes based on config
        search_model_config = get_model_config("search")
        self.enabled_search_agents = {}
        for model_name in search_model_config.values():
            if isinstance(model_name, str) and model_name in self.search_agents:
                self.enabled_search_agents[model_name] = self.search_agents[model_name]
        
        # Intelligent intent analyzer
        self.intelligent_intent_analyzer = IntelligentIntentAnalyzer()
        self.aggregator_node = AggregatorNode()
        self.rag_summarizer_node = RAGSummarizerNode()
        self.scholar_search_node = ScholarSearchAgent()
        self.legislation_scraper_node = LegislationScraperAgent()
        self.prisma_filter_node = PRISMAFilterNode()
        self.synthesis_node = SynthesisNode()
        self.methodology_writer_node = MethodologyWriterNode()

        # Tools
        self.github_issues_tool = GitHubIssuesTool()
        self.casp_appraisal_tool = CASPAppraisalTool()
        self.mermaid_diagram_tool = MermaidDiagramTool()
        self.gibbs_framework_tool = GibbsFrameworkTool()
        self.action_plan_template_tool = ActionPlanTemplateTool()
        self.case_study_framework_tool = CaseStudyFrameworkTool()
        self.cost_model_tool = CostModelTool()
    
    def create_graph(self) -> StateGraph:
        """Create the LangGraph state graph for the workflow."""
        
        # Create the graph with our state schema
        builder = StateGraph(HandyWriterzState)
        
        # Add revolutionary orchestration nodes
        builder.add_node("memory_retriever", self._execute_memory_retriever)
        builder.add_node("master_orchestrator", self._execute_master_orchestrator)
        builder.add_node("enhanced_user_intent", self._execute_enhanced_user_intent)
        
        # Add existing workflow nodes
        builder.add_node("user_intent", self._execute_user_intent)
        builder.add_node("planner", self._execute_planner)
        
        # Add EvidenceGuard search nodes
        builder.add_node("search_crossref", self._execute_search_crossref)
        builder.add_node("search_pmc", self._execute_search_pmc)
        builder.add_node("search_ss", self._execute_search_ss)
        builder.add_node("source_verifier", self._execute_source_verifier)
        builder.add_node("citation_audit", self._execute_citation_audit)
        builder.add_node("source_fallback_controller", self._execute_source_fallback_controller)
        
        # Add production-ready AI search nodes
        for agent_name, agent_instance in self.enabled_search_agents.items():
            builder.add_node(f"search_{agent_name}", self._create_search_execution_method(agent_instance, agent_name))
        builder.add_node("fetch_github_issues", self._fetch_github_issues)
        builder.add_node("aggregator", self._execute_aggregator)
        builder.add_node("rag_summarizer", self._execute_rag_summarizer)
        builder.add_node("scholar_search", self._execute_scholar_search)
        builder.add_node("legislation_scraper", self._execute_legislation_scraper)
        builder.add_node("prisma_filter", self._execute_prisma_filter)
        builder.add_node("casp_appraisal", self._execute_casp_appraisal)
        builder.add_node("synthesis", self._execute_synthesis)
        builder.add_node("methodology_writer", self._execute_methodology_writer)
        builder.add_node("generate_prisma_diagram", self._execute_generate_prisma_diagram)
        builder.add_node("execute_parallel_searches", self._execute_parallel_searches)
        
        # Add intelligent intent analyzer
        builder.add_node("intelligent_intent_analyzer", self._execute_intelligent_intent_analyzer)
        
        # Add revolutionary sophisticated agents
        builder.add_node("source_filter", self._execute_source_filter)
        builder.add_node("writer", self._execute_writer)
        builder.add_node("evaluator", self._execute_evaluator)
        builder.add_node("turnitin_advanced", self._execute_turnitin_loop)
        builder.add_node("formatter_advanced", self._execute_formatter)
        builder.add_node("memory_writer", self._execute_memory_writer)
        builder.add_node("fail_handler_advanced", self._execute_fail_handler)
        
        # Add revolutionary swarm intelligence agents
        builder.add_node("swarm_coordinator", self._execute_swarm_coordinator)
        builder.add_node("emergent_intelligence", self._execute_emergent_intelligence)
        
        # Define the workflow edges
        self._add_workflow_edges(builder)
        
        return builder.compile(name="handywriterz-academic-writing-agent")
    
    def _add_workflow_edges(self, builder: StateGraph):
        """Add edges to define the revolutionary workflow."""
        
        # 🎭 START WITH MEMORY RETRIEVAL
        builder.add_edge(START, "memory_retriever")
        
        # After retrieving memory, proceed to the planner
        builder.add_edge("memory_retriever", "planner")

        # The planner decides which sub-graph to execute
        builder.add_conditional_edges(
            "planner",
            self._route_to_pipeline,
            {
                "dissertation_pipeline": "scholar_search",
                "reflection_pipeline": "privacy_manager", # Placeholder
                "case_study_pipeline": "fetch_case_data", # Placeholder
                "technical_report_pipeline": "search_github", # Placeholder
                "comparative_essay_pipeline": "scholar_search", # Placeholder
                "default_pipeline": "master_orchestrator"
            }
        )

        # Default pipeline: Master Orchestrator routes to Enhanced User Intent or User Intent
        builder.add_conditional_edges(
            "master_orchestrator",
            self._route_from_orchestrator,
            {
                "enhanced_user_intent": "enhanced_user_intent",
                "user_intent": "user_intent"
            }
        )

        # Enhanced User Intent Analyzer decides whether to proceed or ask for clarification
        builder.add_conditional_edges(
            "enhanced_user_intent",
            self._route_after_intent_analysis,
            {
                "proceed_to_search": "execute_parallel_searches", # Trigger parallel search
                "clarification_needed": END
            }
        )

        # User Intent (legacy) also proceeds to parallel search
        builder.add_edge("user_intent", "execute_parallel_searches")

        # All parallel search agents join into aggregator
        builder.add_edge("execute_parallel_searches", "aggregator") # This implicitly handles the fan-out and join
        builder.add_edge("search_crossref", "aggregator")
        builder.add_edge("search_pmc", "aggregator")
        builder.add_edge("search_ss", "aggregator")
        for agent_name in self.enabled_search_agents:
            builder.add_edge(f"search_{agent_name}", "aggregator")

        # Aggregator to RAG Summarizer
        builder.add_edge("aggregator", "rag_summarizer")

        # RAG Summarizer to Source Verifier
        builder.add_edge("rag_summarizer", "source_verifier")

        # Source Verifier to Source Filter or Fallback
        builder.add_conditional_edges(
            "source_verifier",
            self._route_after_source_verifier,
            {
                "source_filter": "source_filter",
                "source_fallback_controller": "source_fallback_controller"
            }
        )

        # Source Fallback Controller routes back to search or fail
        builder.add_conditional_edges(
            "source_fallback_controller",
            self._route_from_fail_handler, # Re-using fail handler routing for now
            {"search_crossref": "search_crossref", "end": "fail_handler_advanced"} # Route back to search or fail
        )

        # Source Filter to Writer or Swarm Coordinator
        builder.add_conditional_edges(
            "source_filter",
            self._route_after_source_filter,
            {
                "writer": "writer",
                "swarm_coordinator": "swarm_coordinator"
            }
        )

        # Swarm Coordinator to Emergent Intelligence
        builder.add_edge("swarm_coordinator", "emergent_intelligence")

        # Emergent Intelligence to Writer
        builder.add_edge("emergent_intelligence", "writer")

        # Writer to Evaluator
        builder.add_edge("writer", "evaluator")

        # Evaluator to Turnitin or Fail Handler
        builder.add_conditional_edges(
            "evaluator",
            self._route_after_evaluation,
            {
                "turnitin_advanced": "turnitin_advanced",
                "fail_handler_advanced": "fail_handler_advanced"
            }
        )

        # Turnitin to Formatter, Writer (for revision), or Fail Handler
        builder.add_conditional_edges(
            "turnitin_advanced",
            self._route_after_turnitin,
            {
                "formatter_advanced": "formatter_advanced",
                "writer": "writer", # For revision
                "fail_handler_advanced": "fail_handler_advanced"
            }
        )

        # Citation Audit to Writer (for revision) or Formatter
        builder.add_conditional_edges(
            "citation_audit",
            self._route_after_citation_audit,
            {
                "revision_needed": "writer", # Loop back to writer for revision
                "proceed": "formatter_advanced" # Proceed to formatting
            }
        )

        # Formatter to Memory Writer
        builder.add_edge("formatter_advanced", "memory_writer")
        
        # Memory Writer to End
        builder.add_edge("memory_writer", END)
        
        # Fail handler routes back to appropriate recovery or END
        builder.add_conditional_edges(
            "fail_handler_advanced",
            self._route_from_fail_handler,
            {"writer": "writer", "search_crossref": "search_crossref", "swarm_coordinator": "swarm_coordinator", "end": END}
        )

        # Build the dissertation pipeline
        self._create_dissertation_pipeline(builder)

        # Build placeholder pipelines
        self._create_reflection_pipeline(builder)
        self._create_case_study_pipeline(builder)
        self._create_technical_report_pipeline(builder)
        self._create_comparative_essay_pipeline(builder)
    
    def _route_to_pipeline(self, state: HandyWriterzState) -> str:
        """Routes to the correct pipeline based on the planner's output."""
        task_type = state.get("task_type", "default")
        if "dissertation" in task_type:
            return "dissertation_pipeline"
        elif "reflection" in task_type:
            return "reflection_pipeline"
        elif "case study" in task_type:
            return "case_study_pipeline"
        elif "technical report" in task_type:
            return "technical_report_pipeline"
        elif "comparative essay" in task_type:
            return "comparative_essay_pipeline"
        return "default_pipeline"

    def _create_dissertation_pipeline(self, builder: StateGraph):
        """Creates the sub-graph for the dissertation workflow."""
        builder.add_edge("scholar_search", "legislation_scraper")
        builder.add_edge("legislation_scraper", "prisma_filter")
        builder.add_edge("prisma_filter", "casp_appraisal")
        builder.add_edge("casp_appraisal", "synthesis")
        builder.add_edge("synthesis", "methodology_writer")
        builder.add_edge("methodology_writer", "generate_prisma_diagram")
        builder.add_edge("generate_prisma_diagram", "formatter_advanced")

    def _create_reflection_pipeline(self, builder: StateGraph):
        """Creates the sub-graph for the reflection workflow."""
        builder.add_node("privacy_manager", self._execute_placeholder) # Still a placeholder for now
        builder.add_edge("privacy_manager", "user_intent") # Re-evaluate intent for reflection
        builder.add_edge("user_intent", "writer") # Write the reflection
        builder.add_edge("writer", "evaluator") # Evaluate the reflection
        builder.add_edge("evaluator", "formatter_advanced") # Format the reflection

    def _create_case_study_pipeline(self, builder: StateGraph):
        """Creates the sub-graph for the case study workflow."""
        builder.add_node("fetch_case_data", self._execute_placeholder) # Placeholder for data fetching
        builder.add_edge("fetch_case_data", "aggregator") # Aggregate case data
        builder.add_edge("aggregator", "rag_summarizer") # Summarize case data
        builder.add_edge("rag_summarizer", "writer") # Write the case study
        builder.add_edge("writer", "evaluator") # Evaluate the case study
        builder.add_edge("evaluator", "formatter_advanced") # Format the case study

    def _create_technical_report_pipeline(self, builder: StateGraph):
        """Creates the sub-graph for the technical report workflow."""
        builder.add_edge("search_github", "aggregator") # Search GitHub for relevant info
        builder.add_edge("aggregator", "rag_summarizer") # Summarize search results
        builder.add_edge("rag_summarizer", "writer") # Write the technical report
        builder.add_edge("writer", "evaluator") # Evaluate the report
        builder.add_edge("evaluator", "formatter_advanced") # Format the report

    def _create_comparative_essay_pipeline(self, builder: StateGraph):
        """Creates the sub-graph for the comparative essay workflow."""
        builder.add_edge("scholar_search", "aggregator") # Search for academic sources
        builder.add_edge("aggregator", "rag_summarizer") # Summarize sources
        builder.add_edge("rag_summarizer", "synthesis") # Synthesize information for comparison
        builder.add_edge("synthesis", "writer") # Write the comparative essay
        builder.add_edge("writer", "evaluator") # Evaluate the essay
        builder.add_edge("evaluator", "formatter_advanced") # Format the essay

    async def _execute_placeholder(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """A placeholder node for unimplemented pipelines."""
        return {"status": "placeholder"}
    
    # Revolutionary Node execution methods
    async def _execute_master_orchestrator(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute revolutionary Master Orchestrator agent."""
        try:
            result = await self.master_orchestrator(state, config)
            return {**result, "current_node": "master_orchestrator"}
        except Exception as e:
            return await self._handle_node_error(state, "master_orchestrator", e)
    
    async def _execute_enhanced_user_intent(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute revolutionary Enhanced User Intent agent."""
        try:
            result = await self.enhanced_user_intent(state, config)
            return {**result, "current_node": "enhanced_user_intent"}
        except Exception as e:
            return await self._handle_node_error(state, "enhanced_user_intent", e)

    async def _execute_memory_retriever(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute memory retriever."""
        try:
            result = await self.memory_retriever_node.execute(state, config)
            return {**result, "current_node": "memory_retriever"}
        except Exception as e:
            return await self._handle_node_error(state, "memory_retriever", e)
    
    # Legacy Node execution methods
    async def _execute_user_intent(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute user intent processing."""
        try:
            result = await self.user_intent_node(state, config)
            return {**result, "current_node": "user_intent"}
        except Exception as e:
            return await self._handle_node_error(state, "user_intent", e)
    
    async def _execute_planner(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute planning."""
        try:
            result = await self.planner_node(state, config)
            return {**result, "current_node": "planner"}
        except Exception as e:
            return await self._handle_node_error(state, "planner", e)

    # EvidenceGuard Node execution methods
    async def _execute_search_crossref(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute CrossRef search."""
        try:
            result = await self.search_crossref_node(state, config)
            return {**result, "current_node": "search_crossref"}
        except Exception as e:
            return await self._handle_node_error(state, "search_crossref", e)

    async def _execute_search_pmc(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute PubMed Central search."""
        try:
            result = await self.search_pmc_node(state, config)
            return {**result, "current_node": "search_pmc"}
        except Exception as e:
            return await self._handle_node_error(state, "search_pmc", e)

    async def _execute_search_ss(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute Semantic Scholar search."""
        try:
            result = await self.search_ss_node(state, config)
            return {**result, "current_node": "search_ss"}
        except Exception as e:
            return await self._handle_node_error(state, "search_ss", e)

    async def _execute_source_verifier(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute source verifier."""
        try:
            result = await self.source_verifier_node(state, config)
            return {**result, "current_node": "source_verifier"}
        except Exception as e:
            return await self._handle_node_error(state, "source_verifier", e)

    async def _execute_citation_audit(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute citation audit."""
        try:
            result = await self.citation_audit_node(state, config)
            return {**result, "current_node": "citation_audit"}
        except Exception as e:
            return await self._handle_node_error(state, "citation_audit", e)

    async def _execute_source_fallback_controller(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute source fallback controller."""
        try:
            result = await self.source_fallback_controller_node(state, config)
            return {**result, "current_node": "source_fallback_controller"}
        except Exception as e:
            return await self._handle_node_error(state, "source_fallback_controller", e)

    # Production-ready AI Search Agent execution methods
    async def _execute_search_gemini(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute Gemini AI search with advanced knowledge synthesis."""
        try:
            result = await self.gemini_search_node.execute(state, config)
            return {**result, "current_node": "search_gemini"}
        except Exception as e:
            return await self._handle_node_error(state, "search_gemini", e)

    async def _execute_search_perplexity(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute Perplexity real-time search with source validation."""
        try:
            result = await self.perplexity_search_node.execute(state, config)
            return {**result, "current_node": "search_perplexity"}
        except Exception as e:
            return await self._handle_node_error(state, "search_perplexity", e)

    async def _execute_search_o3(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute O3 advanced reasoning search with hypothesis generation."""
        try:
            result = await self.o3_search_node.execute(state, config)
            return {**result, "current_node": "search_o3"}
        except Exception as e:
            return await self._handle_node_error(state, "search_o3", e)

    async def _execute_intelligent_intent_analyzer(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute intelligent intent analysis with clarification handling."""
        try:
            result = await self.intelligent_intent_analyzer.execute(state, config)
            return {**result, "current_node": "intelligent_intent_analyzer"}
        except Exception as e:
            return await self._handle_node_error(state, "intelligent_intent_analyzer", e)

    async def _execute_search_claude(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute Claude search."""
        try:
            result = await self.claude_search_node.execute(state, config)
            return {**result, "current_node": "search_claude"}
        except Exception as e:
            return await self._handle_node_error(state, "search_claude", e)

    # Note: Deepseek, Qwen, and Grok search agents are temporarily disabled
    # Uncomment and add proper imports if these agents are needed

    async def _execute_search_openai(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute OpenAI search."""
        try:
            result = await self.openai_search_node.execute(state, config)
            return {**result, "current_node": "search_openai"}
        except Exception as e:
            return await self._handle_node_error(state, "search_openai", e)

    async def _execute_search_github(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute GitHub search."""
        try:
            result = await self.github_search_node.execute(state, config)
            return {**result, "current_node": "search_github"}
        except Exception as e:
            return await self._handle_node_error(state, "search_github", e)

    async def _fetch_github_issues(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Fetch GitHub issues for each repository."""
        repos = state.get("github_repos", [])
        all_issues = []
        for repo in repos:
            issues = self.github_issues_tool.get_open_issues(repo["full_name"])
            all_issues.extend(issues)
        return {"github_issues": all_issues}

    async def _execute_aggregator(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute the aggregator node."""
        try:
            result = await self.aggregator_node.execute(state, config)
            return {**result, "current_node": "aggregator"}
        except Exception as e:
            return await self._handle_node_error(state, "aggregator", e)

    async def _execute_rag_summarizer(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute the RAG summarizer node."""
        try:
            result = await self.rag_summarizer_node.execute(state, config)
            return {**result, "current_node": "rag_summarizer"}
        except Exception as e:
            return await self._handle_node_error(state, "rag_summarizer", e)

    async def _execute_scholar_search(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute the scholar search node."""
        try:
            result = await self.scholar_search_node.execute(state, config)
            return {**result, "current_node": "scholar_search"}
        except Exception as e:
            return await self._handle_node_error(state, "scholar_search", e)

    async def _execute_legislation_scraper(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute the legislation scraper node."""
        try:
            result = await self.legislation_scraper_node.execute(state, config)
            return {**result, "current_node": "legislation_scraper"}
        except Exception as e:
            return await self._handle_node_error(state, "legislation_scraper", e)

    async def _execute_prisma_filter(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute the PRISMA filter node."""
        try:
            result = await self.prisma_filter_node.execute(state, config)
            return {**result, "current_node": "prisma_filter"}
        except Exception as e:
            return await self._handle_node_error(state, "prisma_filter", e)

    async def _execute_casp_appraisal(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute the CASP appraisal tool."""
        studies = state.get("filtered_studies", [])
        appraisal_table = self.casp_appraisal_tool.appraise_studies(studies)
        return {"casp_appraisal_table": appraisal_table.to_dict("records")}

    async def _execute_synthesis(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute the synthesis node."""
        try:
            result = await self.synthesis_node.execute(state, config)
            return {**result, "current_node": "synthesis"}
        except Exception as e:
            return await self._handle_node_error(state, "synthesis", e)

    async def _execute_methodology_writer(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute the methodology writer node."""
        try:
            result = await self.methodology_writer_node.execute(state, config)
            return {**result, "current_node": "methodology_writer"}
        except Exception as e:
            return await self._handle_node_error(state, "methodology_writer", e)

    async def _execute_generate_prisma_diagram(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute the generate PRISMA diagram tool."""
        prisma_counts = state.get("prisma_counts", {})
        prisma_diagram = self.mermaid_diagram_tool.generate_prisma_diagram(prisma_counts)
        return {"prisma_diagram": prisma_diagram}

    async def _execute_parallel_searches(self, state: HandyWriterzState, config: RunnableConfig) -> List[Send]:
        """Execute all enabled AI search agents in parallel."""
        return self._route_to_ai_search_agents(state)

    async def _execute_source_filter(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute source filtering."""
        try:
            result = await self.source_filter_node(state, config)
            return {**result, "current_node": "source_filter"}
        except Exception as e:
            return await self._handle_node_error(state, "source_filter", e)
    
    async def _execute_writer(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute writing."""
        try:
            result = await self.writer_node(state, config)
            return {**result, "current_node": "writer"}
        except Exception as e:
            return await self._handle_node_error(state, "writer", e)
    
    async def _execute_memory_writer(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute memory writer for user fingerprints."""
        try:
            result = await self.memory_writer_node(state, config)
            return {**result, "current_node": "memory_writer", "workflow_status": "completed"}
        except Exception as e:
            return await self._handle_node_error(state, "memory_writer", e)
    
    # Revolutionary sophisticated agent execution methods
    async def _execute_evaluator(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute revolutionary multi-model evaluator."""
        try:
            result = await self.evaluator_node(state, config)
            return {**result, "current_node": "evaluator_advanced"}
        except Exception as e:
            return await self._handle_node_error(state, "evaluator_advanced", e)
    
    async def _execute_turnitin_loop(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute revolutionary Turnitin agent."""
        try:
            result = await self.turnitin_loop_node(state, config)
            return {**result, "current_node": "turnitin_advanced"}
        except Exception as e:
            return await self._handle_node_error(state, "turnitin_advanced", e)
    
    async def _execute_formatter(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute revolutionary document formatter."""
        try:
            result = await self.formatter_node(state, config)
            return {**result, "current_node": "formatter_advanced"}
        except Exception as e:
            return await self._handle_node_error(state, "formatter_advanced", e)
    
    async def _execute_fail_handler(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute revolutionary fail handler."""
        try:
            result = await self.fail_handler_node(state, config)
            return {**result, "current_node": "fail_handler_advanced"}
        except Exception as e:
            # Meta-failure handling
            return {
                "workflow_status": "critical_failure",
                "error_message": f"Fail handler failed: {str(e)}",
                "current_node": "critical_failure",
                "escalation_required": True
            }
    
    # Revolutionary Swarm Intelligence execution methods
    async def _execute_swarm_coordinator(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute revolutionary swarm intelligence coordinator."""
        try:
            result = await self.swarm_coordinator_node(state, config)
            return {**result, "current_node": "swarm_coordinator"}
        except Exception as e:
            return await self._handle_node_error(state, "swarm_coordinator", e)
    
    async def _execute_emergent_intelligence(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute revolutionary emergent intelligence engine."""
        try:
            result = await self.emergent_intelligence_node(state, config)
            return {**result, "current_node": "emergent_intelligence"}
        except Exception as e:
            return await self._handle_node_error(state, "emergent_intelligence", e)
    
    # Revolutionary Routing functions
    def _route_from_orchestrator(self, state: HandyWriterzState) -> str:
        """Revolutionary routing from Master Orchestrator based on workflow intelligence."""
        if state.get("use_swarm_intelligence"):
            return "swarm_coordinator"

        orchestration_result = state.get("orchestration_result", {})
        workflow_intelligence = orchestration_result.get("workflow_intelligence", {})
        
        # Determine complexity and route accordingly
        complexity = workflow_intelligence.get("academic_complexity", 5.0)
        success_probability = orchestration_result.get("success_probability", 0.8)
        
        # Use Enhanced User Intent for complex or high-value requests
        if complexity >= 7.0 or success_probability >= 0.9:
            return "enhanced_user_intent"
        else:
            return "user_intent"  # Fallback to legacy processing
    
    def _route_after_intent_analysis(self, state: HandyWriterzState) -> str:
        """Route after intelligent intent analysis based on clarity and completeness."""
        intent_analysis_result = state.get("intent_analysis_result", {})
        should_proceed = intent_analysis_result.get("should_proceed", False)
        clarifying_questions = state.get("clarifying_questions", [])
        
        # Check if user params indicate "general" mode (do nothing mode)
        user_params = state.get("user_params", {})
        field = user_params.get("field", "").lower()
        if field == "general" and not should_proceed:
            # In general mode with unclear intent, do nothing gracefully
            state.update({
                "workflow_status": "clarification_requested",
                "response_type": "clarification_questions",
                "final_response": {
                    "message": "I'd be happy to help with your academic writing! To provide the best assistance, I need some additional information:",
                    "clarifying_questions": clarifying_questions,
                    "suggestion": "Please provide more specific details about your academic requirements."
                }
            })
            return "clarification_needed"
        
        if should_proceed:
            return "planner"
        else:
            # Need clarification - end workflow gracefully with questions
            state.update({
                "workflow_status": "clarification_requested",
                "response_type": "clarification_questions",
                "final_response": {
                    "message": "To provide optimal academic assistance, I need clarification on a few points:",
                    "clarifying_questions": clarifying_questions,
                    "note": "Once you provide these details, I can offer comprehensive academic writing support."
                }
            })
            return "clarification_needed"
    
    # Revolutionary parallel routing with AI agents
    def _route_to_ai_search_agents(self, state: HandyWriterzState) -> List[Send]:
        """Route to revolutionary AI search agents in parallel for maximum intelligence and source diversity."""
        sends = [
            Send("search_crossref", state),
            Send("search_pmc", state),
            Send("search_ss", state),
        ]
        
        for agent_name in self.enabled_search_agents:
            sends.append(Send(f"search_{agent_name}", state))
            
        return sends

    def _route_after_source_verifier(self, state: HandyWriterzState) -> str:
        """Route after source verification, checking if fallback is needed."""
        if state.get("need_fallback"):
            return "source_fallback_controller"
        return "source_filter"
    
    def _route_after_source_filter(self, state: HandyWriterzState) -> str:
        """Route after source filtering: determine if swarm intelligence is needed."""
        sources = state.get("sources", [])
        
        if len(sources) < state.get("params", {}).get("min_sources", 3):
            return "fail_handler_advanced"  # Not enough sources
        
        # Determine if problem complexity warrants swarm intelligence
        complexity_score = self._calculate_swarm_complexity_score(state)
        
        # Use swarm intelligence for complex problems
        if complexity_score >= 7.0:
            return "swarm_coordinator"
        else:
            return "writer"  # Use traditional workflow for simpler problems

    def _route_after_citation_audit(self, state: HandyWriterzState) -> str:
        """Route after citation audit."""
        if state.get("citation_error"):
            # TODO: Add revision count to avoid infinite loops
            return "revision_needed"
        return "proceed"
    
    def _calculate_swarm_complexity_score(self, state: HandyWriterzState) -> float:
        """Calculate problem complexity score to determine swarm intelligence need."""
        user_request = state.get("user_request", "")
        requirements = state.get("requirements", [])
        verified_sources = state.get("sources", [])
        
        complexity = 5.0  # Base complexity
        
        # Factor in request length and sophistication
        if len(user_request) > 500:
            complexity += 1.0
        if len(user_request) > 1000:
            complexity += 1.0
        
        # Factor in number of requirements
        complexity += len(requirements) * 0.5
        
        # Factor in source diversity and complexity
        complexity += min(2.0, len(verified_sources) * 0.2)
        
        # Factor in complex keywords that suggest need for collective reasoning
        complex_keywords = [
            "analyze", "synthesize", "evaluate", "compare", "critique", "argue",
            "interdisciplinary", "multi-faceted", "complex", "comprehensive",
            "research paper", "dissertation", "thesis", "systematic review"
        ]
        
        for keyword in complex_keywords:
            if keyword.lower() in user_request.lower():
                complexity += 0.5
        
        # Factor in orchestration intelligence if available
        orchestration_result = state.get("orchestration_result", {})
        workflow_intelligence = orchestration_result.get("workflow_intelligence", {})
        if workflow_intelligence.get("academic_complexity", 0) >= 7.0:
            complexity += 1.0
        
        return min(complexity, 10.0)
    
    def _route_after_evaluation(self, state: HandyWriterzState) -> str:
        """Route after evaluation."""
        is_complete = state.get("is_complete", False)
        if is_complete:
            return "formatter_advanced"
        else:
            # In a real scenario, you might want to loop back to the writer
            # or trigger a different recovery mechanism.
            return "fail_handler_advanced"
    
    def _route_after_turnitin(self, state: HandyWriterzState) -> str:
        """Route after revolutionary Turnitin processing."""
        turnitin_passed = state.get("turnitin_passed", False)
        similarity_passed = state.get("similarity_passed", False)
        ai_detection_passed = state.get("ai_detection_passed", False)
        revision_count = state.get("revision_count", 0)
        
        if turnitin_passed and similarity_passed and ai_detection_passed:
            return "formatter_advanced"  # Perfect - ready for sophisticated formatting
        elif revision_count < 4 and (similarity_passed or ai_detection_passed):
            return "writer"  # Partially passed, needs targeted revision
        else:
            return "fail_handler_advanced"  # Failed academic integrity standards
    
    def _route_from_fail_handler(self, state: HandyWriterzState) -> str:
        """Route from revolutionary fail handler based on recovery strategy."""
        recovery_result = state.get("recovery_successful", False)
        recovery_strategy = state.get("recovery_strategy", "")
        failure_count = state.get("failure_count", 0)
        
        if recovery_result and "retry" in recovery_strategy.lower():
            return "writer"  # Recovery successful, retry writing
        elif recovery_result and "search" in recovery_strategy.lower():
            return "search_crossref"  # Recovery suggests new search
        elif recovery_result and "swarm" in recovery_strategy.lower():
            return "swarm_coordinator"  # Recovery suggests swarm intelligence approach
        elif failure_count < 2 and self._calculate_swarm_complexity_score(state) >= 6.0:
            # For complex problems with multiple failures, try swarm intelligence
            return "swarm_coordinator"
        else:
            return END  # Unrecoverable failure, end workflow
    
    # Helper methods
    async def _handle_node_error(self, state: HandyWriterzState, node_name: str, error: Exception) -> Dict[str, Any]:
        """Handle node execution errors."""
        error_info = {
            "workflow_status": "failed",
            "error_message": str(error),
            "failed_node": node_name,
            "current_node": "fail_handler"
        }
        
        # Increment retry count
        retry_count = state.get("retry_count", 0) + 1
        error_info["retry_count"] = retry_count
        
        # Determine if error is recoverable
        if retry_count < 3 and hasattr(error, 'recoverable') and error.recoverable:
            error_info["workflow_status"] = "retry_pending"
        
        return error_info

    def _create_search_execution_method(self, agent_instance, agent_name):
        """Create a new execution method for a search agent."""
        async def _execute_search(state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
            """Dynamically created search execution method."""
            try:
                result = await agent_instance.execute(state, config)
                return {**result, "current_node": f"search_{agent_name}"}
            except Exception as e:
                return await self._handle_node_error(state, f"search_{agent_name}", e)
        return _execute_search


# Create the main graph instance
def create_handywriterz_graph() -> StateGraph:
    """Create and return the HandyWriterz workflow graph."""
    orchestrator = HandyWriterzOrchestrator()
    return orchestrator.create_graph()


# Export the main graph
handywriterz_graph = create_handywriterz_graph()