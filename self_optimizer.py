from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import streamlit as st


MIN_IMPRESSIONS = 20
MIN_CLICKS = 5

DEFAULT_MEMORY = {
    "versao_modelo": "3.0-Evidência",
    "ciclos_executados": 0,
    "melhor_prateleira": "não determinada",
    "parametros_otimizacao": {
        "intensidade_gancho": "Normal",
        "foco_conversao": "Aguardando métricas",
        "estilo_copy": "AIDA Padrão",
    },
    "evidencia": {
        "publicacoes_medidas": 0,
        "impressoes": 0,
        "cliques": 0,
        "conversoes": 0,
        "melhor_variante": None,
        "confianca": 0.0,
        "ultima_avaliacao": "Ainda não há métricas reais.",
    },
    "ajustes_realizados": [
        "O agente só altera estratégia depois de observar métricas reais.",
        "Ciclos executados sem impressões não são tratados como aprendizagem.",
    ],
}


def _writable_memory_path() -> Path:
    configured = os.environ.get("NEXUS_LEARNING_LOG_PATH")
    candidates = [Path(configured)] if configured else []
    data_dir = os.environ.get("NEXUS_DATA_DIR")
    if data_dir:
        candidates.append(Path(data_dir) / "nexus_learning_log.json")
    candidates.extend([Path.cwd() / "nexus_learning_log.json", Path("/tmp/nexus_nexus_learning_log.json")])
    for candidate in candidates:
        try:
            candidate.parent.mkdir(parents=True, exist_ok=True)
            if candidate.exists() or os.access(candidate.parent, os.W_OK):
                return candidate
        except OSError:
            continue
    return Path("/tmp/nexus_nexus_learning_log.json")


LOG_OTIMIZACAO = str(_writable_memory_path())


def carregar_memoria_agente() -> dict[str, Any]:
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


def guardar_memoria_agente(memoria: dict[str, Any]) -> bool:
    path = Path(LOG_OTIMIZACAO)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(memoria, file, ensure_ascii=False, indent=4)
        temporary.replace(path)
        return True
    except OSError:
        return False


def _metric_snapshot(product_name: str | None = None) -> dict[str, Any]:
    """Agrega apenas métricas armazenadas; nunca cria projeções."""
    try:
        import metrics_store
        rows = metrics_store.performance_rows()
    except Exception as exc:
        return {"available": False, "error": str(exc), "rows": [], "by_variant": {}}

    filtered = [row for row in rows if not product_name or row.get("product_name") == product_name]
    by_variant: dict[str, dict[str, float]] = {}
    for row in filtered:
        variant = row.get("variant") or "unknown"
        item = by_variant.setdefault(variant, {"impressions": 0, "clicks": 0, "conversions": 0, "ctr": 0.0, "conversion_rate": 0.0})
        item["impressions"] += int(row.get("impressions") or 0)
        item["clicks"] += int(row.get("clicks") or 0)
        item["conversions"] += int(row.get("conversions") or 0)

    for item in by_variant.values():
        item["ctr"] = item["clicks"] / item["impressions"] if item["impressions"] else 0.0
        item["conversion_rate"] = item["conversions"] / item["clicks"] if item["clicks"] else 0.0

    totals = {
        "publicacoes_medidas": len(filtered),
        "impressoes": sum(item["impressions"] for item in by_variant.values()),
        "cliques": sum(item["clicks"] for item in by_variant.values()),
        "conversoes": sum(item["conversions"] for item in by_variant.values()),
    }
    return {"available": True, "rows": filtered, "by_variant": by_variant, **totals}


def obter_resumo_evidencia(product_name: str | None = None) -> dict[str, Any]:
    snapshot = _metric_snapshot(product_name)
    by_variant = snapshot.get("by_variant", {})
    eligible = {
        variant: stats for variant, stats in by_variant.items()
        if stats["impressions"] >= MIN_IMPRESSIONS and stats["clicks"] >= MIN_CLICKS
    }
    ranked = sorted(
        eligible.items(),
        key=lambda pair: (pair[1]["conversion_rate"], pair[1]["ctr"]),
        reverse=True,
    )
    best_variant = ranked[0][0] if ranked else None
    confidence = 0.0
    if best_variant:
        stats = eligible[best_variant]
        confidence = min(1.0, stats["impressions"] / 1000) * 0.5 + min(1.0, stats["clicks"] / 100) * 0.5
    return {**snapshot, "eligible": eligible, "best_variant": best_variant, "confidence": round(confidence, 3)}


def _apply_evidence_strategy(memoria: dict[str, Any], evidence: dict[str, Any], prateleira_atual: str) -> str:
    memoria["evidencia"] = {
        "publicacoes_medidas": evidence.get("publicacoes_medidas", 0),
        "impressoes": evidence.get("impressoes", 0),
        "cliques": evidence.get("cliques", 0),
        "conversoes": evidence.get("conversoes", 0),
        "melhor_variante": evidence.get("best_variant"),
        "confianca": evidence.get("confidence", 0.0),
        "ultima_avaliacao": "",
    }
    best = evidence.get("best_variant")
    if not best:
        if evidence.get("impressoes", 0) == 0:
            feedback = "Sem aprendizagem: ainda não existem impressões reais registadas."
        else:
            feedback = f"Amostra insuficiente: são necessários pelo menos {MIN_IMPRESSIONS} impressões e {MIN_CLICKS} cliques por variante."
        memoria["evidencia"]["ultima_avaliacao"] = feedback
        return feedback

    memoria["melhor_prateleira"] = prateleira_atual or memoria.get("melhor_prateleira", "não determinada")
    if best == "video_b":
        memoria["parametros_otimizacao"] = {
            "intensidade_gancho": "Alta retenção",
            "foco_conversao": "Vídeo B vencedor por CTR/conversão",
            "estilo_copy": "AIDA curta com demonstração",
        }
    else:
        memoria["parametros_otimizacao"] = {
            "intensidade_gancho": "Clareza visual",
            "foco_conversao": "Imagem A vencedora por CTR/conversão",
            "estilo_copy": "AIDA com CTA direto",
        }
    stats = evidence["eligible"][best]
    feedback = (
        f"Aprendizagem confirmada: {best} lidera com CTR {stats['ctr']:.2%} e "
        f"taxa de conversão {stats['conversion_rate']:.2%} na amostra elegível."
    )
    memoria["evidencia"]["ultima_avaliacao"] = feedback
    return feedback


def avaliar_e_otimizar(produto_atual, prateleira_atual, *, campaign_id: int | None = None):
    memoria = carregar_memoria_agente()
    memoria["versao_modelo"] = "3.0-Evidência"
    memoria["ciclos_executados"] = int(memoria.get("ciclos_executados", 0)) + 1
    memoria.setdefault("ajustes_realizados", [])
    evidence = obter_resumo_evidencia(produto_atual)
    feedback = _apply_evidence_strategy(memoria, evidence, prateleira_atual)
    memoria["ajustes_realizados"].append(f"Ciclo #{memoria['ciclos_executados']}: {feedback}")
    memoria["ajustes_realizados"] = memoria["ajustes_realizados"][-100:]
    guardar_memoria_agente(memoria)
    return feedback


def obter_instrucao_estrategica():
    memoria = carregar_memoria_agente()
    parametros = memoria.get("parametros_otimizacao", {})
    evidencia = memoria.get("evidencia", {})
    return (
        f" [OTIMIZAÇÃO NEXUS: Gancho {parametros.get('intensidade_gancho')}, "
        f"Foco {parametros.get('foco_conversao')}, Estilo {parametros.get('estilo_copy')}, "
        f"Melhor variante {evidencia.get('melhor_variante') or 'sem evidência'}]"
    )


def exibir_painel_evolutivo():
    st.subheader("🧠 Cérebro Evolutivo & Auto-Otimização baseada em evidência")
    st.markdown("Ciclos executados são separados de aprendizagem comprovada. O agente só altera a estratégia quando existem métricas reais suficientes.")
    memoria = carregar_memoria_agente()
    evidencia = memoria.get("evidencia", {})
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ciclos executados", memoria.get("ciclos_executados", 0))
    col2.metric("Impressões medidas", evidencia.get("impressoes", 0))
    col3.metric("Cliques medidos", evidencia.get("cliques", 0))
    col4.metric("Conversões medidas", evidencia.get("conversoes", 0))
    st.divider()
    st.markdown(f"**Melhor variante comprovada:** `{evidencia.get('melhor_variante') or 'ainda não determinada'}`")
    st.markdown(f"**Confiança da amostra:** `{float(evidencia.get('confianca', 0.0)):.1%}`")
    st.info(evidencia.get("ultima_avaliacao", "Ainda não há métricas reais."))
    st.markdown("#### 🧬 Histórico de avaliações")
    for ajuste in reversed(memoria.get("ajustes_realizados", [])):
        st.markdown(f"- {ajuste}")
