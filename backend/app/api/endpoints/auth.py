from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.services.auth_service import auth_service
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

class SignupBody(BaseModel):
    email: EmailStr
    password: str
    metadata: dict | None = None

class LoginBody(BaseModel):
    email: EmailStr
    password: str

@router.post("/signup")
def signup(body: SignupBody):
    try:
        resp = auth_service.signup(body.email, body.password, body.metadata)
        return {
            "user": resp.user.model_dump(),
            "session": resp.session.model_dump() if resp.session else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login")
def login(body: LoginBody):
    try:
        resp = auth_service.login(body.email, body.password)
        return {
            "access_token": resp.session.access_token,
            "refresh_token": resp.session.refresh_token,
            "user": resp.user.model_dump(),
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Authentication failed: {str(e)}")

@router.get("/me")
def read_current_user(current_user = Depends(get_current_user)):
    return current_user.model_dump()