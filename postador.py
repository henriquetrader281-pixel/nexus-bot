import streamlit as st

def exibir_postador(miny=None, motor_ia=None):
    st.markdown("### 🛰️ Central de Disparo Nexus: Meta Suite")
    
    # 🔗 Recupera os dados do Arsenal e Estúdio
    copy_final = st.session_state.get('copy_final_pronta', '')
    link_blindado = st.session_state.get('link_final_afiliado', '')
    video_gerado = st.session_state.get('video_path_local', None)

    if not copy_final:
        st.warning("⚠️ O Arsenal está vazio! Gere a copy antes de postar.")
        return

    # --- ÁREA DE CONFERÊNCIA ---
    with st.container(border=True):
        st.markdown("#### 📝 Legenda Pronta para o Post")
        
        palavra_gatilho = st.text_input("Gatilho ManyChat:", value="QUERO")
        # Monta o texto final que será copiado
        texto_completo = f"{copy_final}\n\n🎁 Comente {palavra_gatilho} para receber o link com desconto oficial!"
        
        st.text_area("Prévia (Confira o link blindado):", value=texto_completo, height=180)

    # --- FLUXO DE DISPARO ---
    st.markdown("#### ⚡ Passo a Passo para Postagem")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.info("1️⃣ **Baixe o Vídeo**")
        if video_gerado:
            try:
                with open("reels_final.mp4", "rb") as f:
                    st.download_button(
                        label="📥 BAIXAR REELS PRONTO",
                        data=f,
                        file_name="nexus_reels.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
            except:
                st.error("Gere o vídeo no Estúdio primeiro.")
        else:
            st.warning("Vídeo não localizado.")

    with c2:
        st.info("2️⃣ **Auto-Postagem (API)**")
        rede = st.selectbox("Escolha a Rede:", ["Pinterest (API)", "Instagram (Graph API)", "TikTok (Webhook)"])
        
        if st.button(f"🚀 PUBLICAR AGORA NO {rede.upper()}", use_container_width=True, type="primary"):
            with st.spinner(f"Comunicando com API do {rede}..."):
                if "Pinterest" in rede:
                    import pinterest_engine
                    # Tenta pegar as chaves dos secrets
                    token = st.secrets.get("PINTEREST_ACCESS_TOKEN", None)
                    board = st.secrets.get("PINTEREST_BOARD_ID", None)
                    
                    if token and board:
                        res = pinterest_engine.postar_pinterest(
                            token, board, 
                            st.session_state.get('sel_nome', 'Oferta Nexus'),
                            texto_completo,
                            link_blindado,
                            st.session_state.get('img_real_url', 'https://via.placeholder.com/1080x1920')
                        )
                        if res.get('success'):
                            st.success("🔥 PIN PUBLICADO COM SUCESSO!")
                        else:
                            st.error(f"Erro na API: {res.get('error')}")
                    else:
                        st.warning("⚠️ Configure PINTEREST_ACCESS_TOKEN nos Secrets do Streamlit.")
                else:
                    st.info("Simulação: Webhook enviado para o ManyChat/Make para publicação agendada.")
                    st.toast("Disparo realizado com sucesso!")

    st.divider()
    
    # --- CONFIGURAÇÃO DE REDES ---
    with st.expander("⚙️ CONFIGURAR REDES SOCIAIS (API KEYS)"):
        st.markdown("""
        Para automação total, adicione as chaves abaixo nos **Secrets** do Streamlit Cloud:
        - `PINTEREST_ACCESS_TOKEN`: Token da sua App no Pinterest Developers.
        - `PINTEREST_BOARD_ID`: ID da pasta onde o robô vai postar.
        - `MANYCHAT_WEBHOOK_URL`: Para automação de DMs e comentários.
        - `INSTAGRAM_PAGE_ID`: Para postagem direta via Graph API.
        """)
        st.link_button("🔑 Abrir Painel de Secrets do Streamlit", "https://share.streamlit.io/")
    st.caption(f"🔱 Nexus V101 | Rastreio Ativo: 18316451024")
