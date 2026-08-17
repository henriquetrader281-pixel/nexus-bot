from __future__ import annotations

import streamlit as st

import global_engine
import leads_engine


def exibir_inteligencia_leads() -> None:
    st.header("🎯 Inteligência & Leads Nexus")
    st.caption("Descoberta de procura, espionagem internacional, palavras-chave e intenção de compra alimentam a mesma campanha.")
    with st.expander("🎯 Sniper de Leads · Google, fóruns e intenção", expanded=True):
        leads_engine.exibir_aba_leads()
    with st.expander("🌍 Espionagem Global · Pinterest e tendências internacionais", expanded=False):
        global_engine.exibir_espionagem_global()
