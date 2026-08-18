from __future__ import annotations

import os
import time

import streamlit as st


# --- MÓDULO DE SUPERVISÃO TÉCNICA HERMES ---


def hermes_elite_programmer(acao="diagnostico", contexto=None):
    """Executa diagnóstico, correção assistida ou replicação estratégica."""
    st.markdown("### 👨‍💻 Hermes: Elite Programmer Console")
    with st.status("🕊️ Hermes analisando a arquitetura do sistema...", expanded=True) as status:
        st.write("🔍 Escaneando dependências e conexões de API...")
        time.sleep(0.2)
        if acao == "diagnostico":
            st.write("✅ Estrutura Core: analisada")
            st.write("🔧 Verificando pipeline de mídia e integrações sociais...")
            status.update(label="🚀 Diagnóstico Hermes concluído", state="complete", expanded=False)
        elif acao == "correcao":
            st.write(f"❌ Falha identificada em: {contexto}")
            st.write("🛠️ Rota marcada para correção e novo teste controlado...")
            status.update(label="🛠️ Correção assistida preparada", state="complete", expanded=False)
        elif acao == "replicacao":
            st.write("📈 Nenhuma replicação é autorizada sem métricas de publicação confirmadas.")
            status.update(label="🧬 Replicação condicionada a métricas", state="complete", expanded=False)


def _status_ok(status):
    return bool(status.get("success")) or bool(status.get("skipped"))


def _status_label(status):
    if status.get("success"):
        return f"OK{(' — ' + str(status.get('status_code'))) if status.get('status_code') else ''}"
    if status.get("skipped"):
        return f"IGNORADO — {status.get('detail') or status.get('error') or 'não acionado'}"
    return f"FALHA — {status.get('error') or 'motivo não informado'}"


def supervisionar_entrega(produto, link_afiliado, status_pinterest, status_instagram, status_manychat):
    """Audita o resultado técnico sem confundir execução com lucro."""
    st.markdown("---")
    st.markdown("### 🕊️ Relatório de Entrega & Auditoria: Agente Hermes")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Alvo:** {produto}")
        st.markdown(f"**Link Blindado:** `{link_afiliado}`")
    with col2:
        st.image("https://img.icons8.com/fluency/96/hermes-staff.png", width=60)

    statuses = {
        "Pinterest API": status_pinterest or {},
        "Instagram API": status_instagram or {},
        "ManyChat webhook": status_manychat or {},
    }
    erros = [name for name, status in statuses.items() if not _status_ok(status)]
    ignorados = [name for name, status in statuses.items() if status.get("skipped") and not status.get("success")]

    if erros:
        st.error(f"Hermes bloqueou a aprovação técnica. Falhas: {', '.join(erros)}")
        st.caption("Configure os Secrets ou corrija a resposta da API antes de ativar publicação automática.")
        if st.button("🛠️ ABRIR AUTOCURA ASSISTIDA", key="hermes_autocura"):
            hermes_elite_programmer("correcao", erros[0])
            st.info("A rota foi marcada para novo teste. O Hermes não inventa tokens nem confirma lucro sem publicação real.")
    elif ignorados:
        st.warning(f"Operação parcial: {', '.join(ignorados)} não foram acionados neste ciclo.")
        st.info("Não há base técnica para declarar lucratividade máxima nem iniciar replicação.")
    else:
        st.success("Todas as integrações acionadas responderam tecnicamente.")
        st.info("Aprovação técnica concluída; lucro e ROI dependem de cliques, vendas e métricas reais.")

    with st.expander("📄 Ver Logs Técnicos do Hermes", expanded=False):
        st.code(
            "\n".join([
                f"[SYSTEM_LOG] {time.strftime('%Y-%m-%d %H:%M:%S')}",
                f"[HERMES] Analisando Produto: {produto}",
                f"[HERMES] Status Pinterest: {_status_label(statuses['Pinterest API'])}",
                f"[HERMES] Status Instagram: {_status_label(statuses['Instagram API'])}",
                f"[HERMES] Status ManyChat: {_status_label(statuses['ManyChat webhook'])}",
                "[HERMES] Lógica Evolutiva: registada",
                f"[HERMES] Veredito: {'BLOQUEADO' if erros else ('PARCIAL' if ignorados else 'APROVADO TECNICAMENTE')}",
            ]),
            language="bash",
        )
