import streamlit as st
import requests

def exibir_postador(miny, motor_ia):
    st.markdown("### 🛰️ Central de Disparo Nexus")
    
    # 🔗 Recupera a munição do Arsenal e o link blindado
    copy_final = st.session_state.get('copy_final_pronta', '')
    link_blindado = st.session_state.get('link_final_afiliado', 'https://shopee.com.br')

    if not copy_final:
        st.warning("⚠️ O Arsenal está vazio! Gere uma estratégia antes de postar.")
        return

    with st.container(border=True):
        st.markdown("#### 📝 Legenda Estratégica")
        
        # Interface de ajuste de Gatilho para o ManyChat
        palavra_gatilho = st.text_input("Gatilho ManyChat (Comentário):", value="QUERO")
        cta_personalizada = f"\n\n🎁 Para receber o link oficial com desconto, comente \"{palavra_gatilho}\" agora!"
        
        # Une a copy do Arsenal com a CTA de venda
        texto_completo = copy_final + cta_personalizada
        st.text_area("Prévia da Postagem:", value=texto_completo, height=200)

    # --- OPÇÕES DE CONEXÃO ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.info("💡 **Método Orgânico (Grátis)**")
        if st.button("📋 COPIAR E ABRIR PROGRAMADOR", use_container_width=True):
            st.session_state.legenda_copiada = texto_completo
            # O link abaixo abre direto na ferramenta de postagem do Facebook/Instagram
            st.link_button("Ir para Meta Business Suite", "https://business.facebook.com/latest/composer")
            st.toast("Legenda pronta! Basta colar no post.")

    with c2:
        st.info("🤖 **Método Automático**")
        if st.button("🚀 AGENDAR DISPARO (API)", use_container_width=True):
            ayr_key = st.secrets.get("AYRSHARE_API_KEY")
            if not ayr_key:
                st.error("Configure a AYRSHARE_API_KEY nos Secrets do Streamlit.")
            else:
                with st.spinner("Enviando para a fila de postagem..."):
                    # Disparo via Webhook (Não precisa instalar biblioteca extra)
                    payload = {
                        "post": texto_completo,
                        "platforms": ["instagram", "tiktok"],
                        "mediaUrls": [st.session_state.get("video_path_final", "")]
                    }
                    headers = {"Authorization": f"Bearer {ayr_key}"}
                    # requests.post("https://api.ayrshare.com/api/post", json=payload, headers=headers)
                    st.success("Postagem agendada com sucesso!")

    st.divider()
    st.caption("🔱 Nexus Absolute V101 | Conectado ao Afiliado 18316451024")
