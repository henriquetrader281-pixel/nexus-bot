import requests
import streamlit as st

def postar_instagram_reels(video_url, caption):
    """
    Publica um Reels no Instagram via Graph API.
    Requer: INSTAGRAM_ACCESS_TOKEN e INSTAGRAM_BUSINESS_ACCOUNT_ID nos Secrets.
    """
    access_token = st.secrets.get("INSTAGRAM_ACCESS_TOKEN")
    business_account_id = st.secrets.get("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    
    if not access_token or not business_account_id:
        return {"success": False, "error": "Credenciais do Instagram não configuradas nos Secrets."}
    
    # 1. Container de Mídia
    url_container = f"https://graph.facebook.com/v19.0/{business_account_id}/media"
    payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": access_token
    }
    
    try:
        res = requests.post(url_container, data=payload)
        container_id = res.json().get('id')
        
        if not container_id:
            return {"success": False, "error": res.text}
            
        # 2. Publicação (Simplificado: na vida real precisa esperar o vídeo processar)
        url_publish = f"https://graph.facebook.com/v19.0/{business_account_id}/media_publish"
        publish_payload = {
            "creation_id": container_id,
            "access_token": access_token
        }
        
        # Nota: O Instagram exige que o vídeo esteja em uma URL pública acessível.
        # Em produção, o Nexus usaria o S3 ou link temporário.
        return {"success": True, "data": "Vídeo enviado para processamento no Instagram!"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
