#app/api/endpoints/user/auth.py
from datetime import datetime, timedelta, timezone
from enum import Enum
from fastapi import APIRouter, Form, Body, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import EmailStr
from app.services.blacklist_service import add_token_to_blacklist
from app.database import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse
from app.core.security import hashed_password, verify_password, get_current_user, oauth2_scheme
from app.core.config import settings
from app.utils.send_reset_password_email import send_reset_password_email  # Email utility
import logging
from app.utils.email_utils import send_email
from app.models.user import User, SubscriptionType

logger = logging.getLogger("uvicorn.error")

router = APIRouter()

# Constants
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

# Helper function to create access tokens (for login)
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Helper function to create password reset tokens (for forgot-password)
def create_reset_token(email: str, expires_delta: timedelta = None):
    to_encode = {"sub": email}
    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Helper function to verify the reset token (for password reset)
def verify_reset_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        return email
    except JWTError:
        return None

# Helper function to authenticate user by username and password
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return False
    return user

# Route to login and get an access token
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": user.username}, expires_delta=refresh_token_expires)
    
    # Save the refresh token in the database
    user.refresh_token = hashed_password(refresh_token)
    # Update last login timestamp
    user.last_login_date = datetime.now(tz=timezone.utc)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_type": user.user_type,
        "token_type": "bearer",
        "firstname": user.firstname,
        "lastname": user.lastname
    }

    

@router.post("/refresh-token", response_model=Token)
async def refresh_access_token(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    logger.info(f"Refresh token: {refresh_token}")
    """Refresh access token using the refresh token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the refresh token
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_type: str = payload.get("type")
        if token_type != "refresh":
            raise credentials_exception
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception

    # Fetch the user
    user = db.query(User).filter(User.username == username).first()
    if user is None or user.refresh_token is None:
        raise credentials_exception

    # Verify the refresh token matches the stored hashed refresh token
    if not verify_password(refresh_token, user.refresh_token):
        raise credentials_exception

    # Create new tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    new_refresh_token = create_refresh_token(
        data={"sub": user.username},
        expires_delta=refresh_token_expires
    )

    # Update the user's refresh token in the database
    user.refresh_token = hashed_password(new_refresh_token)
    db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user_type": user.user_type,
        "firstname": user.firstname,
        "lastname":  user.lastname
    }


# Define UserType enum
class UserType(str, Enum):
    SIGHTED = "Sighted"
    VISUALLY_IMPAIRED = "Visually_Impaired"

def validate_password(password: str) -> bool:
    return len(password) >= 8

# @router.post("/register", response_model=UserResponse)
# async def register_user(
#     username: str = Form(...),
#     firstname: str = Form(...),
#     lastname: str = Form(...),
#     email: str = Form(...),
#     user_type: UserType = Form(...),
#     subscription_type: str = Form("free"),
#     password: str = Form(...),
#     db: Session = Depends(get_db)
# ):
#     # Validate the subscription_type input
#     if subscription_type not in ["free", "premium"]:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid subscription type. Must be 'free' or 'premium'."
#         )
#     # Check existing username
#     db_user = db.query(User).filter(User.username == username).first()
#     if db_user:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Username already registered",
#         )
    
#     # Check existing email
#     db_email = db.query(User).filter(User.email == email).first()
#     if db_email:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Email already registered",
#         )
    
#     # Validate password
#     if not validate_password(password):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Password must be at least 8 characters long",
#         )
    
#     # Create new user
#     new_user = User(
#         username=username,
#         firstname=firstname,
#         lastname=lastname,
#         email=email,
#         user_type=user_type,
#         password_hash=hashed_password(password),
#         subscription_type=subscription_type,
#         registration_date=datetime.now(tz=timezone.utc),
#         last_login_date=datetime.now(tz=timezone.utc),
#     )

#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user




@router.post("/register", response_model=UserResponse)
async def register_user(
    background_tasks: BackgroundTasks,
    username: str = Form(...),
    firstname: str = Form(...),
    lastname: str = Form(...),
    email: EmailStr = Form(...),
    user_type: UserType = Form(...),
    subscription_type: SubscriptionType = Form(SubscriptionType.free),  # Using enum for subscription type
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Register a new user with chosen user_type and subscription_type.

    **Example Request:**
    ```bash
    curl -X POST "http://localhost:8000/user/register" \
         -F "username=johndoe" \
         -F "firstname=John" \
         -F "lastname=Doe" \
         -F "email=john@example.com" \
         -F "user_type=Sighted" \
         -F "subscription_type=free" \
         -F "password=secretpassword"
    ```

    **Example Response:**
    ```json
    {
        "id": 1,
        "username": "johndoe",
        "firstname": "John",
        "lastname": "Doe",
        "email": "john@example.com",
        "user_type": "Sighted",
        "subscription_type": "free",
        "registration_date": "2024-12-20T15:53:55.855Z",
        "last_login_date": "2024-12-20T15:53:55.855Z"
    }
    ```

    After successful registration, a welcome email is sent to the user.
    """
    # Check existing username
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # Check existing email
    db_email = db.query(User).filter(User.email == email).first()
    if db_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Validate password
    if not validate_password(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long",
        )
    
    new_user = User(
        username=username,
        firstname=firstname,
        lastname=lastname,
        email=email,
        user_type=user_type,
        subscription_type=subscription_type,
        password_hash=hashed_password(password),
        registration_date=datetime.now(tz=timezone.utc),
        last_login_date=datetime.now(tz=timezone.utc),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send welcome email in the background
    subject = "Welcome to Vinsighte!"
    body = f"""
    <html>
    <body>
    <h1>Hello {firstname},</h1>
    <p>Thank you for registering with Vinsighte. We are excited to have you on board!</p>
    <p>Enjoy our services,</p>
    <p>The Vinsighte Team</p>
    </body>
    </html>
    """
    background_tasks.add_task(send_email, subject, email, body)

    return new_user


@router.post("/change-subscription-type")
async def change_subscription_type(
    new_subscription_type: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change the current user's subscription type to either 'free' or 'premium'.

    **Parameters:**
    - **new_subscription_type**: The desired new subscription type (free or premium).

    **Authentication:**  
    User must be logged in.

    **Example Request:**
    ```bash
    curl -X POST "http://localhost:8000/user/change-subscription-type" \
         -H "Authorization: Bearer YOUR_JWT_TOKEN" \
         -F "new_subscription_type=premium"
    ```

    **Example Response:**
    ```json
    {
      "message": "Subscription type changed to premium."
    }
    ```
    """
    if new_subscription_type not in ["free", "premium"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subscription type. Must be 'free' or 'premium'."
        )

    current_user.subscription_type = new_subscription_type
    db.commit()
    db.refresh(current_user)
    return {"message": f"Subscription type changed to {new_subscription_type}."}


@router.post("/forgot-password")
async def forgot_password(
    email: EmailStr,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Initiate the password reset process for a user by sending a reset password email.

    **Parameters:**
    - **email**: The email of the user who forgot their password.

    **Behavior:**
    - Checks if the user exists by email.
    - Generates a password reset token.
    - Sends a reset password email asynchronously with a link to reset the password.

    **Example Request:**
    ```bash
    curl -X POST "http://localhost:8000/user/forgot-password" \
         -H "Content-Type: application/json" \
         -d '{"email": "john@example.com"}'
    ```

    **Example Response:**
    ```json
    {
      "message": "Password reset email sent."
    }
    ```
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist.",
        )
    
    reset_token_expires = timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    reset_token = create_reset_token(email=email, expires_delta=reset_token_expires)

    reset_link = f"http://your-frontend-url.com/reset-password?token={reset_token}"
    background_tasks.add_task(send_reset_password_email, email, reset_link)
    
    return {"message": "Password reset email sent."}


@router.post("/reset-password")
async def reset_password(
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    """
    Reset the user's password using a valid reset token provided via email.

    **Parameters:**
    - **token**: The reset token obtained from the password reset email.
    - **new_password**: The new password chosen by the user.

    **Behavior:**
    - Verifies the token to extract the user's email.
    - Updates the user's password if the token is valid and user is found.

    **Example Request:**
    ```bash
    curl -X POST "http://localhost:8000/user/reset-password" \
         -H "Content-Type: application/json" \
         -d '{"token": "RESET_TOKEN_HERE", "new_password": "newSecretPass"}'
    ```

    **Example Response:**
    ```json
    {
      "message": "Password reset successful."
    }
    ```
    """
    email = verify_reset_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token."
        )
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    
    user.password_hash = hashed_password(new_password)
    db.commit()
    
    return {"message": "Password reset successful."}


@router.post("/change-password")
async def change_password(
    current_password: str, 
    new_password: str, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Change the current user's password.

    **Parameters:**
    - **current_password**: The user's current password.
    - **new_password**: The user's new password, which must be different from the current one.

    **Behavior:**
    - Verifies the current password.
    - Ensures the new password is different from the old one.
    - Updates the user's password.

    **Example Request:**
    ```bash
    curl -X POST "http://localhost:8000/user/change-password" \
         -H "Authorization: Bearer YOUR_JWT_TOKEN" \
         -F "current_password=oldPass123" \
         -F "new_password=newPass456"
    ```

    **Example Response:**
    ```json
    {
      "message": "Password changed successfully."
    }
    ```
    """
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    if verify_password(new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as the old password"
        )

    current_user.password_hash = hashed_password(new_password)
    db.commit()

    return {"message": "Password changed successfully."}


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log out the current user by invalidating their refresh token.

    **Behavior:**
    - Sets the user's refresh token to None, preventing future token refreshes.
    - The user's access token will eventually expire, completing the logout process.

    **Example Request:**
    ```bash
    curl -X POST "http://localhost:8000/user/logout" \
         -H "Authorization: Bearer YOUR_JWT_TOKEN"
    ```

    **Example Response:**
    ```json
    {
      "message": "Successfully logged out."
    }
    ```
    """
    try:
        current_user.refresh_token = None
        db.commit()
        return {"message": "Successfully logged out."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while logging out."
        )


# #Change subscription type route
# @router.post("/change-subscription-type")
# async def change_subscription_type(
#     new_subscription_type: str = Form(...),
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     if new_subscription_type not in ["free", "premium"]:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid subscription type. Must be 'free' or 'premium'."
#         )

#     current_user.subscription_type = new_subscription_type
#     db.commit()
#     db.refresh(current_user)
#     return {"message": f"Subscription type changed to {new_subscription_type}."}


# # Forgot Password route
# @router.post("/forgot-password")
# async def forgot_password(email: EmailStr, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
#     # Check if the user exists
#     user = db.query(User).filter(User.email == email).first()
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User with this email does not exist.",
#         )
    
#     # Generate a reset token
#     reset_token_expires = timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
#     reset_token = create_reset_token(email=email, expires_delta=reset_token_expires)

#     # Construct the reset link and send the email in the background
#     reset_link = f"http://your-frontend-url.com/reset-password?token={reset_token}"
#     background_tasks.add_task(send_reset_password_email, email, reset_link)
    
#     return {"message": "Password reset email sent."}

# # Reset Password route
# @router.post("/reset-password")
# async def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
#     # Verify the token and extract the email
#     email = verify_reset_token(token)
#     if not email:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid or expired token."
#         )
    
#     # Get the user by email
#     user = db.query(User).filter(User.email == email).first()
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found."
#         )
    
#     # Hash the new password and update the database
#     user.password_hash = hashed_password(new_password)
#     db.commit()
    
#     return {"message": "Password reset successful."}

# # Change Password route
# @router.post("/change-password")
# async def change_password(
#     current_password: str, 
#     new_password: str, 
#     current_user: User = Depends(get_current_user), 
#     db: Session = Depends(get_db)
# ):
#     # Verify the current password
#     if not verify_password(current_password, current_user.password_hash):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Current password is incorrect"
#         )
    
#     # Check if the new password is different from the old password
#     if verify_password(new_password, current_user.password_hash):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="New password cannot be the same as the old password"
#         )

#     # Hash the new password and update the user
#     current_user.password_hash = hashed_password(new_password)
#     db.commit()

#     return {"message": "Password changed successfully."}




# @router.post("/logout")
# async def logout(
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     try:
#         # Invalidate the refresh token by setting it to None
#         current_user.refresh_token = None
#         db.commit()
#         return {"message": "Successfully logged out."}
#     except Exception as e:
#         # Optionally log the exception details
#         # logger.error(f"Logout error: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="An error occurred while logging out."
#         )