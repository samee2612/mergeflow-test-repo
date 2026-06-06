from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, HTTPException, status
from pydantic import ValidationError

from backend.schemas.auth import ErrorResponse, LoginRequest, LoginResponse
from backend.services.auth_service import authenticate_user


router = APIRouter(tags=["auth"])


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Log in with email and password",
    responses={
        400: {
            "model": ErrorResponse,
            "description": "The request body is missing required fields or contains invalid values.",
        },
        401: {
            "model": ErrorResponse,
            "description": "The supplied email and password do not match a known user.",
        },
    },
)
def login(payload: dict[str, Any] | None = Body(default=None)) -> LoginResponse:
    """Validate credentials and return a bearer token for authenticated users."""
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required.",
        )

    try:
        request = LoginRequest(**payload)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required and must be valid.",
        ) from None

    auth_token = authenticate_user(request.email, request.password, request.remember_me)
    if auth_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    return LoginResponse(token=auth_token.token, token_type=auth_token.token_type)
