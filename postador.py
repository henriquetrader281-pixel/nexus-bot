import os
from pathlib import Path
import streamlit as st


def exibir_postador(miny=None, motor_ia=None):
    st.markdown("### 🛰️ Central de Disparo Nexus: Meta Suite")
    
    # 🔗 Recupera os dados do Agente, Arsenal e Estúdio
    # Tenta pegar a copy final, se não houver, tenta a copy ativa do agente
    copy_final = st.session_state.get('copy_final_pronta', st.session_state.get('copy_ativa', ''))
    link_blindado = st.session_state.get('link_final_afiliado', st.session_state.get('sel_link', ''))
    video_gerado = st.session_state.get('video_path_local', st.session_state.get('nexus_video_demo', None))

    if not copy_final:
        st.warning("⚠️ O Arsenal e o Agente estão vazios! Execute o Agente de 1-Clique ou gere uma copy no Arsenal antes de postar.")
        return

    # --- ÁREA DE CONFERÊNCIA ---
    with st.container(border=True):
        st.markdown("#### 📝 Legenda Pronta para o Post")
        
        palavra_gatilho = st.text_input("Gatilho ManyChat:", value="QUERO")
        # Monta o texto final que será copiado
        texto_completo = f"{copy_final}\n\n🎁 Comente {palavra_gatilho} para receber o link com desconto oficial!"
        
        st.text_area("Prévia (Confira o link oficial):", value=texto_completo, height=180)

    # --- PRÉVIA COMPARATIVA OBRIGATÓRIA ---
    from creative_preview import exibir_previa_comparativa
    exibir_previa_comparativa({
        "product_name": st.session_state.get("sel_nome", "Oferta Nexus"),
        "official_affiliate_url": link_blindado,
        "image_path": st.session_state.get("image_path_local"),
        "video_path": video_gerado,
        "image_url": st.session_state.get("img_real_url"),
        "video_url": st.session_state.get("nexus_video_demo"),
        "image_description": texto_completo,
        "video_description": "Roteiro curto: gancho, demonstração do produto e CTA.",
        "cta": "Ver oferta oficial",
    })

    # --- FLUXO DE DISPARO ---
    st.markdown("#### ⚡ Passo a Passo para Postagem")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.info("1️⃣ **Baixe o Vídeo**")
        if video_gerado and Path(str(video_gerado)).is_file():
            try:
                with open(str(video_gerado), "rb") as f:
                    st.download_button(
                        label="📥 BAIXAR REELS PRONTO",
                        data=f,
                        file_name=Path(str(video_gerado)).name,
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
                        if res.get('success'):
                            try:
                                import metrics_store
                                campaign_id = st.session_state.get('metrics_campaign_id')
                                if not campaign_id:
                                    campaign_id = metrics_store.create_campaign("Mercado Livre", link_blindado, st.session_state.get('sel_nome', 'Oferta'))
                                creative_id = st.session_state.get('metrics_creative_id')
                                if not creative_id:
                                    creative_id = metrics_store.create_creative(
                                        campaign_id,
                                        "image_a",
                                        st.session_state.get('sel_nome', 'Oferta'),
                                        texto_completo,
                                        "Ver oferta oficial",
                                        asset_url=st.session_state.get('img_real_url'),
                                        width=1000,
                                        height=1500,
                                        status="ready",
                                    )
                                pin_data = res.get('data') or {}
                                publication_id = metrics_store.record_publication(
                                    creative_id,
                                    "pinterest",
                                    external_post_id=str(pin_data.get('id')) if pin_data.get('id') else None,
                                    external_url=res.get('url'),
                                    status="published",
                                )
                                st.session_state.metrics_publication_id = publication_id
                            except Exception as metrics_error:
                                st.warning(f"Pin publicado, mas o registo analítico falhou: {metrics_error}")
                            st.success("🔥 PIN PUBLICADO E REGISTADO NAS MÉTRICAS!")
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
        st.markdown("#### 🔍 Auxiliar: Encontrar ID da Pasta Pinterest")
        if st.button("📋 LISTAR MINHAS PASTAS E IDs", use_container_width=True):
            token_temp = st.secrets.get("PINTEREST_ACCESS_TOKEN")
            if token_temp:
                import pinterest_engine
                res_boards = pinterest_engine.listar_pastas_pinterest(token_temp)
                if res_boards['success']:
                    if not res_boards['items']:
                        st.warning("Nenhuma pasta encontrada. Crie uma pasta no Pinterest primeiro.")
                    else:
                        st.info("Copie o número (ID) da pasta desejada:")
                        for b in res_boards['items']:
                            st.code(f"Nome: {b['name']} | ID: {b['id']}", language="text")
                else:
                    st.error(f"Erro ao listar: {res_boards['error']}")
            else:
                st.warning("⚠️ Insira primeiro o PINTEREST_ACCESS_TOKEN nos Secrets.")
        
        st.divider()
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
