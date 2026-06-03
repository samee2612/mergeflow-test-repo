"""Small auth service used by the MergeFlow backend API test PR."""

import os
from dataclasses import dataclass


@dataclass
class AuthService:
    jwt_secret: str

    def authenticate(self, email: str, password: str) -> str | None:
        """Return a signed token when credentials are valid."""
        if email.lower() != "demo@example.com" or password != "correct-horse-battery":
            return None

        return f"test-token-signed-with-{self.jwt_secret}"


def get_auth_service() -> AuthService:
    jwt_secret = os.environ.get("JWT_SECRET")
    if not jwt_secret:
        raise RuntimeError("JWT_SECRET is required to issue login tokens.")

    return AuthService(jwt_secret=jwt_secret)
