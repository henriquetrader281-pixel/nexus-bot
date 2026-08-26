from pathlib import Path

from PIL import Image

import media_pipeline


def test_media_pipeline_reuses_matching_manifest(tmp_path, monkeypatch):
    source = tmp_path / "produto.png"
    Image.new("RGB", (120, 120), "#22c55e").save(source)
    calls = {"image": 0, "video": 0}

    def make_image(*args):
        calls["image"] += 1
        output = args[2] / "image_a.jpg"
        output.write_bytes(b"image")
        return output

    def make_video(*args, **kwargs):
        calls["video"] += 1
        output = args[2] / "video_b.mp4"
        output.write_bytes(b"video")
        return output

    monkeypatch.setattr(media_pipeline, "make_image_a", make_image)
    monkeypatch.setattr(media_pipeline, "make_video_b", make_video)
    campaign = {"product_name": "Produto de teste", "image_path": str(source), "hooks": ["Gancho"]}

    first = media_pipeline.generate_campaign_media(campaign, output_root=tmp_path / "out")
    second = media_pipeline.generate_campaign_media(campaign, output_root=tmp_path / "out")

    assert first["fingerprint"] == second["fingerprint"]
    assert calls == {"image": 1, "video": 1}
    assert second["audio_status"] == "not_available"
