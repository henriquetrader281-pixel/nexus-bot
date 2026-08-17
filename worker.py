import os
import sys
from unittest.mock import MagicMock


class SessionState(dict):
    """Estado mínimo compatível com st.session_state no modo headless."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value

# 1. MOCK DO STREAMLIT (Essencial para rodar no GitHub Actions sem erro)
mock_st = MagicMock()
# Simula os segredos do GitHub como se fossem st.secrets
mock_st.secrets = {
    "ML_TRACKING_ID": os.environ.get("ML_TRACKING_ID"),
    "GROQ_API_KEY": os.environ.get("GROQ_API_KEY"),
    "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY"),
    "PINTEREST_ACCESS_TOKEN": os.environ.get("PINTEREST_ACCESS_TOKEN"),
    "PINTEREST_BOARD_ID": os.environ.get("PINTEREST_BOARD_ID"),
    "MANYCHAT_WEBHOOK_URL": os.environ.get("MANYCHAT_WEBHOOK_URL"),
    "ELEVENLABS_API_KEY": os.environ.get("ELEVENLABS_API_KEY")
}
mock_st.session_state = SessionState()
sys.modules['streamlit'] = mock_st

# 2. IMPORTA OS MOTORES DO NEXUS
import autonomo_engine
import hermes_engine

def executar_plantao_nexus():
    print("🚀 [WORKER] Iniciando Plantão 24h Nexus Bot...")
    try:
        # Executa o ciclo mestre de 1-clique em modo silencioso
        # O provedor padrão é gemini para maior precisão na gringa
        resultado = autonomo_engine.executar_ciclo_mestre_um_clique(provedor="gemini")
        
        produto = resultado.get("produto", "produto não identificado")
        link_ml = resultado.get("link_ml", "link não disponível")
        print(f"✅ [WORKER] Ciclo concluído para '{produto}'. Supervisão Hermes executada.")
        print(f"🔗 [WORKER] Link de Venda: {link_ml}")
        
    except Exception as e:
        print(f"❌ [WORKER] Falha no plantão: {str(e)}")

if __name__ == "__main__":
    executar_plantao_nexus()
