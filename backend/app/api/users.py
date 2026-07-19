from app.core.logging import logger
from app.core.rate_limiter import rate_limiter
from app.core.security import (
    create_access_token,
    hash_password,
    oauth2_scheme,
    verify_password,
    verify_token,
)
from app.db.dependencies import get_db
from app.models.user import Users
from app.schemas.user import UserCreate, UserLogin, UserResponse
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Register a new user",
    description="Creates a new user account and returns the created user.",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Invalid request"},
        429: {"description": "Too many registration attempts"},
    },
)
def register_user(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    rate_limiter.allow(
        key=f"register:{request.client.host}", limit=3, window_seconds=60
    )
    existing_user = db.query(Users).filter(Users.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    db_user = Users(email=user.email, hashed_password=hash_password(user.password))

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    logger.info(
        "User registered successfully",
        extra={"email": db_user.email, "user_id": db_user.id},
    )

    return db_user


@router.post(
    "/login",
    summary="User login",
    description="Authenticates a user and returns a JWT access token.",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
        429: {"description": "Too many login attempts"},
    },
)
def login(user_data: UserLogin, request: Request, db: Session = Depends(get_db)):

    rate_limiter.allow(key=f"login:{request.client.host}", limit=5, window_seconds=60)

    user = db.query(Users).filter(Users.email == user_data.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id)})

    logger.info("User logged in", extra={"user_id": user.id, "email": user.email})

    return {"access_token": token, "token_type": "bearer"}


@router.post(
    "/token",
    summary="OAuth2 token endpoint",
    description="Returns an OAuth2 compatible JWT access token.",
)
def token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(Users).filter(Users.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token({"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):

    check_id = verify_token(token)

    if check_id is None:
        raise HTTPException(status_code=401, detail=" Invalid Token")

    user = db.query(Users).filter(Users.id == int(check_id)).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials ")

    return user


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Current authenticated user",
    description="Returns the currently authenticated user's profile.",
)
def get_me(current_user: Users = Depends(get_current_user)):
    return current_user
