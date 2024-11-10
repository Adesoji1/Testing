import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import asyncio

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ocr_service import OCRService
from app.core.config import settings
import unittest
from unittest.mock import patch, MagicMock
import asyncio
from app.services.tts_service import TTSService

class TestTTSService(unittest.TestCase):
    @patch("app.services.tts_service.boto3.client")  # Patch boto3 client creation
    def test_convert_text_to_speech(self, mock_boto_client):
        # Mock the Polly client and its synthesize_speech method
        mock_polly_client = MagicMock()
        mock_polly_client.synthesize_speech.return_value = {
            "AudioStream": MagicMock(read=lambda: b"Fake MP3 audio content")
        }
        mock_boto_client.return_value = mock_polly_client

        # Initialize TTSService
        tts_service = TTSService()
        text_to_convert = "Hello, this is a test."

        # Run the async convert_text_to_speech function within the test
        audio_content = asyncio.run(tts_service.convert_text_to_speech(text_to_convert))
        
        # Assertions
        self.assertEqual(audio_content, b"Fake MP3 audio content")
        mock_polly_client.synthesize_speech.assert_called_once_with(
            Text=text_to_convert,
            OutputFormat='mp3',
            VoiceId=tts_service.voice_id
        )

if __name__ == "__main__":
    unittest.main()
