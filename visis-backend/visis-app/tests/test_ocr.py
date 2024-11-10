import unittest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch, MagicMock
from app.services.ocr_service import OCRService
import asyncio

class TestOCRService(unittest.TestCase):
    @patch("app.services.ocr_service.boto3.client")  # Mock boto3 client creation
    def test_extract_text_from_image(self, mock_boto_client):
        # Load the image file as bytes
        image_path = r"C:\Users\testing\Desktop\mock.png"
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()

        # Mock the Textract client and its detect_document_text method
        mock_textract_client = MagicMock()
        mock_textract_client.detect_document_text.return_value = {
            "Blocks": [
                {"BlockType": "LINE", "DetectedText": "Sample extracted text from image"}
            ]
        }
        mock_boto_client.return_value = mock_textract_client

        # Initialize OCRService
        ocr_service = OCRService()

        # Run the async extract_text_from_image function within the test
        text, language = asyncio.run(ocr_service.extract_text_from_image(image_bytes))
        
        # Assertions
        self.assertEqual(text, "Sample extracted text from image")
        self.assertEqual(language, "en")
        mock_textract_client.detect_document_text.assert_called_once_with(
            Document={"Bytes": image_bytes}
        )

if __name__ == "__main__":
    unittest.main()
