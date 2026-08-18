#!/usr/bin/env python3
"""Gera criativos locais a partir de um link oficial de afiliado do Mercado Livre.

O script resolve o link para extrair metadados públicos, baixa a imagem Open Graph
quando disponível, cria uma Imagem A (1000x1500) e um Vídeo B curto (1080x1920).
Ele NÃO publica nem altera o link oficial.

Exemplo:
  python generate_creatives.py \
    --url https://meli.la/11v5uxd \
    --output-dir generated_creatives
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont, ImageOps

try:
    from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
except ImportError:
    from moviepy import AudioFileClip, ImageClip, concatenate_videoclips


USER_AGENT = "NexusBot-CreativeGenerator/1.0"
TIMEOUT = 20


@dataclass
class ProductData:
    official_affiliate_url: str
    resolved_url: str
    title: str
    image_url: Optional[str] = None
    price: Optional[str] = None
    marketplace: str = "Mercado Livre"


def require_http_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("O link precisa ser uma URL HTTP(S) completa.")
    return value


def fetch_product_data(official_url: str) -> ProductData:
    official_url = require_http_url(official_url)
    response = requests.get(
        official_url,
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT,
        allow_redirects=True,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    def meta(*keys: str) -> Optional[str]:
        for key in keys:
            tag = soup.find("meta", attrs={"property": key}) or soup.find("meta", attrs={"name": key})
            if tag and tag.get("content"):
                return str(tag["content"]).strip()
        return None

    title = meta("og:title", "twitter:title") or (soup.title.get_text(" ", strip=True) if soup.title else "Produto Mercado Livre")
    image_url = meta("og:image", "twitter:image")

    def normalise_image(value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        candidate = urljoin(response.url, str(value).strip())
        if not candidate.startswith(("http://", "https://")):
            return None
        if candidate.lower().endswith(".svg"):
            return None
        return candidate

    image_url = normalise_image(image_url)
    if not image_url:
        image_link = soup.find("link", attrs={"rel": lambda rel: rel and "image_src" in rel})
        image_url = normalise_image(image_link.get("href") if image_link else None)

    if not image_url:
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            try:
                data = json.loads(script.get_text(strip=True))
            except (TypeError, ValueError, json.JSONDecodeError):
                continue
            candidates = data if isinstance(data, list) else [data]
            for item in candidates:
                if isinstance(item, dict):
                    value = item.get("image")
                    if isinstance(value, list):
                        value = value[0] if value else None
                    if isinstance(value, dict):
                        value = value.get("url")
                    image_url = normalise_image(value)
                    if image_url:
                        break
            if image_url:
                break

    if not image_url:
        for image_tag in soup.find_all("img"):
            value = image_tag.get("src") or image_tag.get("data-src") or image_tag.get("data-lazy-src")
            candidate = normalise_image(value)
            if candidate and not any(term in candidate.lower() for term in ("logo", "icon", "avatar")):
                image_url = candidate
                break

    price = meta("product:price:amount", "og:price:amount")
    return ProductData(
        official_affiliate_url=official_url,
        resolved_url=response.url,
        title=title[:180],
        image_url=image_url,
        price=price,
    )


def safe_name(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9À-ÿ]+", "_", value).strip("_")
    return value[:80] or "produto_mercado_livre"


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = []
    if bold:
        candidates.append(Path(__file__).parent / "assets/fonts/Montserrat-ExtraBold.ttf")
    candidates.extend([
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
    ])
    for candidate in candidates:
        if candidate.exists():
            try:
                return ImageFont.truetype(str(candidate), size)
            except OSError:
                continue
    return ImageFont.load_default()


def wrap_text_by_width(draw: ImageDraw.ImageDraw, text: str, font, max_width: int, max_lines: int = 2) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and draw.textbbox((0, 0), candidate, font=font)[2] > max_width:
            lines.append(current)
            current = word
            if len(lines) >= max_lines:
                break
        else:
            current = candidate
    if len(lines) < max_lines and current:
        lines.append(current)
    return lines[:max_lines]


def download_image(product: ProductData, output_dir: Path) -> Path:
    if not product.image_url:
        raise RuntimeError("A página não forneceu uma imagem Open Graph pública.")
    response = requests.get(product.image_url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
    response.raise_for_status()
    source = output_dir / "source_product_image.jpg"
    source.write_bytes(response.content)
    with Image.open(source) as image:
        image.convert("RGB").save(source, format="JPEG", quality=94)
    return source


def fit_product(source: Path, size: tuple[int, int]) -> Image.Image:
    with Image.open(source) as image:
        return ImageOps.fit(image.convert("RGB"), size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.42))


def draw_gradient(image: Image.Image, start_y: int) -> None:
    pixels = image.load()
    width, height = image.size
    for y in range(max(0, start_y), height):
        alpha = int(210 * ((y - start_y) / max(1, height - start_y)))
        for x in range(width):
            r, g, b = pixels[x, y]
            pixels[x, y] = (int(r * (1 - alpha / 255)), int(g * (1 - alpha / 255)), int(b * (1 - alpha / 255)))


def make_image_a(product: ProductData, source: Path, output_dir: Path) -> Path:
    canvas = fit_product(source, (1000, 1500))
    draw_gradient(canvas, 880)
    draw = ImageDraw.Draw(canvas)
    title_font = load_font(54, bold=True)
    body_font = load_font(34)
    cta_font = load_font(32, bold=True)
    title = product.title.replace(" - Mercado Livre", "")
    title = " ".join(title.split()[:5])
    lines = wrap_text_by_width(draw, title, title_font, 890, max_lines=2)
    y = 930
    for line in lines:
        draw.text((54, y), line, font=title_font, fill="white", stroke_width=1, stroke_fill="#111827")
        y += 66
    benefit = "Praticidade para o dia a dia"
    draw.text((54, y + 12), benefit, font=body_font, fill="#dbeafe")
    cta_box = (54, 1350, 470, 1430)
    draw.rounded_rectangle(cta_box, radius=18, fill="#67e8f9")
    draw.text((82, 1373), "VER OFERTA OFICIAL", font=cta_font, fill="#07111e")
    output = output_dir / "creative_image_a.jpg"
    canvas.save(output, quality=94, optimize=True)
    return output


def _with_duration(clip, duration: float):
    method = getattr(clip, "with_duration", None) or getattr(clip, "set_duration")
    return method(duration)


def _with_audio(clip, audio):
    method = getattr(clip, "with_audio", None) or getattr(clip, "set_audio")
    return method(audio)


def _subclip(audio, end: float):
    method = getattr(audio, "subclipped", None) or getattr(audio, "subclip")
    return method(0, end)


def make_video_b(product: ProductData, source: Path, output_dir: Path, audio_path: Optional[Path] = None, caption_lines: Optional[list[str]] = None) -> Path:
    size = (1080, 1920)
    product_name = " ".join(product.title.replace(" - Mercado Livre", "").split()[:6]) or "Produto selecionado"
    marketplace = product.marketplace or "Mercado Livre"
    price_line = f"Preço encontrado: {product.price}." if product.price else f"Veja preço e disponibilidade no {marketplace}."
    captions = [str(item).strip() for item in (caption_lines or []) if str(item).strip()]
    hook_caption = captions[0] if captions else "Você ainda sofre com isso?"
    benefit_caption = captions[1] if len(captions) > 1 else f"Conheça uma solução prática: {product_name}."
    cta_caption = captions[2] if len(captions) > 2 else price_line
    scenes = [
        (hook_caption, f"Pare o scroll: {product_name}."),
        (product_name, benefit_caption),
        ("Confira a oferta oficial", cta_caption),
    ]
    frame_paths = []
    for index, (headline, subline) in enumerate(scenes, start=1):
        frame = fit_product(source, size)
        draw_gradient(frame, 980)
        draw = ImageDraw.Draw(frame)
        headline_font = load_font(74, bold=True)
        subline_font = load_font(40)
        y = 1110
        for line in wrap_text_by_width(draw, headline, headline_font, 950, max_lines=2):
            draw.text((60, y), line, font=headline_font, fill="white", stroke_width=2, stroke_fill="#0b1020")
            y += 88
        sub_y = y + 18
        for sub_line in wrap_text_by_width(draw, subline, subline_font, 950, max_lines=2):
            draw.text((60, sub_y), sub_line, font=subline_font, fill="#dbeafe", stroke_width=1, stroke_fill="#0b1020")
            sub_y += 52
        if index == 3:
            draw.rounded_rectangle((60, 1660, 570, 1750), radius=20, fill="#72f1a8")
            draw.text((94, 1687), "VER OFERTA OFICIAL", font=load_font(34, bold=True), fill="#06130b")
        frame_path = output_dir / f"video_frame_{index}.jpg"
        frame.save(frame_path, quality=92)
        frame_paths.append(frame_path)

    clips = [_with_duration(ImageClip(str(path)), 3.3) for path in frame_paths]
    video = concatenate_videoclips(clips, method="compose")
    output = output_dir / "creative_video_b.mp4"
    if audio_path and audio_path.exists():
        audio = AudioFileClip(str(audio_path))
        video = _with_audio(video, _subclip(audio, min(audio.duration, video.duration)))
    video.write_videofile(str(output), fps=24, codec="libx264", audio_codec="aac", logger=None)
    video.close()
    for clip in clips:
        clip.close()
    return output


def generate_creatives(official_url: str, output_dir: str, audio_path: str | None = None) -> dict:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    product = fetch_product_data(official_url)
    source = download_image(product, output)
    image = make_image_a(product, source, output)
    video = make_video_b(product, source, output, Path(audio_path) if audio_path else None)
    manifest = {
        "product": asdict(product),
        "image_a": str(image),
        "video_b": str(video),
        "publication": "not_executed",
        "note": "O link oficial foi preservado e nenhum canal social foi acionado.",
    }
    (output / "creative_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="link oficial do afiliado, por exemplo https://meli.la/...")
    parser.add_argument("--output-dir", default="generated_creatives", help="diretório de saída")
    parser.add_argument("--audio", help="arquivo MP3/WAV opcional para narração")
    args = parser.parse_args()
    manifest = generate_creatives(args.url, args.output_dir, args.audio)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
