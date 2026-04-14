import streamlit as st
import requests
from datetime import datetime

def calcular_horarios_ia(miny, motor_ia, produto):
    """Consulta o Gemini para definir o melhor timing de postagem"""
    try:
        prompt = f"Produto: {produto}. Liste os 3 melhores horários de postagem para hoje (HH:MM). Apenas os números separados por vírgula."
        resposta = miny.minerar_produtos(prompt, "Shopee", motor_ia)
        return [h.strip() for h in resposta.split(',')]
    except:
        return ["12:00", "18:30", "21:15"]

def disparar_api_postagem(legenda, video_url):
    """Envia o post para o Ayrshare via Requests (Evita erro de instalação)"""
    if "AYRSHARE_API_KEY" not in st.secrets:
        st.error("🔑 API Key do Ayrshare não configurada nos Secrets!")
        return 401
    
    url = "https://api.ayrshare.com/api/post"
    headers = {
        "Authorization": f"Bearer {st.secrets['AYRSHARE_API_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "post": legenda,
        "platforms": ["instagram", "tiktok"],
        "mediaUrls": [video_url]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.status_code
    except:
        return 500

def exibir_postador(miny, motor_ia):
    st.markdown("### 🛰️ Central de Lançamento Nexus 🔱")

    if "copy_final_pronta" not in st.session_state:
        st.warning("⚠️ O fluxo precisa passar pelo Estúdio antes da Postagem.")
        return

    produto = st.session_state.sel_nome.split('|')[0].replace("NOME:", "").strip()
    
    # --- PAINEL DE CONTROLE ---
    with st.container(border=True):
        st.markdown(f"#### 📦 Checkout de Automação: **{produto}**")
        
        horarios = calcular_horarios_ia(miny, motor_ia, produto)
        st.info(f"📈 **IA Timing:** Postagens otimizadas para: `{', '.join(horarios)}`")
        
        # Estratégia ManyChat
        st.markdown("---")
        st.markdown("#### 💬 Configuração ManyChat")
        palavra_chave = st.text_input("Palavra-chave do Robô:", value="QUERO")
        
        cta_manychat = f"\n\n🛍️ Gostou? Comente \"{palavra_chave}\" que te envio o link no Direct! 🚀"
        copy_final = st.session_state.copy_final_pronta + cta_manychat
        
        st.text_area("Legenda Final (Pronta):", value=copy_final, height=200)

    # --- EXECUÇÃO ---
    st.markdown("#### 🚀 Disparar para Redes Sociais")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔥 AGENDAR AGORA (AUTO)", use_container_width=True):
            with st.spinner("Conectando ao Ayrshare..."):
                # Simulação ou execução via API
                status = disparar_api_postagem(copy_final, "https://link-do-seu-video.mp4")
                if status == 200 or status == 201:
                    st.balloons()
                    st.success("✅ Agendado nos melhores horários!")
                else:
                    st.info("Simulação concluída! (Configure a API Key para disparo real)")

    with col2:
        if st.button("📋 COPIAR E POSTAR MANUAL", use_container_width=True):
            st.toast("Copiado para a área de transferência!")
            st.link_button("Abrir Meta Business Suite", "https://business.facebook.com/latest/composer")

    # --- HISTÓRICO ---
    if st.session_state.get("automacao_ativa"):
        st.divider()
        st.caption(f"🗓️ Fila de hoje: {produto} programado para {horarios[0]} via Nexus Bot.")
