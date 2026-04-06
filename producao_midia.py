import requests
import streamlit as st

def gerar_video_ia(produto, roteiro, link_afiliado):
    """
    Envia os dados para o Webhook do Make.com/n8n para 
    processamento de vídeo e automação social.
    """
    webhook_url = st.secrets.get("WEBHOOK_POST_URL")
    
    if not webhook_url:
        return "❌ Erro: WEBHOOK_POST_URL não configurado nos Secrets."
    
    payload = {
        "comando": "GERAR_VIDEO_COMPLETO",
        "produto": produto,
        "roteiro": roteiro,
        "link": link_afiliado,
        "motor_video": "Veo/NanoBanana",
        "motor_audio": "Lyria 3"
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code == 200:
            return f"✅ Sucesso! Mídia para '{produto}' enviada para produção."
        else:
            return f"⚠️ Webhook recebeu, mas retornou status: {response.status_code}"
    except Exception as e:
        return f"core❌ Falha na conexão com o motor de produção: {str(e)}"
