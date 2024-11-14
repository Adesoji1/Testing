# # tts_service.py

# import boto3
# import logging
# import asyncio
# from botocore.exceptions import BotoCoreError, ClientError

# logger = logging.getLogger(__name__)

# class TTSService:
#     def __init__(self, polly_client=None, region_name: str = 'us-east-1', voice_id: str = 'Joanna'):
#         """Initialize AWS Polly client."""
#         self.polly_client = polly_client or boto3.client('polly', region_name=region_name)
#         self.voice_id = voice_id

#     async def convert_text_to_speech(self, text: str) -> bytes:
#         """Convert text to speech using Amazon Polly.

#         Args:
#             text (str): The text to convert to speech.

#         Returns:
#             bytes: The synthesized speech audio in MP3 format.
#         """
#         try:
#             loop = asyncio.get_event_loop()
#             response = await loop.run_in_executor(
#                 None,
#                 lambda: self.polly_client.synthesize_speech(
#                     Text=text,
#                     OutputFormat='mp3',
#                     VoiceId=self.voice_id
#                 )
#             )
#             audio_stream = response.get('AudioStream')
#             audio_bytes = audio_stream.read()
#             logger.info("Text-to-speech conversion completed successfully using Amazon Polly.")
#             return audio_bytes
#         except (BotoCoreError, ClientError) as e:
#             logger.error(f"Amazon Polly error: {str(e)}")
#             raise e
#         except Exception as e:
#             logger.error(f"TTS error: {str(e)}")
#             raise e

# # Initialize the TTS service
# tts_service = TTSService(region_name='us-east-1')  # Replace with your AWS region if different



# tts_service.py

import boto3
import logging
import asyncio
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self, polly_client=None, region_name: str = 'us-east-1', voice_id: str = 'Joanna'):
        """Initialize AWS Polly client."""
        self.polly_client = polly_client or boto3.client('polly', region_name=region_name)
        self.voice_id = voice_id

    async def convert_text_to_speech(self, text: str) -> bytes:
        """Convert text to speech using Amazon Polly.

        Args:
            text (str): The text to convert to speech.

        Returns:
            bytes: The synthesized speech audio in MP3 format.
        """
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.polly_client.synthesize_speech(
                    Text=text,
                    OutputFormat='mp3',
                    VoiceId=self.voice_id
                )
            )
            logger.info(f"AWS Polly Response: {response}")
            audio_stream = response.get('AudioStream')
            audio_bytes = audio_stream.read()
            logger.info("Text-to-speech conversion completed successfully using Amazon Polly.")
            return audio_bytes
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Amazon Polly error: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"TTS error: {str(e)}")
            raise e

# Initialize the TTS service
tts_service = TTSService(region_name='us-east-1')  # Replace with your AWS region if different