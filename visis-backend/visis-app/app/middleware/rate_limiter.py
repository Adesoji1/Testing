# app/middlewares/rate_limiter.py

# from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address
# from fastapi import FastAPI, Request, Response
# from starlette.responses import JSONResponse
# from app.core.config import settings
# import logging

# limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])

# def add_rate_limiting(app: FastAPI):
#     app.state.limiter = limiter
#     app.add_exception_handler(limiter.rate_limit_exceeded_handler, _rate_limit_exceeded_handler)

# app/middlewares/rate_limiter.py

# from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.errors import RateLimitExceeded
# from slowapi.util import get_remote_address
# from fastapi import FastAPI, Request, Response
# from starlette.responses import JSONResponse
# from app.core.config import settings
# import logging

# # Initialize the Limiter with the desired rate limits
# limiter = Limiter(
#     key_func=get_remote_address,
#     default_limits=[settings.RATE_LIMIT]
# )

# def add_rate_limiting(app: FastAPI):
#     # Attach the Limiter to the FastAPI application's state
#     app.state.limiter = limiter
    
#     # Add the rate limit exceeded exception handler
#     app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)




# app/middleware/rate_limiter.py

# app/middleware/rate_limiter.py

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import FastAPI
from app.core.config import settings

# Initialize the Limiter with the desired rate limits
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT],
    headers_enabled=True  # Enable rate limit headers
)

# def add_rate_limiting(app: FastAPI):
#     # Attach the Limiter to the FastAPI application's state
#     app.state.limiter = limiter

#     # Add the rate limit exceeded exception handler
#     app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

#     # Add the SlowAPI middleware
#     app.add_middleware(SlowAPIMiddleware)

def add_rate_limiting(app: FastAPI):
    # Comment out the rate limiting middleware
    # app.add_middleware(SlowAPIMiddleware)
    pass
