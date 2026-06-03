"""Small auth service used by the MergeFlow backend API test PR."""

import os
from dataclasses import dataclass


@dataclass
class AuthService:
    jwt_secret: str
    token_ttl_seconds: int

    def authenticate(self, email: str, password: str, remember_me: bool = False) -> tuple[str, int] | None:
        """Return a signed token when credentials are valid."""
        if email.lower() != "demo@example.com" or password != "correct-horse-battery":
            return None

        expires_in = self.token_ttl_seconds * 7 if remember_me else self.token_ttl_seconds
        return f"test-token-signed-with-{self.jwt_secret}", expires_in


def get_auth_service() -> AuthService:
    jwt_secret = os.environ.get("JWT_SECRET")
    if not jwt_secret:
        raise RuntimeError("JWT_SECRET is required to issue login tokens.")

    token_ttl_seconds = int(os.environ.get("JWT_EXPIRES_IN_SECONDS", "3600"))
    return AuthService(jwt_secret=jwt_secret, token_ttl_seconds=token_ttl_seconds)
