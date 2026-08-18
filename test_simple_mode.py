import sys
import types

fake_streamlit = types.ModuleType("streamlit")
fake_streamlit.secrets = {}
fake_streamlit.session_state = {}
sys.modules["streamlit"] = fake_streamlit

import simple_mode

analysis = simple_mode.analisar_palavras_chave(
    "Organizador Rotativo 360",
    "perder tempo procurando temperos",
    "cozinha prática, organização, desejo",
)
assert analysis["keywords"]
assert len(analysis["hooks"]) >= 8
assert analysis["intent"]
assert analysis["intent_label"]
assert analysis["caption"]
copy, warning = simple_mode.gerar_copy(
    {"product_name": "Organizador Rotativo 360", "pain": "perder tempo procurando temperos"},
    analysis,
)
assert "Organizador Rotativo 360" in copy
assert "QUERO" in copy
assert warning is not None
print("SIMPLE_MODE_TEST_OK")
