import unittest
from unittest.mock import patch, MagicMock
import json

from agent.nodes.memory_writer import MemoryWriter
from agent.handywriterz_state import HandyWriterzState

class TestMemoryWriter(unittest.TestCase):

    @patch('agent.nodes.memory_writer.get_supabase_client')
    def test_fingerprint_calculation(self, mock_get_supabase):
        # This test focuses on the fingerprint calculation logic
        writer = MemoryWriter("test_writer")
        text = "This is a test sentence. This is another one."
        fingerprint = writer._calculate_fingerprint(text)
        
        self.assertAlmostEqual(fingerprint['avg_sentence_len'], 5.5)
        self.assertAlmostEqual(fingerprint['lexical_diversity'], 0.727, places=3)

    @patch('agent.nodes.memory_writer.get_supabase_client')
    def test_fingerprint_merge(self, mock_get_supabase):
        writer = MemoryWriter("test_writer")
        old_fp = {"avg_sentence_len": 10.0, "lexical_diversity": 0.5}
        new_fp = {"avg_sentence_len": 20.0, "lexical_diversity": 0.8}
        
        merged = writer._merge_fingerprints(old_fp, new_fp, alpha=0.5)
        
        self.assertEqual(merged['avg_sentence_len'], 15.0)
        self.assertEqual(merged['lexical_diversity'], 0.65)

    @patch('agent.nodes.memory_writer.get_supabase_client')
    def test_execute_new_fingerprint(self, mock_get_supabase):
        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None

        writer = MemoryWriter("test_writer")
        state = HandyWriterzState(
            final_draft_content="A new draft for a new user.",
            user_id="new_user_123"
        )
        
        result = writer.execute(state)
        
        mock_supabase.table.return_value.insert.assert_called_once()
        self.assertIn("writing_fingerprint", result)
        self.assertIsNotNone(result["writing_fingerprint"])

    @patch('agent.nodes.memory_writer.get_supabase_client')
    def test_execute_update_fingerprint(self, mock_get_supabase):
        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        
        existing_data = {"fingerprint_json": json.dumps({"avg_sentence_len": 10.0})}
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = existing_data

        writer = MemoryWriter("test_writer")
        state = HandyWriterzState(
            final_draft_content="An updated draft.",
            user_id="existing_user_456"
        )
        
        result = writer.execute(state)
        
        mock_supabase.table.return_value.update.assert_called_once()
        self.assertIn("writing_fingerprint", result)
        self.assertIsNotNone(result["writing_fingerprint"])

if __name__ == '__main__':
    unittest.main()