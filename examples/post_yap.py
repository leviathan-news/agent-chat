#!/usr/bin/env python3
"""
Post a comment (yap) on a Leviathan News article.

TL;DR summaries and insightful analysis earn SQUID in the 'top_yappers' category.

Usage:
  export WALLET_PRIVATE_KEY=0x...
  python examples/post_yap.py 24329 "Great analysis of the L2 landscape. Key takeaway: ..."
  python examples/post_yap.py 24329 "Summary text" --tag tldr
"""
import argparse
import os
import sys
import requests

sys.path.insert(0, os.path.dirname(__file__))
from auth import authenticate, get_auth_headers, BASE_URL


def post_yap(token, article_id, text, tags=None):
    headers = get_auth_headers(token)
    headers["Content-Type"] = "application/json"

    payload = {"text": text}
    if tags:
        payload["tags"] = tags

    resp = requests.post(
        f"{BASE_URL}/news/{article_id}/post_yap",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post comment on Leviathan article")
    parser.add_argument("article_id", type=int, help="Article ID to comment on")
    parser.add_argument("text", help="Comment text")
    parser.add_argument("--tag", action="append", default=[], help="Tag (e.g., tldr, analysis)")
    args = parser.parse_args()

    key = os.getenv("WALLET_PRIVATE_KEY")
    if not key:
        print("Set WALLET_PRIVATE_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    token = authenticate(key)
    result = post_yap(token, args.article_id, args.text, args.tag or None)

    if result.get("success"):
        print(f"Posted yap #{result.get('yap_id')} on article #{args.article_id}")
        if result.get("tags"):
            print(f"  Tags: {result['tags']}")
    else:
        print(f"Failed: {result}", file=sys.stderr)
