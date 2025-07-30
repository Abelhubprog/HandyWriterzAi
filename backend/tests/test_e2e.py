import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
import asyncio

from main import app # Assuming your FastAPI app is in main.py

class TestE2EWorkflow(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    @patch('agent.nodes.derivatives.Derivatives._generate_slide_bullets')
    @patch('agent.nodes.arweave.upload_to_arweave')
    def test_full_workflow_with_slides_and_arweave(self, mock_upload_arweave, mock_gen_slides):
        # Mock the external services
        mock_gen_slides.return_value = ["Slide 1", "Slide 2"]
        mock_upload_arweave.return_value = "arweave_tx_id_123"

        # This is a simplified e2e test that would need to be much more complex
        # in a real application. It would involve setting up a test database,
        # mocking all external API calls, and then running the full agent graph.
        
        # For now, we'll just simulate the final part of the workflow
        # where the derivatives and arweave nodes would be called.
        
        async def run_final_steps():
            from agent.nodes.derivatives import Derivatives
            from agent.nodes.arweave import Arweave
            from agent.handywriterz_state import HandyWriterzState

            derivatives_node = Derivatives("derivatives")
            arweave_node = Arweave("arweave")

            state = HandyWriterzState(
                final_draft_content="This is the final draft.",
                final_docx_content=b"docx content"
            )

            derivatives_result = await derivatives_node.execute(state)
            arweave_result = await arweave_node.execute(state)

            self.assertEqual(derivatives_result['slide_bullets'], ["Slide 1", "Slide 2"])
            self.assertEqual(arweave_result['arweave_transaction_id'], "arweave_tx_id_123")

        asyncio.run(run_final_steps())

if __name__ == '__main__':
    unittest.main()