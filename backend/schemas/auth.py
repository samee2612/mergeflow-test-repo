from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        description="User email address used for login.",
        examples=["demo@example.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Plain-text password submitted over HTTPS.",
        examples=["correct-horse-battery"],
    )


class LoginResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token for authenticated requests.")
    token_type: str = Field(default="bearer", description="OAuth token type.")