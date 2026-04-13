import streamlit as st
import os
import threading
from pathlib import Path
from nexus_video_engine import generate_daily_reels
# Essa biblioteca permite que a Thread converse com o Streamlit sem dar erro
from streamlit.runtime.scriptrunner import add_script_run_ctx

# 1. Atualize a função invisível no topo do arquivo:
def rodar_motor_no_fundo(url, musica_trend): # <-- Adicione musica_trend aqui
    try:
        os.makedirs("video", exist_ok=True)
        # Passa a música para o motor
        videos = generate_daily_reels(url, musica_trend) 
        st.session_state["last_videos"] = videos
        st.session_state["status_motor"] = "concluido"
    except Exception as e:
        st.session_state["erro_motor"] = str(e)
        st.session_state["status_motor"] = "erro"

# 2. Dentro do render_studio_tab(), adicione o aviso visual:
def render_studio_tab():
    st.header("🎥 Nexus Studio: Produção de Reels")
    
    # ... (código do link_selecionado que você já tem) ...

    # --- NOVIDADE: PUXA O ÁUDIO DO TRENDS ---
    musica_trend = st.session_state.get("musica_selecionada", "")
    if musica_trend:
        st.info(f"🎵 Áudio Viral do Trends ativo: **{musica_trend}**")
    # ----------------------------------------
    
    url = st.text_input("Link do Produto (Shopee):", value=link_selecionado)

    if st.button("🚀 GERAR 3 VÍDEOS AGORA", width='stretch'):
        if not url:
            st.error("Selecione um produto no Scanner primeiro!")
        else:
            st.session_state["status_motor"] = "rodando"
            
            # --- NOVIDADE: PASSA A MÚSICA PARA A THREAD ---
            t = threading.Thread(target=rodar_motor_no_fundo, args=(url, musica_trend))
            # ----------------------------------------------
            add_script_run_ctx(t)
            t.start()
            st.rerun()
            
    # ... (resto do código continua igual)

# 2. ABA DO ESTÚDIO
def render_studio_tab():
    st.header("🎥 Nexus Studio: Produção de Reels")
    
    link_selecionado = st.session_state.get("sel_link", "")
    nome_selecionado = st.session_state.get("sel_nome", "")
    
    if link_selecionado:
        st.success(f"🎯 Produto Selecionado: **{nome_selecionado}**")
    
    url = st.text_input("Link do Produto (Shopee):", value=link_selecionado)

    # Inicia o status do motor se você acabou de abrir o app
    if "status_motor" not in st.session_state:
        st.session_state["status_motor"] = "parado"

    if st.button("🚀 GERAR 3 VÍDEOS AGORA", width='stretch'):
        if not url:
            st.error("Selecione um produto no Scanner primeiro!")
        else:
            # Muda o status e avisa o sistema que começou a rodar
            st.session_state["status_motor"] = "rodando"
            
            # Cria a Thread (O trabalhador invisível)
            t = threading.Thread(target=rodar_motor_no_fundo, args=(url,))
            add_script_run_ctx(t) # Conecta o trabalhador ao seu Session State
            t.start()
            
            # Recarrega a tela instantaneamente para liberar seu mouse
            st.rerun()

    # --- MENSAGEM ENQUANTO RODA ---
    if st.session_state["status_motor"] == "rodando":
        st.info("⚙️ **O motor está trabalhando em segundo plano!** Você já pode navegar nas abas 📈 Trends e 🌍 Radar livremente.")
        st.spinner("Renderizando os 3 vídeos...")

    # --- SE OCORRER UM ERRO ---
    if st.session_state["status_motor"] == "erro":
        st.error(f"Erro no motor: {st.session_state.get('erro_motor')}")
        if st.button("Limpar Erro"):
            st.session_state["status_motor"] = "parado"
            st.rerun()

    # --- EXIBIÇÃO DOS VÍDEOS (Quando Termina) ---
    if st.session_state["status_motor"] == "concluido" and "last_videos" in st.session_state:
        st.success("✅ Todos os vídeos foram gerados com sucesso!")
        st.divider()
        cols = st.columns(3)
        for i, v_path in enumerate(st.session_state["last_videos"]):
            with cols[i]:
                st.write(f"Variação {i+1}")
                if os.path.exists(v_path):
                    st.video(str(v_path))
                    if st.button(f"📲 Postar V{i+1}", key=f"p_{i}"):
                        st.info("Enviando para o nexus_poster.py...")
                else:
                    st.error("Arquivo de vídeo não encontrado.")
