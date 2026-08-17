"""Compatibilidade do gerador legado com o pipeline único de mídia."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable

from generate_creatives import ProductData, make_video_b


def _first_local_image(image_urls: Iterable[str]) -> Path | None:
    for value in image_urls:
        path = Path(str(value))
        if path.is_file():
            return path
    return None


def criar_reels_elite(image_urls, audio_path=None, output_path="reels_final.mp4"):
    """Gera um Vídeo B vertical a partir da primeira imagem local válida."""
    source = _first_local_image(image_urls)
    if source is None:
        print("Erro no Estúdio de Elite: nenhuma imagem local válida foi fornecida.")
        return None
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    product = ProductData(
        official_affiliate_url="",
        resolved_url="",
        title="Produto selecionado",
        image_url=None,
        marketplace="Mercado Livre",
    )
    generated = make_video_b(product, source, output.parent, Path(audio_path) if audio_path else None)
    if generated.resolve() != output.resolve():
        shutil.copy2(generated, output)
    return str(output)


def criar_reels_afiliado(image_path, copy_reels=None, output_path="reels_final.mp4"):
    """Alias mantido para o teste legado e integrações antigas."""
    return criar_reels_elite([image_path], output_path=output_path)


def obter_musica_tendencia(estilo="viral"):
    """Retorna um caminho configurável; não inventa uma música que não exista."""
    candidates = {
        "viral": "viral.mp3",
        "agressivo": "agressivo.mp3",
        "estético": "estetico.mp3",
    }
    path = Path(candidates.get(estilo, "default.mp3"))
    return str(path) if path.exists() else None


__all__ = ["criar_reels_elite", "criar_reels_afiliado", "obter_musica_tendencia"]
