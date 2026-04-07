import streamlit as st

def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio de Edição Nexus | Nível CEO")
    
    if "copy_ativa" in st.session_state:
        # Área de edição da Copy
        with st.container(border=True):
            st.markdown("#### 📝 Munição Pronta para Uso")
            copy_final = st.text_area("Refine sua legenda aqui:", 
                                     value=st.session_state.copy_ativa, 
                                     height=250)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📋 Copiar para Instagram/WhatsApp", use_container_width=True):
                    st.toast("Copiado! Basta colar na sua rede social.")
            
        st.divider()

        # SUPER IA: DIREÇÃO DE VÍDEO
        st.markdown("#### 🚀 Upgrade de Vídeo (Gemini Plus)")
        if st.button("🧠 GERAR ROTEIRO DE VÍDEO VIRAL", use_container_width=True):
            with st.spinner("Analisando padrões de viralização para este produto..."):
                
                # O Gemini vai criar a estratégia do vídeo
                prompt_estudio = f"""
                Atue como Diretor de Arte e Estrategista de TikTok/Reels.
                Produto: {st.session_state.sel_nome}
                Legenda base: {copy_final}
                
                Crie um roteiro de edição de alto nível dividido em:
                1. O GANCHO (Primeiros 3 segundos): O que deve aparecer na tela e qual texto usar.
                2. O DESENVOLVIMENTO: Como mostrar o produto (ângulos, detalhes).
                3. O CTA (Fechamento): Como pedir o clique no link.
                4. TRILHA SONORA: Que tipo de áudio usar (Trend, Urgência ou Satisfatório).
                
                Seja direto e use termos de edição (Corte seco, Zoom in, Overlay).
                """
                
                roteiro = miny.minerar_produtos(prompt_estudio, "Shopee", motor_ia)
                st.session_state.roteiro_video = roteiro

        if "roteiro_video" in st.session_state:
            with st.expander("🎥 Roteiro de Edição Estratégica (Siga isso!)", expanded=True):
                st.markdown(st.session_state.roteiro_video)
                st.info("💡 Dica: Use o CapCut para seguir essas instruções e veja sua conversão dobrar.")

    else:
        st.warning("⚠️ Nenhuma munição enviada. Vá ao Arsenal primeiro!")

def formatar_para_estudio(texto, link):
    """Garante que o link e o texto fiquem perfeitos para o Estúdio"""
    return f"{texto}\n\n🛒 COMPRE AQUI: {link}"
