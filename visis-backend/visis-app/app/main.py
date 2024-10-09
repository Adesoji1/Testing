# from fastapi import FastAPI
# from app.api.endpoints.admin import admin_users, admin_documents, admin_settings
# from app.api.endpoints.user import auth, documents, audiobooks, bookmarks, preferences, scanning, accessibility, languages, activities, feedback
# from app.database import init_db

# app = FastAPI()

# # Initialize the database
# init_db()

# # Include admin routers
# app.include_router(admin_users.router)
# app.include_router(admin_documents.router)
# app.include_router(admin_settings.router)

# # Include user routers
# app.include_router(auth.router)
# app.include_router(documents.router)
# # app.include_router(audiobooks.router)
# app.include_router(bookmarks.router)
# app.include_router(preferences.router)
# app.include_router(scanning.router)
# # app.include_router(accessibility.router)
# app.include_router(languages.router)
# app.include_router(activities.router)
# # app.include_router(feedback.router)

# @app.get("/")
# async def read_root():
#     return {"message": "Visis App API is running"}

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from app.api.endpoints.admin import admin_users, admin_documents, admin_settings
from app.api.endpoints.user import auth, documents, bookmarks, preferences, scanning, languages, activities
from app.database import init_db
from app.middleware.ip_whitelist import validate_ip

# Initialize the FastAPI app
app = FastAPI()

# Add CORS settings to allow your frontend React Native app access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8081"
    ],  # Frontend React Native ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add IP validation middleware
app.middleware("http")(validate_ip)

# Initialize the database
init_db()

# Include admin routers
app.include_router(admin_users.router)
app.include_router(admin_documents.router)
app.include_router(admin_settings.router)

# Include user routers
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(bookmarks.router)
app.include_router(preferences.router)
app.include_router(scanning.router)
app.include_router(languages.router)
app.include_router(activities.router)

# Commented out routers
# app.include_router(audiobooks.router)
# app.include_router(accessibility.router)
# app.include_router(feedback.router)

# Root endpoint to verify the API is running
@app.get("/")
async def read_root():
    return {"message": "Visis App API is running"}

# Custom error handler for 404 Not Found errors
@app.exception_handler(404)
async def not_found_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": "The requested resource was not found"},
    )

# Custom error handler for 422 Unprocessable Entity errors
@app.exception_handler(422)
async def unprocessable_entity_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": "Unprocessable Entity: The server understands the content type of the request entity, and the syntax of the request entity is correct, but it was unable to process the contained instructions."},
    )

