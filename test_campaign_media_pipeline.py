import shutil
import sys
import tempfile
import types
from pathlib import Path

from PIL import Image


class SessionState(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__


fake_streamlit = types.ModuleType("streamlit")
fake_streamlit.session_state = SessionState()
sys.modules["streamlit"] = fake_streamlit

import campaign_state
import media_pipeline
from generate_creatives import ProductData


def fake_fetch_product_data(url):
    return ProductData(
        official_affiliate_url=url,
        resolved_url=url,
        title="Power Bank 10000mah",
        image_url="https://cdn.example.test/power-bank.jpg",
        marketplace="Mercado Livre",
    )


media_pipeline.fetch_product_data = fake_fetch_product_data
output = Path("/tmp/nexus_campaign_media_test")
shutil.rmtree(output, ignore_errors=True)
with tempfile.TemporaryDirectory() as temp_dir:
    manual = Path(temp_dir) / "power_bank.png"
    Image.new("RGB", (600, 600), "#172554").save(manual)
    campaign = campaign_state.set_campaign(
        product_name="Power Bank 10000mah",
        pain="Ficar sem bateria fora de casa",
        official_affiliate_url="https://meli.la/11v5uxd",
        image_path=str(manual),
        marketplace="Mercado Livre",
        copy="Você ainda fica sem bateria? Veja a oferta oficial.",
        hooks=["Você ainda fica sem bateria?", "Veja uma solução prática.", "Confira a oferta oficial."],
        source="integration_test",
    )
    manifest = media_pipeline.generate_campaign_media(campaign, output_root=output)
    assert Path(manifest["image_a"]).is_file()
    assert Path(manifest["video_b"]).is_file()
    assert manifest["product"]["official_affiliate_url"] == "https://meli.la/11v5uxd"
    campaign_state.set_campaign(
        image_path=manifest["image_a"],
        video_path=manifest["video_b"],
        image_url=manifest["product"].get("image_url"),
        media_manifest=manifest,
    )
    assert fake_streamlit.session_state["image_path_local"] == manifest["image_a"]

    def blocked_fetch(url):
        raise RuntimeError("403 Client Error: Forbidden")

    media_pipeline.fetch_product_data = blocked_fetch
    fallback_campaign = {
        "product_name": "Power Bank manual",
        "official_affiliate_url": "https://meli.la/11v5uxd",
        "image_path": str(manual),
    }
    fallback = media_pipeline._build_product(fallback_campaign)
    assert fallback.image_url is None
print("CAMPAIGN_MEDIA_PIPELINE_TEST_OK")
