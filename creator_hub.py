from __future__ import annotations

import streamlit as st

import arsenal
import studio_tab


def exibir_creator_hub() -> None:
    st.header("🎬 Studio Nexus · Copy, Imagem e Vídeo")
    st.caption("Escolha a copy, gere a mídia real e envie tudo para a prévia de publicação sem trocar de setor.")
    with st.expander("📝 Arsenal de Copy AIDA", expanded=True):
        arsenal.exibir_arsenal(None, None)
    with st.expander("🎥 Produção de Imagem A + Vídeo B", expanded=True):
        studio_tab.exibir_estudio(None, None)
