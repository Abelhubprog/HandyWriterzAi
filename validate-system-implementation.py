#!/usr/bin/env python3
"""
HandyWriterz System Implementation Validator
Validates the complete user journey implementation against userjourneys.md requirements
"""

import os
import sys
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemImplementationValidator:
    """Validates that all components from userjourneys.md are properly implemented"""
    
    def __init__(self):
        self.validation_results = []
        self.critical_errors = []
        self.warnings = []
        self.passed_tests = 0
        self.total_tests = 0
        
    def validate_import(self, module_path: str, component_name: str) -> bool:
        """Validate that a module can be imported successfully"""
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, component_name):
                logger.info(f"✅ {component_name} imported successfully from {module_path}")
                return True
            else:
                self.warnings.append(f"Component {component_name} not found in {module_path}")
                return False
        except ImportError as e:
            self.critical_errors.append(f"Failed to import {module_path}: {e}")
            return False
        except Exception as e:
            self.critical_errors.append(f"Error importing {module_path}: {e}")
            return False
    
    def validate_core_graph_structure(self) -> bool:
        """Validate the core HandyWriterz graph structure"""
        logger.info("🔍 Validating core graph structure...")
        
        # Test core graph import
        success = self.validate_import("src.agent.handywriterz_graph", "handywriterz_graph")
        if not success:
            return False
            
        # Test state management
        success &= self.validate_import("src.agent.handywriterz_state", "HandyWriterzState")
        
        return success
    
    def validate_revolutionary_agents(self) -> bool:
        """Validate all revolutionary agents are implemented"""
        logger.info("🤖 Validating revolutionary agents...")
        
        revolutionary_agents = [
            ("src.agent.nodes.enhanced_user_intent", "EnhancedUserIntentAgent"),
            ("src.agent.nodes.master_orchestrator", "MasterOrchestratorAgent"), 
            ("src.agent.nodes.swarm_intelligence_coordinator", "swarm_intelligence_coordinator_node"),
            ("src.agent.nodes.emergent_intelligence_engine", "emergent_intelligence_engine_node"),
            ("src.agent.nodes.writer", "revolutionary_writer_agent_node"),
            ("src.agent.nodes.evaluator_advanced", "EvaluatorAdvancedNode"),
            ("src.agent.nodes.formatter_advanced", "revolutionary_formatter_node"),
            ("src.agent.nodes.turnitin_advanced", "revolutionary_turnitin_node"),
            ("src.agent.nodes.fail_handler_advanced", "revolutionary_fail_handler_node")
        ]
        
        success = True
        for module_path, component_name in revolutionary_agents:
            if self.validate_import(module_path, component_name):
                self.passed_tests += 1
            else:
                success = False
            self.total_tests += 1
        
        return success
    
    def validate_search_agents(self) -> bool:
        """Validate all search agents are implemented"""
        logger.info("🔍 Validating search agents...")
        
        search_agents = [
            ("src.agent.nodes.search_gemini", "GeminiSearchAgent"),
            ("src.agent.nodes.search_claude", "ClaudeSearchAgent"),
            ("src.agent.nodes.search_openai", "OpenAISearchAgent"),
            ("src.agent.nodes.search_perplexity", "PerplexitySearchAgent"),
            ("src.agent.nodes.search_o3", "O3SearchAgent"),
            ("src.agent.nodes.search_crossref", "SearchCrossRef"),
            ("src.agent.nodes.search_pmc", "SearchPMC"),
            ("src.agent.nodes.search_ss", "SearchSS")
        ]
        
        success = True
        for module_path, component_name in search_agents:
            if self.validate_import(module_path, component_name):
                self.passed_tests += 1
            else:
                success = False
            self.total_tests += 1
        
        return success
    
    def validate_quality_assurance_agents(self) -> bool:
        """Validate quality assurance and evaluation agents"""
        logger.info("🛡️ Validating quality assurance agents...")
        
        qa_agents = [
            ("src.agent.nodes.source_verifier", "SourceVerifier"),
            ("src.agent.nodes.source_filter", "SourceFilterNode"),
            ("src.agent.nodes.citation_audit", "CitationAudit"),
            ("src.agent.nodes.evaluator", "EvaluatorNode"),
            ("src.agent.nodes.qa_swarm.fact_checking", "FactCheckingNode"),
            ("src.agent.nodes.qa_swarm.bias_detection", "BiasDetectionNode"),
            ("src.agent.nodes.qa_swarm.ethical_reasoning", "EthicalReasoningNode"),
            ("src.agent.nodes.qa_swarm.argument_validation", "ArgumentValidationNode"),
            ("src.agent.nodes.qa_swarm.originality_guard", "OriginalityGuardNode")
        ]
        
        success = True
        for module_path, component_name in qa_agents:
            if self.validate_import(module_path, component_name):
                self.passed_tests += 1
            else:
                success = False
            self.total_tests += 1
        
        return success
    
    def validate_writing_swarm_agents(self) -> bool:
        """Validate writing swarm agents"""
        logger.info("✍️ Validating writing swarm agents...")
        
        writing_agents = [
            ("src.agent.nodes.writing_swarm.academic_tone", "AcademicToneNode"),
            ("src.agent.nodes.writing_swarm.clarity_enhancer", "ClarityEnhancerNode"),
            ("src.agent.nodes.writing_swarm.structure_optimizer", "StructureOptimizerNode"),
            ("src.agent.nodes.writing_swarm.style_adaptation", "StyleAdaptationNode"),
            ("src.agent.nodes.writing_swarm.citation_master", "CitationMasterNode")
        ]
        
        success = True
        for module_path, component_name in writing_agents:
            if self.validate_import(module_path, component_name):
                self.passed_tests += 1
            else:
                success = False
            self.total_tests += 1
        
        return success
    
    def validate_research_swarm_agents(self) -> bool:
        """Validate research swarm agents"""
        logger.info("📚 Validating research swarm agents...")
        
        research_agents = [
            ("src.agent.nodes.research_swarm.arxiv_specialist", "ArxivSpecialistNode"),
            ("src.agent.nodes.research_swarm.scholar_network", "ScholarNetworkNode"), 
            ("src.agent.nodes.research_swarm.methodology_expert", "MethodologyExpertNode"),
            ("src.agent.nodes.research_swarm.cross_disciplinary", "CrossDisciplinaryNode"),
            ("src.agent.nodes.research_swarm.trend_analysis", "TrendAnalysisNode")
        ]
        
        success = True
        for module_path, component_name in research_agents:
            if self.validate_import(module_path, component_name):
                self.passed_tests += 1
            else:
                success = False
            self.total_tests += 1
        
        return success
    
    def validate_services(self) -> bool:
        """Validate core services"""
        logger.info("⚙️ Validating core services...")
        
        services = [
            ("src.services.llm_service", "get_llm_client"),
            ("src.services.database_service", "DatabaseService"),
            ("src.services.embedding_service", "EmbeddingService"),
            ("src.services.vector_storage", "VectorStorage"),
            ("src.services.chunking_service", "ChunkingService"),
            ("src.services.model_service", "ModelService")
        ]
        
        success = True
        for module_path, component_name in services:
            if self.validate_import(module_path, component_name):
                self.passed_tests += 1
            else:
                success = False
            self.total_tests += 1
        
        return success
    
    def validate_api_endpoints(self) -> bool:
        """Validate API endpoints and routing"""
        logger.info("🌐 Validating API endpoints...")
        
        api_components = [
            ("src.main", "app"),
            ("src.agent.routing.unified_processor", "UnifiedProcessor"),
            ("src.api.files", "router"),
            ("src.api.chat", "router") 
        ]
        
        success = True
        for module_path, component_name in api_components:
            if self.validate_import(module_path, component_name):
                self.passed_tests += 1
            else:
                success = False
            self.total_tests += 1
        
        return success
    
    def validate_user_journey_phases(self) -> bool:
        """Validate that all 15 phases from userjourneys.md are covered"""
        logger.info("📋 Validating user journey phases...")
        
        # The 15 phases from userjourneys.md
        required_phases = [
            "File Upload & Multi-format Processing",
            "Intelligent File Analysis", 
            "Chat Submission & Intelligent Routing",
            "Memory Retrieval & User Fingerprinting",
            "Enhanced User Intent Analysis",
            "Master Orchestrator Coordination", 
            "Comprehensive Research Phase Execution",
            "Source Aggregation & Quality Assessment",
            "Swarm Intelligence Coordination Phase",
            "Advanced RAG Integration & Memory Synthesis",
            "Sophisticated Writing Phase Execution", 
            "Multi-dimensional Quality Assurance",
            "Advanced Evaluation & Turnitin Processing",
            "Advanced Formatting & Citation Processing",
            "Memory Update & Response Delivery"
        ]
        
        # Map phases to implementation components
        phase_coverage = {
            "File Upload & Multi-format Processing": self.validate_import("src.api.files", "router"),
            "Intelligent File Analysis": self.validate_import("src.services.chunking_service", "ChunkingService"),
            "Chat Submission & Intelligent Routing": self.validate_import("src.agent.routing.unified_processor", "UnifiedProcessor"),
            "Memory Retrieval & User Fingerprinting": self.validate_import("src.agent.nodes.memory_retriever", "MemoryRetrieverNode"),
            "Enhanced User Intent Analysis": self.validate_import("src.agent.nodes.enhanced_user_intent", "EnhancedUserIntentAgent"),
            "Master Orchestrator Coordination": self.validate_import("src.agent.nodes.master_orchestrator", "MasterOrchestratorAgent"),
            "Comprehensive Research Phase Execution": self.validate_import("src.agent.nodes.search_gemini", "GeminiSearchAgent"),
            "Source Aggregation & Quality Assessment": self.validate_import("src.agent.nodes.source_filter", "SourceFilterNode"),
            "Swarm Intelligence Coordination Phase": self.validate_import("src.agent.nodes.swarm_intelligence_coordinator", "swarm_intelligence_coordinator_node"),
            "Advanced RAG Integration & Memory Synthesis": self.validate_import("src.agent.nodes.rag_summarizer", "RAGSummarizerNode"),
            "Sophisticated Writing Phase Execution": self.validate_import("src.agent.nodes.writer", "revolutionary_writer_agent_node"),
            "Multi-dimensional Quality Assurance": self.validate_import("src.agent.nodes.qa_swarm.fact_checking", "FactCheckingNode"),
            "Advanced Evaluation & Turnitin Processing": self.validate_import("src.agent.nodes.turnitin_advanced", "revolutionary_turnitin_node"),
            "Advanced Formatting & Citation Processing": self.validate_import("src.agent.nodes.formatter_advanced", "revolutionary_formatter_node"),
            "Memory Update & Response Delivery": self.validate_import("src.agent.nodes.memory_writer", "MemoryWriter")
        }
        
        covered_phases = 0
        for phase, is_covered in phase_coverage.items():
            if is_covered:
                covered_phases += 1
                logger.info(f"✅ Phase covered: {phase}")
            else:
                logger.warning(f"⚠️ Phase missing: {phase}")
            self.total_tests += 1
        
        self.passed_tests += covered_phases
        coverage_percentage = (covered_phases / len(required_phases)) * 100
        
        logger.info(f"📊 Phase coverage: {covered_phases}/{len(required_phases)} ({coverage_percentage:.1f}%)")
        
        return coverage_percentage >= 80  # 80% minimum coverage required
    
    def run_comprehensive_validation(self) -> bool:
        """Run complete system validation"""
        logger.info("🎯 Starting HandyWriterz System Implementation Validation")
        logger.info("=" * 60)
        
        validation_results = {
            "Core Graph Structure": self.validate_core_graph_structure(),
            "Revolutionary Agents": self.validate_revolutionary_agents(),
            "Search Agents": self.validate_search_agents(), 
            "Quality Assurance Agents": self.validate_quality_assurance_agents(),
            "Writing Swarm Agents": self.validate_writing_swarm_agents(),
            "Research Swarm Agents": self.validate_research_swarm_agents(),
            "Core Services": self.validate_services(),
            "API Endpoints": self.validate_api_endpoints(),
            "User Journey Phases": self.validate_user_journey_phases()
        }
        
        self.generate_validation_report(validation_results)
        
        # Determine overall success
        overall_success = all(validation_results.values()) and not self.critical_errors
        
        return overall_success
    
    def generate_validation_report(self, validation_results: Dict[str, bool]):
        """Generate comprehensive validation report"""
        logger.info("\n" + "=" * 60)
        logger.info("🎯 SYSTEM IMPLEMENTATION VALIDATION REPORT")
        logger.info("=" * 60)
        
        # Summary
        passed_categories = sum(validation_results.values())
        total_categories = len(validation_results)
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        status = "✅ READY" if passed_categories == total_categories and not self.critical_errors else "❌ NEEDS WORK"
        logger.info(f"📊 Overall Status: {status}")
        logger.info(f"📈 Success Rate: {success_rate:.1f}% ({self.passed_tests}/{self.total_tests} tests passed)")
        logger.info(f"📋 Categories: {passed_categories}/{total_categories} passed")
        
        # Category breakdown
        logger.info(f"\n📊 CATEGORY BREAKDOWN:")
        for category, passed in validation_results.items():
            status_icon = "✅" if passed else "❌"
            logger.info(f"   {status_icon} {category}")
        
        # Critical errors
        if self.critical_errors:
            logger.info(f"\n🚨 CRITICAL ERRORS ({len(self.critical_errors)}):")
            for error in self.critical_errors[:5]:  # Show first 5 errors
                logger.error(f"   ❌ {error}")
            if len(self.critical_errors) > 5:
                logger.info(f"   ... and {len(self.critical_errors) - 5} more errors")
        
        # Warnings
        if self.warnings:
            logger.info(f"\n⚠️ WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:3]:  # Show first 3 warnings
                logger.warning(f"   ⚠️ {warning}")
            if len(self.warnings) > 3:
                logger.info(f"   ... and {len(self.warnings) - 3} more warnings")
        
        # YC Demo Day readiness
        logger.info(f"\n🎪 YC DEMO DAY READINESS:")
        if success_rate >= 90 and not self.critical_errors:
            logger.info("   🏆 System fully ready for YC Demo Day")
            logger.info("   🚀 All critical components implemented")
            logger.info("   💡 Revolutionary features operational")
        elif success_rate >= 75:
            logger.info("   🔧 System mostly ready, minor issues to address")
            logger.info("   ⚠️ Some components need attention")
        else:
            logger.info("   🚨 System needs significant work before demo")
            logger.info("   ❌ Critical components missing or broken")
        
        # Next steps
        logger.info(f"\n📝 NEXT STEPS:")
        if self.critical_errors:
            logger.info("   1. Fix critical import/implementation errors")
            logger.info("   2. Re-run validation after fixes")
            logger.info("   3. Run end-to-end integration tests")
        else:
            logger.info("   1. Address any remaining warnings")
            logger.info("   2. Run full deployment test: ./deploy-production.sh")
            logger.info("   3. Execute YC demo test: python test_yc_demo_ready.py")
        
        logger.info("=" * 60)

def main():
    """Main validation execution"""
    print("🎯 HandyWriterz System Implementation Validator")
    print("=" * 50)
    
    validator = SystemImplementationValidator()
    
    try:
        is_valid = validator.run_comprehensive_validation()
        
        # Exit codes
        if is_valid:
            print("\n✨ System validation completed successfully!")
            sys.exit(0)
        else:
            print("\n⚠️ System validation found issues")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Validation failed with error: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()