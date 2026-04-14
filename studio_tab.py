import streamlit as st

def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio de Automação Nexus 🔱")
    
    if "sel_nome" not in st.session_state:
        st.warning("⚠️ Selecione um produto primeiro.")
        return

    produto = st.session_state.sel_nome.split('|')[0].strip()

    # --- BOTÃO DE EXECUÇÃO TOTAL ---
    if st.button(f"🚀 EXECUTAR AUTOMAÇÃO TOTAL: {produto}", use_container_width=True):
        col1, col2 = st.columns(2)
        
        with col1:
            with st.spinner("🤖 Gerando Legenda AIDA..."):
                # Executa a copy e já salva na sessão automaticamente
                prompt_aida = f"Gere legenda AIDA para {produto} com ID 18316451024."
                st.session_state.copy_final = miny.minerar_produtos(prompt_aida, "Shopee", motor_ia)
                st.success("Legenda Gerada!")

        with col2:
            with st.spinner("🎬 Preparando Prompt de Vídeo..."):
                # Gera o prompt técnico que será enviado para a IA de vídeo
                prompt_ia_video = f"Create a 4k cinematic product video for {produto}, professional lighting."
                st.session_state.prompt_ia_video = miny.minerar_produtos(prompt_ia_video, "Shopee", motor_ia)
                st.success("Prompt de Vídeo Pronto!")

    # --- ÁREA DE SAÍDA AUTOMÁTICA ---
    if "copy_final" in st.session_state:
        st.text_area("📄 Copy Pronta para Postar:", value=st.session_state.copy_final, height=150)
        
        st.markdown("#### 🎥 Gerador de Vídeo Automático")
        # Aqui é onde o Nexus "colaria" o comando se as ferramentas tivessem API aberta
        st.info(f"O Nexus preparou o comando: '{st.session_state.prompt_ia_video}'")
        
        # Simulando a integração automática
        if st.button("▶️ ENVIAR PARA FILA DE RENDERIZAÇÃO"):
            st.warning("Conectando aos servidores de vídeo... (Requer integração API Luma/Runway)")
            # Aqui entrará o código de requisição POST para gerar o vídeo automático
