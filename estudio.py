import streamlit as st

def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio de Edição Nexus | Retenção & AIDA 🔱")
    
    # 1. VERIFICAÇÃO: Só roda se houver um produto selecionado
    if "sel_nome" not in st.session_state or not st.session_state.sel_nome:
        st.warning("⚠️ Selecione um produto no Scanner antes de entrar no Estúdio!")
        return

    # 2. LIMPEZA DO NOME (Isola o produto da lista de 30)
    produto_limpo = st.session_state.sel_nome.split('|')[0].replace("NOME:", "").strip()

    # --- ABA DE GERAÇÃO ---
    with st.container(border=True):
        st.markdown(f"#### 🎯 Estratégia para: {produto_limpo}")
        
        if st.button("🔥 GERAR MUNIÇÃO DE ELITE (AIDA)", use_container_width=True):
            with st.spinner("Limpando ruído e gerando copy de impacto..."):
                
                # PROMPT BLINDADO: Mata a lista de 30 produtos aqui
                prompt_blindado = f"""
                [RESET DE CONTEXTO]: Ignore qualquer lista anterior.
                VOCÊ É: Especialista em Reels Virais.
                PRODUTO: {produto_limpo}
                
                TAREFA: Gere uma legenda AIDA curta e impactante.
                REGRAS: Sem listas, sem dados técnicos, comece no Hook 🚨.
                """
                
                resposta_ia = miny.minerar_produtos(prompt_blindado, "Shopee", motor_ia)
                
                # Blindagem do Link (ID: 18316451024)
                link_raw = st.session_state.get('sel_link', 'https://shopee.com.br')
                link_base = link_raw.split('?')[0].split('|')[0].strip()
                link_final = f"{link_base}?smtt=18316451024"

                st.session_state.copy_final_pronta = f"{resposta_ia.strip()}\n\n🔗 **LINK EXCLUSIVO:** {link_final}"

        # Exibe a munição se ela já foi gerada
        if "copy_final_pronta" in st.session_state:
            st.text_area("Munição Pronta:", value=st.session_state.copy_final_pronta, height=200)

    # --- MAPA DE CORTES ---
    st.divider()
    if st.button("🧠 GERAR MAPA DE CORTES (RETENÇÃO)", use_container_width=True):
        with st.spinner("Calculando tempos de cena..."):
            prompt_video = f"Crie um roteiro de 15s para {produto_limpo}. Foque em 3s de Hook e 12s de desejo visual."
            st.session_state.roteiro_video = miny.minerar_produtos(prompt_video, "Shopee", motor_ia)

    if "roteiro_video" in st.session_state:
        with st.expander("🎥 ROTEIRO DE EDIÇÃO", expanded=True):
            st.markdown(st.session_state.roteiro_video)
