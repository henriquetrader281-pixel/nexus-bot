import streamlit as st

def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio de Edição Nexus | Nível CEO 🔱")
    
    if "sel_nome" in st.session_state and st.session_state.sel_nome:
        produto = st.session_state.sel_nome
        
        # --- BLOCO 1: O FUNIL AIDA (CONVERSÃO) ---
        with st.container(border=True):
            st.markdown("#### 🎯 Legenda AIDA (Alta Conversão)")
            if st.button(f"🔥 GERAR MUNIÇÃO AIDA: {produto}", use_container_width=True):
                with st.spinner("Gemini Plus aplicando Engenharia de Vendas..."):
                    prompt_aida = f"""
                    Atue como Copywriter Sênior. Crie uma legenda AIDA para: {produto}.
                    [ATENÇÃO]: Hook agressivo para parar o scroll.
                    [INTERESSE]: Curiosidade sobre o benefício.
                    [DESEJO]: A transformação que o produto traz.
                    [AÇÃO]: CTA direto para o link abaixo.
                    Use emojis e quebras de linha.
                    """
                    copy_aida = miny.minerar_produtos(prompt_aida, "Shopee", motor_ia)
                    
                    # Link Blindado com seu ID
                    link_base = st.session_state.get('sel_link', 'https://shopee.com.br')
                    if "?" in link_base: link_base = link_base.split("?")[0]
                    link_final = f"{link_base}?smtt=18316451024"
                    
                    st.session_state.copy_final_pronta = f"{copy_aida.strip()}\n\n🛒 **PROMOÇÃO AQUI:** {link_final}"

            if "copy_final_pronta" in st.session_state:
                st.text_area("Copie sua Legenda:", value=st.session_state.copy_final_pronta, height=220)

        st.divider()

        # --- BLOCO 2: ROTEIRO E TRENDS (RETENÇÃO) ---
        st.markdown("#### ⚡ Radar de Retenção e Trends")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🧠 ROTEIRO DE EDIÇÃO VIRAL", use_container_width=True):
                with st.spinner("Criando mapa de cortes..."):
                    prompt_video = f"Crie um roteiro de 10-15 seg para {produto}. Foque em: 0-3s Hook Visual, 3-10s Detalhes Satisfatórios, 10-15s CTA."
                    st.session_state.roteiro_video = miny.minerar_produtos(prompt_video, "Shopee", motor_ia)
        
        with c2:
            if st.button("🎵 ÁUDIOS EM ALTA (TRENDS)", use_container_width=True):
                # Aqui listamos as músicas que mais estão convertendo para Shopee agora
                st.session_state.trends_atual = [
                    "🔥 Casca de Bala (Thullio Milionário) - Perfeito para 'Achadinhos'",
                    "⚡ RAM TCHUM (Dennis DJ) - Ideal para produtos de utilidade rápida",
                    "✨ Praise Jah In The Moonlight - Para vídeos estéticos/satisfatórios",
                    "💎 MTG Quem Não Quer Sou Eu - Trend de ostentação de utilidades"
                ]

        # Exibição dos resultados de retenção
        col_res1, col_res2 = st.columns(2)
        if "roteiro_video" in col_res1 and st.session_state.roteiro_video:
            with col_res1.expander("🎥 MAPA DE EDIÇÃO", expanded=True):
                st.markdown(st.session_state.roteiro_video)
        
        if "trends_atual" in st.session_state:
            with col_res2.expander("🎵 TRENDS RECOMENDADAS", expanded=True):
                for t in st.session_state.trends_atual:
                    st.write(t)
                st.info("💡 Dica: No TikTok, use o áudio em 'volume 5%' para não abafar a narração.")

    else:
        st.warning("⚠️ Selecione um produto no Scanner antes de entrar no Estúdio!")
