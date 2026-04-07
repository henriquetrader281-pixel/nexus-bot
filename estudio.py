import streamlit as st

def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio de Edição Nexus | Retenção & AIDA 🔱")
    
    # 1. VERIFICAÇÃO DE SEGURANÇA: Só roda se houver um produto no Scanner
    if "sel_nome" not in st.session_state or not st.session_state.sel_nome:
        st.warning("⚠️ Nenhum produto selecionado! Vá ao SCANNER e clique em 'Selecionar'.")
        return

    # 2. ISOLAMENTO DO PRODUTO (Mata a lista de 30 produtos aqui)
    # Pega apenas o nome antes do primeiro pipe '|'
    produto_foco = st.session_state.sel_nome.split('|')[0].replace("NOME:", "").strip()

    # --- BLOCO 1: MUNIÇÃO DE ELITE (COPY AIDA) ---
    with st.container(border=True):
        st.markdown(f"#### 🎯 Estratégia de Venda: **{produto_foco}**")
        
        if st.button("🔥 GERAR MUNIÇÃO AIDA + LINK BLINDADO", use_container_width=True):
            with st.spinner("Limpando ruído e gerando copy de impacto..."):
                
                # PROMPT DE CHOQUE: Força a IA a esquecer o histórico e focar no AIDA
                prompt_blindado = f"""
                [RESET DE CONTEXTO]: Ignore qualquer lista de 30 produtos anterior.
                VOCÊ É: Um Diretor de Conversão e Copywriter Sênior.
                PRODUTO ÚNICO: {produto_foco}

                TAREFA: Gere uma legenda seguindo o método AIDA.
                REGRAS CRÍTICAS:
                - PROIBIDO listar outros produtos.
                - PROIBIDO repetir dados como 'CALOR' ou 'VALOR'.
                - Comece direto no Hook com emoji 🚨.
                
                FORMATO:
                🚨 [ATENÇÃO]: Hook agressivo.
                💡 [INTERESSE]: Problema/Curiosidade.
                ✨ [DESEJO]: Benefício transformador.
                🛒 [AÇÃO]: Chamada para o link.
                """
                
                # Chamada da IA
                resultado_ia = miny.minerar_produtos(prompt_blindado, "Shopee", motor_ia)
                
                # 3. BLINDAGEM DO LINK (ID: 18316451024)
                link_raw = st.session_state.get('sel_link', 'https://shopee.com.br')
                # Limpa https duplicado ou parâmetros antigos
                link_limpo = link_raw.split('?')[0].split('|')[0].strip()
                if "https" not in link_limpo: 
                    link_limpo = f"https://shopee.com.br/search?keyword={produto_foco.replace(' ', '+')}"
                
                link_afiliado = f"{link_limpo}?smtt=18316451024"

                # Salva na sessão
                st.session_state.copy_final_pronta = f"{resultado_ia.strip()}\n\n🔗 **LINK EXCLUSIVO:** {link_afiliado}"
                st.rerun()

        # Exibe a munição pronta
        if "copy_final_pronta" in st.session_state:
            st.text_area("Copiou, Colou, Vendeu:", value=st.session_state.copy_final_pronta, height=220)
            if st.button("📋 Marcar como Pronto"):
                st.toast("Munição pronta para o campo de batalha!")

    st.divider()

    # --- BLOCO 2: MAPA DE RETENÇÃO (ROTEIRO) ---
    st.markdown("#### ⚡ Radar de Retenção (Instruções de Edição)")
    
    if st.button("🧠 GERAR ROTEIRO DE CORTES RÁPIDOS", use_container_width=True):
        with st.spinner("Calculando ganchos visuais..."):
            prompt_video = f"""
            Crie um roteiro de edição VIRAL de 15s para {produto_foco}.
            Divida em:
            0-3s: O Hook (O que escrever na tela para parar o scroll?)
            3-12s: O Desejo (Que cenas mostrar?)
            12-15s: O CTA (Como pedir o clique?)
            """
            st.session_state.roteiro_video = miny.minerar_produtos(prompt_video, "Shopee", motor_ia)
            st.rerun()

    if "roteiro_video" in st.session_state:
        with st.expander("🎥 MAPA DE CORTES (SIGA ISSO NO CAPCUT)", expanded=True):
            st.markdown(st.session_state.roteiro_video)
            st.info("
