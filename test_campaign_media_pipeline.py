import shutil
import sys
import types
from pathlib import Path


class SessionState(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__


fake_streamlit = types.ModuleType("streamlit")
fake_streamlit.session_state = SessionState()
sys.modules["streamlit"] = fake_streamlit

import campaign_state
from media_pipeline import generate_campaign_media

output = Path("/tmp/nexus_campaign_media_test")
shutil.rmtree(output, ignore_errors=True)

campaign = campaign_state.set_campaign(
    product_name="Power Bank 10000mah",
    pain="Ficar sem bateria fora de casa",
    official_affiliate_url="https://meli.la/11v5uxd",
    marketplace="Mercado Livre",
    copy="Você ainda fica sem bateria? Veja a oferta oficial.",
    source="integration_test",
)
manifest = generate_campaign_media(campaign, output_root=output)
assert Path(manifest["image_a"]).is_file()
assert Path(manifest["video_b"]).is_file()
assert manifest["product"]["official_affiliate_url"] == "https://meli.la/11v5uxd"
campaign_state.set_campaign(
    image_path=manifest["image_a"],
    video_path=manifest["video_b"],
    image_url=manifest["product"]["image_url"],
    media_manifest=manifest,
)
assert fake_streamlit.session_state["image_path_local"] == manifest["image_a"]
print("CAMPAIGN_MEDIA_PIPELINE_TEST_OK")
