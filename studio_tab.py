import streamlit as st
import threading
import time
from pathlib import Path
from nexus_video_engine import generate_daily_reels

def render_studio_tab():
    st.header("🎥 Nexus Studio: Produção de Reels")
    
    # --- O SEGREDO ESTÁ AQUI ---
    # Ele verifica se existe algo selecionado no Scanner/Arsenal. 
    # Se não houver, fica vazio.
    link_selecionado = st.session_state.get("sel_link", "")
    
    if link_selecionado:
        st.success(f"✅ Produto detectado: {st.session_state.get('sel_nome', 'Sem nome')}")
    
    # O 'value' faz o link aparecer automaticamente na caixa
    url = st.text_input("Link do Produto (Shopee):", value=link_selecionado)
    # ---------------------------

    if st.button("🚀 GERAR VÍDEOS AGORA", width='stretch'):
        # ... resto do código
    
    url = st.text_input("Cole o link da Shopee aqui:", placeholder="https://shopee.com.br/produto...")
    
    if st.button("🚀 Gerar 3 Vídeos (AIDA)", width='stretch'):
        if not url:
            st.error("Por favor, cole um link válido.")
        else:
            status = st.empty()
            with st.spinner("O Nexus está a trabalhar nos teus vídeos..."):
                try:
                    # Roda o motor de vídeo
                    videos = generate_daily_reels(url)
                    st.session_state["last_videos"] = videos
                    st.success("✅ 3 vídeos gerados com sucesso!")
                except Exception as e:
                    st.error(f"Erro na geração: {e}")

    if "last_videos" in st.session_state:
        st.divider()
        st.subheader("🎬 Vídeos Prontos")
        for i, v_path in enumerate(st.session_state["last_videos"]):
            with st.container(border=True):
                st.write(f"Variação {i+1}")
                st.video(str(v_path))
                if st.button(f"📲 Postar Vídeo {i+1}", key=f"post_{i}"):
                    st.info("A enviar para o sistema de postagem...")
