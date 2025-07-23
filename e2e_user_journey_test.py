#!/usr/bthon3
"""
End-to-End User Journey
ts.

Available APIs:
- Gemini 2.5 Pro (for simple and advanced queries)
ing)

Test Focus: User journeys, not monkey testing
"""

import asyncio
import json
import time
import requests
import logging
import os
import sys
from typing import
from dataclasses import dataclass
from enum
import subprocess
from pathlib import Path

# Configurg
logging.basicConfig(
    level=logging.INFO,
,
    handlers=[
        logging.FileHang'),

    ]
)
logger = logging.getLogger(__name__)

class TestComplexity(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"

@dataclass
class UserJourneyScenario:
    name: str
    descrip str
    prompt: str
    complexity: TestComplexity
    expected_features: List[str]
    user_params: None
    files: Optional[List[str]] = None
    success_criteria: Optional[List[sne

ester:
    def __init__(self, base):
        self.e_url
        self.session =()
        self.test_results = []
        self.server_process = None

        # Check API keys
        self.gemini_key = os.getenv("GEMINI_A")
        self.)

        if no_key:
            logger.error("❌ GEMINI_API_KEY not found in environment")
            sys.exit(1)
        if not self.perplexity_key:
            logger.error("❌ PERPLEXITY_AP")
            sys.exit(1)

")

    def "):
        """Log test step with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        logger.info()
        if details:
            logger.inils}")

    def start_server(self) -> bool:
        """Start the HandyWriterz server for testin
        self.log_step("🚀 Starting HandyWriterz server...")

:
            # Change to backend directory
            backend_dir = Path(end"
            if not backend_dir.exists():
                backend_dir = Path(__fil

            # Start the server using the handywriterz_server.py
            server_script = backend_dir / "handywriterz_server.py"
            if not server_script.exists():
                # Try alternative locations
                server_script = .py"
.exists():
                    self.log_step("❌ Server script no
                    return False

            self.server_process = subprocess.Popen(
                [sys.executable, str(server_script)],
                cwd=str(backend_dir),
                stdout=subprocess.PIPE,
                stderPE


            # Wait for server to start
            max_wait = 30
            for i in range(max_wait):
                try:
                    response = requests.get(f"
                    if response.s
                        self.log_step("✅ Server st)

              except:
                    time(1)

            self.log_step("❌ Server failed to start within 30 seconds")
            return False

        except Exception as e:
       (e))
            retulse

    def stop_server(self):
        """Stop the test server"""
        if self.server_process:
            self.log_step("🔄 Stopping server...")
            self.server_process.terminate()
            self.server_process.wait()
            self.log_step("✅ Server stopped"

    def check_system_health(self) -> bl:
      "
        self.log_step

        try:
            response = se
            if response.status_code == 200:
                self.log_step("✅ System health check passed")
ue
            else:

                return False
        except Exception as e:
            self.log_step("❌ System health check failed", f"Error: {e}")
            return False

    y]:
        """"
        self.log_step("📊 Getting system status...")

        try:
            response = self.session.get(f"{self.base_url}/api/status", timeout=10)
            if response.status_code == 200:
                status = response.json()
                self.log_step("✅ S

                # Log key system info
                systems = status.get("systems", {})
                simple_status = systems.get("simple_gemini", {}).get("status", "unknn")
                advanced_status = systems.get("advanced_handywriterz")

      ies:",
              }")

            atus
            else:
                self.log_step(
                return {}
        except Exception as e:
            self.log_step(
 n {}

    def test_chat_endpoint(self, prompt: str, user_pny]:
        """Test the"""
        self.log_step(f"💬 Testing chat endpoint...")
        self.log_step("📝 Prompt:",

        start_time()

        t
            # Test the endpoint

                "prompt": prompt,
                "user_params"r {}
            }

            response = st(
                f"{self.base_url}/api/ch,
                json=data,
                timeout=300  # 5 minutes timeout for comueries
            )



           202]:
                result = response.json()

                # Letails




                self.log_step("✅ Chat request completed",
                    f"System: {system_usedars")

                result["_test_metadata"] = {
                    "response_time": response_time,
                  ",
             s_code
                }

                return result
            else:
                self.log_step("❌ Chat request failed",
                    f"Status: {response.status_code}, Time: {respo")
                return {
                    "success": Fal
                    "errode}",
               ": {
             ime,
                        "endpoint": "/api/chat",
                        "stus_code
                    }
                }
        except Exception as e:
            response_time = time.time() - start_time
            self.log_step("❌ Chat ref}s")
            return {
                "success": False,
                "error": str(e),
                "_test_metadata": {
                    "response_tim
                    "endpo",
e)
                }
            }

    def validate_response_quality(self, resuly]:
        """Validate response meets expe
        self.log_step("🔍 Validat)

        valation = {
            "passed": True,
            "issues": [],
            "score": 0,
            "details": {}
        }

        # Check basic success

            ")
            validation["passed"] = False
        else:
            validation["score"] += 25

        # Check response content
        response_text = result.get
        if not response_text or0:
y")
            validatiFalse
        else:
            validation["score"] += 25
            validation["details"]["response_lengtht)

        # Check response time
        response_time = result.get("_test_metadata)
        validation["detaime

        if scen

        elif scenario.complexity == TestComplexity.COMPLEX and response_time > 300:
            validation["issues"].append("Complex query took too long")
        else:
            validation["score"] += 20

        # Check expected features
        if scenario.expecteatures:
            for features:
            0:
                    validation["score"] += 5
                elif feature == "sources" and result.get("sources", []):
                    validation["score"] += 5
                elif feature == "quality_score" and result.get("quality_score"):
                    validation["score"] += 5
                elif feature == "system_routing" and red"):
                    v+= 5
                elif feature == "fast_response" and r10:
                    vali5
                elif feature =500:
                5

        # Check success criteria
        if scenario.success_criteria:
            for criteria in scenario.success_criteria:

                    validati
*"]):
                    validation["score"] += 5
                elif criteria == "academic_tone" and any(word in respon):
    ] += 5

        # Final score calculation
        validation["score"] = min(100, e"])

      >= 70:
            self.log_step("✅ Response quality validation passed", f"Score: {validati
        else:
            self.log_step("❌ Response quality valida
                f"Score: {vali])}")

        return validation

    def run_user_journey_scenariony]:
        """
        self.log_step(f"🚀 Starting scenario: {scenario.name}")
        self.log_step(f"📊 Complexity: {scenario.complexity.value}")
        self.log_st")


            "scenario.name,
            "description": scenario.desciption,
            "complexity": scenario.complexity.e,
            "start_time": time.time(),
            "steps": {}
        }

        # Step 1: Send chat request
        chat_result = self.test_chat_endpoint(scenario.prompt, scenario.usems)
        scenario_result["steps"]["chat_request"] = chat_result

        # Step 2: Validate response
ario)
        scenario_result

        # Calculate overall success
        scenario_result["success"] = validation["passed"]
        scenario_re"]
        scenario_result["total_time"] = time.time() - scenario_result["start_time"]

        # Log sion
        if scenario_result["success"]:
            self.log_step(f"✅ Scenario '{s

        else:
            self.log_step(f"❌ Scenario '{scenario.name}' failed",
                f"Quality: {validation['score']}/1)}")

        return scenario_result

    def run_comprehensive_user_journey_y]:
        """Run comprehensive user journey test su
        self.log_step("")


        # Define user journey scenarios
        scenarios = [
            # Simple queries - Quick responses
            UserJourneyScenario(
                name="Quick Question",
                description="Us",
                prompt="What is artificial intelligence and how does it work?",
                complexity=TestComplexity.SIMPLE,
                expected_features=["fast_response", "system_],
                success_criteria=se"]
            ),

            UserJourneyScenario(
                name="Basic Explan
       ,
                prompt="Explain mamples",
              ,
                expected_features=["fast_response", "detailed_response"],
                success_criteria=["contains_explanation", "structured_respoe"]
            ),

         s
            UserJourneyScenario(
                name="Comparative Analysis",
                description="Us",

                complexity=TestComplexity.MEDIUM,
                expected_features=["detailed_r"],
]
            ),

            UserJourneyScenario(
                name="Research Query",
                description="User",
        .",
                complexity=TestCoIUM,

                success_criteria=["academse"]
            ),

            # Complex academic wr
        nario(
       ",
                description="Ug",
                prompion.",
                complexity=
                expected_fea"],

    ",
                    "pages": 2,
                    "field": "education technology",
                    "citationStyle": "APA"

]
            ),

            UserJourneyScenario(
                name="Liter",
                description="User requests help wew",
                prom",
                complexity=TestCompLEX,
                exp],
                user_params={
                    "writeupType": "literature_re
                    "pages": 3,
                    "f
            "
                },
                success_criteria=["
            ),

            # Real-world user scenarios
            UserJ
                name="Student Homework
                description="Student needs help understanding a complex topic",
                prompt="I'm struggling to unde?",

                expec"],
"]
            ),

            UserJourneyScenario(
                name="Professional Research",
                description="Pr
                pros.",
                complexity=TestComplexity.COMPLEX,
                expected_features=["sources", "d"],
"]
            )
        ]

        # Pre-flight checks
        if not sel
            return {"success": False, "erro

()


        test_results = {
            "test_suite": "Comprehensive User Journey Test",
            "start_te(),
            "system_status": systus,
            "api_credits": {
",
               able"
            },
            "scenarios": [],
            "sum
        }

        fo
            try:
         )
                test_results["scenarios"].append(result)
                self.test_results.append(result)

                # Add delay between tests to respect rate limits


            except Exception as e:
                self.log_step)
                test_results["sced({
                    "scenario": scenario.name,
                    "succe
         ),
ue
                })

       mary
        total_scenarios = len(test_results["scenarios"])
        successful_scenarios = sum(1 for s in test_results["scenarios"] if s.get("success", False))
        average_quality = sum(s.get("quality else 0
        total_time = t

        test_results["summary"] = {
            "total_scenarios":
            "successful_scenarios": successful_scenarios,
            "success_rate": (successful_scenarios / total_scenarioselse 0,
e_quality,
          me,
            "overall_success": successful_scen
        }

esults
        self.loeted")
        self.log_step(f"✅ Success Rate: {test_results['summary']['success_rate']:.
        self.log_step(f"📈 /100")
        self.l")

        return

    def generate_detailed_report(self, results: Dict[str, Any]) -> str:
        """Generate a detailed test report"""
        report = []
        report.aort")

        report.append("")

        # Executive Summary
        s"]
        report.append("## Executiv")
        report.append(f"- **Test Sui
        report.append(f"- **Total Scenarios**: ios']}")
        report.append(f"- **Successful**: {summary['succes}")
        report.appen
        report.append(f"- **Aver0")
        report.append(f"- **Total Tim")
")
            rt.a("")

        #  Exceptions Used
sed")
        api_credits = r, {})
        report.append(f"- **Gemini 2.5 Pro**: {api_credits.get('ge)
        reporn')}")
        report.append("")

        # System Status
        if results.get("system_status"):
            status = results["system_status"]
            report.append("## System Status")
            systems = status.ge)
            report.append(f"- )
            repor
            report.append(f"- **Routing*")
"")

        # Scenario Results
        report.append("## Detailed Scenario Results
        for scenario in resul
            name = scenario.get("scenario", "Unkwn")
            description = scenario.get("desc")
L"
            quality = scenario.ge
            time_taken = scenario.get("total_ti)

            report.append(f"### {name}")
            report.append")
            report.append(f"- **Resul")
            report.append(f"- **Quality Score**: {quality}/100")
            report.append(f"- **Time**: {time_take

            # Add validation issue any
            validation = scenario.get("s {})
            if validation.get("issues"):
                report.append(f"- **Issues**: {', '.join")

           g info
            chat_result = scenario.get("steps", {}).get("chat_request", {})
            if chat_result.get(


      preview
            response = chat_result.get("r
            if response:
                preview = response[:200nse
                report.append(f"- **Response Preview}")

            report.append("")

        # Recommendons
        report.append("## Recommendations")
        if summary['success_rate'] >= 90:
          ")
        elif summary['success_rate'] >= 75:
            report.appen")
        e
            report.append("- ❌ Performance issues deteion")

        if summary['ave 70:
on")

        report.append("- 📊 Monitor API us)
        report.append("- 🔄ce")
        report.append("")

        return "\n".join(report)

def main():
    """Main test execution"""
    print("🚀 HandyWriterz E2E User Journe")
    print("=" * 60)
    print("🔑 Testing wit")
    print")
    print("=" * 60)

    # Initialize teer
    tester = E2E

    # Start
    server_started = False
    if not tester.check_:
        print("🚀 Starting test
rver()
        if not server_srted:
 ")


    try:
        #e
        results = tester.run_comprehensive_user_journey_

        # Gener report
        report = testults)

        # Save results
        with open("e2e_us f:
            json.dump(re

        with open("e2e_user_journey_report as f:
        )

        print("\n" + "=" * 60)
        printry:")

        print(f"Aver/100")
   )
")
        print("\")
        print("📄 Raw results saved to: ")
")

    finally:
      it
:
            tester.stop_server()

if __name__ == "
  main()
