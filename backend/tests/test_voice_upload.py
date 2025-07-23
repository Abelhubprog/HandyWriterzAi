import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from io import BytesIO

# This assumes your FastAPI app instance is accessible for testing
# You might need to adjust the import path based on your project structure
from main import app 

class TestVoiceUpload(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    @patch('api.whisper.model')
    def test_voice_upload_transcription(self, mock_whisper_model):
        # Mock the transcription result
        mock_whisper_model.transcribe.return_value = {
            "text": "This is a test transcript.",
            "language": "en"
        }

        # Create a dummy MP3 file in memory
        dummy_mp3_content = b"dummy mp3 data"
        mp3_file = ("test.mp3", BytesIO(dummy_mp3_content), "audio/mpeg")

        response = self.client.post("/api/whisper", files={"file": mp3_file})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['transcript'], "This is a test transcript.")
        self.assertEqual(data['language'], "en")
        mock_whisper_model.transcribe.assert_called_once()

    def test_voice_upload_invalid_file_type(self):
        dummy_txt_content = b"this is not an mp3"
        txt_file = ("test.txt", BytesIO(dummy_txt_content), "text/plain")

        response = self.client.post("/api/whisper", files={"file": txt_file})

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid file type", response.json()['detail'])

if __name__ == '__main__':
    unittest.main()