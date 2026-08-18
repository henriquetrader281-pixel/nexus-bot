"""Pipeline único de mídia do Nexus.

A entrada é sempre a campanha partilhada. O módulo baixa a imagem pública
associada ao link oficial, cria a Imagem A e o Vídeo B e devolve os caminhos
para as restantes abas. Não publica nem cria um link de afiliado novo.
"""

from __future__ import annotations

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
    product_name = str(campaign.get("product_name") or "Produto selecionado").strip()
    image_url = campaign.get("image_url")
    marketplace = campaign.get("marketplace") or _marketplace_from_url(official_url)

    if official_url.startswith(("http://", "https://")):
        try:
            product = fetch_product_data(official_url)
            # A seleção do usuário é a fonte de verdade do texto; a página oficial
            # é a fonte de verdade da imagem e dos metadados disponíveis.
            product.title = product_name or product.title
            product.marketplace = marketplace
            if image_url and not product.image_url:
                product.image_url = image_url
            return product
        except Exception:
            if not image_url:
                raise

    return ProductData(
        official_affiliate_url=official_url or "https://example.invalid/sem-link",
        resolved_url=official_url,
        title=product_name,
        image_url=image_url,
        price=campaign.get("price"),
        marketplace=marketplace,
    )


def generate_campaign_media(campaign: dict[str, Any], *, output_root: str | Path = OUTPUT_ROOT) -> dict[str, Any]:
    """Gera os dois formatos e retorna caminhos locais mais o manifesto."""
    if not campaign.get("product_name"):
        raise ValueError("Nenhum produto selecionado para gerar mídia.")
    if not campaign.get("image_url") and not campaign.get("official_affiliate_url"):
        raise ValueError("A campanha precisa de um link oficial ou de uma imagem pública do produto.")

    product = _build_product(campaign)
    if not product.image_url:
        raise RuntimeError("O link não forneceu uma imagem pública do produto. Cole uma URL JPG/PNG pública no campo 'URL pública da imagem do produto' em Afiliados.")

    output_dir = Path(output_root) / _safe_slug(product.title)
    output_dir.mkdir(parents=True, exist_ok=True)
    source = download_image(product, output_dir)
    audio_path = campaign.get("audio_path")
    audio = Path(audio_path) if audio_path and Path(audio_path).exists() else None
    image_path = make_image_a(product, source, output_dir)
    video_path = make_video_b(product, source, output_dir, audio)

    manifest = {
        "product": {
            "name": product.title,
            "marketplace": product.marketplace,
            "official_affiliate_url": product.official_affiliate_url,
            "image_url": product.image_url,
        },
        "image_a": str(image_path),
        "video_b": str(video_path),
        "audio": str(audio) if audio else None,
        "publication": "not_executed",
    }
    (output_dir / "campaign_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest


__all__ = ["generate_campaign_media"]
