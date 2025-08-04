"""
Unit Tests for Prompt Orchestrator System
Tests policy loading, prompt assembly, and validation functionality.
"""

import pytest
import os
import tempfile
import yaml
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from src.services.prompt_orchestrator import (
    PromptOrchestrator, PromptPolicies, UseCasePolicy, UserParams,
    EvidenceSnippet, CostLevel, AcademicLevel, CitationStyle, UseCase,
    get_prompt_orchestrator, ModelHints, QualityMetrics, OutputContract
)


class TestPromptOrchestrator:
    """Test suite for PromptOrchestrator functionality."""
    
    @pytest.fixture
    def sample_policies_data(self) -> Dict[str, Any]:
        """Sample policies data for testing."""
        return {
            "version": "1.0.0",
            "global_defaults": {
                "id": "global",
                "name": "Global Defaults",
                "description": "Test global defaults",
                "objectives": ["Test objective 1", "Test objective 2"],
                "constraints": ["Test constraint 1"],
                "safety_rules": {
                    "verify_citations": True,
                    "never_fabricate": True,
                    "disclose_uncertainties": True,
                    "redact_pii": True,
                    "require_evidence_grounding": True,
                    "plagiarism_check": True
                },
                "model_hints": {
                    "planner": "test-planner-model",
                    "researcher": ["test-researcher-1", "test-researcher-2"],
                    "writer": "test-writer-model",
                    "evaluator": "test-evaluator-model"
                },
                "quality_metrics": {
                    "coherence_threshold": 0.85,
                    "citation_count_min": 10,
                    "evidence_coverage_threshold": 0.8,
                    "originality_threshold": 0.85,
                    "accuracy_threshold": 0.9
                },
                "output_contract": {
                    "format_type": "markdown",
                    "sections": ["Introduction", "Body", "Conclusion"],
                    "required_fields": [],
                    "word_count_tolerance": 0.1
                }
            },
            "use_cases": {
                "general": {
                    "id": "general",
                    "name": "General Assistant",
                    "description": "General purpose assistant",
                    "objectives": ["Provide helpful responses", "Maintain accuracy"],
                    "constraints": ["Be concise", "Verify information"],
                    "output_contract": {
                        "format_type": "markdown",
                        "sections": ["Plan", "Answer", "References"],
                        "required_fields": ["plan", "answer"]
                    }
                },
                "dissertation": {
                    "id": "dissertation",
                    "name": "Dissertation Assistant",
                    "description": "Doctoral dissertation writing support",
                    "objectives": [
                        "Produce comprehensive dissertation",
                        "Ensure academic rigor",
                        "Maintain originality"
                    ],
                    "constraints": [
                        "Follow citation style requirements",
                        "Meet word count targets",
                        "Include required sections"
                    ],
                    "quality_metrics": {
                        "coherence_threshold": 0.9,
                        "citation_count_min": 40,
                        "evidence_coverage_threshold": 0.85,
                        "originality_threshold": 0.85,
                        "accuracy_threshold": 0.95
                    },
                    "output_contract": {
                        "format_type": "markdown",
                        "sections": [
                            "Abstract", "Introduction", "Literature Review",
                            "Methodology", "Results", "Discussion", "Conclusion", "References"
                        ],
                        "required_fields": ["abstract", "methodology", "references"],
                        "word_count_tolerance": 0.1
                    }
                }
            }
        }
    
    @pytest.fixture
    def temp_policies_file(self, sample_policies_data):
        """Create temporary policies file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(sample_policies_data, f)
            yield f.name
        os.unlink(f.name)
    
    @pytest.fixture
    def temp_templates_dir(self):
        """Create temporary templates directory for testing."""
        temp_dir = tempfile.mkdtemp()
        
        # Create basic template files
        templates = {
            "header.jinja": "# Test Header\nYou are {{ use_case_name }}.",
            "safety.jinja": "## Safety Rules\n- Never fabricate information",
            "tools_contracts.jinja": "## Tools Available\n- Search: Find information",
            "usecase_general.jinja": "## General Mode\nObjectives: {{ objectives|join(', ') }}",
            "usecase_dissertation.jinja": "## Dissertation Mode\nRequirements: {{ constraints|join(', ') }}",
            "output_contract_general.jinja": "## Output Format\nSections: {{ sections|join(', ') }}",
            "output_contract_dissertation.jinja": "## Dissertation Output\nRequired: {{ required_fields|join(', ') }}"
        }
        
        for template_name, content in templates.items():
            template_path = os.path.join(temp_dir, template_name)
            with open(template_path, 'w') as f:
                f.write(content)
        
        yield temp_dir
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
    
    def test_orchestrator_initialization(self, temp_policies_file, temp_templates_dir):
        """Test PromptOrchestrator initialization with valid configuration."""
        orchestrator = PromptOrchestrator(
            policies_path=temp_policies_file,
            templates_path=temp_templates_dir
        )
        
        assert orchestrator.policies is not None
        assert orchestrator.jinja_env is not None
        assert orchestrator.policies.version == "1.0.0"
        assert "general" in orchestrator.policies.use_cases
        assert "dissertation" in orchestrator.policies.use_cases
    
    def test_policy_loading_with_missing_file(self, temp_templates_dir):
        """Test graceful handling of missing policies file."""
        orchestrator = PromptOrchestrator(
            policies_path="/nonexistent/file.yaml",
            templates_path=temp_templates_dir
        )
        
        # Should create default policies
        assert orchestrator.policies is not None
        assert "general" in orchestrator.policies.use_cases
    
    def test_get_policy_exact_match(self, temp_policies_file, temp_templates_dir):
        """Test policy retrieval with exact use case match."""
        orchestrator = PromptOrchestrator(
            policies_path=temp_policies_file,
            templates_path=temp_templates_dir
        )
        
        policy = orchestrator.get_policy("dissertation")
        assert policy.id == "dissertation"
        assert policy.name == "Dissertation Assistant"
        assert len(policy.objectives) == 3
    
    def test_get_policy_fallback_to_general(self, temp_policies_file, temp_templates_dir):
        """Test policy retrieval fallback for unknown use case."""
        orchestrator = PromptOrchestrator(
            policies_path=temp_policies_file,
            templates_path=temp_templates_dir
        )
        
        policy = orchestrator.get_policy("unknown_use_case")
        assert policy.id == "general"
        assert policy.name == "General Assistant"
    
    def test_prompt_assembly_general_case(self, temp_policies_file, temp_templates_dir):
        """Test complete prompt assembly for general use case."""
        orchestrator = PromptOrchestrator(
            policies_path=temp_policies_file,
            templates_path=temp_templates_dir
        )
        
        user_params = UserParams(
            citation_style=CitationStyle.APA,
            word_count_target=1000,
            academic_level=AcademicLevel.GRADUATE
        )
        
        evidence_snippets = [
            EvidenceSnippet(
                text="Test evidence snippet 1",
                citation="Test Author (2023)",
                confidence_score=0.9
            ),
            EvidenceSnippet(
                text="Test evidence snippet 2", 
                citation="Another Author (2023)",
                confidence_score=0.8
            )
        ]
        
        result = orchestrator.assemble_prompt(
            use_case="general",
            user_params=user_params,
            memory_summary="Previous conversation about testing",
            evidence_snippets=evidence_snippets,
            budget_level=CostLevel.STANDARD,
            custom_context={"test_context": "test_value"}
        )
        
        # Validate result structure
        assert result.prompt_id is not None
        assert result.policy_version == "1.0.0"
        assert result.system_prompt is not None
        assert result.developer_prompt is not None
        assert result.output_contract is not None
        assert result.metadata["use_case"] == "general"
        assert result.metadata["evidence_count"] == 2
        assert result.token_estimate > 0
        
        # Validate prompt content
        assert "Test Header" in result.system_prompt
        assert "General Assistant" in result.system_prompt
        assert "Safety Rules" in result.system_prompt
        assert "Test evidence snippet 1" in result.developer_prompt
        assert "Test evidence snippet 2" in result.developer_prompt
    
    def test_prompt_assembly_dissertation_case(self, temp_policies_file, temp_templates_dir):
        """Test prompt assembly for dissertation use case with specific requirements."""
        orchestrator = PromptOrchestrator(
            policies_path=temp_policies_file,
            templates_path=temp_templates_dir
        )
        
        user_params = UserParams(
            citation_style=CitationStyle.HARVARD,
            word_count_target=50000,
            academic_level=AcademicLevel.DOCTORAL
        )
        
        result = orchestrator.assemble_prompt(
            use_case="dissertation",
            user_params=user_params,
            budget_level=CostLevel.PREMIUM
        )
        
        # Validate dissertation-specific content
        assert result.metadata["use_case"] == "dissertation"
        assert result.output_contract.sections == [
            "Abstract", "Introduction", "Literature Review", "Methodology", 
            "Results", "Discussion", "Conclusion", "References"
        ]
        assert "abstract" in result.output_contract.required_fields
        assert "methodology" in result.output_contract.required_fields
        assert "references" in result.output_contract.required_fields
        
        # Validate dissertation-specific templates
        assert "Dissertation Assistant" in result.system_prompt
        assert "Dissertation Mode" in result.system_prompt
    
    def test_budget_constraints_application(self, temp_policies_file, temp_templates_dir):
        """Test budget level application to evidence snippets."""
        orchestrator = PromptOrchestrator(
            policies_path=temp_policies_file,
            templates_path=temp_templates_dir
        )
        
        # Create many evidence snippets
        evidence_snippets = [
            EvidenceSnippet(
                text=f"Evidence snippet {i}",
                citation=f"Author {i} (2023)",
                confidence_score=0.9 - (i * 0.01)  # Decreasing confidence
            ) for i in range(20)
        ]
        
        user_params = UserParams()
        
        # Test budget level limiting
        result_budget = orchestrator.assemble_prompt(
            use_case="general",
            user_params=user_params,
            evidence_snippets=evidence_snippets,
            budget_level=CostLevel.BUDGET
        )
        
        result_premium = orchestrator.assemble_prompt(
            use_case="general", 
            user_params=user_params,
            evidence_snippets=evidence_snippets,
            budget_level=CostLevel.PREMIUM
        )
        
        # Budget should have fewer evidence snippets in prompt
        assert "Evidence snippet 19" not in result_budget.developer_prompt
        assert "Evidence snippet 19" in result_premium.developer_prompt
        assert result_budget.metadata["evidence_count"] < result_premium.metadata["evidence_count"]
    
    def test_template_existence_checking(self, temp_policies_file, temp_templates_dir):
        """Test template existence checking functionality."""
        orchestrator = PromptOrchestrator(
            policies_path=temp_policies_file,
            templates_path=temp_templates_dir
        )
        
        assert orchestrator._template_exists("header.jinja")
        assert orchestrator._template_exists("safety.jinja")
        assert not orchestrator._template_exists("nonexistent.jinja")
    
    def test_prompt_id_generation(self, temp_policies_file, temp_templates_dir):
        """Test prompt ID generation for reproducibility."""
        orchestrator = PromptOrchestrator(
            policies_path=temp_policies_file,
            templates_path=temp_templates_dir
        )
        
        # Same inputs should generate same prompt ID
        prompt_id_1 = orchestrator._generate_prompt_id("test content", "general")
        prompt_id_2 = orchestrator._generate_prompt_id("test content", "general")
        
        assert prompt_id_1 == prompt_id_2
        assert prompt_id_1.startswith("general_")
        assert len(prompt_id_1) > 8  # Should include hash
    
    def test_token_estimation(self, temp_policies_file, temp_templates_dir):
        """Test token estimation functionality."""
        orchestrator = PromptOrchestrator(
            policies_path=temp_policies_file,
            templates_path=temp_templates_dir
        )
        
        # Test token estimation
        short_text = "Hello world"
        long_text = "This is a much longer piece of text " * 100
        
        short_estimate = orchestrator._estimate_tokens(short_text)
        long_estimate = orchestrator._estimate_tokens(long_text)
        
        assert short_estimate < long_estimate
        assert short_estimate > 0
        assert long_estimate > short_estimate * 50  # Should be significantly larger
    
    def test_policy_validation(self, temp_policies_file, temp_templates_dir):
        """Test policy validation functionality."""
        orchestrator = PromptOrchestrator(
            policies_path=temp_policies_file,
            templates_path=temp_templates_dir
        )
        
        validation_report = orchestrator.validate_policies()
        
        assert validation_report["valid"] == True
        assert validation_report["version"] == "1.0.0"
        assert validation_report["use_cases_count"] == 2
        assert isinstance(validation_report["missing_templates"], list)
        assert isinstance(validation_report["warnings"], list)
    
    def test_global_orchestrator_instance(self):
        """Test global orchestrator instance management."""
        # Should create singleton instance
        orchestrator_1 = get_prompt_orchestrator()
        orchestrator_2 = get_prompt_orchestrator()
        
        assert orchestrator_1 is orchestrator_2
        assert isinstance(orchestrator_1, PromptOrchestrator)
    
    @patch('src.services.prompt_orchestrator.logger')
    def test_logging_integration(self, mock_logger, temp_policies_file, temp_templates_dir):
        """Test logging integration and observability."""
        orchestrator = PromptOrchestrator(
            policies_path=temp_policies_file,
            templates_path=temp_templates_dir
        )
        
        user_params = UserParams()
        
        result = orchestrator.assemble_prompt(
            use_case="general",
            user_params=user_params,
            budget_level=CostLevel.STANDARD
        )
        
        # Verify logging was called
        mock_logger.info.assert_called()
        
        # Check for structured logging call with prompt assembly completion
        info_calls = [call for call in mock_logger.info.call_args_list if "Prompt Assembly Complete" in str(call)]
        assert len(info_calls) > 0
    
    def test_error_handling_invalid_templates(self, temp_policies_file):
        """Test error handling with invalid template directory."""
        orchestrator = PromptOrchestrator(
            policies_path=temp_policies_file,
            templates_path="/nonexistent/templates"
        )
        
        user_params = UserParams()
        
        # Should not crash, should use fallback prompts
        result = orchestrator.assemble_prompt(
            use_case="general",
            user_params=user_params
        )
        
        assert result is not None
        assert result.system_prompt is not None
        assert "HandyWriterz" in result.system_prompt  # Should use fallback
    
    def test_evidence_snippet_formatting(self, temp_policies_file, temp_templates_dir):
        """Test evidence snippet formatting in templates."""
        orchestrator = PromptOrchestrator(
            policies_path=temp_policies_file,
            templates_path=temp_templates_dir
        )
        
        evidence_snippets = [
            EvidenceSnippet(
                text="Machine learning improves efficiency",
                citation="Smith, J. (2023)",
                source_url="https://example.com/paper1"
            ),
            EvidenceSnippet(
                text="AI systems require careful validation",
                citation="Jones, M. (2023)", 
                source_url="https://example.com/paper2"
            )
        ]
        
        # Test citation formatting
        formatted = orchestrator._format_citations(evidence_snippets, "apa")
        
        assert "1. Machine learning improves efficiency (Smith, J. (2023))" in formatted
        assert "2. AI systems require careful validation (Jones, M. (2023))" in formatted
    
    def test_redaction_functionality(self, temp_policies_file, temp_templates_dir):
        """Test PII redaction in logging."""
        orchestrator = PromptOrchestrator(
            policies_path=temp_policies_file,
            templates_path=temp_templates_dir
        )
        
        # Test text with potential PII
        text_with_pii = """
        This is a test document with email@example.com and 
        API key abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
        """
        
        redacted = orchestrator._redact_for_logging(text_with_pii)
        
        assert "[REDACTED_EMAIL]" in redacted
        assert "[REDACTED_KEY]" in redacted
        assert "email@example.com" not in redacted
        assert "abc123def456ghi789jkl012mno345pqr678stu901vwx234yz" not in redacted


class TestUserParams:
    """Test suite for UserParams class."""
    
    def test_user_params_creation(self):
        """Test UserParams creation with various parameters."""
        params = UserParams(
            citation_style=CitationStyle.APA,
            word_count_target=2000,
            academic_level=AcademicLevel.DOCTORAL,
            file_ids=["file1", "file2"],
            custom_instructions="Please focus on methodology"
        )
        
        assert params.citation_style == CitationStyle.APA
        assert params.word_count_target == 2000
        assert params.academic_level == AcademicLevel.DOCTORAL
        assert len(params.file_ids) == 2
        assert params.custom_instructions == "Please focus on methodology"
    
    def test_user_params_defaults(self):
        """Test UserParams with default values."""
        params = UserParams()
        
        assert params.citation_style == CitationStyle.APA
        assert params.word_count_target is None
        assert params.academic_level == AcademicLevel.GRADUATE
        assert params.file_ids == []
        assert params.deadline_sensitivity == False


class TestEvidenceSnippet:
    """Test suite for EvidenceSnippet class."""
    
    def test_evidence_snippet_creation(self):
        """Test EvidenceSnippet creation and attributes."""
        snippet = EvidenceSnippet(
            text="Test evidence content",
            citation="Author (2023)",
            source_url="https://example.com",
            confidence_score=0.95,
            snippet_id="test-snippet-1"
        )
        
        assert snippet.text == "Test evidence content"
        assert snippet.citation == "Author (2023)"
        assert snippet.source_url == "https://example.com"
        assert snippet.confidence_score == 0.95
        assert snippet.snippet_id == "test-snippet-1"
    
    def test_evidence_snippet_defaults(self):
        """Test EvidenceSnippet with default values."""
        snippet = EvidenceSnippet(
            text="Test content",
            citation="Test citation"
        )
        
        assert snippet.source_url is None
        assert snippet.confidence_score == 1.0
        assert snippet.snippet_id is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])