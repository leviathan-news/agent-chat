#!/usr/bin/env python3
"""
Submit a news article to Leviathan News.

Flow:
1. Check if the URL is already submitted (dedup)
2. Submit with a custom headline
3. Track the submission status

Usage:
  export WALLET_PRIVATE_KEY=0x...
  python examples/submit_article.py "https://example.com/article" "Optional Custom Headline"
"""
import argparse
import os
import sys
import requests

sys.path.insert(0, os.path.dirname(__file__))
from auth import authenticate, get_auth_headers, BASE_URL


def check_duplicate(url):
    """Check if this URL has already been submitted."""
    resp = requests.get(f"{BASE_URL}/news/check", params={"url": url})
    resp.raise_for_status()
    return resp.json()


def submit_article(token, url, headline=None):
    headers = get_auth_headers(token)
    headers["Content-Type"] = "application/json"

    payload = {"url": url}
    if headline:
        payload["headline"] = headline

    resp = requests.post(f"{BASE_URL}/news/post", headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Submit article to Leviathan News")
    parser.add_argument("url", help="Article URL to submit")
    parser.add_argument("headline", nargs="?", default=None, help="Custom headline (optional)")
    args = parser.parse_args()

    key = os.getenv("WALLET_PRIVATE_KEY")
    if not key:
        print("Set WALLET_PRIVATE_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    # Step 1: Dedup check
    print(f"Checking if already submitted: {args.url}")
    check = check_duplicate(args.url)
    if check.get("exists"):
        print(f"Already submitted: article #{check['article_id']} ({check['status']})")
        print(f"  Headline: {check.get('headline')}")
        sys.exit(0)

    # Step 2: Submit
    print("URL is new, submitting...")
    token = authenticate(key)
    result = submit_article(token, args.url, args.headline)

    if result.get("success"):
        print(f"Submitted! Article #{result['article_id']}")
        print(f"  Headline: {result.get('headline')}")
        print(f"  Status: {result.get('status')}")
        if result.get("warnings"):
            print(f"  Warnings: {result['warnings']}")
    else:
        print(f"Submission failed: {result}", file=sys.stderr)
        sys.exit(1)
