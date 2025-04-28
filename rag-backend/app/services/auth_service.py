from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.db.models import User
from app.db.base import db
from app.core.exceptions import (
    AuthenticationError,
    ValidationError,
    ConflictError,
    DatabaseError
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.pwd_context = pwd_context

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    async def get_current_user(self, request: Request, session: AsyncSession = Depends(db.get_session)) -> User:
        try:
            # Get token from cookie
            token = request.cookies.get("access_token")
            if not token:
                raise AuthenticationError("No access token found in cookies")
            
            # Remove 'Bearer ' prefix if present
            if token.startswith("Bearer "):
                token = token[7:]
            
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise AuthenticationError("Invalid authentication credentials")
        except JWTError:
            raise AuthenticationError("Invalid authentication credentials")

        try:
            result = await session.execute(select(User).where(User.username == username))
            user = result.scalar_one_or_none()
            if user is None:
                raise AuthenticationError("User not found")
            return user
        except Exception as e:
            raise DatabaseError(f"Error fetching user: {str(e)}")

    async def authenticate_user(self, username: str, password: str, session: AsyncSession) -> str:
        try:
            result = await session.execute(select(User).where(User.username == username))
            user = result.scalar_one_or_none()
            
            if not user:
                raise AuthenticationError("Incorrect username or password")
            if not self.verify_password(password, user.hashed_password):
                raise AuthenticationError("Incorrect username or password")
                
            access_token = self.create_access_token(data={"sub": user.username})
            return access_token
        except AuthenticationError:
            raise
        except Exception as e:
            raise DatabaseError(f"Error authenticating user: {str(e)}")

    async def create_user(self, username: str, password: str, email: str, session: AsyncSession) -> User:
        try:
            # Check if username already exists
            result = await session.execute(select(User).where(User.username == username))
            if result.scalar_one_or_none():
                raise ConflictError("Username already exists")

            # Check if email already exists
            result = await session.execute(select(User).where(User.email == email))
            if result.scalar_one_or_none():
                raise ConflictError("Email already registered")

            # Validate password
            if len(password) < 8:
                raise ValidationError("Password must be at least 8 characters long")

            hashed_password = self.get_password_hash(password)
            user = User(
                username=username,
                email=email,
                hashed_password=hashed_password
            )
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        except (ValidationError, ConflictError):
            raise
        except Exception as e:
            raise DatabaseError(f"Error creating user: {str(e)}")

auth_service = AuthService() 