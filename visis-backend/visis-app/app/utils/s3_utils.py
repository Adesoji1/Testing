


# # s3_utils.py



# import boto3
# from botocore.config import Config
# from botocore.exceptions import (
#     ClientError,
#     NoCredentialsError,
#     PartialCredentialsError,
#     InvalidConfigError,
# )
# from fastapi import HTTPException, status
# from typing import Optional, BinaryIO
# import logging
# from app.core.config import settings

# logger = logging.getLogger(__name__)

# class S3Handler:
#     def __init__(self):
#         self.s3_client = self._initialize_s3_client()
        
#     def _initialize_s3_client(self):
#         """Initialize S3 client with retry configuration and proper credentials."""
#         try:
#             # Configure boto3 with retry strategy and secure settings
#             config = Config(
#                 retries={
#                     'max_attempts': 5,
#                     'mode': 'standard'
#                 },
#                 connect_timeout=5,
#                 read_timeout=10,
#                 s3={
#                     'addressing_style': 'virtual',
#                     'use_accelerate_endpoint': False,
#                     'payload_signing_enabled': True,
#                 }
#             )
            
#             # Prepare parameters for session initialization
#             session_params = {
#                 'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
#                 'aws_secret_access_key': settings.AWS_SECRET_ACCESS_KEY,
#                 'region_name': settings.REGION_NAME
#             }

#             # Optionally include aws_session_token if it's defined
#             if hasattr(settings, 'AWS_SESSION_TOKEN') and settings.AWS_SESSION_TOKEN:
#                 session_params['aws_session_token'] = settings.AWS_SESSION_TOKEN

#             # Initialize session with credentials, enforcing secure connections
#             session = boto3.Session(**session_params)
            
#             s3_client = session.client(
#                 's3',
#                 config=config,
#                 use_ssl=True,   # Enforce SSL/TLS
#                 verify=True     # Verify SSL certificates
#             )
            
#             return s3_client
            
#         except NoCredentialsError:
#             logger.error("AWS credentials not found")
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="AWS credentials not found. Please check your environment variables."
#             )
#         except PartialCredentialsError:
#             logger.error("Incomplete AWS credentials")
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="AWS credentials are incomplete. Please ensure all required credentials are provided."
#             )
#         except InvalidConfigError as e:
#             logger.error(f"Invalid AWS configuration: {str(e)}")
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Invalid AWS configuration: {str(e)}"
#             )
#         except Exception as e:
#             logger.error(f"Unexpected error initializing S3 client: {str(e)}")
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Failed to initialize S3 client. Please contact support."
#             )

#     def upload_file(
#         self,
#         file_obj: BinaryIO,
#         bucket: str,
#         key: str,
#         content_type: Optional[str] = None,
#         kms_key_id: Optional[str] = None
#     ) -> str:
#         """
#         Upload a file to S3 with advanced security features.
        
#         Args:
#             file_obj: File-like object to upload
#             bucket: S3 bucket name
#             key: S3 object key (path)
#             content_type: Optional MIME type of the file
#             kms_key_id: Optional KMS Key ID for server-side encryption
            
#         Returns:
#             str: The URL of the uploaded file
#         """
#         extra_args = {'ContentType': content_type} if content_type else {}
        
#         # Add server-side encryption parameters
#         sse_args = {
#             'ServerSideEncryption': 'aws:kms' if kms_key_id else 'AES256',
#         }
#         if kms_key_id:
#             sse_args['SSEKMSKeyId'] = kms_key_id
        
#         try:
#             # Upload file with additional metadata and encryption
#             self.s3_client.upload_fileobj(
#                 Fileobj=file_obj,
#                 Bucket=bucket,
#                 Key=key,
#                 ExtraArgs={
#                     **extra_args,
#                     **sse_args,
#                     'ACL': 'private',  # Ensure private access
#                 }
#             )
            
#             # Generate pre-signed URL valid for 1 hour
#             url = self.s3_client.generate_presigned_url(
#                 ClientMethod='get_object',
#                 Params={'Bucket': bucket, 'Key': key},
#                 ExpiresIn=3600
#             )
            
#             return url
            
#         except ClientError as e:
#             error_code = e.response['Error']['Code']
#             error_mapping = {
#                 'InvalidAccessKeyId': (
#                     status.HTTP_403_FORBIDDEN,
#                     "Invalid AWS access key. Please verify your credentials."
#                 ),
#                 'SignatureDoesNotMatch': (
#                     status.HTTP_403_FORBIDDEN,
#                     "Invalid AWS secret key. Please verify your credentials."
#                 ),
#                 'AccessDenied': (
#                     status.HTTP_403_FORBIDDEN,
#                     "Access denied to S3 bucket. Please check your IAM permissions."
#                 ),
#                 'NoSuchBucket': (
#                     status.HTTP_404_NOT_FOUND,
#                     f"Bucket '{bucket}' does not exist."
#                 ),
#                 'InvalidBucketName': (
#                     status.HTTP_400_BAD_REQUEST,
#                     f"Invalid bucket name: '{bucket}'"
#                 )
#             }
            
#             status_code, message = error_mapping.get(
#                 error_code,
#                 (status.HTTP_500_INTERNAL_SERVER_ERROR, f"S3 error: {str(e)}")
#             )
            
#             logger.error(f"S3 upload error: {error_code} - {message}")
#             raise HTTPException(status_code=status_code, detail=message)
            
#         except Exception as e:
#             logger.error(f"Unexpected error during S3 upload: {str(e)}")
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Failed to upload file. Please try again later."
#             )

#     def delete_file(self, bucket: str, key: str) -> bool:
#         """Delete a file from S3."""
#         try:
#             self.s3_client.delete_object(Bucket=bucket, Key=key)
#             return True
#         except ClientError as e:
#             logger.error(f"Error deleting file from S3: {str(e)}")
#             return False
        
#     def generate_presigned_url(self, client_method_name,method_parameters=None, expiration=3600, http_method=None):
#         """Generate a pre-signed URL for an S3 object."""
#         try:
#             response = self.s3_client.generate_presigned_url(
#                 ClientMethod=client_method_name,
#                 Params=method_parameters,
#                 ExpiresIn=expiration,
#                 HttpMethod=http_method
#             )
#         except ClientError as e:
#             logging.error(e)
#             return None
#         return response

# # Create a singleton instance
# s3_handler = S3Handler()


import boto3
from botocore.config import Config
from botocore.exceptions import (
    ClientError,
    NoCredentialsError,
    PartialCredentialsError,
    InvalidConfigError,
)
from fastapi import HTTPException, status
from typing import Optional, BinaryIO
import logging
from app.core.config import settings
import io

logger = logging.getLogger(__name__)

class S3Handler:
    def __init__(self):
        self.s3_client = self._initialize_s3_client()
        
    def _initialize_s3_client(self):
        """Initialize S3 client with retry configuration and proper credentials."""
        try:
            # Configure boto3 with retry strategy and secure settings
            config = Config(
                retries={
                    'max_attempts': 5,
                    'mode': 'standard'
                },
                connect_timeout=5,
                read_timeout=10,
                s3={
                    'addressing_style': 'virtual',
                    'use_accelerate_endpoint': False,
                    'payload_signing_enabled': True,
                }
            )
            
            # Prepare parameters for session initialization
            session_params = {
                'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
                'aws_secret_access_key': settings.AWS_SECRET_ACCESS_KEY,
                'region_name': settings.REGION_NAME
            }

            # Optionally include aws_session_token if it's defined
            if hasattr(settings, 'AWS_SESSION_TOKEN') and settings.AWS_SESSION_TOKEN:
                session_params['aws_session_token'] = settings.AWS_SESSION_TOKEN

            # Initialize session with credentials, enforcing secure connections
            session = boto3.Session(**session_params)
            
            s3_client = session.client(
                's3',
                config=config,
                use_ssl=True,   # Enforce SSL/TLS
                verify=True     # Verify SSL certificates
            )
            
            return s3_client
            
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AWS credentials not found. Please check your environment variables."
            )
        except PartialCredentialsError:
            logger.error("Incomplete AWS credentials")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AWS credentials are incomplete. Please ensure all required credentials are provided."
            )
        except InvalidConfigError as e:
            logger.error(f"Invalid AWS configuration: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Invalid AWS configuration: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error initializing S3 client: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize S3 client. Please contact support."
            )

    def upload_file(
        self,
        file_obj: BinaryIO,
        bucket: str,
        key: str,
        content_type: Optional[str] = None,
        kms_key_id: Optional[str] = None
    ) -> str:
        """
        Upload a file to S3 with advanced security features.
        
        Args:
            file_obj: File-like object to upload
            bucket: S3 bucket name
            key: S3 object key (path)
            content_type: Optional MIME type of the file
            kms_key_id: Optional KMS Key ID for server-side encryption
            
        Returns:
            str: The URL of the uploaded file
        """
        extra_args = {'ContentType': content_type} if content_type else {}
        
        # Add server-side encryption parameters
        sse_args = {
            'ServerSideEncryption': 'aws:kms' if kms_key_id else 'AES256',
        }
        if kms_key_id:
            sse_args['SSEKMSKeyId'] = kms_key_id
        
        try:
            # Upload file with additional metadata and encryption
            self.s3_client.upload_fileobj(
                Fileobj=file_obj,
                Bucket=bucket,
                Key=key,
                ExtraArgs={
                    **extra_args,
                    **sse_args,
                    'ACL': 'private',  # Ensure private access
                }
            )
            
            # Generate pre-signed URL valid for 1 month
            url = self.s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=36000
                #ExpiresIn=31536000
            )
            
            return url
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_mapping = {
                'InvalidAccessKeyId': (
                    status.HTTP_403_FORBIDDEN,
                    "Invalid AWS access key. Please verify your credentials."
                ),
                'SignatureDoesNotMatch': (
                    status.HTTP_403_FORBIDDEN,
                    "Invalid AWS secret key. Please verify your credentials."
                ),
                'AccessDenied': (
                    status.HTTP_403_FORBIDDEN,
                    "Access denied to S3 bucket. Please check your IAM permissions."
                ),
                'NoSuchBucket': (
                    status.HTTP_404_NOT_FOUND,
                    f"Bucket '{bucket}' does not exist."
                ),
                'InvalidBucketName': (
                    status.HTTP_400_BAD_REQUEST,
                    f"Invalid bucket name: '{bucket}'"
                )
            }
            
            status_code, message = error_mapping.get(
                error_code,
                (status.HTTP_500_INTERNAL_SERVER_ERROR, f"S3 error: {str(e)}")
            )
            
            logger.error(f"S3 upload error: {error_code} - {message}")
            raise HTTPException(status_code=status_code, detail=message)
            
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file. Please try again later."
            )

    def get_file_content(self, bucket: str, key: str) -> bytes:
        """
        Retrieve file content from S3.

        Args:
            bucket (str): The name of the S3 bucket.
            key (str): The S3 object key.

        Returns:
            bytes: The content of the file.

        Raises:
            HTTPException: If retrieval fails.
        """
        try:
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            return response['Body'].read()
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"ClientError retrieving file from S3: {error_code} - {e.response['Error']['Message']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve file content from S3."
            )
        except Exception as e:
            logger.error(f"Unexpected error retrieving file from S3: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve file content from S3."
            )
    
    def delete_file(self, bucket: str, key: str) -> bool:
        """Delete a file from S3."""
        try:
            self.s3_client.delete_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            logger.error(f"Error deleting file from S3: {str(e)}")
            return False
        
    def generate_presigned_url(self, client_method_name, method_parameters=None, expiration=3600, http_method=None):
        """Generate a pre-signed URL for an S3 object."""
        try:
            response = self.s3_client.generate_presigned_url(
                ClientMethod=client_method_name,
                Params=method_parameters,
                ExpiresIn=expiration,
                HttpMethod=http_method
            )
        except ClientError as e:
            logger.error(e)
            return None
        return response
    



# Create a singleton instance
s3_handler = S3Handler()
