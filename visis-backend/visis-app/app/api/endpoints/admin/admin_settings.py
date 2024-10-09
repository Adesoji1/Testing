from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models import AppSetting
from app.schemas.app_setting import AppSettingResponse, AppSettingCreate
from app.database import SessionLocal
from app.core.security import get_current_user, oauth2_scheme
from jose import JWTError, jwt
from app.core.config import settings
from app.schemas.token import TokenData
from app.models.user import User
from app.core.security import get_current_admin_user

router = APIRouter(
    prefix="/admin/settings",
    tags=["admin-settings"],
    responses={404: {"description": "Not found"}},
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[AppSettingResponse])
def list_settings(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    settings = db.query(AppSetting).offset(skip).limit(limit).all()
    return settings

@router.post("/", response_model=AppSettingResponse, status_code=status.HTTP_201_CREATED)
def create_setting(setting: AppSettingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_setting = AppSetting(**setting.dict())
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting

@router.delete("/{setting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_setting(setting_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    setting = db.query(AppSetting).filter(AppSetting.id == setting_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    db.delete(setting)
    db.commit()
    return {"detail": "Setting deleted successfully"}