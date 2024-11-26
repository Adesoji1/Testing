# # app/schemas/scanning_history.py

# from pydantic import BaseModel, Field
# from datetime import datetime
# from typing import Optional, List

# class ScanningHistoryBase(BaseModel):
#     scan_type: str = Field(..., description="Type of scan performed")
#     scan_content: str = Field(..., description="Content of the scan result")
#     scan_date: datetime = Field(default_factory=datetime.utcnow)
#     audio_url: Optional[str] = Field(None, description="URL to the audio description")

# class ScanningHistoryCreate(ScanningHistoryBase):
#     pass

# class ScanningHistoryResponse(ScanningHistoryBase):
#     id: int
#     user_id: int

#     class Config:
#         from_attributes = True

# class ScanScene(BaseModel):
#     scene_description: str = Field(..., description="Detailed description of the scene")
#     detected_objects: List[str] = Field(default=[], description="List of detected objects")
#     environment_type: str = Field(..., description="Type of environment (indoor/outdoor)")
#     lighting_conditions: str = Field(..., description="Description of lighting")
#     potential_hazards: List[str] = Field(default=[], description="List of potential hazards")
#     audio_url: Optional[str] = Field(None, description="URL to audio description")

# class ScanObject(BaseModel):
#     object_description: str = Field(..., description="Detailed description of the object")
#     location: str = Field(..., description="Location in the scene")
#     size: str = Field(..., description="Approximate size")
#     shape: str = Field(..., description="Shape description")
#     distance: Optional[str] = Field(None, description="Approximate distance")
#     confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Detection confidence")
#     audio_url: Optional[str] = Field(None, description="URL to audio description")

# class ScanColor(BaseModel):
#     color_description: str = Field(..., description="Overall color analysis")
#     dominant_colors: List[str] = Field(..., description="List of dominant colors")
#     color_scheme: str = Field(..., description="Description of color scheme")
#     contrast_level: str = Field(..., description="Level of contrast")
#     brightness: str = Field(..., description="Brightness description")
#     audio_url: Optional[str] = Field(None, description="URL to audio description")

# class ScanningStats(BaseModel):
#     total_scans: int
#     scene_scans: int
#     object_scans: int
#     color_scans: int
#     last_scan_date: Optional[datetime]

#     class Config:
#         from_attributes = True


# app/schemas/scanning_history.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ScanningHistoryBase(BaseModel):
    scan_type: str = Field(..., description="Type of scan performed")
    scan_content: str = Field(..., description="Content of the scan result")
    scan_date: datetime = Field(default_factory=datetime.utcnow)
    audio_url: Optional[str] = Field(None, description="URL to audio description")

class ScanningHistoryCreate(ScanningHistoryBase):
    pass

class ScanningHistoryResponse(ScanningHistoryBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class ScanScene(ScanningHistoryResponse):
    scene_description: str = Field(..., description="Detailed description of the scene")
    environment_type: str = Field(..., description="Type of environment (indoor/outdoor)")
    lighting_conditions: str = Field(..., description="Description of lighting")
    detected_objects: List[str] = Field(default_factory=list)
    potential_hazards: List[str] = Field(default_factory=list)

class ScanObject(ScanningHistoryResponse):
    object_name: str = Field(..., description="Name of the object")
    location: str = Field(..., description="Location in the scene")
    size: str = Field(..., description="Size description")
    shape: str = Field(..., description="Shape description")
    features: List[str] = Field(default_factory=list)
    function: Optional[str] = Field(None, description="Potential function/purpose")

class ScanColor(ScanningHistoryResponse):
    dominant_colors: List[str] = Field(..., description="List of dominant colors")
    color_scheme: str = Field(..., description="Overall color scheme")
    contrast_level: str = Field(..., description="Level of contrast")
    brightness: str = Field(..., description="Overall brightness")
    relationships: List[str] = Field(default_factory=list, description="Color relationships")

class ScanningStats(BaseModel):
    total_scans: int
    scene_scans: int
    object_scans: int
    color_scans: int
    last_scan_date: Optional[datetime]