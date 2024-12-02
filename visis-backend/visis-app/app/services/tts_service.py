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




# import requests
# import logging
# import time
# from app.core.config import settings
# from app.models import Document
# from sqlalchemy.orm import Session
# from typing import Tuple, List,Dict

# logger = logging.getLogger(__name__)

# class TTSService:
#     def __init__(self, api_key: str, language_code: str = "en-ng", gender: int = 0, voice_id: int = 0, age: int = 43):
#         """Initialize CAMB.AI client with default language set to Nigerian English (en-ng)."""
#         self.api_key = api_key
#         self.language_code = language_code  # Default to Nigerian English (en-ng)
#         self.gender = gender
#         self.voice_id = voice_id
#         self.age = age
#         self.camb_ai_url = "https://client.camb.ai/apis/tts"  # CAMB.AI URL

#     def create_tts(self, text: str) -> str:
#         """Send a request to Camb.AI to create a TTS task."""
#         headers = {
#             "x-api-key": self.api_key,
#             "Content-Type": "application/json"
#         }

#         # Use language ID for Nigerian English (en-ng) from Camb.AI
#         payload = {
#             "text": text,
#             "language": 43,  # Nigeria English language ID from CAMB.AI
#             "gender": self.gender,
#             "voice_id": self.voice_id,
#             "age": self.age
#         }

#         try:
#             response = requests.post(self.camb_ai_url, json=payload, headers=headers)
#             response_data = response.json()
#             if response.status_code == 200:
#                 task_id = response_data.get('task_id')
#                 logger.info(f"TTS Task Created: {task_id}")
#                 return task_id
#             else:
#                 logger.error(f"Failed to create TTS task: {response.text}")
#                 return None
#         except Exception as e:
#             logger.error(f"Error creating TTS task: {str(e)}")
#             return None

#     def poll_tts_status(self, task_id: str) -> str:
#         """Poll the TTS status to check if the audio file is ready."""
#         headers = {
#             "x-api-key": self.api_key
#         }

#         try:
#             response = requests.get(f"https://client.camb.ai/apis/tts_result/{task_id}", headers=headers)
#             response_data = response.json()
#             if response.status_code == 200:
#                 status = response_data.get('status')
#                 logger.info(f"TTS Task Status: {status}")
#                 return status
#             else:
#                 logger.error(f"Failed to poll TTS status: {response.text}")
#                 return None
#         except Exception as e:
#             logger.error(f"Error polling TTS status: {str(e)}")
#             return None

#     def get_tts_result(self, task_id: str) -> str:
#         """Fetch the TTS result once the task is complete."""
#         headers = {
#             "x-api-key": self.api_key
#         }

#         try:
#             response = requests.get(f"https://client.camb.ai/apis/tts_result/{task_id}", headers=headers, stream=True)
#             if response.status_code == 200:
#                 audio_url = response.json().get('audio_url')
#                 logger.info(f"Audio URL received: {audio_url}")
#                 return audio_url
#             else:
#                 logger.error(f"Failed to get TTS result: {response.text}")
#                 return None
#         except Exception as e:
#             logger.error(f"Error getting TTS result: {str(e)}")
#             return None

#     def get_voice_id_and_language_code(self, detected_language: str) -> Tuple[str, str]:
#         """Map detected language code to a voice ID and language code, with en-ng as default for English."""
#         # Using 'Gary' for Nigerian English (en-ng)
#         language_voice_map = {
#             'en-ng': ('Gary', 'en-NG'),  # Nigerian English language and voice mapping
#             'en': ('Gary', 'en-NG'),  # Default to Nigerian English if standard English is detected
#             'es': ('Lucia', 'es-ES'),  # European Spanish
#             'fr': ('Celine', 'fr-FR'),  # French
#             'de': ('Marlene', 'de-DE'),  # German
#             'it': ('Carla', 'it-IT'),  # Italian
#             'pt': ('Ines', 'pt-PT'),  # Portuguese (European)
#             'ru': ('Tatyana', 'ru-RU'),  # Russian
#             'ja': ('Mizuki', 'ja-JP'),  # Japanese
#             'ko': ('Seoyeon', 'ko-KR'),  # Korean
#             'ar': ('Zeina', 'arb'),  # Arabic
#             'ar-AE': ('Hala', 'ar-AE'),  # Arabic (Gulf)
#             'nl': ('Lotte', 'nl-NL'),  # Dutch (Netherlands)
#             'nl-BE': ('Lisa', 'nl-BE'),  # Dutch (Belgian)
#             'ca': ('Arlet', 'ca-ES'),  # Catalan
#             'cs': ('Jitka', 'cs-CZ'),  # Czech
#             'yue': ('Hiujin', 'yue-CN'),  # Cantonese
#             'cmn': ('Zhiyu', 'cmn-CN'),  # Mandarin
#             'da': ('Naja', 'da-DK'),  # Danish
#             'fi': ('Suvi', 'fi-FI'),  # Finnish
#             'fr-BE': ('Isabelle', 'fr-BE'),  # French (Belgian)
#             'fr-CA': ('Chantal', 'fr-CA'),  # French (Canadian)
#             'de-AT': ('Hannah', 'de-AT'),  # German (Austrian)
#             'de-CH': ('Sabrina', 'de-CH'),  # German (Swiss)
#             'hi': ('Aditi', 'hi-IN'),  # Hindi
#             'is': ('Dora', 'is-IS'),  # Icelandic
#             'nb': ('Liv', 'nb-NO'),  # Norwegian
#             'pl': ('Ewa', 'pl-PL'),  # Polish
#             'pt-BR': ('Camila', 'pt-BR'),  # Portuguese (Brazilian)
#             'ro': ('Carmen', 'ro-RO'),  # Romanian
#             'es-MX': ('Mia', 'es-MX'),  # Spanish (Mexican)
#             'es-US': ('Penelope', 'es-US'),  # Spanish (US)
#             'sv': ('Astrid', 'sv-SE'),  # Swedish
#             'tr': ('Filiz', 'tr-TR'),  # Turkish
#             'cy': ('Gwyneth', 'cy-GB'),  # Welsh
#         }

#         # Default voice and language for unsupported language codes
#         default_voice = ('Gary', 'en-NG')  # Default to Nigerian English (Gary)
#         return language_voice_map.get(detected_language, default_voice)
    
#     def get_all_language_voices(self) -> Dict[str, List[str]]:
#         """Retrieve all available language-to-voice mappings."""
#         return {
#             'en': ['Joanna', 'Matthew', 'Ivy', 'Salli', 'Joey', 'Danielle', 'Gregory', 'Kendra', 'Kimberly', 'Ruth', 'Stephen', 'Patrick'],
#             'es': ['Lucia', 'Conchita', 'Mia', 'Andrés', 'Lupe', 'Penélope', 'Miguel', 'Pedro'],
#             'fr': ['Céline', 'Léa', 'Mathieu', 'Rémi', 'Isabelle', 'Chantal', 'Gabrielle', 'Liam'],
#             'de': ['Hans', 'Vicki', 'Marlene', 'Daniel', 'Hannah', 'Sabrina'],
#             'nl': ['Lotte', 'Laura', 'Ruben', 'Lisa'],
#             'ar': ['Zeina', 'Hala', 'Zayd'],
#             'ca': ['Arlet'],
#             'cs': ['Jitka'],
#             'yue': ['Hiujin'],
#             'cmn': ['Zhiyu'],
#             'da': ['Naja', 'Mads', 'Sofie'],
#             'en-AU': ['Nicole', 'Olivia', 'Russell'],
#             'en-GB': ['Amy', 'Emma', 'Brian', 'Arthur', 'Geraint'],
#             'en-IN': ['Aditi', 'Raveena', 'Kajal'],
#             'en-IE': ['Niamh'],
#             'en-NZ': ['Aria'],
#             'en-ZA': ['Ayanda'],
#             'fi': ['Suvi'],
#             'fr-CA': ['Chantal', 'Gabrielle', 'Liam'],
#             'fr-BE': ['Isabelle'],
#             'hi': ['Aditi', 'Kajal'],
#             'is': ['Dóra', 'Karl'],
#             'it': ['Carla', 'Bianca', 'Giorgio', 'Adriano'],
#             'ja': ['Mizuki', 'Takumi', 'Kazuha', 'Tomoko'],
#             'ko': ['Seoyeon'],
#             'nb': ['Liv', 'Ida'],
#             'pl': ['Ewa', 'Maja', 'Jacek', 'Jan', 'Ola'],
#             'pt-BR': ['Camila', 'Vitória', 'Ricardo', 'Thiago'],
#             'pt-PT': ['Inês', 'Cristiano'],
#             'ro': ['Carmen'],
#             'ru': ['Tatyana', 'Maxim'],
#             'sv': ['Astrid', 'Elin'],
#             'tr': ['Filiz', 'Burcu'],
#             'cy': ['Gwyneth'],
#             'en-ng': ['Gary'],  # Only Gary is available for Nigerian English
#             'en': ['Gary'],  # Fallback to Nigerian English if standard English is detected
#         }

    
 

# # Initialize the TTS service
# tts_service = TTSService(api_key=settings.TTS_API_KEY, language_code='en-ng')  # Default to Nigerian English
