class OCRProcessingError(Exception):
    """Exception raised for errors in the OCR processing."""
    def __init__(self, message="Error occurred during OCR processing"):
        self.message = message
        super().__init__(self.message)


class TTSProcessingError(Exception):
    """Exception raised for errors in the TTS processing."""
    def __init__(self, message="Error occurred during TTS processing"):
        self.message = message
        super().__init__(self.message)