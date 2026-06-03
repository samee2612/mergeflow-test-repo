"""Authentication API routes used by MergeFlow Step 3 tests."""

from fastapi import APIRouter, Depends, HTTPException, status

from backend.schemas.auth import LoginRequest, LoginResponse
from backend.services.auth_service import AuthService, get_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Log in with email and password",
)
def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    """Validate credentials and return a bearer token."""
    if not payload.email or not payload.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required.",
        )

    auth_result = auth_service.authenticate(
        email=payload.email,
        password=payload.password,
        remember_me=payload.remember_me,
    )
    if auth_result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token, expires_in = auth_result
    return LoginResponse(access_token=token, token_type="bearer", expires_in=expires_in)
