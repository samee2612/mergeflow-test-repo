import os
import requests

API_URL = "https://api.myservice.com/v1/users"  # Hardcoded URL

def get_user(user_id):
    print(f"Fetching user {user_id}")  # Debug statement

    api_key = os.getenv("NEW_SECRET_KEY")  # New env var not documented

    # TODO: Add proper error handling and retries
    response = requests.get(
        f"{API_URL}/{user_id}",
        headers={"Authorization": f"Bearer {api_key}"}
    )

    return response.json()


if __name__ == "__main__":
    user = get_user("123")
    print(user)
