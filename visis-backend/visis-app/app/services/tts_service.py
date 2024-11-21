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
#             logger.info(f"AWS Polly Response: {response}")
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


# tts_service.py asynchronous

# import boto3
# import logging
# from botocore.exceptions import BotoCoreError, ClientError

# logger = logging.getLogger(__name__)

# class TTSService:
#     def __init__(self, polly_client=None, region_name: str = 'us-east-1', voice_id: str = 'Joanna'):
#         """Initialize AWS Polly client."""
#         self.polly_client = polly_client or boto3.client('polly', region_name=region_name)
#         self.voice_id = voice_id

#     def convert_text_to_speech(self, text: str) -> bytes:
#         """Convert text to speech using Amazon Polly."""
#         try:
#             response = self.polly_client.synthesize_speech(
#                 Text=text,
#                 OutputFormat='mp3',
#                 VoiceId=self.voice_id
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

# import boto3
# import logging
# from botocore.exceptions import BotoCoreError, ClientError

# logger = logging.getLogger(__name__)

# class TTSService:
#     def __init__(self, region_name: str = 'us-east-1', voice_id: str = 'Joanna'):
#         """Initialize AWS Polly client."""
#         self.polly_client = boto3.client('polly', region_name=region_name)
#         self.voice_id = voice_id

#     def convert_text_to_speech(self, text: str) -> bytes:
#         """Convert text to speech using Amazon Polly."""
#         try:
#             response = self.polly_client.synthesize_speech(
#                 Text=text,
#                 OutputFormat='mp3',
#                 VoiceId=self.voice_id
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
#app/services/tts_service.py

import boto3
# import tuple
import logging
from botocore.exceptions import BotoCoreError, ClientError
from app.core.config import settings
from typing import Tuple, Dict, List

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self, region_name: str = 'us-east-1', voice_id: str = 'Joanna'):
        """Initialize AWS Polly client."""
        self.polly_client = boto3.client('polly', region_name=region_name)
        self.voice_id = voice_id

    def convert_text_to_speech(self, text: str, detected_language: str = 'en') -> bytes:
        """Convert text to speech using Amazon Polly."""
        try:
            # Map detected language to Polly voice ID and language code
            voice_id, language_code = self.get_voice_id_and_language_code(detected_language)
        
            logger.debug(f"Detected language: {detected_language}")
            logger.debug(f"Using voice ID: {voice_id}")
            logger.debug(f"Using language code: {language_code}")
            response = self.polly_client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=self.voice_id,
                LanguageCode=language_code
            )
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
        
    # def get_voice_id_and_language_code(self, detected_language: str) -> Tuple[str, str]:
    #     """Map detected language code to a Polly voice ID and language code."""
    #     language_voice_map = {
    #         'en': ('Joanna', 'en-US'),
    #         'es': ('Lucia', 'es-ES'),
    #         'fr': ('Celine', 'fr-FR'),
    #         'de': ('Hans', 'de-DE'),
    #         'it': ('Carla', 'it-IT'),
    #         'pt': ('Ines', 'pt-PT'),
    #         'ru': ('Tatyana', 'ru-RU'),
    #         'ja': ('Mizuki', 'ja-JP'),
    #         'ko': ('Seoyeon', 'ko-KR'),
    #         # Add more mappings as needed
    #     }
    #     default_voice = ('Joanna', 'en-US')
    #     return language_voice_map.get(detected_language, default_voice)
    

    def get_voice_id_and_language_code(self, detected_language: str) -> Tuple[str, str]:
        """Map detected language code to a Polly voice ID and language code."""
        language_voice_map = {
            'en': ('Joanna', 'en-US'),  # Default for English
            'es': ('Lucia', 'es-ES'),  # European Spanish
            'fr': ('Celine', 'fr-FR'),  # French
            'de': ('Marlene', 'de-DE'),  # German
            'it': ('Carla', 'it-IT'),  # Italian
            'pt': ('Ines', 'pt-PT'),  # Portuguese (European)
            'ru': ('Tatyana', 'ru-RU'),  # Russian
            'ja': ('Mizuki', 'ja-JP'),  # Japanese
            'ko': ('Seoyeon', 'ko-KR'),  # Korean
            'ar': ('Zeina', 'arb'),  # Arabic
            'ar-AE': ('Hala', 'ar-AE'),  # Arabic (Gulf)
            'nl': ('Lotte', 'nl-NL'),  # Dutch (Netherlands)
            'nl-BE': ('Lisa', 'nl-BE'),  # Dutch (Belgian)
            'ca': ('Arlet', 'ca-ES'),  # Catalan
            'cs': ('Jitka', 'cs-CZ'),  # Czech
            'yue': ('Hiujin', 'yue-CN'),  # Cantonese
            'cmn': ('Zhiyu', 'cmn-CN'),  # Mandarin
            'da': ('Naja', 'da-DK'),  # Danish
            'fi': ('Suvi', 'fi-FI'),  # Finnish
            'fr-BE': ('Isabelle', 'fr-BE'),  # French (Belgian)
            'fr-CA': ('Chantal', 'fr-CA'),  # French (Canadian)
            'de-AT': ('Hannah', 'de-AT'),  # German (Austrian)
            'de-CH': ('Sabrina', 'de-CH'),  # German (Swiss)
            'hi': ('Aditi', 'hi-IN'),  # Hindi
            'is': ('Dora', 'is-IS'),  # Icelandic
            'nb': ('Liv', 'nb-NO'),  # Norwegian
            'pl': ('Ewa', 'pl-PL'),  # Polish
            'pt-BR': ('Camila', 'pt-BR'),  # Portuguese (Brazilian)
            'ro': ('Carmen', 'ro-RO'),  # Romanian
            'es-MX': ('Mia', 'es-MX'),  # Spanish (Mexican)
            'es-US': ('Penelope', 'es-US'),  # Spanish (US)
            'sv': ('Astrid', 'sv-SE'),  # Swedish
            'tr': ('Filiz', 'tr-TR'),  # Turkish
            'cy': ('Gwyneth', 'cy-GB'),  # Welsh
        }

        default_voice = ('Joanna', 'en-US')  # Default to US English if not matched
        return language_voice_map.get(detected_language, default_voice)
    
    def get_all_language_voices(self) -> Dict[str, List[str]]:
        """Retrieve all available language-to-voice mappings."""
        return {
            'en': ['Joanna', 'Matthew', 'Ivy', 'Salli', 'Joey', 'Danielle', 'Gregory', 'Kendra', 'Kimberly', 'Ruth', 'Stephen', 'Patrick'],
            'es': ['Lucia', 'Conchita', 'Mia', 'Andrés', 'Lupe', 'Penélope', 'Miguel', 'Pedro'],
            'fr': ['Céline', 'Léa', 'Mathieu', 'Rémi', 'Isabelle', 'Chantal', 'Gabrielle', 'Liam'],
            'de': ['Hans', 'Vicki', 'Marlene', 'Daniel', 'Hannah', 'Sabrina'],
            'nl': ['Lotte', 'Laura', 'Ruben', 'Lisa'],
            'ar': ['Zeina', 'Hala', 'Zayd'],
            'ca': ['Arlet'],
            'cs': ['Jitka'],
            'yue': ['Hiujin'],
            'cmn': ['Zhiyu'],
            'da': ['Naja', 'Mads', 'Sofie'],
            'en-AU': ['Nicole', 'Olivia', 'Russell'],
            'en-GB': ['Amy', 'Emma', 'Brian', 'Arthur', 'Geraint'],
            'en-IN': ['Aditi', 'Raveena', 'Kajal'],
            'en-IE': ['Niamh'],
            'en-NZ': ['Aria'],
            'en-ZA': ['Ayanda'],
            'fi': ['Suvi'],
            'fr-CA': ['Chantal', 'Gabrielle', 'Liam'],
            'fr-BE': ['Isabelle'],
            'hi': ['Aditi', 'Kajal'],
            'is': ['Dóra', 'Karl'],
            'it': ['Carla', 'Bianca', 'Giorgio', 'Adriano'],
            'ja': ['Mizuki', 'Takumi', 'Kazuha', 'Tomoko'],
            'ko': ['Seoyeon'],
            'nb': ['Liv', 'Ida'],
            'pl': ['Ewa', 'Maja', 'Jacek', 'Jan', 'Ola'],
            'pt-BR': ['Camila', 'Vitória', 'Ricardo', 'Thiago'],
            'pt-PT': ['Inês', 'Cristiano'],
            'ro': ['Carmen'],
            'ru': ['Tatyana', 'Maxim'],
            'sv': ['Astrid', 'Elin'],
            'tr': ['Filiz', 'Burcu'],
            'cy': ['Gwyneth']
        }



# Initialize the TTS service
tts_service = TTSService(region_name=settings.REGION_NAME)
