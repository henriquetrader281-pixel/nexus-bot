import streamlit as st

def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio Automatizado Nexus | Google Labs 🔱")
    
    if "sel_nome" not in st.session_state:
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")
        return

    # Isola o nome para evitar confusão na IA
    produto = st.session_state.sel_nome.split('|')[0].replace("NOME:", "").strip()

    # --- LINHA DE COMANDO: GERAÇÃO DE MUNIÇÃO ---
    c1, c2 = st.columns([1, 1])
    
    with c1:
        if st.button("📝 GERAR COPY & PROMPT 4K (IMAGEM HYPE)", use_container_width=True):
            with st.spinner("Minerando imagem campeã de vendas e otimizando 4K..."):
                # 1. Busca de Imagem Hype (Campeã de Vendas) nos Marketplaces
                search_query = produto.replace(" ", "+")
                marketplace = st.session_state.get('mkt_global', 'Mercado Livre')
                # Filtro de busca para produtos mais vendidos/populares
                img_search_url = f"https://www.google.com/search?q={search_query}+{marketplace}+mais+vendido+original&tbm=isch"
                st.session_state.img_real_url = img_search_url
                
                # 2. Geração de Copy e Prompt 4K seguindo o Roteiro Nexus de 15s
                import tts_engine
                trend = tts_engine.obter_audio_tendencia()
                
                # Recupera o roteiro do agente se disponível para manter consistência
                roteiro_ref = ""
                if "nexus_estrat" in st.session_state:
                    roteiro_ref = "\n".join(st.session_state.nexus_estrat.get('roteiro_15s', []))

                prompt_master = f"""
                Ignore listas. Produto: {produto}. Marketplace: {marketplace}.
                Trend do Dia: {trend['nome']}.
                Roteiro Base: {roteiro_ref}
                
                1. Gere legenda AIDA em Português focada em Envio Full e Alta Qualidade.
                2. Gere um Prompt VISUAL em INGLÊS para o Google Labs seguindo este Roteiro de 15s:
                   - 0-3s: Gancho visual rápido (Close no problema).
                   - 3-10s: Demonstração prática (Produto em ação + Envio Full).
                   - 10-15s: CTA de escassez (Entrega amanhã).
                   
                   DEVE incluir: '8k resolution, photorealistic, cinematic lighting, 4k texture, professional product videography, highly detailed'.
                Separe por '###'
                """
                # Fallback se miny for None (acontece na chamada direta do app.py)
                if miny is None:
                    import mineracao
                    res = mineracao.minerar_produtos(prompt_master, marketplace, None)
                else:
                    res = miny.minerar_produtos(prompt_master, marketplace, motor_ia)
                
                st.session_state.micao_nexus = res.split('###')
                st.rerun()

    # --- EXIBIÇÃO DA MUNIÇÃO ---
    if "micao_nexus" in st.session_state:
        copy_pt = st.session_state.micao_nexus[0].strip()
        prompt_en = st.session_state.micao_nexus[1].strip() if len(st.session_state.micao_nexus) > 1 else ""

        with st.expander("📄 LEGENDA PARA POSTAR", expanded=False):
            st.text_area("Copie aqui:", value=copy_pt, height=150)

        st.success("🎯 PROMPT PARA COLAR NO GOOGLE LABS (OTIMIZADO 4K):")
        st.code(prompt_en, language="text")
        st.caption("DICA: Este prompt foi otimizado para gerar vídeos em alta definição no Google Labs.")

        st.info(f"🖼️ **PESQUISA DE IMAGEM REAL:** [Clique aqui para ver fotos reais do produto no {st.session_state.get('mkt_global', 'Marketplace')}]({st.session_state.get('img_real_url', '#')})")
        st.caption("Use estas imagens como referência visual ou faça upload no Google Labs para guiar a IA.")

        st.divider()
        
        # --- NOVO: NARRAÇÃO E VOZ IA ---
        import tts_engine
        tts_engine.exibir_painel_voz()
        
        st.divider()

        # --- INTEGRAÇÃO DO GOOGLE LABS DENTRO DO NEXUS ---
        st.markdown("#### 📺 Gerador de Vídeo (Execução Direta)")
        
        # Link do projeto específico que você mandou
        url_google = "https://labs.google/fx/pt/tools/flow/project/b7c52242-fa5a-4370-9975-61cc86da1483"
        
        # Criando a janela interna (IFrame)
        # Nota: Alguns sites bloqueiam exibição em IFrame por segurança. 
        # Se o Google bloquear, o botão de 'Abrir em Nova Aba' servirá como backup.
        st.components.v1.iframe(url_google, height=600, scrolling=True)
        
        if st.button("🌍 Não carregou? Abrir Google Labs em tela cheia"):
            st.markdown(f'<a href="{url_google}" target="_blank">Clique aqui para abrir</a>', unsafe_allow_value=True)

    else:
        st.info("Clique no botão acima para preparar a automação do produto.")
