import tempfile
from pathlib import Path

from PIL import Image

import media_pipeline
from generate_creatives import ProductData


media_pipeline.fetch_product_data = lambda url: ProductData(
    official_affiliate_url=url,
    resolved_url=url,
    title="Produto sem OG image",
    image_url=None,
)
product = media_pipeline._build_product({
    "product_name": "Produto sem OG image",
    "official_affiliate_url": "https://meli.la/teste",
    "image_url": "https://cdn.example.test/produto.jpg",
})
assert product.image_url == "https://cdn.example.test/produto.jpg"

with tempfile.TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)
    manual = root / "manual.png"
    Image.new("RGB", (120, 120), "#22c55e").save(manual)
    output = root / "output"
    media_pipeline.make_image_a = lambda product, source, folder: folder / "image_a.jpg"
    media_pipeline.make_video_b = lambda product, source, folder, audio, caption_lines=None: folder / "video_b.mp4"
    result = media_pipeline.generate_campaign_media({
        "product_name": "Produto manual",
        "image_path": str(manual),
    }, output_root=output)
    assert result["image_a"].endswith("image_a.jpg")
    assert result["video_b"].endswith("video_b.mp4")

print("MEDIA_FALLBACK_TEST_OK")
