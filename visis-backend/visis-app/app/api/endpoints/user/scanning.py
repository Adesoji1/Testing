from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models import ScanningHistory, User
from app.schemas.scanning_history import ScanningHistoryCreate, ScanningHistoryResponse
from app.database import SessionLocal
from app.core.security import get_current_user

router = APIRouter(
    prefix="/scanning",
    tags=["scanning"],
    responses={404: {"description": "Not found"}},
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[ScanningHistoryResponse])
def list_scanning_history(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    scanning_history = db.query(ScanningHistory).filter(ScanningHistory.user_id == current_user.id).offset(skip).limit(limit).all()
    return scanning_history

@router.post("/", response_model=ScanningHistoryResponse, status_code=status.HTTP_201_CREATED)
def create_scanning_history(scanning_history: ScanningHistoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_scanning_history = ScanningHistory(**scanning_history.dict(), user_id=current_user.id)
    db.add(db_scanning_history)
    db.commit()
    db.refresh(db_scanning_history)
    return db_scanning_history

@router.delete("/{scanning_history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scanning_history(scanning_history_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    scanning_history = db.query(ScanningHistory).filter(ScanningHistory.id == scanning_history_id, ScanningHistory.user_id == current_user.id).first()
    if not scanning_history:
        raise HTTPException(status_code=404, detail="Scanning history not found")
    db.delete(scanning_history)
    db.commit()
    return {"detail": "Scanning history deleted successfully"}