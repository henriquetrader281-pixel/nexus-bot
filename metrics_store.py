from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("NEXUS_METRICS_DB", str(BASE_DIR / "nexus_metrics.sqlite3")))
SCHEMA_PATH = BASE_DIR / "metrics_schema.sql"


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with connect() as connection:
        connection.executescript(schema)


def create_campaign(marketplace: str, official_affiliate_url: str, product_name: str, product_external_id: str | None = None) -> int:
    if not official_affiliate_url.startswith(("http://", "https://")):
        raise ValueError("official_affiliate_url precisa ser HTTP(S)")
    init_db()
    with connect() as connection:
        cursor = connection.execute(
            "INSERT INTO campaigns (marketplace, official_affiliate_url, product_name, product_external_id) VALUES (?, ?, ?, ?)",
            (marketplace, official_affiliate_url, product_name, product_external_id),
        )
        return int(cursor.lastrowid)


def create_creative(campaign_id: int, variant: str, title: str, description: str, cta: str, *, asset_path: str | None = None, asset_url: str | None = None, width: int | None = None, height: int | None = None, duration_seconds: float | None = None, status: str = "draft") -> int:
    if variant not in {"image_a", "video_b"}:
        raise ValueError("variant precisa ser image_a ou video_b")
    init_db()
    with connect() as connection:
        cursor = connection.execute(
            """INSERT INTO creatives
            (campaign_id, variant, asset_path, asset_url, title, description, cta, width, height, duration_seconds, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (campaign_id, variant, asset_path, asset_url, title, description, cta, width, height, duration_seconds, status),
        )
        return int(cursor.lastrowid)


def record_publication(creative_id: int, channel: str, *, external_post_id: str | None = None, external_url: str | None = None, status: str = "pending") -> int:
    if channel not in {"pinterest", "instagram", "tiktok"}:
        raise ValueError("channel inválido")
    init_db()
    with connect() as connection:
        cursor = connection.execute(
            """INSERT INTO publications
            (creative_id, channel, external_post_id, external_url, status, published_at, last_checked_at)
            VALUES (?, ?, ?, ?, ?, CASE WHEN ? = 'published' THEN datetime('now') ELSE NULL END, datetime('now'))""",
            (creative_id, channel, external_post_id, external_url, status, status),
        )
        return int(cursor.lastrowid)


def record_metrics(publication_id: int, impressions: int, clicks: int, conversions: int, *, spend_cents: int = 0, revenue_cents: int = 0) -> int:
    values = [impressions, clicks, conversions, spend_cents, revenue_cents]
    if any(not isinstance(value, int) or value < 0 for value in values):
        raise ValueError("métricas precisam ser inteiros não negativos")
    if impressions and clicks > impressions:
        raise ValueError("cliques não podem exceder impressões")
    if clicks and conversions > clicks:
        raise ValueError("conversões não podem exceder cliques")
    init_db()
    with connect() as connection:
        cursor = connection.execute(
            """INSERT INTO creative_metrics
            (publication_id, impressions, clicks, conversions, spend_cents, revenue_cents)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (publication_id, impressions, clicks, conversions, spend_cents, revenue_cents),
        )
        return int(cursor.lastrowid)


def performance_rows() -> list[dict[str, Any]]:
    init_db()
    with connect() as connection:
        rows = connection.execute("SELECT * FROM creative_performance ORDER BY campaign_id DESC, variant").fetchall()
        return [dict(row) for row in rows]


if __name__ == "__main__":
    init_db()
    print(f"Banco inicializado em: {DB_PATH}")
