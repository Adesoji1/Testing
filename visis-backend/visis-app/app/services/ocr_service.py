# # ocr_service.py

# import boto3
# import logging
# import asyncio
# from typing import Tuple, Optional
# from botocore.exceptions import BotoCoreError, ClientError

# logger = logging.getLogger(__name__)

# class OCRService:
#     def __init__(self, textract_client=None, s3_client=None, region_name: str = 'us-east-1'):
#         """Initialize AWS Textract and S3 clients."""
#         self.textract_client = textract_client or boto3.client('textract', region_name=region_name)
#         self.s3_client = s3_client or boto3.client('s3', region_name=region_name)

#     async def extract_text_from_pdf(self, bucket_name: str, file_key: str) -> Tuple[str, Optional[str]]:
#         """Extract text from a PDF using Amazon Textract asynchronous API.

#         Args:
#             bucket_name (str): The name of the S3 bucket.
#             file_key (str): The S3 key for the PDF file.

#         Returns:
#             Tuple[str, Optional[str]]: Extracted text and detected language code.
#         """
#         try:
#             logger.info("Starting text extraction from PDF using AWS Textract.")

#             # Start text detection job
#             loop = asyncio.get_event_loop()
#             response = await loop.run_in_executor(
#                 None,
#                 lambda: self.textract_client.start_document_text_detection(
#                     DocumentLocation={
#                         'S3Object': {
#                             'Bucket': bucket_name,
#                             'Name': file_key
#                         }
#                     }
#                 )
#             )
#             job_id = response['JobId']
#             logger.info(f"Started AWS Textract job with JobId: {job_id}")

#             # Poll for job completion
#             await self._wait_for_job_completion(job_id)

#             # Retrieve job results
#             text = await self._get_job_results(job_id)

#             detected_language = 'en'  # Modify this if you handle multiple languages

#             logger.info("Text extraction from PDF completed successfully using AWS Textract.")
#             return text, detected_language
#         except (BotoCoreError, ClientError) as e:
#             logger.error(f"AWS Textract error: {str(e)}")
#             raise e
#         except Exception as e:
#             logger.error(f"OCR error: {str(e)}")
#             raise e

#     async def extract_text_from_image(self, bucket_name: str, file_key: str) -> Tuple[str, Optional[str]]:
#         """Extract text from an image using Amazon Textract.

#         Args:
#             bucket_name (str): The name of the S3 bucket.
#             file_key (str): The S3 key for the image file.

#         Returns:
#             Tuple[str, Optional[str]]: Extracted text and detected language code.
#         """
#         try:
#             logger.info("Starting text extraction from image using AWS Textract.")

#             # Get the image bytes from S3
#             loop = asyncio.get_event_loop()
#             image_bytes = await loop.run_in_executor(
#                 None,
#                 lambda: self.s3_client.get_object(Bucket=bucket_name, Key=file_key)['Body'].read()
#             )

#             # Call Textract to detect text in the image
#             response = await loop.run_in_executor(
#                 None,
#                 lambda: self.textract_client.detect_document_text(
#                     Document={'Bytes': image_bytes}
#                 )
#             )

#             # Extract text from response
#             text = '\n'.join([
#                 item['Text'] for item in response['Blocks']
#                 if item['BlockType'] == 'LINE'
#             ])

#             detected_language = 'en'  # Modify this if you handle multiple languages

#             logger.info("Text extraction from image completed successfully using AWS Textract.")
#             return text, detected_language
#         except (BotoCoreError, ClientError) as e:
#             logger.error(f"AWS Textract error: {str(e)}")
#             raise e
#         except Exception as e:
#             logger.error(f"OCR error: {str(e)}")
#             raise e

#     async def _wait_for_job_completion(self, job_id: str):
#         """Wait for AWS Textract job to complete."""
#         while True:
#             loop = asyncio.get_event_loop()
#             response = await loop.run_in_executor(
#                 None,
#                 lambda: self.textract_client.get_document_text_detection(JobId=job_id)
#             )
#             status = response['JobStatus']
#             if status == 'SUCCEEDED':
#                 break
#             elif status == 'FAILED':
#                 raise Exception('AWS Textract job failed.')
#             else:
#                 logger.info("Waiting for AWS Textract job to complete...")
#                 await asyncio.sleep(5)

#     async def _get_job_results(self, job_id: str) -> str:
#         """Retrieve results from completed AWS Textract job."""
#         loop = asyncio.get_event_loop()
#         text_lines = []

#         next_token = None
#         while True:
#             response = await loop.run_in_executor(
#                 None,
#                 lambda: self.textract_client.get_document_text_detection(
#                     JobId=job_id,
#                     NextToken=next_token
#                 ) if next_token else self.textract_client.get_document_text_detection(JobId=job_id)
#             )

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
# ocr_service = OCRService(region_name='us-east-1')  # Replace with your AWS region if different





# ocr_service.py asynchronous

# import boto3
# import logging
# from typing import Tuple, Optional
# from botocore.exceptions import BotoCoreError, ClientError
# import time

# logger = logging.getLogger(__name__)

# class OCRService:
#     def __init__(self, textract_client=None, s3_client=None, region_name: str = 'us-east-1'):
#         """Initialize AWS Textract and S3 clients."""
#         self.textract_client = textract_client or boto3.client('textract', region_name=region_name)
#         self.s3_client = s3_client or boto3.client('s3', region_name=region_name)

#     def extract_text_from_pdf(self, bucket_name: str, file_key: str) -> Tuple[str, Optional[str]]:
#         """Extract text from a PDF using Amazon Textract asynchronous API."""
#         try:
#             logger.info("Starting text extraction from PDF using AWS Textract.")

#             # Start text detection job
#             response = self.textract_client.start_document_text_detection(
#                 DocumentLocation={
#                     'S3Object': {
#                         'Bucket': bucket_name,
#                         'Name': file_key
#                     }
#                 }
#             )
#             job_id = response['JobId']
#             logger.info(f"Started AWS Textract job with JobId: {job_id}")

#             # Poll for job completion
#             self._wait_for_job_completion(job_id)

#             # Retrieve job results
#             text = self._get_job_results(job_id)

#             detected_language = 'en'  # Modify this if you handle multiple languages

#             logger.info("Text extraction from PDF completed successfully using AWS Textract.")
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

#             detected_language = 'en'  # Modify this if you handle multiple languages

#             logger.info("Text extraction from image completed successfully using AWS Textract.")
#             return text, detected_language
#         except (BotoCoreError, ClientError) as e:
#             logger.error(f"AWS Textract error: {str(e)}")
#             raise e
#         except Exception as e:
#             logger.error(f"OCR error: {str(e)}")
#             raise e

#     def _wait_for_job_completion(self, job_id: str):
#         """Wait for AWS Textract job to complete."""
#         while True:
#             response = self.textract_client.get_document_text_detection(JobId=job_id)
#             status = response['JobStatus']
#             if status == 'SUCCEEDED':
#                 break
#             elif status == 'FAILED':
#                 raise Exception('AWS Textract job failed.')
#             else:
#                 logger.info("Waiting for AWS Textract job to complete...")
#                 time.sleep(5)

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
# ocr_service = OCRService(region_name='us-east-1')  # Replace with your AWS region if different


# # ocr_service.py

# import boto3
# import logging
# from typing import Tuple, Optional
# from botocore.exceptions import BotoCoreError, ClientError
# import time

# logger = logging.getLogger(__name__)

# class OCRService:
#     def __init__(self, region_name: str = 'us-east-1'):
#         """Initialize AWS Textract and S3 clients."""
#         self.textract_client = boto3.client('textract', region_name=region_name)
#         self.s3_client = boto3.client('s3', region_name=region_name)

#     def extract_text_from_pdf(self, bucket_name: str, file_key: str) -> Tuple[str, Optional[str]]:
#         """Extract text from a PDF using Amazon Textract asynchronous API."""
#         try:
#             logger.info("Starting text extraction from PDF using AWS Textract.")

#             # Start text detection job
#             response = self.textract_client.start_document_text_detection(
#                 DocumentLocation={
#                     'S3Object': {
#                         'Bucket': bucket_name,
#                         'Name': file_key
#                     }
#                 }
#             )
#             job_id = response['JobId']
#             logger.info(f"Started AWS Textract job with JobId: {job_id}")

#             # Poll for job completion
#             self._wait_for_job_completion(job_id)

#             # Retrieve job results
#             text = self._get_job_results(job_id)

#             detected_language = 'en'  # Modify this if you handle multiple languages

#             logger.info("Text extraction from PDF completed successfully using AWS Textract.")
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

#             detected_language = 'en'  # Modify this if you handle multiple languages

#             logger.info("Text extraction from image completed successfully using AWS Textract.")
#             return text, detected_language
#         except (BotoCoreError, ClientError) as e:
#             logger.error(f"AWS Textract error: {str(e)}")
#             raise e
#         except Exception as e:
#             logger.error(f"OCR error: {str(e)}")
#             raise e

#     def _wait_for_job_completion(self, job_id: str):
#         """Wait for AWS Textract job to complete."""
#         while True:
#             response = self.textract_client.get_document_text_detection(JobId=job_id)
#             status = response['JobStatus']
#             if status == 'SUCCEEDED':
#                 break
#             elif status == 'FAILED':
#                 raise Exception('AWS Textract job failed.')
#             else:
#                 logger.info("Waiting for AWS Textract job to complete...")
#                 time.sleep(5)

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
# ocr_service = OCRService(region_name='us-east-1')  # Replace with your AWS region if different


# ocr_service.py

# import boto3
# import logging
# from typing import Tuple, Optional
# from botocore.exceptions import BotoCoreError, ClientError
# from app.core.config import settings
# import time
# from tenacity import retry, wait_exponential, stop_after_attempt

# logger = logging.getLogger(__name__)

# class OCRService:
#     def __init__(self, region_name: str = 'us-east-1'):
#         """Initialize AWS Textract, S3, and Comprehend clients."""
#         self.textract_client = boto3.client('textract', region_name=region_name)
#         self.s3_client = boto3.client('s3', region_name=region_name)
#         self.comprehend_client = boto3.client('comprehend', region_name=region_name)

#     @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(5))
#     def _wait_for_job_completion(self, job_id: str):
#         """Wait for AWS Textract job to complete with exponential backoff."""
#         response = self.textract_client.get_document_text_detection(JobId=job_id)
#         status = response['JobStatus']
#         if status == 'SUCCEEDED':
#             return  # Job completed successfully
#         elif status == 'FAILED':
#             raise Exception('AWS Textract job failed.')
#         else:
#             raise Exception('AWS Textract job in progress.')

# # class OCRService:
# #     def __init__(self, region_name: str = 'us-east-1'):
# #         """Initialize AWS Textract and S3 clients."""
# #         self.textract_client = boto3.client('textract', region_name=region_name)
# #         self.s3_client = boto3.client('s3', region_name=region_name)
# #         self.comprehend_client = boto3.client('comprehend', region_name=region_name)

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
#         """Extract text from a PDF using Amazon Textract asynchronous API."""
#         try:
#             logger.info("Starting text extraction from PDF using AWS Textract.")

#             # Start text detection job
#             response = self.textract_client.start_document_text_detection(
#                 DocumentLocation={
#                     'S3Object': {
#                         'Bucket': bucket_name,
#                         'Name': file_key
#                     }
#                 }
#             )
#             job_id = response['JobId']
#             logger.info(f"Started AWS Textract job with JobId: {job_id}")

#             # Poll for job completion
#             self._wait_for_job_completion(job_id)

#             # Retrieve  text job results
#             text = self._get_job_results(job_id)
#             detected_language = self.detect_language(text)

#             # detected_language = 'en'  # Modify this if you handle multiple languages

#             logger.info("Text extraction from PDF completed successfully using AWS Textract.")
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

#     def _wait_for_job_completion(self, job_id: str):
#         """Wait for AWS Textract job to complete."""
#         while True:
#             response = self.textract_client.get_document_text_detection(JobId=job_id)
#             status = response['JobStatus']
#             if status == 'SUCCEEDED':
#                 break
#             elif status == 'FAILED':
#                 raise Exception('AWS Textract job failed.')
#             else:
#                 logger.info("Waiting for AWS Textract job to complete...")
#                 time.sleep(5)

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


import logging
import boto3
import io
from typing import Tuple, Optional
from botocore.exceptions import BotoCoreError, ClientError
from app.core.config import settings
from pdf2image import convert_from_bytes

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self, region_name: str = 'us-east-1'):
        """Initialize AWS Textract, S3, and Comprehend clients."""
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
        """Extract text from a PDF using Amazon Textract synchronous API."""
        try:
            logger.info("Starting text extraction from PDF using AWS Textract synchronous API.")

            # Download the PDF file from S3
            pdf_file_obj = self.s3_client.get_object(Bucket=bucket_name, Key=file_key)
            pdf_file = pdf_file_obj['Body'].read()

            # Convert PDF to images (one image per page)
            images = convert_from_bytes(pdf_file)

            text = ''
            for page_number, page_image in enumerate(images, start=1):
                # Convert PIL image to bytes
                image_bytes = io.BytesIO()
                page_image.save(image_bytes, format='JPEG')
                image_bytes.seek(0)

                # Use the synchronous Textract API
                response = self.textract_client.detect_document_text(
                    Document={'Bytes': image_bytes.read()}
                )

                # Extract text from response
                page_text = ''
                for item in response['Blocks']:
                    if item['BlockType'] == 'LINE':
                        page_text += item['Text'] + '\n'

                text += page_text

            # Detect language
            detected_language = self.detect_language(text)

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

            detected_language = self.detect_language(text)

            logger.info("Text extraction from image completed successfully using AWS Textract.")
            return text, detected_language
        except (BotoCoreError, ClientError) as e:
            logger.error(f"AWS Textract error: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"OCR error: {str(e)}")
            raise e

    # Method for TXT files
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

# Initialize the OCR service
ocr_service = OCRService(region_name=settings.REGION_NAME)
