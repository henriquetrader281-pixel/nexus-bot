import requests
import json

def postar_pinterest(access_token, board_id, title, description, link, image_url):
    """
    Publica um Pin diretamente na API do Pinterest.
    Endpoint oficial: https://api.pinterest.com/v5/pins
    """
    url = "https://api.pinterest.com/v5/pins"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "board_id": board_id,
        "title": title[:100],  # Limite de 100 caracteres do Pinterest
        "description": description[:500],
        "link": link,
        "media_source": {
            "source_type": "image_url",
            "url": image_url
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}
