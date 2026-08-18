from __future__ import annotations

import sys
import types


class SessionState(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__


class Progress:
    def progress(self, *_args, **_kwargs):
        return None


fake_streamlit = types.ModuleType("streamlit")
fake_streamlit.session_state = SessionState()
fake_streamlit.secrets = {}
fake_streamlit.progress = lambda *_args, **_kwargs: Progress()
fake_streamlit.success = lambda *_args, **_kwargs: None
fake_streamlit.warning = lambda *_args, **_kwargs: None
fake_streamlit.info = lambda *_args, **_kwargs: None
fake_streamlit.error = lambda *_args, **_kwargs: None
fake_streamlit.code = lambda *_args, **_kwargs: None
fake_streamlit.button = lambda *_args, **_kwargs: False
fake_streamlit.balloons = lambda *_args, **_kwargs: None
sys.modules["streamlit"] = fake_streamlit

import autonomo_engine
import campaign_state


def blocked_miner(*_args, **_kwargs):
    raise RuntimeError("403 Client Error: Mercado Livre não devolveu um produto com imagem pública")


autonomo_engine.obter_produto_real_validado = blocked_miner
autonomo_engine.time.sleep = lambda _seconds: None
result = autonomo_engine.executar_ciclo_mestre_um_clique(publicar=True)

assert result["status"] == "blocked"
assert result["publication"] == "not_executed"
assert "403" in result["reason"]
assert campaign_state.get_campaign()["mining_status"] == "blocked"
assert fake_streamlit.session_state["nexus_mining_error"] == result["reason"]
assert "image_path_local" not in fake_streamlit.session_state
assert "video_path_local" not in fake_streamlit.session_state
print("AUTONOMOUS_BLOCKED_HANDLED_OK")
