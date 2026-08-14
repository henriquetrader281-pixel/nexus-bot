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
                # Simulação de URL pública para vídeo (Em produção seria S3 ou link do Estúdio)
                video_url_publica = st.session_state.get('nexus_video_demo', 'https://assets.mixkit.co/videos/preview/mixkit-hands-typing-on-a-computer-keyboard-42998-large.mp4')
                
                if "Pinterest" in rede:
                    import pinterest_engine
                    token = st.secrets.get("PINTEREST_ACCESS_TOKEN")
                    board = st.secrets.get("PINTEREST_BOARD_ID")
                    if token and board:
                        res = pinterest_engine.postar_pinterest(token, board, st.session_state.get('sel_nome', 'Oferta'), texto_completo, link_blindado, st.session_state.get('img_real_url', 'https://via.placeholder.com/1080x1920'))
                        if res.get('success'): st.success("🔥 PIN PUBLICADO!")
                        else: st.error(f"Erro Pinterest: {res.get('error')}")
                    else: st.warning("⚠️ Configure PINTEREST_ACCESS_TOKEN nos Secrets.")
                
                elif "Instagram" in rede:
                    import instagram_engine
                    res = instagram_engine.postar_instagram_reels(video_url_publica, texto_completo)
                    if res.get('success'): st.success(f"📸 {res['data']}")
                    else: st.error(f"Erro Instagram: {res.get('error')}")
                
                elif "TikTok" in rede:
                    import tiktok_engine
                    res = tiktok_engine.postar_tiktok_video(video_url_publica, st.session_state.get('sel_nome', 'Oferta Nexus'))
                    if res.get('success'): st.success("🎵 VÍDEO ENVIADO PARA O TIKTOK!")
                    else: st.error(f"Erro TikTok: {res.get('error')}")

    st.divider()
    
    # --- CONFIGURAÇÃO DE REDES & AFILIADOS ---
    with st.expander("⚙️ GUIA DE CONFIGURAÇÃO: SECRETS (API KEYS)", expanded=False):
        st.markdown("""
        Para o Nexus rodar 100% automático, você deve adicionar estas chaves nos **Secrets** do Streamlit Cloud:
        
        ### 🤝 Afiliados & Vendas
        - `ML_TRACKING_ID`: Seu ID de afiliado Mercado Livre.
        - `SHOPEE_TRACKING_ID`: Seu ID de afiliado Shopee.
        - `AMAZON_TRACKING_ID`: Seu ID de associado Amazon.
        - `MANYCHAT_WEBHOOK_URL`: URL do seu fluxo no ManyChat.
        
        ### 📱 Redes Sociais (Postagem Direta)
        - `INSTAGRAM_ACCESS_TOKEN`: Token de acesso de longa duração (Graph API).
        - `INSTAGRAM_BUSINESS_ACCOUNT_ID`: ID da sua conta Business.
        - `TIKTOK_ACCESS_TOKEN`: Token da Content Posting API do TikTok.
        - `PINTEREST_ACCESS_TOKEN`: Token do Pinterest Developers.
        - `PINTEREST_BOARD_ID`: ID da sua pasta no Pinterest.
        
        ### 🧠 Inteligência Artificial
        - `GROQ_API_KEY`: Para o motor de copy ultra-rápido.
        - `OPENAI_API_KEY`: Para o motor de visão e análise.
        - `GEMINI_API_KEY`: Para o Google Labs e análise de tendências.
        """)
        st.link_button("🔑 Abrir Painel de Secrets do Streamlit", "https://share.streamlit.io/")
        st.caption("Dica: Vá em 'Settings' -> 'Secrets' no seu dashboard do Streamlit Cloud.")
    st.caption(f"🔱 Nexus V101 | Rastreio Ativo: 18316451024")
