from fastapi import Request, status
from fastapi.responses import JSONResponse

# Allow access for frontend ports (e.g., React Native running on port 8081 or 3000)
ALLOWED_PORTS = ["8081", "3000"]  # Modify this list to add more ports if necessary

async def validate_ip(request: Request, call_next):
    # Get the client's IP address
    client_ip = request.client.host

    # Check if the request is coming from the allowed ports
    if str(request.url.port) not in ALLOWED_PORTS:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": f"Port {request.url.port} is not allowed to access this resource."}
        )

    # Proceed with the request if the port is allowed
    return await call_next(request)




# from fastapi import Request, status
# from fastapi.responses import JSONResponse

# # List of whitelisted IPs
# WHITELISTED_IPS = ["127.0.0.1", "192.168.1.1","98.97.79.27","102.90.46.87"]  # Add your IPs here

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



# from fastapi import Request, status
# from fastapi.responses import JSONResponse

# # List of whitelisted IPs
# WHITELISTED_IPS = ["127.0.0.1", "192.168.1.1", "98.97.79.27"]  # Add your IPs here

# async def validate_ip(request: Request, call_next):
#     # Get the client's IP address from headers or request client
#     client_ip = request.headers.get('X-Forwarded-For', request.client.host)

#     # Allow access for frontend ports (e.g., React Native running on port 8081 or 3000)
#     allowed_ports = ["8081", "3000"]

#     # Check if the client's IP is in the whitelist or accessing from allowed ports
#     if client_ip not in WHITELISTED_IPS and str(request.url.port) not in allowed_ports:
#         return JSONResponse(
#             status_code=status.HTTP_403_FORBIDDEN,
#             content={"message": f"IP {client_ip} is not allowed to access this resource."}
#         )
    
#     # Proceed with the request if IP or port is allowed
#     return await call_next(request)
