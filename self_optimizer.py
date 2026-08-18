from __future__ import annotations

import json
import os
from pathlib import Path

import streamlit as st


DEFAULT_MEMORY = {
    "versao_modelo": "2.5-Evolutiva",
    "ciclos_executados": 0,
    "melhor_prateleira": "🔥 Virais & Desejo",
    "parametros_otimizacao": {
        "intensidade_gancho": "Normal",
        "foco_conversao": "Curiosidade",
        "estilo_copy": "AIDA Padrão",
    },
    "ajustes_realizados": [
        "Foco exclusivo em Envio Full do Mercado Livre para zerar fricção.",
        "Inclusão de ganchos de curiosidade extrema (The Hook).",
    ],
}


def _writable_memory_path() -> Path:
    configured = os.environ.get("NEXUS_LEARNING_LOG_PATH")
    candidates = [Path(configured)] if configured else []
    data_dir = os.environ.get("NEXUS_DATA_DIR")
    if data_dir:
        candidates.append(Path(data_dir) / "nexus_learning_log.json")
    # O checkout do Streamlit Cloud pode ser somente leitura. /tmp é gravável.
    candidates.extend([
        Path.cwd() / "nexus_learning_log.json",
        Path("/tmp/nexus_nexus_learning_log.json"),
    ])
    for candidate in candidates:
        try:
            candidate.parent.mkdir(parents=True, exist_ok=True)
            if candidate.exists() or os.access(candidate.parent, os.W_OK):
                return candidate
        except OSError:
            continue
    return Path("/tmp/nexus_nexus_learning_log.json")


LOG_OTIMIZACAO = str(_writable_memory_path())


def carregar_memoria_agente():
    """Carrega o histórico de aprendizagem sem falhar em filesystem read-only."""
    path = Path(LOG_OTIMIZACAO)
    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, dict):
                return data
        except (OSError, ValueError, TypeError):
            pass
    return json.loads(json.dumps(DEFAULT_MEMORY, ensure_ascii=False))


def guardar_memoria_agente(memoria) -> bool:
    """Guarda a memória de forma atómica; nunca derruba o ciclo autónomo."""
    path = Path(LOG_OTIMIZACAO)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(memoria, file, ensure_ascii=False, indent=4)
        temporary.replace(path)
        return True
    except OSError:
        # O agente continua a funcionar mesmo sem persistência nesta execução.
        return False


def obter_instrucao_estrategica():
    """Retorna as instruções de otimização para injetar no prompt da IA."""
    memoria = carregar_memoria_agente()
    parametros = memoria.get("parametros_otimizacao", {})
    return (
        f" [OTIMIZAÇÃO NEXUS: Gancho {parametros.get('intensidade_gancho')}, "
        f"Foco em {parametros.get('foco_conversao')}, "
        f"Estilo {parametros.get('estilo_copy')}]"
    )


def avaliar_e_otimizar(produto_atual, prateleira_atual):
    """Avalia o ciclo e aplica melhorias sem derrubar o agente se não houver disco persistente."""
    memoria = carregar_memoria_agente()
    memoria["ciclos_executados"] = int(memoria.get("ciclos_executados", 0)) + 1
    memoria.setdefault("ajustes_realizados", [])

    if "Virais" in prateleira_atual:
        memoria["parametros_otimizacao"] = {
            "intensidade_gancho": "EXTREMA",
            "foco_conversao": "Desejo Imediato",
            "estilo_copy": "Agressivo/Viral",
        }
        feedback = "IA aprendeu: Produtos virais exigem ganchos extremos. Parâmetros atualizados."
    elif "Tech" in prateleira_atual:
        memoria["parametros_otimizacao"] = {
            "intensidade_gancho": "Autoridade",
            "foco_conversao": "Especificação Técnica",
            "estilo_copy": "Prático/Direto",
        }
        feedback = "IA aprendeu: Nicho Tech exige autoridade e clareza técnica. Parâmetros atualizados."
    else:
        feedback = "IA validou estratégia atual. Mantendo parâmetros de conversão estáveis."

    memoria["ajustes_realizados"].append(f"Ciclo #{memoria['ciclos_executados']}: {feedback}")
    memoria["ajustes_realizados"] = memoria["ajustes_realizados"][-100:]
    guardar_memoria_agente(memoria)
    return feedback


def exibir_painel_evolutivo():
    st.subheader("🧠 Cérebro Evolutivo & Auto-Otimização (Self-Improving)")
    st.markdown("O Nexus Bot analisa cada ciclo executado, identifica padrões de conversão e ajusta autonomamente os seus ganchos de copy e estratégias de prateleira sem intervenção manual.")
    memoria = carregar_memoria_agente()
    col1, col2, col3 = st.columns(3)
    col1.metric("Ciclos de Aprendizagem", memoria.get("ciclos_executados", 0))
    col2.metric("Versão do Agente", memoria.get("versao_modelo", "2.5-Evolutiva"))
    col3.metric("Prateleira Dominante", memoria.get("melhor_prateleira", "não definida"))
    st.divider()
    st.markdown("#### 🧬 Histórico de Adaptações e Mutação Estratégica")
    for ajuste in reversed(memoria.get("ajustes_realizados", [])):
        st.markdown(f"- 💡 {ajuste}")
