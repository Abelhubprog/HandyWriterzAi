#!/usr/bin/env python3
"""
User Journey Test for HandyWriterz Unified AI Plat
ests the complete flow from user prompt to results across different complexity levels.
"""

import asyncio
import json
import time
import requests
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QueryComplexity(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"

@dataclass
class TestScenario:
    name: str
    prompt: str
    complexity: QueryComplexity
    expected_system: str
    user_params: Optional[Dict[str, Any]] = None
    files: Optional[List[str]] = None
    expected_features: Optional[List[str]] = None

class UserJourneyTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
st_results = []

    def log_test_step(self, step: str, details: str = ""):
        """Log test step with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        logger.info(f"[{timestamp}] {step}")
        if details:
            logger.info(f"    {details}")

    def check_system_health(self) -> bool:
        """Verify system is ready for testing"""
        self.log_test_step("🔍 Checking system health...")

        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.log_test_step("✅ System health check passed")
                return True
            else:
                self.log_test_step("❌ System health check failed", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test_step("❌ System health check failed", f"Error: {e}")
            return False

    def get_system_status(self) -> Dict[str, Any]:
        """Get detailed system status"""
        self.log_test_step("📊 Getting system status...")

        try:
            response = self.session.get(f"{self.base_url}/api/status")
            if response.status_code == 200:
                status = response.json()
                self.log_test_step("✅ System status retrieved")

                # Log key system info
                systems = status.get("systems", {})
                simple_status = systems.get("simple_gemini", {}).get("status", "unknown")
                advanced_status = systems.get("advanced_handywriterz", {}).get("status", "unknown")

                self.log_test_step("📋 System Capabilities:",
                    f"Simple: {simple_status}, Advanced: {advanced_status}")

                return status
            else:
                self.log_test_step("❌ Failed to get system status", f"Status: {response.status_code}")
                return {}
        except Exception as e:
            self.log_test_step("❌ Failed to get system status", f"Error: {e}")
            return {}

    def analyze_request_complexity(self, prompt: str, user_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze how the system would route a request"""
        self.log_test_step("🔍 Analyzing request complexity...")

        try:
            data = {"message": prompt}
            if user_params:
                data["user_params"] = json.dumps(user_params)

            response = self.session.post(f"{self.base_url}/api/analyze", data=data)

            if response.status_code == 200:
                analysis = response.json()
                routing = analysis.get("routing_decision", {})

                self.log_test_step("✅ Complexity analysis completed",
                    f"System: {routing.get('system')}, Score: {routing.get('complexity'):.1f}")

                return analysis
            else:
                self.log_test_step("❌ Complexity analysis failed", f"Status: {response.status_code}")
                return {}
        except Exception as e:
            self.log_test_step("❌ Complexity analysis failed", f"Error: {e}")
            return {}

    def send_chat_request(self, prompt: str, user_params: Dict[str, Any] = None,
                         endpoint: str = "/api/chat") -> Dict[str, Any]:
        """Send chat request and measure response"""
        self.log_test_step(f"💬 Sending chat request to {endpoint}...")
        self.log_test_step("📝 Prompt:", prompt[:100] + "..." if len(prompt) > 100 else prompt)

        start_time = time.time()

        try:
            data = {"prompt": prompt}
            if user_params:
                data["user_params"] = user_params

            # Use JSON for the unified endpoint
            if endpoint == "/api/chat":
                response = self.session.post(f"{self.base_url}{endpoint}", json=data)
            else:
                # Use form data for specific endpoints
                form_data = {"message": prompt}
                if user_params:
                    form_data["user_params"] = json.dumps(user_params)
                response = self.session.post(f"{self.base_url}{endpoint}", data=form_data)

            response_time = time.time() - start_time

            if response.status_code in [200, 202]:
                result = response.json()

                # Log response details
                system_used = result.get("system_used", "unknown")
                success = result.get("success", False)
                response_length = len(result.get("response", ""))

                self.log_test_step("✅ Chat request completed",
                    f"System: {system_used}, Success: {success}, Time: {response_time:.2f}s, Length: {response_length} chars")

                result["_test_metadata"] = {
                    "response_time": response_time,
                    "endpoint": endpoint,
                    "status_code": response.status_code
                }

                return result
            else:
                self.log_test_step("❌ Chat request failed",
                    f"Status: {response.status_code}, Time: {response_time:.2f}s")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "_test_metadata": {
                        "response_time": response_time,
                        "endpoint": endpoint,
                        "status_code": response.status_code
                    }
                }
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_step("❌ Chat request failed", f"Error: {e}, Time: {response_time:.2f}s")
            return {
                "success": False,
                "error": str(e),
                "_test_metadata": {
                    "response_time": response_time,
                    "endpoint": endpoint,
                    "error": str(e)
                }
            }

    def validate_response_quality(self, result: Dict[str, Any], scenario: TestScenario) -> Dict[str, Any]:
        """Validate response meets expected quality criteria"""
        self.log_test_step("🔍 Validating response quality...")

        validation = {
            "passed": True,
            "issues": [],
            "score": 0,
            "details": {}
        }

        # Check basic success
        if not result.get("success", False):
            validation["issues"].append("Request failed")
            validation["passed"] = False
        else:
            validation["score"] += 20

        # Check response content
        response_text = result.get("response", "")
        if not response_text or len(response_text.strip()) < 10:
            validation["issues"].append("Response too short or empty")
            validation["passed"] = False
        else:
            validation["score"] += 30
            validation["details"]["response_length"] = len(response_text)

        # Check system routing
        system_used = result.get("system_used", "")
        expected_system = scenario.expected_system

        if expected_system == "auto":
            # For auto routing, just check that a system was used
            if system_used:
                validation["score"] += 20
            else:
                validation["issues"].append("No system routing information")
        elif expected_system in system_used:
            validation["score"] += 20
        else:
            validation["issues"].append(f"Expected {expected_system} system, got {system_used}")

        # Check response time
        response_time = result.get("_test_metadata", {}).get("response_time", 0)
        validation["details"]["response_time"] = response_time

        if scenario.complexity == QueryComplexity.SIMPLE and response_time > 10:
            validation["issues"].append("Simple query took too long")
        elif scenario.complexity == QueryComplexity.COMPLEX and response_time > 300:
            validation["issues"].append("Complex query took too long")
        else:
            validation["score"] += 15

        # Check expected features
        if scenario.expected_features:
            for feature in scenario.expected_features:
                if feature == "citations" and result.get("citation_count", 0) > 0:
                    validation["score"] += 5
                elif feature == "sources" and result.get("sources", []):
                    validation["score"] += 5
                elif feature == "quality_score" and result.get("quality_score"):
                    validation["score"] += 5

        # Final score calculation
        validation["score"] = min(100, validation["score"])

        if validation["passed"] and validation["score"] >= 70:
            self.log_test_step("✅ Response quality validation passed", f"Score: {validation['score']}/100")
        else:
            self.log_test_step("❌ Response quality validation failed",
                f"Score: {validation['score']}/100, Issues: {', '.join(validation['issues'])}")

        return validation

    def run_scenario(self, scenario: TestScenario) -> Dict[str, Any]:
        """Run a complete user journey scenario"""
        self.log_test_step(f"🚀 Starting scenario: {scenario.name}")
        self.log_test_step(f"📊 Complexity: {scenario.complexity.value}")

        scenario_result = {
            "scenario": scenario.name,
            "complexity": scenario.complexity.value,
            "start_time": time.time(),
            "steps": {}
        }

        # Step 1: Analyze complexity (optional, for insight)
        if scenario.complexity != QueryComplexity.SIMPLE:
            analysis = self.analyze_request_complexity(scenario.prompt, scenario.user_params)
            scenario_result["steps"]["complexity_analysis"] = analysis

        # Step 2: Send main request
        chat_result = self.send_chat_request(scenario.prompt, scenario.user_params)
        scenario_result["steps"]["chat_request"] = chat_result

        # Step 3: Validate response
        validation = self.validate_response_quality(chat_result, scenario)
        scenario_result["steps"]["validation"] = validation

        # Calculate overall success
        scenario_result["success"] = validation["passed"]
        scenario_result["quality_score"] = validation["score"]
        scenario_result["total_time"] = time.time() - scenario_result["start_time"]

        # Log scenario completion
        if scenario_result["success"]:
            self.log_test_step(f"✅ Scenario '{scenario.name}' completed successfully",
                f"Quality: {validation['score']}/100, Time: {scenario_result['total_time']:.2f}s")
        else:
            self.log_test_step(f"❌ Scenario '{scenario.name}' failed",
                f"Quality: {validation['score']}/100, Issues: {len(validation['issues'])}")

        return scenario_result

    def run_user_journey_test(self) -> Dict[str, Any]:
        """Run complete user journey test suite"""
        self.log_test_step("🎯 Starting User Journey Test Suite")

        # Test scenarios covering different user journeys
        scenarios = [
            # Simple queries - should use Gemini system
            TestScenario(
                name="Quick Question",
                prompt="What is artificial intelligence?",
                complexity=QueryComplexity.SIMPLE,
                expected_system="simple",
                expected_features=["fast_response"]
            ),

            TestScenario(
                name="Basic Explanation",
                prompt="Explain how machine learning works in simple terms",
                complexity=QueryComplexity.SIMPLE,
                expected_system="simple",
                expected_features=["fast_response"]
            ),

            # Medium complexity - should trigger hybrid or routing decision
            TestScenario(
                name="Detailed Analysis",
                prompt="Compare and contrast supervised and unsupervised machine learning algorithms with examples",
                complexity=QueryComplexity.MEDIUM,
                expected_system="auto",  # Let system decide
                expected_features=["detailed_response"]
            ),

            # Complex academic writing - should use HandyWriterz system
            TestScenario(
                name="Academic Essay",
                prompt="Write a comprehensive essay on the impact of artificial intelligence on modern education",
                complexity=QueryComplexity.COMPLEX,
                expected_system="advanced",
                user_params={
                    "writeupType": "essay",
                    "pages": 3,
                    "field": "education technology",
                    "citationStyle": "APA"
                },
                expected_features=["citations", "sources", "quality_score"]
            ),

            TestScenario(
                name="Research Paper",
                prompt="Create a research paper analyzing the ethical implications of AI in healthcare",
                complexity=QueryComplexity.COMPLEX,
                expected_system="advanced",
                user_params={
                    "writeupType": "research_paper",
                    "pages": 5,
                    "field": "healthcare ethics",
                    "citationStyle": "APA",
                    "includeAbstract": True
                },
                expected_features=["citations", "sources", "quality_score", "abstract"]
            )
        ]

        # Pre-flight checks
        if not self.check_system_health():
            return {"success": False, "error": "System health check failed"}

        system_status = self.get_system_status()

        # Run all scenarios
        test_results = {
            "test_suite": "User Journey Test",
            "start_time": time.time(),
            "system_status": system_status,
            "scenarios": [],
            "summary": {}
        }

        for scenario in scenarios:
            try:
                result = self.run_scenario(scenario)
                test_results["scenarios"].append(result)
                self.test_results.append(result)
            except Exception as e:
                self.log_test_step(f"❌ Scenario '{scenario.name}' crashed", f"Error: {e}")
                test_results["scenarios"].append({
                    "scenario": scenario.name,
                    "success": False,
                    "error": str(e),
                    "crashed": True
                })

        # Calculate summary
        total_scenarios = len(test_results["scenarios"])
        successful_scenarios = sum(1 for s in test_results["scenarios"] if s.get("success", False))
        average_quality = sum(s.get("quality_score", 0) for s in test_results["scenarios"]) / total_scenarios if total_scenarios > 0 else 0
        total_time = time.time() - test_results["start_time"]

        test_results["summary"] = {
            "total_scenarios": total_scenarios,
            "successful_scenarios": successful_scenarios,
            "success_rate": (successful_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0,
            "average_quality_score": average_quality,
            "total_test_time": total_time,
            "overall_success": successful_scenarios >= (total_scenarios * 0.8)  # 80% success threshold
        }

        # Log final results
        self.log_test_step("📊 User Journey Test Suite Completed")
        self.log_test_step(f"✅ Success Rate: {test_results['summary']['success_rate']:.1f}% ({successful_scenarios}/{total_scenarios})")
        self.log_test_step(f"📈 Average Quality: {average_quality:.1f}/100")
        self.log_test_step(f"⏱️  Total Time: {total_time:.2f}s")

        return test_results

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a detailed test report"""
        report = []
        report.append("# HandyWriterz User Journey Test Report")
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Summary
        summary = results["summary"]
        report.append("## Test Summary")
        report.append(f"- **Total Scenarios**: {summary['total_scenarios']}")
        report.append(f"- **Successful**: {summary['successful_scenarios']}")
        report.append(f"- **Success Rate**: {summary['success_rate']:.1f}%")
        report.append(f"- **Average Quality**: {summary['average_quality_score']:.1f}/100")
        report.append(f"- **Total Time**: {summary['total_test_time']:.2f}s")
        report.append(f"- **Overall Result**: {'✅ PASS' if summary['overall_success'] else '❌ FAIL'}")
        report.append("")

        # System Status
        if results.get("system_status"):
            status = results["system_status"]
            report.append("## System Status")
            systems = status.get("systems", {})
            report.append(f"- **Simple System**: {systems.get('simple_gemini', {}).get('status', 'unknown')}")
            report.append(f"- **Advanced System**: {systems.get('advanced_handywriterz', {}).get('status', 'unknown')}")
            report.append(f"- **Routing**: {'Enabled' if status.get('routing', {}).get('enabled') else 'Disabled'}")
            report.append("")

        # Scenario Details
        report.append("## Scenario Results")
        for scenario in results["scenarios"]:
            name = scenario.get("scenario", "Unknown")
            success = "✅ PASS" if scenario.get("success", False) else "❌ FAIL"
            quality = scenario.get("quality_score", 0)
            time_taken = scenario.get("total_time", 0)

            report.append(f"### {name}")
            report.append(f"- **Result**: {success}")
            report.append(f"- **Quality Score**: {quality}/100")
            report.append(f"- **Time**: {time_taken:.2f}s")

            # Add validation issues if any
            validation = scenario.get("steps", {}).get("validation", {})
            if validation.get("issues"):
                report.append(f"- **Issues**: {', '.join(validation['issues'])}")

            # Add system routing info
            chat_result = scenario.get("steps","chat_request", {})
            if chat_result.get("system_used"):
                report.append(f"- **System Used**: {chat_result['system_used']}")

            report.append("")

        return "\n".join(report)

def main():
    """Main test execution"""
    print("🚀 HandyWriterz User Journey Test")
    print("=" * 50)

    # Initialize tester
    tester = UserJourneyTester()

    # Run test suite
    results = tester.run_user_journey_test()

    # Generate and save report
    report = tester.generate_report(results)

    # Save results
    with open("user_journey_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    with open("user_journey_test_report.md", "w") as f:
        f.write(report)

    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Success Rate: {results['summary']['success_rate']:.1f}%")
    print(f"Average Quality: {results['summary']['average_quality_score']:.1f}/100")
    print(f"Overall Result: {'✅ PASS' if results['summary']['overall_success'] else '❌ FAIL'}")
    print("\n📄 Detailed report saved to: user_journey_test_report.md")
    print("📄 Raw results saved to: user_journey_test_results.json")

if __name__ == "__main__":
    main()
