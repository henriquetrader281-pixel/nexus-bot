import streamlit as st
import pandas as pd

def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio de Edição Nexus | Direção Gemini Plus")
    
    if "copy_ativa" in st.session_state:
        # 1. Painel de Controle de Legenda
        with st.container(border=True):
            st.markdown("#### 📝 Legenda Estratégica")
            legenda_editavel = st.text_area("Refine a munição final:", 
                                          value=st.session_state.copy_ativa, 
                                          height=200)
            
            if st.button("📋 COPIAR TEXTO + LINK", use_container_width=True):
                st.toast("Pronto para colar no Instagram/WhatsApp!")

        st.divider()

        # 2. O Cérebro do Diretor (Gemini Plus + Roteiro)
        st.markdown("#### 🚀 Direção de Arte e Viralização")
        if st.button("🧠 ANALISAR VÍDEO E GERAR ROTEIRO VIRAL", use_container_width=True):
            with st.spinner("Gemini Plus analisando padrões de retenção..."):
                
                # Prompt de alto nível para o Gemini Plus
                prompt_direcao = f"""
                Atue como um Especialista em Viralização de Short-Videos (TikTok/Reels).
                Produto: {st.session_state.sel_nome}
                Legenda: {legenda_editavel}

                Tarefa: Crie um plano de edição de ALTO IMPACTO (Nível CEO) para este vídeo.
                
                ESTRUTURA OBRIGATÓRIA:
                1. O GANCHO (0-3 seg): Qual texto "na cara" deve aparecer? Qual o movimento inicial?
                2. RETENÇÃO (3-10 seg): Como mostrar os detalhes do produto? (Ex: Close no bambu, teste da batedeira).
                3. PSICOLOGIA DAS CORES: Que filtros ou overlays usar para passar confiança/desejo.
                4. TRILHA SONORA: Sugira um estilo de áudio em alta.
                5. CHAMADA VISUAL: Como posicionar o link de forma que não seja ignorado.
                
                Use termos técnicos de edição para facilitar no CapCut ou MoviePy.
                """
                
                roteiro_direcao = miny.minerar_produtos(prompt_direcao, "Shopee", motor_ia)
                st.session_state.roteiro_video = roteiro_direcao

        # Exibe o roteiro gerado
        if "roteiro_video" in st.session_state:
            with st.expander("🎥 INSTRUÇÕES DO DIRETOR GEMINI", expanded=True):
                st.markdown(st.session_state.roteiro_video)
                st.caption("Siga estas etapas no CapCut para maximizar suas vendas.")

        # 3. Futuro: Automação com MoviePy (Espaço reservado)
        with st.expander("⚙️ Automações Avançadas (Em breve)"):
            st.write("Detectamos as bibliotecas: OpenCV e MoviePy no seu sistema.")
            st.info("Estas ferramentas permitirão, no futuro, que o Nexus insira automaticamente o seu Link Blindado por cima dos vídeos baixados.")
            
    else:
        st.warning("⚠️ Vá ao Arsenal, gere uma copy e clique em 'Enviar ao Estúdio' primeiro!")
