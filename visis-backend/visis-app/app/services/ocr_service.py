# ocr_service.py

import boto3
import logging
import asyncio
from typing import Tuple, Optional
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self, textract_client=None, s3_client=None, region_name: str = 'us-east-1'):
        """Initialize AWS Textract and S3 clients."""
        self.textract_client = textract_client or boto3.client('textract', region_name=region_name)
        self.s3_client = s3_client or boto3.client('s3', region_name=region_name)

    async def extract_text_from_pdf(self, bucket_name: str, file_key: str) -> Tuple[str, Optional[str]]:
        """Extract text from a PDF using Amazon Textract asynchronous API.

        Args:
            bucket_name (str): The name of the S3 bucket.
            file_key (str): The S3 key for the PDF file.

        Returns:
            Tuple[str, Optional[str]]: Extracted text and detected language code.
        """
        try:
            logger.info("Starting text extraction from PDF using AWS Textract.")

            # Start text detection job
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.textract_client.start_document_text_detection(
                    DocumentLocation={
                        'S3Object': {
                            'Bucket': bucket_name,
                            'Name': file_key
                        }
                    }
                )
            )
            job_id = response['JobId']
            logger.info(f"Started AWS Textract job with JobId: {job_id}")

            # Poll for job completion
            await self._wait_for_job_completion(job_id)

            # Retrieve job results
            text = await self._get_job_results(job_id)

            detected_language = 'en'  # Modify this if you handle multiple languages

            logger.info("Text extraction from PDF completed successfully using AWS Textract.")
            return text, detected_language
        except (BotoCoreError, ClientError) as e:
            logger.error(f"AWS Textract error: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"OCR error: {str(e)}")
            raise e

    async def extract_text_from_image(self, bucket_name: str, file_key: str) -> Tuple[str, Optional[str]]:
        """Extract text from an image using Amazon Textract.

        Args:
            bucket_name (str): The name of the S3 bucket.
            file_key (str): The S3 key for the image file.

        Returns:
            Tuple[str, Optional[str]]: Extracted text and detected language code.
        """
        try:
            logger.info("Starting text extraction from image using AWS Textract.")

            # Get the image bytes from S3
            loop = asyncio.get_event_loop()
            image_bytes = await loop.run_in_executor(
                None,
                lambda: self.s3_client.get_object(Bucket=bucket_name, Key=file_key)['Body'].read()
            )

            # Call Textract to detect text in the image
            response = await loop.run_in_executor(
                None,
                lambda: self.textract_client.detect_document_text(
                    Document={'Bytes': image_bytes}
                )
            )

            # Extract text from response
            text = '\n'.join([
                item['Text'] for item in response['Blocks']
                if item['BlockType'] == 'LINE'
            ])

            detected_language = 'en'  # Modify this if you handle multiple languages

            logger.info("Text extraction from image completed successfully using AWS Textract.")
            return text, detected_language
        except (BotoCoreError, ClientError) as e:
            logger.error(f"AWS Textract error: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"OCR error: {str(e)}")
            raise e

    async def _wait_for_job_completion(self, job_id: str):
        """Wait for AWS Textract job to complete."""
        while True:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.textract_client.get_document_text_detection(JobId=job_id)
            )
            status = response['JobStatus']
            if status == 'SUCCEEDED':
                break
            elif status == 'FAILED':
                raise Exception('AWS Textract job failed.')
            else:
                logger.info("Waiting for AWS Textract job to complete...")
                await asyncio.sleep(5)

    async def _get_job_results(self, job_id: str) -> str:
        """Retrieve results from completed AWS Textract job."""
        loop = asyncio.get_event_loop()
        text_lines = []

        next_token = None
        while True:
            response = await loop.run_in_executor(
                None,
                lambda: self.textract_client.get_document_text_detection(
                    JobId=job_id,
                    NextToken=next_token
                ) if next_token else self.textract_client.get_document_text_detection(JobId=job_id)
            )

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
ocr_service = OCRService(region_name='us-east-1')  # Replace with your AWS region if different