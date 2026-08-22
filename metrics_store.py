from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR / "metrics_schema.sql"


def _resolve_db_path() -> Path:
    configured = os.getenv("NEXUS_METRICS_DB")
    if configured:
        return Path(configured)
    for directory in (BASE_DIR / ".nexus_media", Path("/tmp")):
        try:
            directory.mkdir(parents=True, exist_ok=True)
            probe = directory / ".nexus_write_probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            return directory / "nexus_metrics.sqlite3"
        except OSError:
            continue
    return Path("/tmp/nexus_metrics.sqlite3")


DB_PATH = _resolve_db_path()


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


def register_video_project(project: dict[str, Any]) -> None:
    """Sincroniza o manifesto de projeto com o banco de métricas."""
    init_db()
    with connect() as connection:
        connection.execute(
            """INSERT INTO video_projects (project_id, title, product_name, niche, platform, project_version)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_id) DO UPDATE SET
                title=excluded.title,
                product_name=excluded.product_name,
                niche=excluded.niche,
                platform=excluded.platform,
                project_version=excluded.project_version,
                updated_at=datetime('now')""",
            (
                str(project.get("project_id") or ""),
                str(project.get("title") or "Projeto"),
                str(project.get("product_name") or "Tema"),
                project.get("niche"),
                str(project.get("platform") or "TikTok").lower().replace(" youtube shorts", "").replace(" instagram reels", ""),
                int(project.get("version") or 1),
            ),
        )


def record_video_publication(project_id: str, platform: str, *, external_post_id: str | None = None, external_url: str | None = None, status: str = "draft") -> int:
    platform = platform.lower().replace(" youtube shorts", "").replace(" instagram reels", "")
    if platform not in {"tiktok", "youtube", "instagram"}:
        raise ValueError("platform inválida")
    if status not in {"draft", "published", "failed", "removed"}:
        raise ValueError("status inválido")
    init_db()
    with connect() as connection:
        cursor = connection.execute(
            """INSERT INTO video_publications (project_id, platform, external_post_id, external_url, status, published_at, last_checked_at)
            VALUES (?, ?, ?, ?, ?, CASE WHEN ? = 'published' THEN datetime('now') ELSE NULL END, datetime('now'))
            ON CONFLICT(project_id, platform) DO UPDATE SET
                external_post_id=excluded.external_post_id,
                external_url=excluded.external_url,
                status=excluded.status,
                published_at=excluded.published_at,
                last_checked_at=excluded.last_checked_at""",
            (project_id, platform, external_post_id, external_url, status, status),
        )
        if cursor.lastrowid:
            return int(cursor.lastrowid)
        row = connection.execute("SELECT id FROM video_publications WHERE project_id = ? AND platform = ?", (project_id, platform)).fetchone()
        return int(row[0])


def record_video_metrics(publication_id: int, *, views: int = 0, impressions: int = 0, avg_watch_time_seconds: float = 0.0, completed_views: int = 0, likes: int = 0, comments: int = 0, shares: int = 0, clicks: int = 0, follower_delta: int = 0) -> int:
    integer_values = {"views": views, "impressions": impressions, "completed_views": completed_views, "likes": likes, "comments": comments, "shares": shares, "clicks": clicks, "follower_delta": follower_delta}
    if any(not isinstance(value, int) or (key != "follower_delta" and value < 0) for key, value in integer_values.items()):
        raise ValueError("métricas de vídeo precisam ser inteiros válidos")
    if avg_watch_time_seconds < 0:
        raise ValueError("avg_watch_time_seconds não pode ser negativo")
    init_db()
    with connect() as connection:
        cursor = connection.execute(
            """INSERT INTO video_metrics (publication_id, views, impressions, avg_watch_time_seconds, completed_views, likes, comments, shares, clicks, follower_delta)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (publication_id, views, impressions, float(avg_watch_time_seconds), completed_views, likes, comments, shares, clicks, follower_delta),
        )
        return int(cursor.lastrowid)


def list_video_publications(project_id: str | None = None) -> list[dict[str, Any]]:
    init_db()
    query = "SELECT id, project_id, platform, external_post_id, external_url, status, published_at, last_checked_at FROM video_publications"
    params: tuple[Any, ...] = ()
    if project_id:
        query += " WHERE project_id = ?"
        params = (project_id,)
    query += " ORDER BY id DESC"
    with connect() as connection:
        return [dict(row) for row in connection.execute(query, params).fetchall()]


def video_performance_rows(project_id: str | None = None) -> list[dict[str, Any]]:
    init_db()
    query = """SELECT vp.project_id, vp.platform, vp.status, COALESCE(SUM(vm.views), 0) AS views,
        COALESCE(SUM(vm.impressions), 0) AS impressions,
        COALESCE(SUM(vm.likes), 0) AS likes, COALESCE(SUM(vm.comments), 0) AS comments,
        COALESCE(SUM(vm.shares), 0) AS shares, COALESCE(SUM(vm.clicks), 0) AS clicks,
        COALESCE(SUM(vm.completed_views), 0) AS completed_views,
        COALESCE(SUM(vm.follower_delta), 0) AS follower_delta,
        CASE WHEN COALESCE(SUM(vm.impressions), 0) > 0 THEN CAST(SUM(vm.clicks) AS REAL) / SUM(vm.impressions) ELSE 0 END AS ctr,
        CASE WHEN COALESCE(SUM(vm.views), 0) > 0 THEN CAST(SUM(vm.completed_views) AS REAL) / SUM(vm.views) ELSE 0 END AS completion_rate,
        CASE WHEN COALESCE(SUM(vm.views), 0) > 0 THEN CAST(SUM(vm.likes + vm.comments + vm.shares) AS REAL) / SUM(vm.views) ELSE 0 END AS engagement_rate
        FROM video_publications vp LEFT JOIN video_metrics vm ON vm.publication_id = vp.id"""
    params: tuple[Any, ...] = ()
    if project_id:
        query += " WHERE vp.project_id = ?"
        params = (project_id,)
    query += " GROUP BY vp.project_id, vp.platform, vp.status ORDER BY vp.project_id, vp.platform"
    with connect() as connection:
        return [dict(row) for row in connection.execute(query, params).fetchall()]


if __name__ == "__main__":
    init_db()
    print(f"Banco inicializado em: {DB_PATH}")
