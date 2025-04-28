from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from app.db.base import db
from app.services.auth_service import auth_service
from app.db.models import User
from app.api.pydantic_models import UserCreate, UserOut
from app.core.exceptions import AuthenticationError, ValidationError
from app.core.config import settings

router = APIRouter()

@router.get("/validate")
async def validate_user(current_user: User = Depends(auth_service.get_current_user)):
    return {"username": current_user.username}

@router.post("/signup", response_model=UserOut)
async def signup(
    user_data: UserCreate,
    session: AsyncSession = Depends(db.get_session)
):
    try:
        user = await auth_service.create_user(
            username=user_data.username,
            password=user_data.password,
            email=user_data.email,
            session=session
        )
        return UserOut(id=user.id, username=user.username)
    except (ValidationError, AuthenticationError) as e:
        raise
    except Exception as e:
        raise ValidationError(str(e))

@router.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(db.get_session)
):
    try:
        token = await auth_service.authenticate_user(form_data.username, form_data.password, session)
        
        # Set the token in an HTTP-only cookie
        response.set_cookie(
            key="access_token",
            value=f"Bearer {token}",
            httponly=True,
            secure=True,  # Set to True in production
            samesite="lax",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        return {"message": "Login successful"}
    except AuthenticationError as e:
        raise
    except Exception as e:
        raise ValidationError(str(e))

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    return {"message": "Logged out successfully"} 