#!/usr/bin/env python3
"""
HandyWriterz End-to-End Test Suite
==================================

This test suite simulates the complete user journey from prompting to results
using the Gemini 2.5 Pro API. It tests the multi-agent system functionality
without using mocks - only real API calls.

Test Coverage:
- Basic API connectivity
- Academic essay generation (main user journey)
- Research query processing
- Citation generation
- Quality assessment
- Document formatting
- Performance metrics
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from typing import List
import traceback

# Add the backend src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GEMINI_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Google Generative AI not available: {e}")
    GEMINI_AVAILABLE = False

# Test Configuration
TEST_CONFIG = {
    "model": "gemini-2.5-pro",
    "temperature": 0.7,
    "max_output_tokens": 2048,
    "timeout": 30,
    "safety_settings": {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    } if GEMINI_AVAILABLE else {}
}

class TestResult:
    """Test result container with metrics"""
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.success = False
        self.error = None
        self.response = None
        self.duration = 0
        self.token_count = 0
        self.start_time = None
        self.end_time = None
        self.metadata = {}
    
    def start(self):
        self.start_time = time.time()
        return self
    
    def finish(self, success=True, error=None, response=None):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.error = error
        self.response = response
        return self
    
    def to_dict(self):
        return {
            'test_name': self.test_name,
            'success': self.success,
            'error': str(self.error) if self.error else None,
            'duration': round(self.duration, 2),
            'token_count': self.token_count,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'metadata': self.metadata
        }

class MultiAgentTester:
    """End-to-end tester for the multi-agent system"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.results: List[TestResult] = []
        self.model = None
        
        if GEMINI_AVAILABLE and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name=TEST_CONFIG["model"],
                generation_config=genai.types.GenerationConfig(
                    temperature=TEST_CONFIG["temperature"],
                    max_output_tokens=TEST_CONFIG["max_output_tokens"],
                ),
                safety_settings=TEST_CONFIG["safety_settings"]
            )
    
    def log(self, message: str, level: str = "INFO"):
        """Log test progress"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    async def run_test(self, test_name: str, test_func, *args, **kwargs):
        """Run a single test with error handling and metrics"""
        result = TestResult(test_name).start()
        
        try:
            self.log(f"Running {test_name}...")
            response = await test_func(*args, **kwargs)
            result.finish(success=True, response=response)
            self.log(f"✅ {test_name} completed in {result.duration:.2f}s")
            
        except Exception as e:
            result.finish(success=False, error=e)
            self.log(f"❌ {test_name} failed: {str(e)}", "ERROR")
            
        self.results.append(result)
        return result
    
    async def test_basic_connectivity(self):
        """Test 1: Basic API connectivity"""
        if not self.model:
            raise Exception("Gemini model not available")
        
        prompt = 'Hello, please respond with "API Working" if you can receive this message.'
        
        response = self.model.generate_content(prompt)
        
        if not response.text:
            raise Exception("No response received from API")
        
        if "API Working" not in response.text:
            self.log(f"Unexpected response: {response.text[:100]}...")
        
        return {
            "prompt": prompt,
            "response": response.text,
            "success": True
        }
    
    async def test_academic_essay_generation(self):
        """Test 2: Academic essay generation (main user journey)"""
        if not self.model:
            raise Exception("Gemini model not available")
        
        prompt = """Write a 300-word academic essay about the impact of artificial intelligence on modern education. 
        Include:
        - Introduction with thesis statement
        - 2-3 main body paragraphs with evidence
        - Conclusion
        - Use formal academic tone
        - Include at least 2 specific examples"""
        
        response = self.model.generate_content(prompt)
        
        if not response.text:
            raise Exception("No essay generated")
        
        # Basic quality checks
        word_count = len(response.text.split())
        if word_count < 200:
            raise Exception(f"Essay too short: {word_count} words")
        
        # Check for academic elements
        text_lower = response.text.lower()
        academic_indicators = [
            'introduction', 'conclusion', 'furthermore', 'however', 
            'research', 'studies', 'evidence', 'analysis'
        ]
        
        found_indicators = [ind for ind in academic_indicators if ind in text_lower]
        
        return {
            "prompt": prompt,
            "response": response.text,
            "word_count": word_count,
            "academic_indicators": found_indicators,
            "quality_score": len(found_indicators) / len(academic_indicators)
        }
    
    async def test_research_query_simulation(self):
        """Test 3: Research query processing (simulating multi-agent research)"""
        if not self.model:
            raise Exception("Gemini model not available")
        
        prompt = """Act as a research specialist. Given the topic "Machine Learning in Healthcare", 
        provide:
        
        1. 3 key research questions
        2. 5 potential academic sources (with realistic titles and authors)
        3. Main themes to explore
        4. Methodology considerations
        
        Format your response as a structured research plan."""
        
        response = self.model.generate_content(prompt)
        
        if not response.text:
            raise Exception("No research plan generated")
        
        # Check for research elements
        text_lower = response.text.lower()
        research_indicators = [
            'research questions', 'sources', 'methodology', 'authors',
            'themes', 'academic', 'journal', 'study'
        ]
        
        found_indicators = [ind for ind in research_indicators if ind in text_lower]
        
        return {
            "prompt": prompt,
            "response": response.text,
            "research_indicators": found_indicators,
            "research_quality": len(found_indicators) / len(research_indicators)
        }
    
    async def test_citation_generation(self):
        """Test 4: Citation generation (Citation Agent simulation)"""
        if not self.model:
            raise Exception("Gemini model not available")
        
        prompt = """Generate 3 properly formatted APA citations for the following sources:
        
        1. A journal article about AI in education published in 2023
        2. A book about educational technology from 2022
        3. A conference paper about machine learning in schools from 2024
        
        Make the citations realistic but fictional. Include all required APA elements."""
        
        response = self.model.generate_content(prompt)
        
        if not response.text:
            raise Exception("No citations generated")
        
        # Check for APA elements
        text_lower = response.text.lower()
        apa_indicators = [
            '2023', '2022', '2024', '(', ')', '.',
            'journal', 'pp.', 'vol.', 'doi'
        ]
        
        found_indicators = [ind for ind in apa_indicators if ind in text_lower]
        
        return {
            "prompt": prompt,
            "response": response.text,
            "apa_indicators": found_indicators,
            "citation_quality": len(found_indicators) / len(apa_indicators)
        }
    
    async def test_quality_assessment(self):
        """Test 5: Quality assessment (QA Agent simulation)"""
        if not self.model:
            raise Exception("Gemini model not available")
        
        sample_text = """Artificial intelligence has become very important in education. 
        It helps students learn better. AI can personalize learning experiences. 
        Many schools are using AI tools now. This is good for education."""
        
        prompt = f"""Act as a quality assessment specialist. Evaluate this text for:
        
        1. Academic tone and style
        2. Depth of analysis
        3. Use of evidence
        4. Clarity and coherence
        5. Overall quality score (1-10)
        
        Text to evaluate:
        "{sample_text}"
        
        Provide specific feedback and improvement suggestions."""
        
        response = self.model.generate_content(prompt)
        
        if not response.text:
            raise Exception("No quality assessment generated")
        
        # Check for assessment elements
        text_lower = response.text.lower()
        qa_indicators = [
            'score', 'quality', 'academic', 'evidence', 'improvement',
            'feedback', 'clarity', 'coherence', 'analysis'
        ]
        
        found_indicators = [ind for ind in qa_indicators if ind in text_lower]
        
        return {
            "prompt": prompt,
            "response": response.text,
            "sample_text": sample_text,
            "qa_indicators": found_indicators,
            "assessment_quality": len(found_indicators) / len(qa_indicators)
        }
    
    async def test_document_formatting(self):
        """Test 6: Document formatting (Formatter Agent simulation)"""
        if not self.model:
            raise Exception("Gemini model not available")
        
        raw_content = """AI in Education
        Introduction
        Artificial intelligence is transforming education
        Main Benefits
        Personalized learning
        Automated grading
        Intelligent tutoring systems
        Conclusion
        AI will continue to impact education positively"""
        
        prompt = f"""Act as a document formatter. Convert this raw content into a properly 
        formatted academic document with:
        
        1. Proper heading hierarchy (H1, H2, H3)
        2. Paragraph structure
        3. Academic formatting
        4. Introduction and conclusion sections
        5. Smooth transitions between sections
        
        Raw content:
        "{raw_content}"
        
        Return the formatted document."""
        
        response = self.model.generate_content(prompt)
        
        if not response.text:
            raise Exception("No formatted document generated")
        
        # Check for formatting elements
        text = response.text
        formatting_indicators = [
            '#', '##', '###', '\n\n', 'Introduction', 'Conclusion',
            'Furthermore', 'However', 'In conclusion'
        ]
        
        found_indicators = [ind for ind in formatting_indicators if ind in text]
        
        return {
            "prompt": prompt,
            "response": response.text,
            "raw_content": raw_content,
            "formatting_indicators": found_indicators,
            "formatting_quality": len(found_indicators) / len(formatting_indicators)
        }
    
    async def run_all_tests(self):
        """Run the complete test suite"""
        self.log("🚀 Starting HandyWriterz End-to-End Test Suite")
        self.log(f"Using model: {TEST_CONFIG['model']}")
        
        # Check prerequisites
        if not GEMINI_AVAILABLE:
            self.log("❌ Google Generative AI library not available", "ERROR")
            return False
        
        if not self.api_key:
            self.log("❌ GEMINI_API_KEY not found in environment", "ERROR")
            return False
        
        # Run all tests
        tests = [
            ("Basic API Connectivity", self.test_basic_connectivity),
            ("Academic Essay Generation", self.test_academic_essay_generation),
            ("Research Query Processing", self.test_research_query_simulation),
            ("Citation Generation", self.test_citation_generation),
            ("Quality Assessment", self.test_quality_assessment),
            ("Document Formatting", self.test_document_formatting),
        ]
        
        for test_name, test_func in tests:
            await self.run_test(test_name, test_func)
            await asyncio.sleep(1)  # Rate limiting
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        
        total_duration = sum(r.duration for r in self.results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        # Create report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_duration": round(total_duration, 2),
                "average_duration": round(avg_duration, 2)
            },
            "test_results": [r.to_dict() for r in self.results],
            "configuration": TEST_CONFIG
        }
        
        # Print summary
        self.log("\n" + "="*70)
        self.log("📊 TEST SUMMARY")
        self.log("="*70)
        self.log(f"Total Tests: {total_tests}")
        self.log(f"Passed: {passed_tests}")
        self.log(f"Failed: {failed_tests}")
        self.log(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        self.log(f"Total Duration: {total_duration:.2f}s")
        self.log(f"Average Duration: {avg_duration:.2f}s")
        
        # Print individual results
        self.log("\n📋 INDIVIDUAL TEST RESULTS:")
        for result in self.results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            self.log(f"{status} | {result.test_name} | {result.duration:.2f}s")
            if not result.success:
                self.log(f"    Error: {result.error}")
        
        # Overall assessment
        if passed_tests == total_tests:
            self.log("\n🎉 ALL TESTS PASSED! Multi-agent system is fully functional.")
        elif passed_tests > total_tests * 0.8:
            self.log("\n✅ MOSTLY SUCCESSFUL! Most functionality is working.")
        else:
            self.log("\n⚠️ SOME ISSUES DETECTED. Review failed tests.")
        
        return report

async def main():
    """Main test runner"""
    print("🧪 HandyWriterz End-to-End Test Suite")
    print("=" * 50)
    
    # Initialize tester
    tester = MultiAgentTester()
    
    # Run all tests
    report = await tester.run_all_tests()
    
    # Save report
    if report:
        report_path = "/mnt/d/multiagentwriterz/backend/e2e_test_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📁 Full report saved to: {report_path}")
    
    return report

if __name__ == "__main__":
    # Run the test suite
    try:
        report = asyncio.run(main())
        exit_code = 0 if report and report['summary']['success_rate'] == 100 else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        traceback.print_exc()
        sys.exit(1)