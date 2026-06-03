from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
def login(email: str, password: str):
    if email == "admin@tes1t.com" and password == "password":
        return {
            "token": "jwt-token"
        }

    return {
        "error": "invalid credentials"
    }