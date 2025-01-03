# from fastapi import Request, status
# from fastapi.responses import JSONResponse

# # List of whitelisted IPs
# WHITELISTED_IPS = ["127.0.0.1", "192.168.1.1"]  # Add your IPs here

# async def validate_ip(request: Request, call_next):
#     # Get the client's IP address
#     client_ip = request.client.host

#     # Allow access for frontend ports (e.g., React Native running on port 8081 or 3000)
#     allowed_ports = ["8081", "3000"]

#     # Check if the client's IP is in the whitelist or accessing from allowed ports
#     if client_ip not in WHITELISTED_IPS and request.url.port not in allowed_ports:
#         return JSONResponse(
#             status_code=status.HTTP_403_FORBIDDEN,
#             content={"message": f"IP {client_ip} is not allowed to access this resource."}
#         )
    
#     # Proceed with the request if IP or port is allowed
#     return await call_next(request)


# import os
# from fastapi import Request, status
# from fastapi.responses import JSONResponse

# # Get the port from the environment (Render sets this dynamically)
# RENDER_PORT = os.getenv("PORT", "10000")  # Default to 10000 if not set

# # Allow access for frontend ports and the dynamically assigned Render port
# ALLOWED_PORTS = ["8081", "3000", RENDER_PORT]

# async def validate_ip(request: Request, call_next):
#     # Get the request's port
#     port = request.url.port

#     # Allow if the port is None (e.g., no port specified in the request)
#     if port is None:
#         return await call_next(request)

#     # Allow requests from the allowed ports
#     if str(port) not in ALLOWED_PORTS:
#         return JSONResponse(
#             status_code=status.HTTP_403_FORBIDDEN,
#             content={"message": f"Port {port} is not allowed to access this resource."}
#         )

#     # Proceed with the request if the port is allowed
#     return await call_next(request)




# app/middleware/ip_whitelist.py

import os
from fastapi import Request, status
from fastapi.responses import JSONResponse

# Get the port from the environment (Render sets this dynamically)
RENDER_PORT = os.getenv("PORT", "10000")  # Default to 10000 if not set

# Allow access for frontend ports and the dynamically assigned Render port
ALLOWED_PORTS = ["8081", "3000", "8000", RENDER_PORT]

async def validate_ip(request: Request, call_next):
    # Exempt the /donations/callback endpoint from port validation
    if request.url.path.startswith("/donations/callback"):
        return await call_next(request)
    

    # Get the request's port
    port = request.url.port

    # Allow if the port is None (e.g., no port specified in the request)
    if port is None:
        return await call_next(request)

    # Allow requests from the allowed ports
    if str(port) not in ALLOWED_PORTS:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": f"Port {port} is not allowed to access this resource."},
        )

    # Proceed with the request if the port is allowed
    return await call_next(request)
