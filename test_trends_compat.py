import sys
import types


class SessionState(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__


fake_streamlit = types.ModuleType("streamlit")
fake_streamlit.session_state = SessionState()
fake_streamlit.secrets = {}
sys.modules["streamlit"] = fake_streamlit

import trends

calls = []


class FakeTrendReq:
    def __init__(self, **kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            raise TypeError("Retry.__init__() got an unexpected keyword argument 'method_whitelist'")


trends.TrendReq = FakeTrendReq
client = trends._trend_client()
assert isinstance(client, FakeTrendReq)
assert len(calls) == 2
print("TRENDS_COMPAT_TEST_OK")
