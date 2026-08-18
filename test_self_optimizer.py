import os
import sys
import tempfile
import types
from pathlib import Path


class DummyStreamlit(types.ModuleType):
    pass


sys.modules["streamlit"] = DummyStreamlit("streamlit")
os.environ["NEXUS_LEARNING_LOG_PATH"] = str(Path(tempfile.gettempdir()) / "nexus_learning_test.json")
path = Path(os.environ["NEXUS_LEARNING_LOG_PATH"])
path.unlink(missing_ok=True)

import self_optimizer

feedback = self_optimizer.avaliar_e_otimizar("Produto teste", "🔥 Virais & Desejo")
assert "IA aprendeu" in feedback
assert path.is_file()
memoria = self_optimizer.carregar_memoria_agente()
assert memoria["ciclos_executados"] == 1
print("SELF_OPTIMIZER_TEST_OK")
