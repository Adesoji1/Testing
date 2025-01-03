# 
# app/main.py
import os
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter
from app.middleware.rate_limiter import add_rate_limiting
from app.middleware.ip_whitelist import validate_ip
# from app.utils.paystack_utils import close_client
from app.database import init_db
from app.core.config import settings
from app.api.endpoints.admin import admin_users, admin_documents, admin_settings
from app.api.endpoints.user import auth, documents, bookmarks, preferences, scanning, languages, activities
from app.api.endpoints.user.donations import router as donations_router
from app.api.endpoints.user.transactions import router as transactions_router
from app.api.endpoints.user.subscriptions import router as subscription_router
# from app.api.endpoints.user.subscriptions import router as subscriptions_router
from app.api.endpoints.search_document import router as search_document_router
from app.api.endpoints.payment_callback import router as callback_router
from app.api.endpoints.user. donations_public  import public_router as donations_public_router
from app.api.endpoints.user.transactions_public import public_router as transactions_public_router
from app.api.endpoints.user import pdfreader, audiobook
from app.api.endpoints.search_document import router as search_router
from app.api.endpoints.invoice_webhook import router as invoice_webhook_router
from fastapi.responses import Response, FileResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles
from app.api.endpoints.user import views as views_endpoint
from app.api.endpoints.user.bank import router as bank_router






# Configure logging with a default level (INFO)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,  # Default logging level
    handlers=[
        logging.StreamHandler(),  # Only console logging
    ],
)
logger = logging.getLogger(__name__)

# Initialize the FastAPI application
app = FastAPI(
    title="Vinsighte App API",
    description="A comprehensive API combining Paystack integration, user, and admin endpoints.",
    version="1.0.0",
)

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize database
init_db()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8081",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)




# Add IP validation middleware
app.middleware("http")(validate_ip)

# Add rate limiting
add_rate_limiting(app)

# @app.get("/favicon.ico", include_in_schema=False)
# async def favicon():
#     return FileResponse(os.path.join("static", "favicon.ico"))

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")


# Log all incoming requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(
        f"Request path: {request.url.path}, Query params: {request.query_params}"
    )
    response = await call_next(request)
    return response

# Include admin routers
app.include_router(admin_users.router)
app.include_router(admin_documents.router)
app.include_router(admin_settings.router)

# Include user routers
app.include_router(donations_public_router)
app.include_router(transactions_public_router)
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(bookmarks.router)
app.include_router(preferences.router)
app.include_router(scanning.router)
app.include_router(languages.router)
app.include_router(activities.router)
app.include_router(donations_router)
app.include_router(transactions_router)
app.include_router(subscription_router, tags=["subscription"])
app.include_router(search_document_router)
app.include_router(pdfreader.router, tags=["pdfreader"], prefix="/user")
app.include_router(audiobook.router, tags=["audiobook"], prefix="/user")
app.include_router(search_router, tags=["search"])
app.include_router(invoice_webhook_router)
app.include_router(callback_router, tags=["callback"])
app.include_router(views_endpoint.router)
app.include_router(bank_router) 

# Root endpoint
@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Visis App API"}

# Custom error handlers
@app.exception_handler(404)
async def not_found_error_handler(request: Request, exc: Exception):
    logger.error(f"404 Error: {str(exc)} - URL: {request.url}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": "The requested resource was not found"},
    )

@app.exception_handler(422)
async def unprocessable_entity_error_handler(request: Request, exc: Exception):
    logger.error(f"422 Error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Unprocessable Entity: The server understands the content type of the request entity, "
            "but it was unable to process the contained instructions."
        },
    )

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTPException: {exc.detail} - Status code: {exc.status_code} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
# # Add the shutdown event handler
# @app.on_event("shutdown")
# async def shutdown_event():
#     await close_client()
#     logger.info("HTTPX client closed")
