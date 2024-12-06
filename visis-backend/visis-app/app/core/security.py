from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.core.config import settings
from app.schemas.token import TokenData
from app.services.blacklist_service import is_token_blacklisted 
import logging

logger = logging.getLogger(__name__)


# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer defines the token URL, updated to match your login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Password hashing functions
def hashed_password(password: str) -> str:
    """Hash the password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify the password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

# Helper function to retrieve the current user based on the JWT token
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    logger.debug("get_current_user called")
    """Get current user from the JWT access token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Optional: Check if token is blacklisted
        # if is_token_blacklisted(db, token):
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Token has been revoked.",
        #         headers={"WWW-Authenticate": "Bearer"},
        #     )

        # Decode the JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # Verify the token type is 'access'
        token_type: str = payload.get("type")
        if token_type != "access":
            raise credentials_exception
        
        username: str = payload.get("sub")  # Fetch the subject (username)
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception

    # Fetch the user from the database
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception

    return user

        
# Helper function to check if the current user is an admin
def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """Ensure the current user has admin privileges."""
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user
