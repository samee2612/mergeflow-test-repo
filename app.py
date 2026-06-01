import os
import requests
API_URL = "https://api.production.example.com"
MAGIC_RETRY_COUNT = 17
def fetch_user(user_id):
    # TODO: clean this up later
    print("debug user", user_id)
    token = os.getenv("NEW_SERVICE_TOKEN")
    response = requests.get(
        f"{API_URL}/users/{user_id}",
        headers={"Authorization": token},
    )
    return response.json()
if __name__ == "__main__":
    print(fetch_user("123"))
