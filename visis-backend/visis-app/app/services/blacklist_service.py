from sqlalchemy.orm import Session
from app.models.blacklist import BlacklistedToken

def add_token_to_blacklist(db: Session, token: str):
    blacklisted_token = BlacklistedToken(token=token)
    db.add(blacklisted_token)
    db.commit()


def is_token_blacklisted(db: Session, token: str) -> bool:
    return db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first() is not None
