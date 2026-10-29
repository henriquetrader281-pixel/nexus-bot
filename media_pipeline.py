"""Pipeline único de mídia do Nexus.

A entrada é sempre a campanha partilhada. O pipeline tenta usar os dados
públicos do anúncio; quando a consulta falha, pode continuar com uma imagem
local enviada pelo usuário. Não publica nem cria um link de afiliado novo.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from generate_creatives import ProductData, download_image, fetch_product_data, make_image_a, make_video_b


OUTPUT_ROOT = Path(".nexus_media")


def _safe_slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9À-ÿ]+", "_", value or "campanha").strip("_")
    return value[:60] or "campanha"


def _marketplace_from_url(url: str | None) -> str:
    host = urlparse(url or "").netloc.lower()
    if "shopee" in host:
        return "Shopee"
    if "amazon" in host:
        return "Amazon"
    return "Mercado Livre"


def _build_product(campaign: dict[str, Any]) -> ProductData:
    official_url = str(campaign.get("official_affiliate_url") or "").strip()
    source_url = str(campaign.get("product_source_url") or official_url).strip()
    product_name = str(campaign.get("product_name") or "Produto selecionado").strip()
    image_url = campaign.get("image_url")
    marketplace = campaign.get("marketplace") or _marketplace_from_url(source_url)

    # A imagem enviada manualmente deve permitir seguir mesmo se o anúncio
    # estiver bloqueado, fora do ar ou sem metadados públicos.
    manual_image = campaign.get("source_image_path") or campaign.get("image_path")
    manual_image_exists = bool(manual_image and Path(str(manual_image)).is_file())

    if source_url.startswith(("http://", "https://")):
        try:
            product = fetch_product_data(source_url)
            product.official_affiliate_url = official_url or ""
            # Quando a seleção veio da API de pesquisa, a thumbnail pertence ao
            # mesmo resultado e deve prevalecer sobre OG images genéricas do anúncio.
            product.title = product_name or product.title
            product.marketplace = marketplace
            if image_url:
                product.image_url = image_url
            return product
        except Exception:
            if not image_url and not manual_image_exists:
                raise
            # Se já existe uma imagem local ou uma URL pública fornecida pelo
            # usuário, não deixar uma falha de scraping bloquear a campanha.

    return ProductData(
        official_affiliate_url=official_url or "",
        resolved_url=source_url,
        title=product_name,
        image_url=image_url,
        price=campaign.get("price"),
        marketplace=marketplace,
    )


def generate_campaign_media(campaign: dict[str, Any], *, output_root: str | Path = OUTPUT_ROOT) -> dict[str, Any]:
    """Gera os dois formatos e retorna caminhos locais mais o manifesto."""
    if not campaign.get("product_name"):
        raise ValueError("Nenhum produto selecionado para gerar mídia.")
    source_candidate = campaign.get("source_image_path") or campaign.get("image_path")
    source_candidate_path = Path(str(source_candidate)) if source_candidate else None
    if source_candidate_path and source_candidate_path.name == "creative_image_a.jpg" and not campaign.get("source_image_path"):
        source_candidate_path = None
    has_local_image = bool(source_candidate_path and source_candidate_path.is_file())
    if not campaign.get("image_url") and not has_local_image and not campaign.get("official_affiliate_url") and not campaign.get("product_source_url"):
        raise ValueError("Informe o produto e envie uma imagem real ou forneça uma URL pública de imagem. A API do marketplace é opcional.")

    product = _build_product(campaign)
    if not product.image_url and not has_local_image:
        raise RuntimeError("Não foi encontrada imagem pública para este produto. Cole uma URL pública JPG/PNG/WebP ou envie a imagem real no campo de upload; não é necessário usar a API do marketplace.")

    output_dir = Path(output_root) / _safe_slug(product.title)
    output_dir.mkdir(parents=True, exist_ok=True)
    if has_local_image:
        source = source_candidate_path
    else:
        source = download_image(product, output_dir)
    audio_path = campaign.get("audio_path")
    audio = Path(audio_path) if audio_path and Path(audio_path).exists() else None
    caption_lines = campaign.get("hooks") or campaign.get("keywords") or []
    fingerprint_payload = {
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "product": product.title,
        "caption_lines": caption_lines,
        "audio": str(audio) if audio else None,
    }
    fingerprint = hashlib.sha256(json.dumps(fingerprint_payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    manifest_path = output_dir / "campaign_manifest.json"
    if manifest_path.is_file():
        try:
            cached = json.loads(manifest_path.read_text(encoding="utf-8"))
            if cached.get("fingerprint") == fingerprint and all(Path(cached.get(key, "")).is_file() for key in ("image_a", "video_b")):
                return cached
        except (OSError, TypeError, ValueError):
            pass

    image_path = make_image_a(product, source, output_dir)
    video_path = make_video_b(product, source, output_dir, audio, caption_lines=caption_lines)
    source_digest = fingerprint_payload["source_sha256"]

    manifest = {
        "fingerprint": fingerprint,
        "copy": campaign.get("copy_final") or campaign.get("copy") or "",
        "keywords": campaign.get("keywords") or [],
        "hooks": campaign.get("hooks") or [],
        "caption": campaign.get("caption") or "",
        "audio_status": "ready" if audio else "not_available",
        "source_image_path": str(source),
        "product": {
            "name": product.title,
            "marketplace": product.marketplace,
            "official_affiliate_url": product.official_affiliate_url,
            "image_url": product.image_url,
            "source_image_url": campaign.get("source_image_url") or campaign.get("image_url") or product.image_url,
            "image_verified": campaign.get("image_verified"),
            "image_source": campaign.get("image_source") or ("upload manual do usuário" if has_local_image else None),
            "product_source_url": campaign.get("product_source_url") or campaign.get("official_affiliate_url"),
        },
        "source_image_sha256": source_digest,
        "caption_lines": caption_lines,
        "image_a": str(image_path),
        "video_b": str(video_path),
        "audio": str(audio) if audio else None,
        "publication": "not_executed",
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest


__all__ = ["generate_campaign_media"]
