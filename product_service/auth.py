import os
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "NEXUS_SUPER_SECRET_KEY")
ALGORITHM = "HS256"

security = HTTPBearer()

def get_current_admin_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        is_admin: bool = payload.get("is_admin", False)
        
        if email is None:
            raise credentials_exception
            
        if not is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
            
        return payload
    except JWTError:
        raise credentials_exception
