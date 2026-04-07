import streamlit as st

def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio de Edição Nexus | Retenção & AIDA 🔱")
    
    # 1. VERIFICAÇÃO DE SEGURANÇA (Dentro da função)
    if "sel_nome" not in st.session_state or not st.session_state.sel_nome:
        st.warning("⚠️ Nenhum produto selecionado! Vá ao SCANNER e clique em 'Selecionar'.")
        return # Para a execução aqui se não houver produto

    # Se chegou aqui, temos um produto!
    produto_bruto = st.session_state.sel_nome
    # Limpa o nome para o Gemini focar só no objeto (Ex: Peneira de Arroz)
    produto_foco = produto_bruto.split('|')[0].replace("NOME:", "").strip()

    # --- BLOCO AIDA (CONVERSÃO) ---
    with st.container(border=True):
        st.markdown(f"#### 🎯 Estratégia de Venda: {produto_foco}")
        
        if st.button("🔥 GERAR LEGENDA AIDA + LINK BLINDADO", use_container_width=True):
            with st.spinner("Gemini Plus isolando produto e criando copy de impacto..."):
                
                prompt_aida = f"""
                Ignore listas. Foque APENAS no produto: {produto_foco}.
                Crie uma legenda AIDA (Atenção, Interesse, Desejo, Ação).
                - Use gatilhos de retenção.
                - Sem dados técnicos.
                - Curto e viral.
                """
                
                copy_gerada = miny.minerar_produtos(prompt_aida, "Shopee", motor_ia)
                
                # Blindagem do Link (ID: 18316451024)
                link_original = st.session_state.get('sel_link', 'https://shopee.com.br')
                link_limpo = link_original.split('?')[0].split('|')[0].strip()
                if "https" not in link_limpo: link_limpo = f"https://shopee.com.br/search?keyword={produto_foco.replace(' ', '+')}"
                
                link_final = f"{link_limpo}?smtt=18316451024"
                st.session_state.copy_final_pronta = f"{copy_gerada.strip()}\n\n🛒 **LINK COM DESCONTO:** {link_final}"

        if "copy_final_pronta" in st.session_state:
            st.text_area("Munição de Elite:", value=st.session_state.copy_final_pronta, height=200)
            if st.button("📋 Copiar para Postagem"):
                st.toast("Copiado!")

    st.divider()

    # --- BLOCO RETENÇÃO (EDIÇÃO VÍDEO) ---
    st.markdown("#### ⚡ Radar de Retenção e Edição")
    if st.button("🧠 BUSCAR ESTRATÉGIA DE VÍDEO VIRAL", use_container_width=True):
        with st.spinner("Analisando padrões de retenção..."):
            prompt_video = f"Crie um roteiro de 15 segundos para {produto_foco}. Foque em 3s de Hook agressivo e 12s de demonstração satisfatória."
            st.session_state.roteiro_video = miny.minerar_produtos(prompt_video, "Shopee", motor_ia)

    if "roteiro_video" in st.session_state:
        with st.expander("🎥 MAPA DE CORTES (CAPCUT)", expanded=True):
            st.markdown(st.session_state.roteiro_video)
