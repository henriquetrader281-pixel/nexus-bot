import os
import sys
import tempfile
import types
from pathlib import Path


class DummyStreamlit(types.ModuleType):
    pass


sys.modules["streamlit"] = DummyStreamlit("streamlit")
root = Path(tempfile.mkdtemp(prefix="nexus_learning_test_"))
os.environ["NEXUS_LEARNING_LOG_PATH"] = str(root / "nexus_learning_test.json")
os.environ["NEXUS_METRICS_DB"] = str(root / "metrics.sqlite3")

import metrics_store
import self_optimizer

feedback_without_data = self_optimizer.avaliar_e_otimizar("Produto teste", "🔥 Virais & Desejo")
assert "aprendizagem" in feedback_without_data.lower()
assert "IA aprendeu" not in feedback_without_data

campaign_id = metrics_store.create_campaign("Mercado Livre", "https://meli.la/teste", "Produto teste")
image_id = metrics_store.create_creative(campaign_id, "image_a", "Produto teste", "Copy A", "QUERO", status="ready")
video_id = metrics_store.create_creative(campaign_id, "video_b", "Produto teste", "Copy B", "QUERO", status="ready")
image_pub = metrics_store.record_publication(image_id, "pinterest", status="published")
video_pub = metrics_store.record_publication(video_id, "pinterest", status="published")
metrics_store.record_metrics(image_pub, impressions=100, clicks=10, conversions=1)
metrics_store.record_metrics(video_pub, impressions=1000, clicks=100, conversions=20)

feedback_with_data = self_optimizer.avaliar_e_otimizar("Produto teste", "🔥 Virais & Desejo")
assert "Aprendizagem confirmada" in feedback_with_data
memory = self_optimizer.carregar_memoria_agente()
assert memory["ciclos_executados"] == 2
assert memory["evidencia"]["melhor_variante"] == "video_b"
assert memory["evidencia"]["impressoes"] == 1100
assert memory["evidencia"]["conversoes"] == 21
print("SELF_OPTIMIZER_TEST_OK")
