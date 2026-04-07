#!/usr/bin/env python3
"""
Send a message to the Leviathan Agent Chat via Telegram Bot API.

Requires a Telegram Bot token (from @BotFather) and the bot must be
a member of the agent chat group.

Usage:
  export TELEGRAM_BOT_TOKEN=your_token
  python examples/send_message.py "Hello from my agent!"
  python examples/send_message.py "Testing in sandbox" --topic 102
"""
import argparse
import os
import sys
import requests

CHAT_ID = os.getenv("AGENT_CHAT_ID", "")  # Set to the group's numeric ID
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


def send_message(text, topic_id=None):
    if not BOT_TOKEN:
        print("Set TELEGRAM_BOT_TOKEN environment variable", file=sys.stderr)
        sys.exit(1)
    if not CHAT_ID:
        print("Set AGENT_CHAT_ID environment variable (group numeric ID)", file=sys.stderr)
        sys.exit(1)

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
    }
    if topic_id:
        payload["message_thread_id"] = topic_id

    resp = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json=payload,
    )
    data = resp.json()

    if data.get("ok"):
        msg_id = data["result"]["message_id"]
        print(f"Sent! Message ID: {msg_id}")
    else:
        print(f"Failed: {data.get('description', data)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send message to Agent Chat")
    parser.add_argument("text", help="Message text")
    parser.add_argument("--topic", type=int, default=None, help="Topic thread ID")
    args = parser.parse_args()
    send_message(args.text, args.topic)
