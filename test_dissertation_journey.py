#!/usr/bin/env python3
"""
End-to-End User Journey Test for Dissertation Generation.

This test simulates a user requesting a dissertation outline and first draft
through the HandyWriterz platform. It starts the server, sends a detailed
prompt to the chat completions endpoint, and validates the response based
on the criteria outlined in Demo5.md.
"""

import asyncio
import json
import time
import requests
import logging
import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dissertation_journey_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class E2EDissertationTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.server_process = None

    def log_step(self, step: str, details: str = ""):
        """Log a test step with a timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        logger.info(f"[{timestamp}] {step}")
        if details:
            logger.info(f"    {details}")

    def start_server(self) -> bool:
        """Start the HandyWriterz server for testing."""
        self.log_step("🚀 Starting HandyWriterz server...")
        try:
            backend_dir = Path(__file__).parent.resolve() / "backend"
            if not backend_dir.exists():
                self.log_step("❌ Backend directory not found.")
                return False

            server_script = backend_dir / "handywriterz_server.py"
            if not server_script.exists():
                self.log_step(f"❌ Server script not found at {server_script}")
                return False

            self.server_process = subprocess.Popen(
                [sys.executable, str(server_script)],
                cwd=str(backend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Wait for the server to start
            max_wait = 60
            for i in range(max_wait):
                try:
                    response = requests.get(f"{self.base_url}/health")
                    if response.status_code == 200:
                        self.log_step("✅ Server started successfully.")
                        return True
                except requests.ConnectionError:
                    time.sleep(1)
            
            self.log_step("❌ Server failed to start within 60 seconds.")
            return False

        except Exception as e:
            self.log_step(f"❌ Exception while starting server: {e}")
            return False

    def stop_server(self):
        """Stop the test server."""
        if self.server_process:
            self.log_step("🔄 Stopping server...")
            self.server_process.terminate()
            self.server_process.wait()
            self.log_step("✅ Server stopped.")

    def test_dissertation_journey(self):
        """Run the full dissertation user journey test."""
        self.log_step("🎯 Starting Dissertation User Journey Test")

        dissertation_prompt = (
            "Write a 5000-word dissertation on the ethical implications of autonomous weapons, "
            "with a focus on international law. Use the APA citation style. The dissertation should "
            "include an introduction, a literature review, a methodology section, a detailed analysis, "
            "and a conclusion. Please also provide a list of potential sources."
        )

        payload = {
            "messages": [{"role": "user", "content": dissertation_prompt}],
            "model": "gpt-4",  # As seen in test_chat.html
            "stream": False,
            "user_params": {
                "writeupType": "dissertation",
                "pages": 5,
                "field": "international law",
                "citationStyle": "APA"
            }
        }

        self.log_step("💬 Sending dissertation request to the backend...", json.dumps(payload, indent=2))
        
        start_time = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat/completions",
                json=payload,
                timeout=600  # 10 minutes timeout for complex query
            )
            response_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                self.log_step(f"✅ Request successful in {response_time:.2f} seconds.")
                self.validate_dissertation_response(result)
            else:
                self.log_step(f"❌ Request failed with status code {response.status_code}")
                logger.error(f"Response body: {response.text}")

        except Exception as e:
            self.log_step(f"❌ An exception occurred: {e}")

    def validate_dissertation_response(self, response: Dict[str, Any]):
        """Validate the response for the dissertation journey."""
        self.log_step("🔍 Validating dissertation response...")

        # Based on Demo5.md, we expect a complex response
        # with multiple sections and sources.
        
        validation_passed = True
        
        if "choices" not in response or not response["choices"]:
            self.log_step("❌ 'choices' field is missing or empty in the response.")
            validation_passed = False
        else:
            content = response["choices"][0].get("message", {}).get("content", "")
            if not content:
                self.log_step("❌ Response content is empty.")
                validation_passed = False
            else:
                self.log_step("✅ Response content is present.")
                
                # Check for key dissertation sections
                expected_sections = ["introduction", "literature review", "methodology", "analysis", "conclusion", "references"]
                for section in expected_sections:
                    if section.lower() in content.lower():
                        self.log_step(f"✅ Found section: {section}")
                    else:
                        self.log_step(f"❌ Missing section: {section}")
                        validation_passed = False
        
        if "sources" in response and response["sources"]:
            self.log_step(f"✅ Found {len(response['sources'])} sources.")
        else:
            # This is not a critical failure, but worth noting
            self.log_step("⚠️ No 'sources' field found in the response.")

        if validation_passed:
            self.log_step("✅ Dissertation response validation successful.")
        else:
            self.log_step("❌ Dissertation response validation failed.")
            logger.info("Full response for debugging:")
            logger.info(json.dumps(response, indent=2))


def main():
    """Main test execution function."""
    tester = E2EDissertationTester()
    server_started = tester.start_server()

    if not server_started:
        logger.error("Halting tests because server failed to start.")
        return

    try:
        tester.test_dissertation_journey()
    finally:
        tester.stop_server()

if __name__ == "__main__":
    main()
