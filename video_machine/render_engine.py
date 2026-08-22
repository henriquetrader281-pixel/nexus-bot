"""Renderização local da Máquina de Vídeos.

O renderizador é determinístico e editável: cada cena vira um frame composto
com Pillow e depois os frames são unidos com MoviePy. Ele não publica nada.
"""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

from .project_store import Scene, VideoProject, save_project


DEFAULT_SIZE = (1080, 1920)


def _font(size: int, bold: bool = False):
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
    ]
    for path in candidates:
        if path.is_file():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                pass
    return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int, max_lines: int = 4) -> list[str]:
    words = str(text or "").split()
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
    if current and len(lines) < max_lines:
        lines.append(current)
    return lines[:max_lines]


def _source_image(project: VideoProject, scene: Scene) -> Image.Image | None:
    candidate = scene.media_path or project.source_image_path
    if candidate and Path(candidate).is_file():
        try:
            with Image.open(candidate) as image:
                return image.convert("RGB").copy()
        except (OSError, ValueError):
            return None
    return None


def _background(size: tuple[int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, "#0B1220")
    pixels = image.load()
    for y in range(height):
        ratio = y / max(1, height - 1)
        color = (11, int(18 + ratio * 22), int(32 + ratio * 42))
        for x in range(width):
            pixels[x, y] = color
    return image


def compose_scene(project: VideoProject, scene: Scene, *, size: tuple[int, int] = DEFAULT_SIZE) -> Image.Image:
    canvas = _background(size)
    source = _source_image(project, scene)
    visual_height = int(size[1] * 0.51)
    if source is not None:
        product = ImageOps.contain(source, (size[0] - 120, visual_height), method=Image.Resampling.LANCZOS)
        x = (size[0] - product.width) // 2
        y = int(size[1] * 0.10) + (visual_height - product.height) // 2
        canvas.paste(product, (x, y))
    else:
        draw = ImageDraw.Draw(canvas)
        placeholder_top = int(size[1] * 0.16)
        placeholder_bottom = int(size[1] * 0.56)
        draw.rounded_rectangle((100, placeholder_top, size[0] - 100, placeholder_bottom), radius=42, fill="#172554", outline="#22D3EE", width=4)
        placeholder = _font(46, bold=True)
        lines = _wrap(draw, project.product_name, placeholder, size[0] - 300, 3)
        y = int((placeholder_top + placeholder_bottom) / 2) - (len(lines) * 34)
        for line in lines:
            width = draw.textbbox((0, 0), line, font=placeholder)[2]
            draw.text(((size[0] - width) / 2, y), line, font=placeholder, fill="#E0F2FE")
            y += 72

    draw = ImageDraw.Draw(canvas)
    panel_top = int(size[1] * 0.56)
    panel_bottom = size[1] - int(size[1] * 0.04)
    draw.rounded_rectangle((44, panel_top, size[0] - 44, panel_bottom), radius=36, fill="#07111E")
    label_font = _font(28, bold=True)
    headline_font = _font(66, bold=True)
    caption_font = _font(36)
    draw.text((86, panel_top + 42), str(scene.label or "CENA").upper(), font=label_font, fill="#67E8F9")
    headline_lines = _wrap(draw, scene.text or project.product_name, headline_font, size[0] - 180, 3)
    y = panel_top + 108
    for line in headline_lines:
        draw.text((86, y), line, font=headline_font, fill="white", stroke_width=1, stroke_fill="#07111E")
        y += 80
    caption = scene.caption or scene.text or ""
    caption_lines = _wrap(draw, caption, caption_font, size[0] - 180, 3)
    y += 24
    for line in caption_lines:
        draw.text((86, y), line, font=caption_font, fill="#D7E9F4")
        y += 50
    cta = "VER DETALHES"
    cta_font = _font(28, bold=True)
    cta_width = draw.textbbox((0, 0), cta, font=cta_font)[2] + 72
    cta_y = panel_bottom - 102
    draw.rounded_rectangle((86, cta_y, 86 + cta_width, cta_y + 62), radius=16, fill="#A7F3D0")
    draw.text((122, cta_y + 17), cta, font=cta_font, fill="#06130B")
    return canvas


def _timestamp(seconds: float) -> str:
    total = max(0, int(round(seconds)))
    hours, rest = divmod(total, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.000"


def write_vtt(project: VideoProject, path: Path) -> Path:
    cursor = 0.0
    lines = ["WEBVTT", ""]
    index = 1
    for scene in project.scenes:
        if not scene.enabled:
            continue
        end = cursor + max(0.5, float(scene.duration_seconds))
        caption = html.escape(scene.caption or scene.text or "").replace("\n", " ")
        if caption:
            lines.extend([str(index), f"{_timestamp(cursor)} --> {_timestamp(end)}", caption, ""])
            index += 1
        cursor = end
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _render_movie(frames: list[tuple[Path, float]], output_path: Path, audio_path: str | None, fps: int) -> None:
    try:
        from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
    except ImportError:
        try:
            from moviepy import AudioFileClip, ImageClip, concatenate_videoclips
        except ImportError as exc:  # pragma: no cover - depends on environment
            raise RuntimeError("MoviePy não está instalado. Instale as dependências do requirements.txt.") from exc

    clips = []
    audio = None
    video = None
    try:
        for path, duration in frames:
            clip = ImageClip(str(path))
            setter = getattr(clip, "with_duration", None) or getattr(clip, "set_duration")
            clips.append(setter(duration))
        video = concatenate_videoclips(clips, method="compose")
        if audio_path and Path(audio_path).is_file():
            audio = AudioFileClip(str(audio_path))
            end = min(float(audio.duration), float(video.duration))
            subclip_method = getattr(audio, "subclipped", None) or getattr(audio, "subclip")
            audio_cut = subclip_method(0, end)
            audio_setter = getattr(video, "with_audio", None) or getattr(video, "set_audio")
            video = audio_setter(audio_cut)
        video.write_videofile(str(output_path), fps=fps, codec="libx264", audio_codec="aac", logger=None)
    finally:
        if video is not None:
            video.close()
        if audio is not None:
            audio.close()
        for clip in clips:
            clip.close()


def render_project(project: VideoProject, *, output_dir: str | Path | None = None) -> dict[str, Any]:
    enabled = [scene for scene in project.scenes if scene.enabled]
    if not enabled:
        raise ValueError("Adicione ao menos uma cena habilitada antes de renderizar.")
    output = Path(output_dir or (Path(".nexus_media") / "video_projects" / re.sub(r"[^a-zA-Z0-9_-]+", "_", project.project_id)))
    output.mkdir(parents=True, exist_ok=True)
    total = sum(max(0.5, float(scene.duration_seconds)) for scene in enabled)
    if total > project.duration_limit_seconds:
        scale = project.duration_limit_seconds / total
        for scene in enabled:
            scene.duration_seconds = max(0.5, round(scene.duration_seconds * scale, 2))
        total = sum(scene.duration_seconds for scene in enabled)
        project.touch()

    frames: list[tuple[Path, float]] = []
    for index, scene in enumerate(enabled, start=1):
        frame_path = output / f"scene_{index:03d}.jpg"
        compose_scene(project, scene).save(frame_path, quality=94, optimize=True)
        frames.append((frame_path, float(scene.duration_seconds)))
    thumbnail_path = output / "thumbnail.jpg"
    compose_scene(project, enabled[0], size=(1080, 1350)).save(thumbnail_path, quality=94, optimize=True)
    subtitle_path = write_vtt(project, output / "subtitles.vtt")
    video_path = output / "render.mp4"
    _render_movie(frames, video_path, project.audio_path, project.fps)
    project.render_path = str(video_path)
    project.thumbnail_path = str(thumbnail_path)
    project.subtitle_path = str(subtitle_path)
    project.status = "rendered"
    save_project(project)
    return {
        "project_id": project.project_id,
        "render_path": str(video_path),
        "thumbnail_path": str(thumbnail_path),
        "subtitle_path": str(subtitle_path),
        "total_duration_seconds": round(total, 2),
        "scene_count": len(enabled),
        "format": f"{project.width}x{project.height}@{project.fps}",
        "publication": "not_executed",
    }


__all__ = ["compose_scene", "render_project", "write_vtt"]
