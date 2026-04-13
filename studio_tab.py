import streamlit as st
from pathlib import Path
from nexus_video_engine import generate_daily_reels

def render_studio_tab():
    st.header("🎥 Nexus Studio: Produção de Reels")
    
    # 1. Recupera os dados salvos no 'cérebro' (Session State) pelo Scanner/Arsenal
    link_selecionado = st.session_state.get("sel_link", "")
    nome_selecionado = st.session_state.get("sel_nome", "")
    
    # Exibe um aviso visual se um produto foi selecionado
    if link_selecionado:
        st.success(f"🎯 Pronto para processar: **{nome_selecionado}**")
    else:
        st.info("💡 Selecione um produto no Scanner ou cole o link abaixo.")

    # 2. O campo de input agora usa o 'value' para vir preenchido
    url = st.text_input(
        "Link do Produto (Shopee):", 
        value=link_selecionado, 
        placeholder="https://shopee.com.br/produto..."
    )

    # 3. Botão único de geração
    if st.button("🚀 GERAR 3 VÍDEOS (AIDA)", width='stretch'):
        if not url:
            st.error("Por favor, cole ou selecione um link da Shopee primeiro.")
        else:
            with st.spinner("O Nexus está extraindo fotos e criando as variações AIDA..."):
                try:
                    # Chama o motor de vídeo (nexus_video_engine.py)
                    videos = generate_daily_reels(url)
                    
                    # Salva os caminhos dos vídeos para não sumirem ao recarregar a página
                    st.session_state["last_videos"] = videos
                    st.success("✅ Os 3 Reels foram gerados com sucesso!")
                except Exception as e:
                    st.error(f"Erro no motor de vídeo: {e}")

    # 4. Exibição dos vídeos gerados
    if "last_videos" in st.session_state:
        st.divider()
        st.subheader("🎬 Galeria de Produção")
        
        # Cria colunas para os vídeos não ficarem gigantes um embaixo do outro
        cols = st.columns(3)
        
        for i, v_path in enumerate(st.session_state["last_videos"]):
            with cols[i]:
                st.write(f"Variação {i+1}")
                if Path(v_path).exists():
                    st.video(str(v_path))
                    if st.button(f"📲 Postar V{i+1}", key=f"post_{i}"):
                        st.info("Enviando para o nexus_poster.py...")
                else:
                    st.error("Arquivo não encontrado.")
