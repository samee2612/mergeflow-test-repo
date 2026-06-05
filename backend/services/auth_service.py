from __future__ import annotations

from dataclasses import dataclass
import os
import secrets


DEMO_USERS = {
    "admin@example.com": {
        "password": "correct-horse-battery-staple",
        "user_id": "admin-user",
    }
}


@dataclass(frozen=True)
class AuthToken:
    token: str
    token_type: str = "bearer"
    expires_in: int = 3600


def authenticate_user(email: str, password: str, remember_me: bool = False) -> AuthToken | None:
    """Return a demo token when credentials match the in-memory user store."""
    normalized_email = email.strip().lower()
    user = DEMO_USERS.get(normalized_email)
    if not user:
        return None

    expected_password = user["password"]
    if not secrets.compare_digest(password, expected_password):
        return None

    issuer = os.getenv("AUTH_TOKEN_ISSUER", "mergeflow-test")
    token = f"{issuer}-token-for-{user['user_id']}"
    expires_in = 86400 if remember_me else 3600
    return AuthToken(token=token, expires_in=expires_in)
