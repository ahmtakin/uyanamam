import requests
import os
from auth import get_jwt


TOKEN_CACHE_PATH = "jwt_token.txt"


def is_valid_jwt(token: str) -> bool:
    """Checks if the token looks like a valid JWT."""
    return token and token.count(".") == 2 and all(len(part) > 0 for part in token.split("."))


def get_cached_token() -> str | None:
    """Returns cached JWT if exists and valid."""
    if not os.path.exists(TOKEN_CACHE_PATH):
        return None
    with open(TOKEN_CACHE_PATH, "r") as f:
        token = f.read().strip()
        return token if is_valid_jwt(token) else None


def save_token(token: str):
    """Saves the token to a file."""
    os.makedirs(os.path.dirname(TOKEN_CACHE_PATH) or ".", exist_ok=True)
    with open(TOKEN_CACHE_PATH, "w") as f:
        f.write(token)


def get_or_fetch_token() -> str:
    """Returns a valid JWT, either from cache or by authenticating."""
    token = get_cached_token()
    if token:
        return token
    token = get_jwt()
    if is_valid_jwt(token):
        save_token(token)
        return token
    raise ValueError("Failed to retrieve valid JWT token.")


def build_headers(token: str) -> dict:
    """Builds headers with the given JWT."""
    token = token.strip('"')
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


def enroll(crns: list[str]):
    """
    Enrolls in courses by sending a POST request with CRNs formatted under ECRN.
    :param crns: List of CRN strings
    """
    if not crns:
        raise ValueError("CRNs list is empty.")

    token = get_or_fetch_token()
    headers = build_headers(token)

    url = "https://obs.itu.edu.tr/api/ders-kayit/v21"
    payload = {
        "ECRN": crns,
        "SCRN": []
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print("[+] Enrollment request successful.")
        print(response.json())
    else:
        print("[-] Enrollment failed.")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
