import sys
import types

fake_streamlit = types.ModuleType("streamlit")
fake_streamlit.secrets = {}

class SessionState(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__

fake_streamlit.session_state = SessionState()
sys.modules["streamlit"] = fake_streamlit

import trends


class Response:
    content = b'''<?xml version="1.0"?><rss><channel><item><title>produto em alta</title></item><item><title>organizacao casa</title></item><item><title>produto em alta</title></item></channel></rss>'''

    def raise_for_status(self):
        return None


def fake_get(*args, **kwargs):
    return Response()


trends.requests.get = fake_get
values = trends.fetch_google_trends_rss()
assert values == ["produto em alta", "organizacao casa"]
trends._save_trends(values, "Google Trending Now RSS — Brasil")
assert fake_streamlit.session_state["real_trends"] == values
assert trends.campaign_state.get_campaign()["trends"] == values
print("TRENDS_RSS_TEST_OK")
