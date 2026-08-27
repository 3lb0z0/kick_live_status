import json
import requests

CLIENT_ID = "your kick client id"
CLIENT_SECRET = "your kick client secret"
TEST_STREAMER = "iceposeidon"


def get_app_access_token(client_id: str, client_secret: str) -> str:
    """Obtain an OAuth Access Token from Kick."""
    token_url = "https://id.kick.com/oauth/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    print(f"[DEBUG] Requesting Token from {token_url}...")
    response = requests.post(token_url, data=payload, headers=headers)
    
    print(f"[DEBUG] Token Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"[DEBUG] Token Response Body: {response.text}")

    response.raise_for_status()
    token_data = response.json()
    return token_data.get("access_token")


def fetch_streamer_status(access_token: str, client_id: str, streamer: str):
    """Fetch channel and live status with full debug output."""
    # Attempting slug parameter endpoint fallback
    endpoints = [
        f"https://api.kick.com/public/v1/channels?slug={streamer}",
        f"https://api.kick.com/public/v1/channels/{streamer}",
    ]

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Client-ID": client_id,
        "Accept": "application/json",
    }

    for url in endpoints:
        print(f"\n[DEBUG] Testing Endpoint: {url}")
        response = requests.get(url, headers=headers)

        print(f"[DEBUG] Response HTTP Status: {response.status_code}")
        print(f"[DEBUG] Response Headers: {dict(response.headers)}")

        try:
            body = response.json()
            print(f"[DEBUG] JSON Payload:\n{json.dumps(body, indent=2)}")
        except Exception:
            print(f"[DEBUG] Raw Text Payload: {response.text}")

        if response.status_code == 200:
            print(f"\nSuccessfully queried endpoint: {url}")
            break


if __name__ == "__main__":
    try:
        print("Fetching Access Token...")
        token = get_app_access_token(CLIENT_ID, CLIENT_SECRET)
        print("Access Token obtained successfully!")

        print(f"\nChecking status for streamer '{TEST_STREAMER}'...")
        fetch_streamer_status(token, CLIENT_ID, TEST_STREAMER)
    except Exception as e:
        print(f"\n[ERROR] Test execution failed: {e}")