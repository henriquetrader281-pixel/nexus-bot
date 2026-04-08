import streamlit as st

def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio de Edição Nexus Absolute")

    # 1. Recupera a copy vinda do Arsenal
    copy_para_editar = st.session_state.get("copy_ativa", "")

    if copy_para_editar:
        with st.container(border=True):
            st.markdown("#### 📝 Edição de Legenda (Pronta para Instagram/FB)")
            # Área de texto para você dar o toque final
            legenda_final = st.text_area("Ajuste sua legenda aqui:", value=copy_para_editar, height=200)
            
            # Botão de gatilho para o ManyChat
            if st.button("💎 Adicionar Gatilho ManyChat", width='stretch'):
                legenda_final += "\n\n🔥 Comenta 'EU QUERO' que te envio o link no Direct!"
                st.session_state.copy_ativa = legenda_final
                st.rerun()

        st.divider()

        # 2. Geração de Roteiro de Vídeo (O que falar ou mostrar no Reels)
        if st.button("📽️ GERAR ROTEIRO DE VÍDEO VIRAIL", width='stretch'):
            with st.spinner("Criando cena por cena..."):
                prompt_estudio = f"""
                Ignore saudações. Crie um roteiro de vídeo de 15 segundos para Reels/TikTok.
                Produto: {st.session_state.get('sel_nome', 'Produto')}
                Base da Copy: {legenda_final}
                Divida em: CENA 1 (Gancho), CENA 2 (Desejo), CENA 3 (CTA).
                """
                try:
                    # Usa o Gemini Pro (Estável)
                    roteiro = miny.minerar_produtos(prompt_estudio, "", "gemini-1.5-pro")
                    st.session_state.roteiro_ativo = roteiro
                except Exception as e:
                    st.error(f"Erro no Estúdio: {e}")

        if "roteiro_ativo" in st.session_state:
            with st.expander("🎬 Roteiro Tático Detalhado", expanded=True):
                st.write(st.session_state.roteiro_ativo)
    else:
        st.info("💡 Vá ao Arsenal e clique em 'Enviar ao Estúdio' para começar a produção.")
