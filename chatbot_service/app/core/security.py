import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# Use the exact same global secret key as the User Service
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "NEXUS_SUPER_SECRET_KEY")
ALGORITHM = "HS256"

# This expects the frontend/Postman to send the standard Bearer token
# Swagger UI will now correctly point to the Auth service for login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="https://nexus-shop-ai.onrender.com/api/v1/users/login")

def get_current_user_payload(token: str = Depends(oauth2_scheme)) -> dict:
    """Extracts and cryptographically verifies the JWT across microservice boundaries."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception
