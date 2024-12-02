# # app/api/endpoints/user/scanning.py
import io
import logging
import asyncio
from datetime import datetime
from typing import List, Union
from concurrent.futures import ThreadPoolExecutor

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from PIL import Image
from pydub import AudioSegment
from pydub.effects import normalize

from app.models.user import User
from app.models.scanning_history import ScanningHistory
from app.schemas.scanning_history import ScanningHistoryResponse
from app.utils.s3_utils import s3_handler
from app.services.tts_service import TTSService
from app.core.config import settings

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import google.generativeai as genai
import boto3
import io

from app.models import ScanningHistory, User
from app.schemas.scanning_history import (
    ScanningHistoryCreate,
    ScanningHistoryResponse,
    ScanScene,
    ScanObject,
    ScanColor
)
from app.database import get_db
from app.core.security import get_current_user
from app.core.config import settings

router = APIRouter(prefix="/scanning", tags=["scanning"])

# Initialize clients
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")
polly = boto3.client('polly', region_name=settings.AWS_REGION)
s3 = boto3.client('s3', region_name=settings.AWS_REGION)
from PIL import Image




logger = logging.getLogger(__name__)

# Initialize TTS service
tts_service = TTSService(region_name=settings.AWS_REGION)

def apply_immersive_effects(audio: AudioSegment) -> AudioSegment:
    """Apply immersive audio effects."""
    audio = normalize(audio)
    left = audio.pan(-0.5)
    right = audio.pan(0.5)
    return left.overlay(right)

async def process_text_chunks_in_parallel(text_chunks: List[str]) -> List[bytes]:
    """Process text chunks for TTS in parallel."""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=4) as executor:
        tasks = [
            loop.run_in_executor(executor, tts_service.convert_text_to_speech, chunk)
            for chunk in text_chunks
        ]
        audio_chunks = await asyncio.gather(*tasks)
    return audio_chunks

async def generate_audio(analysis_text: str) -> io.BytesIO:
    """Generate audio from text and apply effects."""
    try:
        # Split text into manageable chunks
        max_length = 3000
        text_chunks = [analysis_text[i:i + max_length] for i in range(0, len(analysis_text), max_length)]

        # Convert text chunks to speech in parallel
        audio_chunks = await process_text_chunks_in_parallel(text_chunks)

        # Combine audio chunks
        combined_audio_io = io.BytesIO()
        for chunk_audio in audio_chunks:
            combined_audio_io.write(chunk_audio)

        # Apply immersive effects
        combined_audio_io.seek(0)
        audio = AudioSegment.from_file(combined_audio_io, format="mp3")
        immersive_audio = apply_immersive_effects(audio)

        # Export to BytesIO
        processed_audio_io = io.BytesIO()
        immersive_audio.export(processed_audio_io, format="mp3", bitrate="64k")
        processed_audio_io.seek(0)

        return processed_audio_io

    except Exception as e:
        logging.error(f"Error generating audio: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate audio")

def extract_section(text: str, section: str) -> str:
    """Extract specific section content from text."""
    try:
        lines = text.split('\n')
        content = []
        in_section = False
        
        for line in lines:
            if section.lower() in line.lower() and ('-' in line or ':' in line):
                in_section = True
                continue
            elif in_section and line.strip():
                if line.startswith('-') or line.startswith('*'):
                    content.append(line.lstrip('- *').strip())
                elif any(marker in line for marker in [':', '-']) and not line.startswith(' '):
                    break
        return ' '.join(content) if content else "Not specified"
    except Exception as e:
        logger.error(f"Error extracting section {section}: {str(e)}")
        return "Not specified"

def extract_list(text: str, section: str) -> List[str]:
    """Extract list items from a section."""
    try:
        lines = text.split('\n')
        items = []
        in_section = False
        
        for line in lines:
            if section.lower() in line.lower() and ('-' in line or ':' in line):
                in_section = True
                continue
            elif in_section and line.strip():
                if line.startswith('-') or line.startswith('*'):
                    items.append(line.lstrip('- *').strip())
                elif any(marker in line for marker in [':', '-']) and not line.startswith(' '):
                    break
        return items if items else ["None detected"]
    except Exception as e:
        logger.error(f"Error extracting list {section}: {str(e)}")
        return ["Error processing list"]

def parse_gemini_response(response_text: str, scan_type: str) -> dict:
    """Parse structured data from Gemini response."""
    try:
        if scan_type == "scene":
            return {
                "scene_description": extract_section(response_text, "Overall environment"),
                "environment_type": "indoor" if "indoor" in response_text.lower() else "outdoor",
                "lighting_conditions": extract_section(response_text, "Lighting conditions"),
                "detected_objects": extract_list(response_text, "Key elements"),
                "potential_hazards": extract_list(response_text, "hazards")
            }
        elif scan_type == "object":
            return {
                "object_name": extract_section(response_text, "Name and type"),
                "location": extract_section(response_text, "Location"),
                "size": extract_section(response_text, "Size"),
                "shape": extract_section(response_text, "shape"),
                "features": extract_list(response_text, "Notable features"),
                "function": extract_section(response_text, "function")
            }
        elif scan_type == "color":
            return {
                "dominant_colors": extract_list(response_text, "Dominant colors"),
                "color_scheme": extract_section(response_text, "patterns"),
                "contrast_level": extract_section(response_text, "Contrast"),
                "brightness": extract_section(response_text, "brightness"),
                "relationships": extract_list(response_text, "relationships")
            }
    except Exception as e:
        logger.error(f"Error parsing response: {str(e)}")
        return {}

async def process_scan(
    file: UploadFile,
    prompt: str,
    scan_type: str,
    db: Session,
    current_user: User
) -> Union[ScanScene, ScanObject, ScanColor]:
    """Process scan request and generate audio response."""
    try:
        # Validate image file
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please upload an image file"
            )

        # Read and process image
        content = await file.read()
        image = Image.open(io.BytesIO(content))
        
        # Get analysis from Gemini
        response = model.generate_content([prompt, image])
        analysis_text = response.text.strip()
        
        if not analysis_text:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate analysis"
            )

        #  Generate audio
        processed_audio_io = await generate_audio(analysis_text)
        
        # Generate unique filename and upload to S3
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        audio_key = f"scans/{current_user.id}/{scan_type}/{timestamp}.mp3"
        
        audio_url = s3_handler.upload_file(
            file_obj=processed_audio_io,
            bucket=settings.S3_BUCKET_NAME,
            key=audio_key,
            content_type="audio/mpeg"
        )

        if not audio_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload audio to S3"
            )

        # Create scan history record
        scan = ScanningHistory(
            user_id=current_user.id,
            scan_type=scan_type,
            scan_content=analysis_text,
            scan_date=datetime.utcnow(),
            audio_url=audio_url
        )

        db.add(scan)
        db.commit()
        db.refresh(scan)

        # Parse response and prepare base data
        parsed_data = parse_gemini_response(analysis_text, scan_type)
        base_data = {
            "id": scan.id,
            "user_id": scan.user_id,
            "scan_type": scan.scan_type,
            "scan_content": scan.scan_content,
            "scan_date": scan.scan_date,
            "audio_url": scan.audio_url
        }

        # Return appropriate response type
        try:
            if scan_type == "scene":
                return ScanScene(**base_data, **parsed_data)
            elif scan_type == "object":
                return ScanObject(**base_data, **parsed_data)
            elif scan_type == "color":
                return ScanColor(**base_data, **parsed_data)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid scan type: {scan_type}"
                )
        except Exception as e:
            logger.error(f"Error creating response object: {str(e)}")
            # Fallback to basic response if parsing fails
            return ScanningHistoryResponse(**base_data)

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Scanning failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scanning failed: {str(e)}"
        )


@router.post("/scene", response_model=ScanningHistoryResponse)
async def scan_scene(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Scan and describe the overall scene"""
    prompt = """Describe this scene in detail, including:
    - Overall environment
    - Key elements and their layout
    - Notable features or hazards
    - Lighting conditions
    - General atmosphere"""
    
    return await process_scan(file, prompt, "scene", db, current_user)

@router.post("/object", response_model=ScanObject)
async def scan_object(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Scan and identify objects"""
    prompt = """Identify and describe the main objects in this image:
    - Name and type of each object
    - Location in the scene
    - Size and shape
    - Notable features
    - Potential function or purpose"""
    
    return await process_scan(file, prompt, "object", db, current_user)

@router.post("/color", response_model=ScanColor)
async def scan_color(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze colors in the scene"""
    prompt = """Analyze the colors in this image:
    - Dominant colors
    - Color patterns or schemes
    - Contrast levels
    - Color relationships
    - Notable color features"""
    
    return await process_scan(file, prompt, "color", db, current_user)

@router.get("/history", response_model=List[ScanningHistoryResponse])
async def get_scanning_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20
):
    """Get user's scanning history"""
    scans = db.query(ScanningHistory)\
        .filter(ScanningHistory.user_id == current_user.id)\
        .order_by(ScanningHistory.scan_date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    return scans




