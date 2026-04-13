import os
import requests
from pathlib import Path

def schedule_post(video_path: Path, caption: str = ""):
    webhook_url = st.secrets.get("N8N_WEBHOOK_URL", "")
    
    if not webhook_url:
        return {"status": "erro", "msg": "Webhook não configurado nos Secrets"}
        
    payload = {
        "video": video_path.name,
        "caption": caption,
        "source": "Nexus Absolute V101"
    }
    
    try:
        requests.post(webhook_url, json=payload, timeout=10)
        return {"status": "sucesso"}
    except Exception as e:
        return {"status": "erro", "msg": str(e)}
