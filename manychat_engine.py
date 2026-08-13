import requests
import streamlit as st
import os

def disparar_webhook_manychat(produto, link_afiliado, copy_texto):
    """
    Envia um POST request para o Webhook do ManyChat ou Make.com com os dados da oferta ativa.
    """
    webhook_url = st.secrets.get("MANYCHAT_WEBHOOK_URL") or os.environ.get("MANYCHAT_WEBHOOK_URL")
    
    if not webhook_url:
        return {"success": False, "error": "URL do Webhook ManyChat não configurada nos Secrets."}
        
    payload = {
        "produto": produto,
        "link_afiliado": link_afiliado,
        "copy": copy_texto,
        "trigger": "QUERO"
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code in [200, 201]:
            return {"success": True, "response": response.text}
        else:
            return {"success": False, "error": f"Erro HTTP {response.status_code}: {response.text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
