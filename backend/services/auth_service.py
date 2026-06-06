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
    session_suffix = "long-lived" if remember_me else "session"
    token = f"{issuer}-{session_suffix}-token-for-{user['user_id']}"
    return AuthToken(token=token)
