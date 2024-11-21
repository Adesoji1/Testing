# services/vision_service.py
import os
import openai
import logging
from tenacity import retry, wait_random_exponential, stop_after_attempt
from openai.error import RateLimitError, OpenAIError, Timeout
from app.core.config import settings

# from openai  import RateLimitError, OpenAIError ,Timeout

logger = logging.getLogger(__name__)

       

class VisionService:
    def __init__(self,api_key: str):
        # openai.api_key = settings.OPENAI_API_KEY
        # openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = ""

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
        retry=(lambda retry_state: isinstance(retry_state.outcome.exception(), (RateLimitError, OpenAIError, Timeout)))
    )
    def analyze_image(self, image_url: str) -> str:
        """Analyze the image using GPT-4 Vision and return the description."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",  # Replace with the correct model name
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe the content of this image in detail."},
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    }
                ],
                max_tokens=1000,
            )
            description = response['choices'][0]['message']['content']
            logger.info(f"GPT-4 Vision description: {description}")
            return description
        except Exception as e:
            logger.error(f"GPT-4 Vision error: {str(e)}")
            raise e


