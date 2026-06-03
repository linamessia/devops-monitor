import os
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

API_KEY_NAME = "X-API-Key"
API_KEY = os.getenv("API_KEY", "dev-secret")

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def verify_api_key(key: str = Security(api_key_header)) -> str:
    """FastAPI dependency that validates the X-API-Key header."""
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return key