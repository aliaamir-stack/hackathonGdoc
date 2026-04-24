import hashlib

import feedparser

from celery_app import celery_app
from database import get_service_client, run_supabase

KEYWORDS = {"outbreak", "alert", "disease", "epidemic", "health"}


@celery_app.task(name="tasks.who_rss.fetch_who_rss")
def fetch_who_rss():
    import asyncio

    asyncio.run(_fetch_who_rss_async())


async def _fetch_who_rss_async():
    feed = feedparser.parse("https://www.who.int/rss-feeds/news-english.xml")
    client = get_service_client()
    for entry in feed.entries:
        content = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
        if not any(word in content for word in KEYWORDS):
            continue
        title = entry.get("title", "").strip()
        title_hash = hashlib.sha256(title.encode("utf-8")).hexdigest()
        existing = await run_supabase(
            client.table("outbreak_alerts")
            .select("id")
            .eq("raw_data->>title_hash", title_hash)
            .limit(1)
            .execute
        )
        if existing.data:
            continue
        await run_supabase(
            client.table("outbreak_alerts")
            .insert(
                {
                    "source": "who_rss",
                    "title": title,
                    "description": entry.get("summary", ""),
                    "severity": "medium",
                    "raw_data": {"title_hash": title_hash, "link": entry.get("link")},
                }
            )
            .execute
        )
