#!/usr/bin/env python3
"""
Check your SQUID earnings and leaderboard position.

Usage:
  export WALLET_PRIVATE_KEY=0x...
  python examples/check_earnings.py
"""
import os
import sys
import requests

sys.path.insert(0, os.path.dirname(__file__))
from auth import authenticate, get_auth_headers, BASE_URL


def check_earnings(token):
    headers = get_auth_headers(token)

    resp = requests.get(f"{BASE_URL}/wallet/me/earnings/", headers=headers)
    resp.raise_for_status()
    data = resp.json()

    user = data.get("user", {})
    month = data.get("current_month", {})
    positions = data.get("leaderboard_positions", {})
    estimated = data.get("estimated_squid", {})

    print(f"User: {user.get('username')} ({user.get('ethereum_address', 'N/A')[:10]}...)")
    print(f"Month: {month.get('month')}/{month.get('year')}")
    print()

    print("Leaderboard Positions:")
    for category, info in positions.items():
        rank = info.get("rank") or "N/A"
        share = info.get("market_share", 0)
        print(f"  {category}: rank #{rank}, {share}% market share")
    print()

    print(f"Estimated SQUID this month: {estimated.get('total', 0):,.0f}")
    breakdown = estimated.get("breakdown", {})
    for category, amount in breakdown.items():
        if amount > 0:
            print(f"  {category}: {amount:,.0f} SQUID")


if __name__ == "__main__":
    key = os.getenv("WALLET_PRIVATE_KEY")
    if not key:
        print("Set WALLET_PRIVATE_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    token = authenticate(key)
    check_earnings(token)
