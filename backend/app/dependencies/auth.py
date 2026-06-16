import os
import jwt
from fastapi import Header, HTTPException
from dotenv import load_dotenv

load_dotenv()

RAW_KEY = os.getenv("CLERK_JWT_PUBLIC_KEY", "")
PUBLIC_KEY = RAW_KEY.replace("\\n", "\n")

def get_current_user(authorization: str = Header(...)) -> str:
    """Extract and verify Clerk JWT, return user_id."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    
    token = authorization.removeprefix("Bearer ")
    
    try:
        payload = jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: no sub")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")