from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        description="Email address for the account attempting to log in.",
        example="admin@example.com",
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Plain text password submitted by the user.",
        example="correct-horse-battery-staple",
    )


class LoginResponse(BaseModel):
    token: str = Field(
        ...,
        description="Bearer token returned after successful authentication.",
        example="demo-token-for-admin-user",
    )
    token_type: str = Field(
        default="bearer",
        description="Token type clients should use in the Authorization header.",
        example="bearer",
    )


class ErrorResponse(BaseModel):
    detail: str = Field(
        ...,
        description="Human-readable error explaining why login failed.",
        example="Invalid email or password.",
    )
