from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from config import get_settings
from database import get_anon_client, run_supabase
from models.schemas import LoginRequest, TokenResponse

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


def _create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = {"sub": subject, "exp": int(expire.timestamp())}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    client = get_anon_client()
    try:
        result = await run_supabase(
            client.table("users")
            .select("id,email,password_hash")
            .eq("email", payload.email)
            .limit(1)
            .execute
        )
        records = result.data or []
        if not records:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        user = records[0]
        if payload.password != user["password_hash"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        token = _create_access_token(user["id"])
        return TokenResponse(access_token=token)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Login failed: {exc}") from exc


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        subject: str | None = payload.get("sub")
        if not subject:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    client = get_anon_client()
    result = await run_supabase(
        client.table("users").select("id,email").eq("id", subject).limit(1).execute
    )
    records = result.data or []
    if not records:
        raise HTTPException(status_code=401, detail="User not found")
    return records[0]
