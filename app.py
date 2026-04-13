import streamlit as st
import os
from pathlib import Path
from nexus_video_engine import generate_daily_reels

def render_studio_tab():
    st.header("🎥 Nexus Studio: Produção de Reels")
    
    link_selecionado = st.session_state.get("sel_link", "")
    nome_selecionado = st.session_state.get("sel_nome", "")
    
    if link_selecionado:
        st.success(f"🎯 Produto Selecionado: **{nome_selecionado}**")
    
    url = st.text_input("Link do Produto (Shopee):", value=link_selecionado)

    if st.button("🚀 GERAR 3 VÍDEOS AGORA", width='stretch'):
        if not url:
            st.error("Selecione um produto no Scanner primeiro!")
        else:
            with st.spinner("O Nexus está criando as variações AIDA..."):
                try:
                    os.makedirs("video", exist_ok=True)
                    videos = generate_daily_reels(url)
                    st.session_state["last_videos"] = videos
                    st.success("✅ Vídeos gerados!")
                except Exception as e:
                    st.error(f"Erro no motor: {e}")

    if "last_videos" in st.session_state:
        st.divider()
        cols = st.columns(3)
        for i, v_path in enumerate(st.session_state["last_videos"]):
            with cols[i]:
                st.write(f"Variação {i+1}")
                # BLOQUEIO DE ERRO: Só mostra o vídeo se o arquivo realmente existir
                if os.path.exists(v_path):
                    st.video(str(v_path))
                    if st.button(f"📲 Postar V{i+1}", key=f"p_{i}"):
                        st.info("Enviando para o nexus_poster.py...")
                else:
                    st.error("Arquivo de vídeo não encontrado. Verifique os logs do FFmpeg.")
