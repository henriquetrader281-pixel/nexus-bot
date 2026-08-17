import sys
import types


class SessionState(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__


fake_streamlit = types.ModuleType("streamlit")
fake_streamlit.session_state = SessionState()
sys.modules["streamlit"] = fake_streamlit

import campaign_state

campaign_state.set_campaign(
    product_name="Produto A",
    official_affiliate_url="https://meli.la/produto-a",
    copy="Copy A",
    image_path="a.jpg",
)
campaign_state.set_campaign(product_name="Produto B", pain="Dor B", source="scanner")
current = campaign_state.get_campaign()
assert current["product_name"] == "Produto B"
assert current.get("official_affiliate_url") is None
assert current.get("copy") is None
assert current.get("image_path") is None
assert fake_streamlit.session_state.get("sel_link") is None
assert fake_streamlit.session_state.get("copy_ativa") is None
print("CAMPAIGN_STATE_TEST_OK")
