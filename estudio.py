import streamlit as st
import nexus_copy as nxcopy # Cérebro de limpeza e prompts
import update # Importante: Para salvar os dados no Dashboard

def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio de Edição Nexus Absolute")

    # 1. Recupera a munição vinda do Arsenal
    copy_para_editar = st.session_state.get("copy_ativa", "")

    if copy_para_editar:
        with st.container(border=True):
            st.markdown("#### 📝 Refino de Legenda (Instagram/TikTok/FB)")
            
            # Área de edição manual
            legenda_final = st.text_area(
                "Ajuste sua legenda aqui:", 
                value=copy_para_editar, 
                height=250,
                help="O ManyChat lerá este texto para responder seus clientes."
            )
            
            # 💡 Automação de Gatilho para o ManyChat
            if st.button("💎 ADICIONAR GATILHO MANYCHAT", width='stretch'):
                gatilho = "\n\n🔥 Comenta 'EU QUERO' que te envio o link no seu Direct agora! 🚀"
                if gatilho not in legenda_final:
                    legenda_final += gatilho
                    st.session_state.copy_ativa = legenda_final
                    st.rerun()

        st.divider()

        # 2. Geração de Roteiro de Vídeo Viral
        if st.button("📽️ GERAR ROTEIRO CINEMATOGRÁFICO", width='stretch'):
            with st.spinner("Desenhando as cenas com Llama 3..."):
                nome_prod = st.session_state.get('sel_nome', 'Produto').split('|')[0]
                prompt_estudio = f"""
                Aja como Diretor de Vídeos Virais. Crie um roteiro de 15 segundos para Reels.
                ###
                Produto: {nome_prod}
                Legenda Base: {legenda_final}
                ###
                FORMATO: CENA 1 (Gancho) | CENA 2 (Uso) | CENA 3 (CTA).
                """
                
                try:
                    roteiro_bruto = miny.minerar_produtos(prompt_estudio, "", motor_ia)
                    st.session_state.roteiro_ativo = nxcopy.limpar_copy(roteiro_bruto)
                except Exception as e:
                    st.error(f"Erro no roteiro: {e}")

        # Exibição do Roteiro
        if "roteiro_ativo" in st.session_state:
            with st.expander("🎬 Roteiro Tático Detalhado", expanded=True):
                st.info(st.session_state.roteiro_ativo)
        
        st.divider()

        # 3. 🎯 O BOTÃO QUE FALTAVA: SALVAR NO DASHBOARD
        st.markdown("#### 📊 Finalização e Registro")
        if st.button("🚀 SALVAR NO RAIO-X E FINALIZAR", width='stretch', type='primary'):
            with st.spinner("Registrando performance no Dashboard..."):
                produto = st.session_state.get('sel_nome', 'Produto')
                link = st.session_state.get('sel_link', '#')
                nicho = st.session_state.get('nicho_input', 'Geral')
                
                # Chama a função do update.py para gravar o CSV
                sucesso = update.aplicar_seo_viral(produto, link, nicho)
                
                if sucesso:
                    st.balloons()
                    st.success("✅ PRODUTO SALVO! Agora confira a aba DASHBOARD.")
                else:
                    st.error("Erro ao salvar. Verifique se o arquivo update.py está correto.")

    else:
        st.info("💡 **Operação Pendente:** Vá ao Arsenal e envie uma estratégia para começar a produção aqui.")
