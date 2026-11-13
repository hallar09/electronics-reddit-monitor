#!/usr/bin/env python3
"""Personal, non-commercial electronics reading list for Reddit."""

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import praw
from dotenv import load_dotenv

load_dotenv()

ALLOWED_SUBREDDITS = (
    "electronics",
    "AskElectronics",
    "embedded",
    "PrintedCircuitBoard",
)

# Seven days is this project's chosen maximum, not a Reddit policy claim.
MAX_RETENTION_DAYS = 7
OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def purge_exports():
    """Remove this tool's generated exports, including old dated exports."""
    if not OUTPUT_DIR.exists():
        return

    paths = list(OUTPUT_DIR.glob("results_*.json"))
    paths.extend([
        OUTPUT_DIR / "results.json",
        OUTPUT_DIR / "results.json.tmp",
    ])

    for path in paths:
        if path.is_file() or path.is_symlink():
            path.unlink()


def get_settings():
    days_back = int(os.getenv("DAYS_BACK", "7"))
    if not 1 <= days_back <= MAX_RETENTION_DAYS:
        raise ValueError("DAYS_BACK must be between 1 and 7.")

    keywords = [
        value.strip().lower()
        for value in os.getenv("KEYWORDS", "").split(",")
        if value.strip()
    ]
    if not keywords:
        raise ValueError("Set at least one KEYWORDS value in .env.")

    allowed = {name.lower(): name for name in ALLOWED_SUBREDDITS}
    requested = [
        value.strip()
        for value in os.getenv(
            "SUBREDDITS", ",".join(ALLOWED_SUBREDDITS)
        ).split(",")
        if value.strip()
    ]

    if not requested:
        raise ValueError("Configure at least one subreddit.")

    unsupported = [
        name for name in requested if name.lower() not in allowed
    ]
    if unsupported:
        raise ValueError(
            "Subreddits outside the supported scope: "
            + ", ".join(unsupported)
        )

    subreddits = list(dict.fromkeys(
        allowed[name.lower()] for name in requested
    ))

    return (
        days_back,
        int(os.getenv("MIN_SCORE", "1")),
        keywords,
        subreddits,
    )


def connect():
    client_id = os.getenv("REDDIT_CLIENT_ID", "")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
    user_agent = os.getenv("REDDIT_USER_AGENT", "")

    if not all((client_id, client_secret, user_agent)):
        raise ValueError(
            "Set REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, "
            "and REDDIT_USER_AGENT in .env."
        )

    # Application-only authentication for public, read-only access.
    # No Reddit account password is required by this script.
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )
    reddit.read_only = True
    return reddit


def fetch_subreddit(reddit, name, cutoff, min_score, keywords):
    results = []

    for post in reddit.subreddit(name).new(limit=100):
        if post.created_utc < cutoff:
            continue

        body = post.selftext or ""

        # Conservative exclusion: also skip posts whose author is gone.
        if post.author is None:
            continue
        if body.strip().lower() in {"[deleted]", "[removed]"}:
            continue
        if getattr(post, "removed_by_category", None):
            continue
        if post.score < min_score:
            continue

        # Text is used transiently for matching, never written to exports.
        text = f"{post.title} {body}".lower()
        if not any(keyword in text for keyword in keywords):
            continue

        results.append({
            "id": post.id,
            "subreddit": name,
            "url": f"https://www.reddit.com{post.permalink}",
            "created_utc": post.created_utc,
        })

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Create a personal electronics reading list."
    )
    parser.add_argument(
        "--purge",
        action="store_true",
        help="Delete generated exports without accessing Reddit.",
    )
    args = parser.parse_args()

    # Clear legacy exports before authentication or network access.
    # If cleanup fails, stop instead of leaving stale exports unnoticed.
    try:
        purge_exports()
    except OSError:
        print("Cleanup failed. Check permissions on the output folder.")
        return 1

    if args.purge:
        print("Generated exports deleted.")
        return 0

    if os.getenv("REDDIT_ACCESS_APPROVED", "").lower() != "true":
        print(
            "API access is disabled. Only set REDDIT_ACCESS_APPROVED=true "
            "after Reddit explicitly approves this use case."
        )
        return 1

    try:
        days_back, min_score, keywords, subreddits = get_settings()
        cutoff = (
            datetime.now(timezone.utc) - timedelta(days=days_back)
        ).timestamp()

        posts_by_id = {}
        with connect() as reddit:
            for name in subreddits:
                for post in fetch_subreddit(
                    reddit, name, cutoff, min_score, keywords
                ):
                    posts_by_id[post["id"]] = post

        results = sorted(
            posts_by_id.values(),
            key=lambda item: item["created_utc"],
            reverse=True,
        )

        OUTPUT_DIR.mkdir(exist_ok=True)
        temporary = OUTPUT_DIR / "results.json.tmp"
        destination = OUTPUT_DIR / "results.json"

        # Restrict newly created export files to the current OS user.
        descriptor = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(results, handle, indent=2)
            handle.write("\n")

        temporary.replace(destination)
        print(f"Saved {len(results)} links to {destination}")
        return 0

    except Exception as exc:
        # Do not preserve partial exports after a failed refresh.
        purge_exports()
        print(f"Refresh failed ({type(exc).__name__}); no export retained.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())))
