from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.core.auth.dependencies import CurrentUserDep
from src.core.settings import get_settings
from src.db.session import AsyncDBSession
from src.repositories.users import user_repository
from src.schemas.user import Token, UserCreate, UserRead
from src.utils.auth import (
    create_access_token,
    get_password_hash,
    verify_password,
)

settings = get_settings()
router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserRead)
async def register(user_in: UserCreate, db: AsyncDBSession):
    user = await user_repository.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists.",
        )

    hashed_password = get_password_hash(user_in.password)
    user_data = user_in.model_dump()
    user_data["hashed_password"] = hashed_password
    del user_data["password"]

    return await user_repository.create(db, obj_in=user_data)


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncDBSession,
):
    user = await user_repository.get_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
async def get_me(current_user: CurrentUserDep):
    return current_user
