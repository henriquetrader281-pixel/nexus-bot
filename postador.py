import streamlit as st

def exibir_postador(miny, motor_ia):
    st.markdown("### 🛰️ Central de Disparo Nexus")
    
    copy_final = st.session_state.get('copy_final_pronta', '')
    
    if not copy_final:
        st.warning("⚠️ Gere uma estratégia no Arsenal primeiro.")
        return

    with st.container(border=True):
        palavra_gatilho = st.text_input("Gatilho ManyChat:", value="QUERO")
        texto_completo = f"{copy_final}\n\n🎁 Comente {palavra_gatilho} para receber o link!"
        st.text_area("Legenda Blindada:", value=texto_completo, height=180)

    st.info("🚀 **POSTAGEM SEGURA (ZERO CUSTO)**")
    
    col1, col2 = st.columns(2)
    with col1:
        # Botão para baixar o vídeo novamente se precisar
        st.download_button("📥 1. BAIXAR VÍDEO", "video_data", file_name="reels.mp4", use_container_width=True)
    with col2:
        # Botão que abre a Meta e avisa que copiou
        if st.button("📋 2. COPIAR E ABRIR META", use_container_width=True):
            st.session_state.legenda_copiada = texto_completo
            st.link_button("ABRIR PROGRAMADOR OFICIAL", "https://business.facebook.com/latest/composer")
            st.toast("Legenda copiada! Cole no post.")

    st.success("✅ Sistema configurado para o Afiliado 18316451024")
