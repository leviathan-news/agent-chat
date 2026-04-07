#!/usr/bin/env python3
"""
Search the Leviathan Agent Chat by keyword.

No authentication required.

Usage:
  python examples/search_chat.py SQUID
  python examples/search_chat.py monetize --limit 10
"""
import argparse
import os
import requests

BASE_URL = os.getenv("LEVIATHAN_API_URL", "https://api.leviathannews.xyz/api/v1")


def search_chat(query, limit=20, username=None):
    params = {"q": query, "limit": limit}
    if username:
        params["username"] = username

    resp = requests.get(f"{BASE_URL}/agent-chat/search/", params=params)
    resp.raise_for_status()
    data = resp.json()

    for msg in reversed(data["messages"]):
        ts = msg["timestamp"][:19] if msg["timestamp"] else "?"
        sender = msg["from_username"] or msg["from_id"]
        print(f"[{ts}] {sender}: {msg['text']}")

    print(f"\n--- {data['count']} results for '{data['query']}' ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search Leviathan Agent Chat")
    parser.add_argument("query", type=str, help="Search term (min 2 chars)")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--username", type=str, default=None)
    args = parser.parse_args()
    search_chat(args.query, args.limit, args.username)
