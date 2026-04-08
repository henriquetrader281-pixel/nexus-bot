import streamlit as st
import streamlit as st
import nexus_copy as nxcopy # 🔱 Nome novo aqui também

# ... (dentro da função gerar roteiro)
try:
    roteiro_bruto = miny.minerar_produtos(prompt_estudio, "", "gemini-1.5-pro")
    st.session_state.roteiro_ativo = nxcopy.limpar_copy(roteiro_bruto)
except Exception as e:
    st.error(f"Erro no motor do Estúdio: {e}")
def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio de Edição Nexus Absolute")

    # 1. Recupera a munição vinda do Arsenal
    copy_para_editar = st.session_state.get("copy_ativa", "")

    if copy_para_editar:
        with st.container(border=True):
            st.markdown("#### 📝 Refino de Legenda (Instagram/TikTok/FB)")
            
            # Área de edição manual para o toque final do humano
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

        # 2. Geração de Roteiro de Vídeo Viral (Scene-by-Scene)
        if st.button("📽️ GERAR ROTEIRO CINEMATOGRÁFICO", width='stretch'):
            with st.spinner("Gemini Plus desenhando as cenas..."):
                
                # Criamos um prompt focado em roteiro visual dentro do contexto de marketing
                nome_prod = st.session_state.get('sel_nome', 'Produto').split('|')[0]
                prompt_estudio = f"""
                Aja como Diretor de Vídeos Virais. Crie um roteiro de 15 segundos para Reels.
                Produto: {nome_prod}
                Base da Estratégia: {legenda_final}
                
                FORMATO DE SAÍDA:
                CENA 1 (0-3s) - Gancho visual e Gancho de texto.
                CENA 2 (3-10s) - Demonstração do benefício real.
                CENA 3 (10-15s) - CTA visual para o Direct.
                
                SEPARE O ROTEIRO DA LEGENDA.
                """
                
                try:
                    # Dispara para o motor Gemini Pro Estável
                    roteiro_bruto = miny.minerar_produtos(prompt_estudio, "", "gemini-1.5-pro")
                    
                    # Usa a limpeza do copy.py para tirar o "Oi" da IA
                    st.session_state.roteiro_ativo = copy.limpar_copy(roteiro_bruto)
                except Exception as e:
                    st.error(f"Erro no motor do Estúdio: {e}")

        # Exibição do Roteiro Gerado
        if "roteiro_ativo" in st.session_state:
            with st.expander("🎬 Roteiro Tático Detalhado", expanded=True):
                st.markdown(st.session_state.roteiro_ativo)
                
                if st.button("📋 COPIAR ROTEIRO COMPLETO", width='stretch'):
                    st.toast("Roteiro pronto para gravação/montagem!")
    else:
        st.info("💡 **Operação Pendente:** Vá ao Arsenal e envie uma estratégia para começar a produção aqui.")
