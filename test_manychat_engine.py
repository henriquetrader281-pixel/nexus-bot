import sys
import types


class SessionState(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__


fake_streamlit = types.ModuleType("streamlit")
fake_streamlit.session_state = SessionState()
fake_streamlit.secrets = {"MANYCHAT_WEBHOOK_URL": "https://hook.example.test/nexus"}
sys.modules["streamlit"] = fake_streamlit

import manychat_engine

calls = []


class Response:
    status_code = 202
    text = "accepted"


def fake_post(url, json, headers, timeout):
    calls.append((url, json, headers, timeout))
    return Response()


manychat_engine.requests.post = fake_post
result = manychat_engine.testar_webhook_manychat()
assert result["success"] is True
assert calls[-1][1]["test_mode"] is True
assert calls[-1][1]["trigger"] == "NEXUS_TEST"

result = manychat_engine.disparar_webhook_manychat("Produto", "https://meli.la/teste", "Copy")
assert result["success"] is True
assert calls[-1][1]["test_mode"] is False
assert calls[-1][1]["trigger"] == "QUERO"
assert calls[-1][1]["link_afiliado"] == "https://meli.la/teste"
print("MANYCHAT_ENGINE_TEST_OK")
