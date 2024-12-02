# from fastapi import FastAPI, Request, status
# from fastapi.responses import JSONResponse
# from starlette.middleware.cors import CORSMiddleware
# from app.api.endpoints.admin import admin_users, admin_documents, admin_settings
# from app.api.endpoints.user import auth, documents, bookmarks, preferences, scanning, languages, activities
# from app.database import init_db
# from app.middleware.ip_whitelist import validate_ip
# import logging
# from app.api.endpoints.search_document import router as search_document_router  # Import the search router

# logging.basicConfig(level=logging.INFO)

# # Initialize the FastAPI app
# app = FastAPI()

# # Add CORS settings to allow your frontend React Native app access
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:3000",
#         "http://localhost:8081"
#     ],  # Frontend React Native ports
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Add IP validation middleware
# app.middleware("http")(validate_ip)

# # Initialize the database
# init_db()

# # Include admin routers
# app.include_router(admin_users.router)
# app.include_router(admin_documents.router)
# app.include_router(admin_settings.router)

# # Include user routers
# app.include_router(auth.router)
# app.include_router(documents.router)
# app.include_router(bookmarks.router)
# app.include_router(preferences.router)
# app.include_router(scanning.router)
# app.include_router(languages.router)
# app.include_router(activities.router)
# app.include_router(search_document_router)

# # Commented out routers
# # app.include_router(audiobooks.router)
# # app.include_router(accessibility.router)
# # app.include_router(feedback.router)

# # Root endpoint to verify the API is running
# @app.get("/")
# async def read_root():
#     return {"message": "Visis App API is running"}

# # Custom error handler for 404 Not Found errors
# @app.exception_handler(404)
# async def not_found_error_handler(request: Request, exc: Exception):
#     return JSONResponse(
#         status_code=status.HTTP_404_NOT_FOUND,
#         content={"message": "The requested resource was not found"},
#     )

# # Custom error handler for 422 Unprocessable Entity errors
# @app.exception_handler(422)
# async def unprocessable_entity_error_handler(request: Request, exc: Exception):
#     return JSONResponse(
#         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#         content={"message": "Unprocessable Entity: The server understands the content type of the request entity, and the syntax of the request entity is correct, but it was unable to process the contained instructions."},
#     )



import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from app.api.endpoints.admin import admin_users, admin_documents, admin_settings
from app.api.endpoints.user import auth, documents, bookmarks, preferences, scanning, languages, activities
from app.database import init_db
from app.middleware.ip_whitelist import validate_ip
from app.api.endpoints.search_document import router as search_document_router  # Import the search router
from app.api.endpoints.user.donations import router as donations_router
from app.api.endpoints.user.transactions import router as transactions_router
from app.api.endpoints.user.subscriptions import router as subscriptions_router


# Set up logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO  # Adjust the level to capture INFO level logs
)

logger = logging.getLogger(__name__)

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
app.include_router(search_document_router)
app.include_router(documents.router)
app.include_router(bookmarks.router)
app.include_router(preferences.router)
app.include_router(scanning.router)
app.include_router(languages.router)
app.include_router(activities.router)
app.include_router(donations_router)
app.include_router(transactions_router)
app.include_router(subscriptions_router)


# Root endpoint to verify the API is running
@app.get("/")
async def read_root():
    logger.info("Root endpoint accessed")  # Log when the root endpoint is accessed
    return {"message": "Visis App API is running"}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request path: {request.url.path}, Query params: {request.query_params}")
    response = await call_next(request)
    return response
# Custom error handler for 404 Not Found errors
@app.exception_handler(404)
async def not_found_error_handler(request: Request, exc: Exception):
    logger.error(f"404 Error: {str(exc)} - URL: {request.url}")  # Log the error with details
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": "The requested resource was not found"},
    )

# Custom error handler for 422 Unprocessable Entity errors
@app.exception_handler(422)
async def unprocessable_entity_error_handler(request: Request, exc: Exception):
    logger.error(f"422 Error: {exc}")  # Log the 422 exception
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": "Unprocessable Entity: The server understands the content type of the request entity, but it was unable to process the contained instructions."},
    )

