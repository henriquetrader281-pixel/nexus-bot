import os

from streamlit.testing.v1 import AppTest

os.environ.setdefault("NEXUS_PASSWORD", "senha-de-teste")
app = AppTest.from_file("app.py", default_timeout=30)
app.run()
if app.exception:
    raise RuntimeError(str(app.exception))

# A tela inicial exige uma senha explicitamente configurada em NEXUS_PASSWORD.
assert any("Chave de Acesso Nexus" in item.label for item in app.text_input)
app.text_input[0].set_value(os.environ["NEXUS_PASSWORD"]).run()
if app.exception:
    raise RuntimeError(str(app.exception))

labels = [tab.label for tab in app.tabs]
expected = {"🚀 ESTEIRA PRINCIPAL", "🧠 AVANÇADO"}
assert expected.issubset(set(labels)), labels
print("APP_STRUCTURE_TEST_OK")
