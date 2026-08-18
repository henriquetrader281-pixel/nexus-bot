"""Fila persistente de campanhas preparadas, sem publicação automática."""

from __future__ import annotations

import json
from typing import Any

import metrics_store


def _json(value: Any, fallback: Any) -> str:
    try:
        return json.dumps(value if value is not None else fallback, ensure_ascii=False, default=str)
    except Exception:
        return json.dumps(fallback, ensure_ascii=False)


def _decode(row: dict[str, Any]) -> dict[str, Any]:
    result = dict(row)
    for field, fallback in (("hooks_json", []), ("keywords_json", []), ("manifest_json", {})):
        raw = result.pop(field, None)
        try:
            result[field.removesuffix("_json")] = json.loads(raw) if raw else fallback
        except (TypeError, ValueError, json.JSONDecodeError):
            result[field.removesuffix("_json")] = fallback
    return result


def save_prepared_campaign(campaign: dict[str, Any], *, status: str = "ready") -> int:
    """Guarda um pacote pronto; não cria link nem chama qualquer rede social."""
    if status not in {"ready", "needs_review", "published", "failed"}:
        raise ValueError("status de campanha inválido")
    metrics_store.init_db()
    fields = (
        campaign.get("product_name") or "Produto sem nome",
        campaign.get("marketplace") or "Mercado Livre",
        str(campaign.get("product_external_id")) if campaign.get("product_external_id") else None,
        campaign.get("product_source_url"),
        campaign.get("official_affiliate_url"),
        campaign.get("image_url"),
        campaign.get("source_image_path"),
        campaign.get("image_path"),
        campaign.get("video_path"),
        campaign.get("audio_path"),
        campaign.get("copy_final") or campaign.get("copy"),
        campaign.get("caption"),
        _json(campaign.get("hooks"), []),
        _json(campaign.get("keywords"), []),
        _json(campaign.get("media_manifest") or campaign.get("manifest"), {}),
        status,
    )
    with metrics_store.connect() as connection:
        cursor = connection.execute(
            """INSERT INTO prepared_campaigns
            (product_name, marketplace, product_external_id, source_product_url,
             official_affiliate_url, image_url, source_image_path, image_path,
             video_path, audio_path, copy_final, caption, hooks_json,
             keywords_json, manifest_json, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
            fields,
        )
        return int(cursor.lastrowid)


def list_prepared_campaigns(*, status: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    metrics_store.init_db()
    query = "SELECT * FROM prepared_campaigns"
    params: list[Any] = []
    if status:
        query += " WHERE status = ?"
        params.append(status)
    query += " ORDER BY created_at DESC, id DESC LIMIT ?"
    params.append(max(1, min(int(limit), 200)))
    with metrics_store.connect() as connection:
        rows = connection.execute(query, params).fetchall()
    return [_decode(dict(row)) for row in rows]


def get_prepared_campaign(campaign_id: int) -> dict[str, Any] | None:
    metrics_store.init_db()
    with metrics_store.connect() as connection:
        row = connection.execute("SELECT * FROM prepared_campaigns WHERE id = ?", (int(campaign_id),)).fetchone()
    return _decode(dict(row)) if row else None


def mark_prepared_campaign(campaign_id: int, status: str) -> bool:
    if status not in {"ready", "needs_review", "published", "failed"}:
        raise ValueError("status de campanha inválido")
    metrics_store.init_db()
    with metrics_store.connect() as connection:
        cursor = connection.execute(
            "UPDATE prepared_campaigns SET status = ?, updated_at = datetime('now') WHERE id = ?",
            (status, int(campaign_id)),
        )
    return cursor.rowcount > 0


def campaign_from_queue_row(row: dict[str, Any]) -> dict[str, Any]:
    """Converte uma linha da fila no contrato usado pelas abas antigas."""
    return {
        "product_name": row.get("product_name"),
        "marketplace": row.get("marketplace"),
        "product_external_id": row.get("product_external_id"),
        "product_source_url": row.get("source_product_url"),
        "official_affiliate_url": row.get("official_affiliate_url"),
        "image_url": row.get("image_url"),
        "source_image_path": row.get("source_image_path"),
        "image_path": row.get("image_path"),
        "video_path": row.get("video_path"),
        "audio_path": row.get("audio_path"),
        "copy_final": row.get("copy_final"),
        "copy": row.get("copy_final"),
        "caption": row.get("caption"),
        "hooks": row.get("hooks") or [],
        "keywords": row.get("keywords") or [],
        "media_manifest": row.get("manifest") or {},
        "queue_id": row.get("id"),
        "queue_status": row.get("status"),
    }


__all__ = [
    "save_prepared_campaign",
    "list_prepared_campaigns",
    "get_prepared_campaign",
    "mark_prepared_campaign",
    "campaign_from_queue_row",
]
