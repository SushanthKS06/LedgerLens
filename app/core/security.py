from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

# Usually provided via env vars
SECRET_KEY = "ledgerlens_super_secret_for_demo"

def create_mock_token(username: str, role: str) -> str:
    """Helper purely for generating valid tokens in tests/scripts."""
    payload = {"sub": username, "role": role}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Validates JWT token and extracts user info and role.
    """
    token = credentials.credentials
    try:
        # Token format {"sub": "username", "role": "analyst"}
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if "role" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Role not found in token",
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
