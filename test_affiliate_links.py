import sys
import types


class SessionState(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__


fake_streamlit = types.ModuleType("streamlit")
fake_streamlit.session_state = SessionState()
fake_streamlit.secrets = {}
sys.modules["streamlit"] = fake_streamlit

import ml_afiliados_engine

official = "https://meli.la/11v5uxd"
assert ml_afiliados_engine.gerar_link_afiliado_dinamico(official, "Mercado Livre") == official
search = ml_afiliados_engine.gerar_link_afiliado_dinamico("Power Bank 10000mah", "Mercado Livre")
assert "nexusbot01" in search
print("AFFILIATE_LINK_TEST_OK")
