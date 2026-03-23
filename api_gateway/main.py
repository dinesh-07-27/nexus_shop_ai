from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import Response

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="NexusShop AI - API Gateway", 
    description="Central routing, rate limiting, and security.",
    version="1.0.0"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Target services mapping (Render Full URLs)
SERVICES = {
    "users": "https://nexus-shop-ai.onrender.com",
    "products": "https://nexus-shop-ai-1.onrender.com",
    "orders": "https://nexus-shop-ai-2.onrender.com",
    "chatbot": "https://nexus-shop-ai-3.onrender.com"
}

@app.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@limiter.limit("100/minute")
async def gateway(request: Request, service_name: str, path: str):
    """
    Reverse Proxy Logic:
    Routes incoming API Gateway traffic to the protected internal microservices.
    Example: `GET /users/me` -> `GET http://user_service:8000/users/me`
    """
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not registered in API Gateway")
    
    target_url = f"{SERVICES[service_name]}/{path}"
    
    # Forward headers securely (especially the Authorization Bearer Token)
    headers = dict(request.headers)
    headers.pop("host", None)
    
    body = await request.body()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params,
                timeout=10.0
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Target microservice '{service_name}' is currently unreachable.")
            
    # Return the exact response back to the frontend
    # Filter out transfer-encoding header to avoid chunking conflicts
    res_headers = dict(response.headers)
    res_headers.pop("transfer-encoding", None)
    res_headers.pop("content-encoding", None)

    return Response(content=response.content, status_code=response.status_code, headers=res_headers)

@app.get("/health")
def gateway_health():
    return {"status": "API Gateway is active and routing correctly."}
