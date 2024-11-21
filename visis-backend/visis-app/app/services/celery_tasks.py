# # app/services/celery_tasks.py

# from app.core.celery_app import celery_app
# import io
# import logging
# from app.database import SessionLocal
# from app.services.ocr_service import OCRService
# from app.services.tts_service import TTSService
# from app.utils.s3_utils import s3_handler
# from app.models import Document
# from app.core.config import settings

# logger = logging.getLogger(__name__)

# # Initialize OCR and TTS services
# ocr_service = OCRService(region_name=settings.REGION_NAME)
# tts_service = TTSService(region_name=settings.REGION_NAME)

# @celery_app.task(bind=True, name="process_document_task")
# def process_document_task(self, document_id: int):
#     """
#     Celery task to process a document (OCR and TTS).
#     """
#     db = SessionLocal()
#     try:
#         # Retrieve the document from the database
#         document = db.query(Document).filter(Document.id == document_id).first()
#         if not document:
#             logger.error(f"Document {document_id} not found.")
#             return

#         # Update processing status to "processing"
#         document.processing_status = "processing"
#         db.commit()

#         # OCR Processing
#         bucket_name = settings.S3_BUCKET_NAME  # Use bucket from settings
#         if document.file_type == "application/pdf":
#             text, detected_language = ocr_service.extract_text_from_pdf(
#                 bucket_name=bucket_name,
#                 file_key=document.file_key,
#             )
#         elif document.file_type.startswith("image/"):
#             text, detected_language = ocr_service.extract_text_from_image(
#                 bucket_name=bucket_name,
#                 file_key=document.file_key,
#             )
#         else:
#             raise Exception("Unsupported file type for processing.")

#         # TTS Processing
#         max_length = 3000
#         text_chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]
#         audio_bytes_io = io.BytesIO()

#         for chunk in text_chunks:
#             chunk_audio = tts_service.convert_text_to_speech(chunk)
#             audio_bytes_io.write(chunk_audio)

#         audio_bytes_io.seek(0)

#         # Upload audio file to S3
#         audio_key = f"{settings.S3_FOLDER_NAME}/audio/{document.user_id}/{document.id}.mp3"
#         audio_url = s3_handler.upload_file(
#             file_obj=audio_bytes_io,
#             bucket=bucket_name,
#             key=audio_key,
#             content_type="audio/mpeg",
#         )

#         # Update the document with processing results
#         document.audio_url = audio_url
#         document.audio_key = audio_key
#         document.processing_status = "completed"
#         document.detected_language = detected_language
#         db.commit()

#         logger.info(f"Processing completed for document {document_id} with audio URL: {audio_url}")

#     except Exception as e:
#         logger.error(f"Error processing document {document_id}: {e}")
#         if document:
#             # Update the document status to "failed"
#             document.processing_status = "failed"
#             document.processing_error = str(e)
#             try:
#                 db.commit()
#             except Exception as db_error:
#                 logger.error(f"Database commit failed: {db_error}")
#     finally:
#         db.close()
