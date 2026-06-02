#!/usr/bin/env python3
"""
Electronics Industry Reddit Monitor
Tracks component, procurement, and hardware engineering discussions on Reddit.
"""

import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import praw
from dotenv import load_dotenv

load_dotenv()

REDDIT_CLIENT_ID     = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USERNAME      = os.getenv("REDDIT_USERNAME", "")
REDDIT_PASSWORD      = os.getenv("REDDIT_PASSWORD", "")
REDDIT_USER_AGENT    = os.getenv("REDDIT_USER_AGENT", f"electronics-reddit-monitor/1.0 (by /u/{os.getenv('REDDIT_USERNAME', 'user')})")

DAYS_BACK  = int(os.getenv("DAYS_BACK", "7"))
MIN_SCORE  = int(os.getenv("MIN_SCORE", "1"))
KEYWORDS   = [k.strip().lower() for k in os.getenv("KEYWORDS", "").split(",") if k.strip()]
SUBREDDITS = [s.strip() for s in os.getenv("SUBREDDITS", "electronics,embedded,AskElectronics").split(",") if s.strip()]


def connect() -> praw.Reddit:
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
        user_agent=REDDIT_USER_AGENT,
    )


def matches_keywords(text: str) -> list[str]:
    lower = text.lower()
    return [kw for kw in KEYWORDS if kw in lower]


def fetch_subreddit(reddit: praw.Reddit, subreddit_name: str, cutoff: float) -> list[dict]:
    results = []
    try:
        sub = reddit.subreddit(subreddit_name)
        for post in sub.new(limit=100):
            if post.created_utc < cutoff:
                break
            if post.score < MIN_SCORE:
                continue
            combined = f"{post.title} {post.selftext}"
            matched = matches_keywords(combined)
            if not matched:
                continue
            results.append({
                "id": post.id,
                "subreddit": subreddit_name,
                "title": post.title,
                "author": str(post.author) if post.author else "[deleted]",
                "score": post.score,
                "num_comments": post.num_comments,
                "url": f"https://reddit.com{post.permalink}",
                "body": post.selftext[:2000],
                "matched_keywords": matched,
                "created_utc": post.created_utc,
                "created_date": datetime.fromtimestamp(post.created_utc, tz=timezone.utc).strftime("%Y-%m-%d"),
            })
        time.sleep(0.6)  # stay within rate limits
    except Exception as e:
        print(f"  Error on r/{subreddit_name}: {e}")
    return results


def main():
    print("Electronics Industry Reddit Monitor")
    print(f"Monitoring {len(SUBREDDITS)} subreddits for {len(KEYWORDS)} keywords")
    print(f"Date range: last {DAYS_BACK} days\n")

    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        print("ERROR: Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env")
        return

    reddit = connect()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)).timestamp()

    all_posts = []
    seen_ids: set = set()

    for subreddit_name in SUBREDDITS:
        print(f"  r/{subreddit_name} ...", end=" ", flush=True)
        posts = fetch_subreddit(reddit, subreddit_name, cutoff)
        new_posts = [p for p in posts if p["id"] not in seen_ids]
        for p in new_posts:
            seen_ids.add(p["id"])
        all_posts.extend(new_posts)
        print(f"{len(new_posts)} matched")

    all_posts.sort(key=lambda p: p["created_utc"], reverse=True)

    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = out_dir / f"results_{date_str}.json"
    out_path.write_text(json.dumps(all_posts, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nFound {len(all_posts)} posts total")
    print(f"Saved to {out_path}")

    if all_posts:
        print("\nTop matches:")
        for p in all_posts[:5]:
            print(f"  [{p['subreddit']}] {p['title'][:80]}")
            print(f"    {p['url']}")


if __name__ == "__main__":
    main()
