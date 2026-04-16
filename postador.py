import streamlit as st

def exibir_postador(miny=None, motor_ia=None):
    st.markdown("### 🛰️ Central de Disparo Nexus: Meta Suite")
    
    # 🔗 Recupera os dados do Arsenal e Estúdio
    copy_final = st.session_state.get('copy_final_pronta', '')
    link_blindado = st.session_state.get('link_final_afiliado', '')
    video_gerado = st.session_state.get('video_path_local', None)

    if not copy_final:
        st.warning("⚠️ O Arsenal está vazio! Gere a copy antes de postar.")
        return

    # --- ÁREA DE CONFERÊNCIA ---
    with st.container(border=True):
        st.markdown("#### 📝 Legenda Pronta para o Post")
        
        palavra_gatilho = st.text_input("Gatilho ManyChat:", value="QUERO")
        # Monta o texto final que será copiado
        texto_completo = f"{copy_final}\n\n🎁 Comente {palavra_gatilho} para receber o link com desconto oficial!"
        
        st.text_area("Prévia (Confira o link blindado):", value=texto_completo, height=180)

    # --- FLUXO DE DISPARO ---
    st.markdown("#### ⚡ Passo a Passo para Postagem")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.info("1️⃣ **Baixe o Vídeo**")
        if video_gerado:
            try:
                with open("reels_final.mp4", "rb") as f:
                    st.download_button(
                        label="📥 BAIXAR REELS PRONTO",
                        data=f,
                        file_name="nexus_reels.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
            except:
                st.error("Gere o vídeo no Estúdio primeiro.")
        else:
            st.warning("Vídeo não localizado.")

    with c2:
        st.info("2️⃣ **Copie e Poste**")
        if st.button("📋 COPIAR LEGENDA E ABRIR META", use_container_width=True):
            # O Streamlit não copia direto para o clipboard do PC por segurança, 
            # então mostramos o aviso e abrimos o link.
            st.code(texto_completo, language=None)
            st.toast("Selecione o texto acima e copie (CTRL+C)!")
            st.link_button("🚀 ABRIR PROGRAMADOR META", "https://business.facebook.com/latest/composer")

    st.divider()
    st.caption(f"🔱 Nexus V101 | Rastreio Ativo: 18316451024")
