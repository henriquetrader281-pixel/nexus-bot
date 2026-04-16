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
        st.info("🤖 **Método Buffer (Ativo)**")
        if st.button("🚀 AGENDAR DISPARO (BUFFER)", use_container_width=True):
            # Recupera as novas chaves do Buffer nos Secrets
            buffer_token = st.secrets.get("BUFFER_ACCESS_TOKEN")
            profile_id = st.secrets.get("BUFFER_PROFILE_ID")
            
            if not buffer_token or not profile_id:
                st.error("Configure BUFFER_ACCESS_TOKEN e BUFFER_PROFILE_ID nos Secrets do Streamlit.")
            else:
                with st.spinner("Enviando para a fila do Buffer..."):
                    # Endpoint oficial do Buffer para criar posts
                    url = "https://api.bufferapp.com/1/updates/create.json"
                    headers = {"Authorization": f"Bearer {buffer_token}"}
                    
                    # O Buffer prefere receber os dados como Data (form-urlencoded)
                    payload = {
                        "profile_ids[]": [profile_id],
                        "text": texto_completo,
                        "media[video]": st.session_state.get("video_path_final", ""),
                        "shorten": False
                    }
                    
                    try:
                        response = requests.post(url, data=payload, headers=headers)
                        if response.status_code == 200:
                            st.success("✅ Nexus enviou a munição para a fila do Buffer!")
                            st.balloons()
                        else:
                            st.error(f"Erro no Buffer: {response.text}")
                    except Exception as e:
                        st.error(f"Falha na conexão: {e}")

    st.divider()
    st.caption("🔱 Nexus Absolute V101 | Conectado ao Afiliado 18316451024")
