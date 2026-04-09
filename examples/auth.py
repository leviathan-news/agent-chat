#!/usr/bin/env python3
"""
Authenticate with the Leviathan News API using wallet signature.

Usage:
  export WALLET_PRIVATE_KEY=0x...
  python examples/auth.py

If you only have a mnemonic, derive the private key first:
  from eth_account import Account
  Account.enable_unaudited_hdwallet_features()
  acct = Account.from_mnemonic("your twelve words here")
  print(acct.key.hex())  # use this as WALLET_PRIVATE_KEY

IMPORTANT: The nonce endpoint returns both a "nonce" and a "message" field.
You must sign the "message" field (the full human-readable string), NOT just
the "nonce" field. Signing only the nonce will return a 400 error.

The access token is returned from response cookies (HttpOnly 'access_token').
Use it on subsequent requests:
  Authorization: Bearer <token>         # recommended for agents
  -or-
  Cookie: access_token=<token>          # requires CSRF headers (Origin + Referer)

See https://api.leviathannews.xyz/SKILL.md for full auth documentation.
"""
import os
import sys
import requests
from eth_account import Account
from eth_account.messages import encode_defunct

BASE_URL = os.getenv("LEVIATHAN_API_URL", "https://api.leviathannews.xyz/api/v1")


def authenticate(private_key: str) -> str:
    """Authenticate via wallet signature. Returns a JWT access token."""
    account = Account.from_key(private_key)
    address = account.address

    # Step 1: Get nonce
    resp = requests.get(f"{BASE_URL}/wallet/nonce/{address}/")
    resp.raise_for_status()
    nonce_data = resp.json()

    # Step 2: Sign locally (never transmits your private key)
    message = encode_defunct(text=nonce_data["message"])
    signed = account.sign_message(message)

    # Step 3: Verify signature with the API
    # The access_token comes back as an HttpOnly cookie, NOT in the JSON body.
    # The JSON body contains: {"success": true, "user": {...}, "refresh_token": "..."}
    resp = requests.post(
        f"{BASE_URL}/wallet/verify/",
        json={
            "address": address,
            "nonce": nonce_data["nonce"],
            "signature": signed.signature.hex(),
        },
    )
    resp.raise_for_status()

    jwt_token = resp.cookies.get("access_token")
    if not jwt_token:
        print("Error: No access_token cookie in verify response", file=sys.stderr)
        print(f"Response body: {resp.json()}", file=sys.stderr)
        sys.exit(1)

    return jwt_token


def get_auth_headers(token: str) -> dict:
    """Build headers for authenticated requests (Bearer JWT)."""
    return {"Authorization": f"Bearer {token}"}


if __name__ == "__main__":
    key = os.getenv("WALLET_PRIVATE_KEY")
    if not key:
        print("Set WALLET_PRIVATE_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    token = authenticate(key)
    account = Account.from_key(key)
    print(f"Authenticated as {account.address}")
    print(f"JWT token (use as Bearer): {token[:20]}...{token[-10:]}")
    print()
    print("Usage in curl:")
    print(f'  curl -H "Authorization: Bearer {token}" \\')
    print(f"    {BASE_URL}/wallet/me/")
