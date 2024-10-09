from sqlalchemy.orm import Session
from app.models import Document
from app.schemas.document import DocumentCreate

def create_document(db: Session, document: DocumentCreate, user_id: int):
    db_document = Document(**document.dict(), user_id=user_id)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_documents(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Document).offset(skip).limit(limit).all()

def delete_document(db: Session, document_id: int):
    document = db.query(Document).filter(Document.id == document_id).first()
    if document:
        db.delete(document)
        db.commit()
        return True
    return False