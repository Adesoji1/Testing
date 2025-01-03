# # app/services/ocr_service.py
# import boto3
# import logging
# from typing import Tuple, Optional
# from botocore.exceptions import BotoCoreError, ClientError
# from app.core.config import settings
# import time
# from fastapi import HTTPException, status


# logger = logging.getLogger(__name__)

# class OCRService:
#     def __init__(self, region_name: str = 'us-east-1'):
#         """Initialize AWS Textract and S3 clients."""
#         self.textract_client = boto3.client('textract', region_name=region_name)
#         self.s3_client = boto3.client('s3', region_name=region_name)
#         self.comprehend_client = boto3.client('comprehend', region_name=region_name)

#     def detect_language(self, text: str) -> Optional[str]:
#         """Detect the dominant language in the text using AWS Comprehend."""
#         try:
#             response = self.comprehend_client.detect_dominant_language(Text=text[:5000])
#             languages = response.get('Languages', [])
#             if languages:
#                 dominant_language = languages[0]['LanguageCode']
#                 logger.info(f"Detected language: {dominant_language}")
#                 return dominant_language
#             else:
#                 logger.info("No dominant language detected.")
#                 return None
#         except (BotoCoreError, ClientError) as e:
#             logger.error(f"AWS Comprehend error: {str(e)}")
#             return None
#         except Exception as e:
#             logger.error(f"Language detection error: {str(e)}")
#             return None
        
    
    
#     def extract_text_from_pdf(self, bucket_name: str, file_key: str) -> Tuple[str, Optional[str]]:
#         """
#         Extract text from a PDF using Amazon Textract asynchronous API.
#         This handles multi-page PDFs properly.
#         """
#         try:
#             logger.info("Starting text extraction from PDF using AWS Textract (async).")

#             # 1) Start text detection job
#             response = self.textract_client.start_document_text_detection(
#                 DocumentLocation={
#                      'S3Object': {
#                          'Bucket': bucket_name,
#                          'Name': file_key
#                      }
#                 }
#             )
#             job_id = response['JobId']
#             logger.info(f"Started AWS Textract job with JobId: {job_id}")

#             # 2) Wait for job to complete
#             self._wait_for_job_completion(job_id, bucket_name, file_key)
#             # self._wait_for_job_completion(job_id)

#             # 3) Retrieve the job results
#             text = self._get_job_results(job_id)

#             # 4) Detect language (optional)
#             detected_language = self.detect_language(text)
#             if not detected_language:
#                 detected_language = "en"

#             logger.info("Text extraction from PDF completed successfully using AWS Textract (async).")
#             return text, detected_language

#         except (BotoCoreError, ClientError) as e:
#             logger.error(f"AWS Textract error: {str(e)}")
#             raise e
#         except Exception as e:
#             logger.error(f"OCR error: {str(e)}")
#             raise e

   
        
        

#     def extract_text_from_image(self, bucket_name: str, file_key: str) -> Tuple[str, Optional[str]]:
#         """Extract text from an image using Amazon Textract."""
#         try:
#             logger.info("Starting text extraction from image using AWS Textract.")

#             # Get the image bytes from S3
#             image_bytes = self.s3_client.get_object(Bucket=bucket_name, Key=file_key)['Body'].read()

#             # Call Textract to detect text in the image
#             response = self.textract_client.detect_document_text(
#                 Document={'Bytes': image_bytes}
#             )

#             # Extract text from response
#             text = '\n'.join([
#                 item['Text'] for item in response['Blocks']
#                 if item['BlockType'] == 'LINE'
#             ])

#             detected_language = self.detect_language(text) # Modify this if you handle multiple language

#             logger.info("Text extraction from image completed successfully using AWS Textract.")
#             return text, detected_language
#         except (BotoCoreError, ClientError) as e:
#             logger.error(f"AWS Textract error: {str(e)}")
#             raise e
#         except Exception as e:
#             logger.error(f"OCR error: {str(e)}")
#             raise e
        
#      #New method for TXT files
#     def extract_text_from_txt(self, bucket_name: str, file_key: str) -> Tuple[str, Optional[str]]:
#         """Extract text from a TXT file."""
#         try:
#             logger.info("Starting text extraction from TXT file.")
#             obj = self.s3_client.get_object(Bucket=bucket_name, Key=file_key)
#             text = obj['Body'].read().decode('utf-8')
#             detected_language = self.detect_language(text)
#             logger.info("Text extraction from TXT file completed successfully.")
#             return text, detected_language
#         except (BotoCoreError, ClientError) as e:
#             logger.error(f"AWS S3 error: {str(e)}")
#             raise e
#         except Exception as e:
#             logger.error(f"OCR error: {str(e)}")
#             raise e

   
           
              
#     def _wait_for_job_completion(self, job_id: str, bucket_name: str, file_key: str, retries: int = 3):
#         """Wait for AWS Textract job to complete with retries."""
#         max_wait_time = 1246  # Total wait time in seconds
#         wait_interval = 5    # Interval between polls
#         total_waited = 0

#         for attempt in range(retries):
#             while total_waited < max_wait_time:
#                 response = self.textract_client.get_document_text_detection(JobId=job_id)
#                 status = response['JobStatus']
#                 if status == 'SUCCEEDED':
#                     logger.info("AWS Textract job succeeded.")
#                     return
#                 elif status == 'FAILED':
#                     logger.error(f"AWS Textract job {job_id} failed.")
#                     break  # Exit to retry
#                 else:
#                     logger.info(f"Waiting for AWS Textract job to complete... ({total_waited}s elapsed)")
#                     time.sleep(wait_interval)
#                     total_waited += wait_interval

#             logger.warning(f"Retrying Textract job {job_id} (Attempt {attempt + 1}/{retries})")
#             response = self.textract_client.start_document_text_detection(
#                 DocumentLocation={'S3Object': {'Bucket': bucket_name, 'Name': file_key}}
#             )
#             job_id = response['JobId']
#             total_waited = 0  # Reset wait time for retry

#         raise Exception('AWS Textract job timed out after multiple retries.') 

  

#     def _get_job_results(self, job_id: str) -> str:
#         """Retrieve results from completed AWS Textract job."""
#         text_lines = []

#         next_token = None
#         while True:
#             if next_token:
#                 response = self.textract_client.get_document_text_detection(
#                     JobId=job_id,
#                     NextToken=next_token
#                 )
#             else:
#                 response = self.textract_client.get_document_text_detection(JobId=job_id)

#             blocks = response.get('Blocks', [])
#             for block in blocks:
#                 if block['BlockType'] == 'LINE':
#                     text_lines.append(block['Text'])

#             next_token = response.get('NextToken', None)
#             if not next_token:
#                 break
#             else:
#                 logger.info(f"Fetching next page of results with NextToken: {next_token}")

#         return '\n'.join(text_lines)

# # Initialize the OCR service
# ocr_service = OCRService(region_name=settings.REGION_NAME)



# app/services/ocr_service.py
import boto3
import logging
from typing import Tuple, Optional
from botocore.exceptions import BotoCoreError, ClientError
from app.core.config import settings
import time

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self, region_name: str = 'us-east-1'):
        """Initialize AWS Textract and S3 clients."""
        self.textract_client = boto3.client('textract', region_name=region_name)
        self.s3_client = boto3.client('s3', region_name=region_name)
        self.comprehend_client = boto3.client('comprehend', region_name=region_name)

    def detect_language(self, text: str) -> Optional[str]:
        """Detect the dominant language in the text using AWS Comprehend."""
        try:
            response = self.comprehend_client.detect_dominant_language(Text=text[:5000])
            languages = response.get('Languages', [])
            if languages:
                dominant_language = languages[0]['LanguageCode']
                logger.info(f"Detected language: {dominant_language}")
                return dominant_language
            else:
                logger.info("No dominant language detected.")
                return None
        except (BotoCoreError, ClientError) as e:
            logger.error(f"AWS Comprehend error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return None

    def extract_text_from_pdf(self, bucket_name: str, file_key: str) -> Tuple[str, Optional[str]]:
        """Extract text from a PDF using Amazon Textract asynchronous API."""
        try:
            logger.info("Starting text extraction from PDF using AWS Textract.")

            # Start text detection job
            response = self.textract_client.start_document_text_detection(
                DocumentLocation={
                    'S3Object': {
                        'Bucket': bucket_name,
                        'Name': file_key
                    }
                }
            )
            job_id = response['JobId']
            logger.info(f"Started AWS Textract job with JobId: {job_id}")

            # Poll for job completion
            self._wait_for_job_completion(job_id)

            # Retrieve job results
            text = self._get_job_results(job_id)

            detected_language = 'en'  # Modify this if you handle multiple languages

            logger.info("Text extraction from PDF completed successfully using AWS Textract.")
            return text, detected_language
        except (BotoCoreError, ClientError) as e:
            logger.error(f"AWS Textract error: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"OCR error: {str(e)}")
            raise e

    def extract_text_from_image(self, bucket_name: str, file_key: str) -> Tuple[str, Optional[str]]:
        """Extract text from an image using Amazon Textract."""
        try:
            logger.info("Starting text extraction from image using AWS Textract.")

            # Get the image bytes from S3
            image_bytes = self.s3_client.get_object(Bucket=bucket_name, Key=file_key)['Body'].read()

            # Call Textract to detect text in the image
            response = self.textract_client.detect_document_text(
                Document={'Bytes': image_bytes}
            )

            # Extract text from response
            text = '\n'.join([
                item['Text'] for item in response['Blocks']
                if item['BlockType'] == 'LINE'
            ])

            detected_language = self.detect_language(text) # Modify this if you handle multiple language

            logger.info("Text extraction from image completed successfully using AWS Textract.")
            return text, detected_language
        except (BotoCoreError, ClientError) as e:
            logger.error(f"AWS Textract error: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"OCR error: {str(e)}")
            raise e
        
     #New method for TXT files
    def extract_text_from_txt(self, bucket_name: str, file_key: str) -> Tuple[str, Optional[str]]:
        """Extract text from a TXT file."""
        try:
            logger.info("Starting text extraction from TXT file.")
            obj = self.s3_client.get_object(Bucket=bucket_name, Key=file_key)
            text = obj['Body'].read().decode('utf-8')
            detected_language = self.detect_language(text)
            logger.info("Text extraction from TXT file completed successfully.")
            return text, detected_language
        except (BotoCoreError, ClientError) as e:
            logger.error(f"AWS S3 error: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"OCR error: {str(e)}")
            raise e

    def _wait_for_job_completion(self, job_id: str):
        """Wait for AWS Textract job to complete."""
        while True:
            response = self.textract_client.get_document_text_detection(JobId=job_id)
            status = response['JobStatus']
            if status == 'SUCCEEDED':
                break
            elif status == 'FAILED':
                raise Exception('AWS Textract job failed.')
            else:
                logger.info("Waiting for AWS Textract job to complete...")
                time.sleep(1) #5

    def _get_job_results(self, job_id: str) -> str:
        """Retrieve results from completed AWS Textract job."""
        text_lines = []

        next_token = None
        while True:
            if next_token:
                response = self.textract_client.get_document_text_detection(
                    JobId=job_id,
                    NextToken=next_token
                )
            else:
                response = self.textract_client.get_document_text_detection(JobId=job_id)

            blocks = response.get('Blocks', [])
            for block in blocks:
                if block['BlockType'] == 'LINE':
                    text_lines.append(block['Text'])

            next_token = response.get('NextToken', None)
            if not next_token:
                break
            else:
                logger.info(f"Fetching next page of results with NextToken: {next_token}")

        return '\n'.join(text_lines)

# Initialize the OCR service
ocr_service = OCRService(region_name=settings.REGION_NAME)
