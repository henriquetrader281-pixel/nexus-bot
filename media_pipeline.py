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
    source_url = str(campaign.get("product_source_url") or official_url).strip()
    product_name = str(campaign.get("product_name") or "Produto selecionado").strip()
    image_url = campaign.get("image_url")
    marketplace = campaign.get("marketplace") or _marketplace_from_url(source_url)

    if source_url.startswith(("http://", "https://")):
        try:
            product = fetch_product_data(source_url)
            product.official_affiliate_url = official_url or source_url
            # A seleção do usuário é a fonte de verdade do texto; a página oficial
            # é a fonte de verdade da imagem e dos metadados disponíveis.
            product.title = product_name or product.title
            product.marketplace = marketplace
            if image_url and not product.image_url:
                product.image_url = image_url
            return product
        except Exception:
            manual_image = campaign.get("image_path")
            if not image_url and not (manual_image and Path(str(manual_image)).is_file()):
                raise

    return ProductData(
        official_affiliate_url=official_url or source_url or "https://example.invalid/sem-link",
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
    if not campaign.get("image_url") and not (source_candidate_path and source_candidate_path.is_file()) and not campaign.get("official_affiliate_url") and not campaign.get("product_source_url"):
        raise ValueError("A campanha precisa de um link oficial, de um produto encontrado ou de uma imagem pública.")

    product = _build_product(campaign)
    if not product.image_url and not (source_candidate_path and source_candidate_path.is_file()):
        raise RuntimeError("O link não forneceu uma imagem pública do produto. Cole uma URL JPG/PNG pública ou suba uma imagem no Modo Simples.")

    output_dir = Path(output_root) / _safe_slug(product.title)
    output_dir.mkdir(parents=True, exist_ok=True)
    if source_candidate_path and source_candidate_path.is_file():
        source = source_candidate_path
    else:
        source = download_image(product, output_dir)
    audio_path = campaign.get("audio_path")
    audio = Path(audio_path) if audio_path and Path(audio_path).exists() else None
    image_path = make_image_a(product, source, output_dir)
    caption_lines = campaign.get("hooks") or campaign.get("keywords") or []
    video_path = make_video_b(product, source, output_dir, audio, caption_lines=caption_lines)

    manifest = {
        "source_image_path": str(source),
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
