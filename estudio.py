import streamlit as st

def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio de Edição Nexus | Retenção & AIDA 🔱")
    
    # 1. SEGURANÇA: Verifica se existe produto selecionado
    if "sel_nome" not in st.session_state or not st.session_state.sel_nome:
        st.warning("⚠️ Selecione um produto no Scanner antes de entrar no Estúdio!")
        return

    # 2. LIMPEZA: Isola o nome do produto para a IA não se perder
    produto_foco = st.session_state.sel_nome.split('|')[0].replace("NOME:", "").strip()

    # --- CONTAINER DA LEGENDA ---
    with st.container(border=True):
        st.markdown(f"#### 🎯 Estratégia: **{produto_foco}**")
        
        if st.button("🔥 GERAR MUNIÇÃO AIDA + LINK", use_container_width=True):
            with st.spinner("Refinando copy e blindando link..."):
                
                # PROMPT CURTO (Economiza tokens/dinheiro)
                prompt_aida = f"""
                Ignore o histórico. Foque APENAS no produto: {produto_foco}.
                Gere uma legenda AIDA (Atenção, Interesse, Desejo, Ação).
                Regras: Direto ao ponto, use emojis, sem introduções.
                """
                
                try:
                    resultado = miny.minerar_produtos(prompt_aida, "Shopee", motor_ia)
                    
                    # Blindagem do Link (ID: 18316451024)
                    link_raw = st.session_state.get('sel_link', 'https://shopee.com.br')
                    link_base = link_raw.split('?')[0].split('|')[0].strip()
                    link_final = f"{link_base}?smtt=18316451024"

                    st.session_state.copy_final_pronta = f"{resultado.strip()}\n\n🛒 **COMPRE AQUI:** {link_final}"
                    st.rerun()
                except Exception as e:
                    st.error(f"Aguarde o reset da IA: {str(e)}")

        # Exibição da copy gerada
        if "copy_final_pronta" in st.session_state:
            st.text_area("Sua munição:", value=st.session_state.copy_final_pronta, height=200)

    st.divider()

    # --- CONTAINER DO ROTEIRO ---
    st.markdown("#### 🎥 Mapa de Cortes (Retenção)")
    if st.button("🧠 GERAR ROTEIRO PARA VÍDEO", use_container_width=True):
        with st.spinner("Criando mapa de cenas..."):
            prompt_video = f"Crie um roteiro de 15s para {produto_foco}. Foque em 3s de Hook e 12s de demonstração."
            try:
                st.session_state.roteiro_video = miny.minerar_produtos(prompt_video, "Shopee", motor_ia)
                st.rerun()
            except:
                st.error("IA em resfriamento. Tente em instantes.")

    if "roteiro_video" in st.session_state:
        with st.expander("🎞️ ROTEIRO CAPCUT", expanded=True):
            st.markdown(st.session_state.roteiro_video)
