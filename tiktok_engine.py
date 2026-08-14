import requests
import streamlit as st

def postar_tiktok_video(video_url, title):
    """
    Publica um vídeo no TikTok via Content Posting API.
    Requer: TIKTOK_ACCESS_TOKEN nos Secrets.
    """
    access_token = st.secrets.get("TIKTOK_ACCESS_TOKEN")
    
    if not access_token:
        return {"success": False, "error": "TIKTOK_ACCESS_TOKEN não configurado nos Secrets."}
    
    url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }
    
    payload = {
        "source": "PULL_FROM_URL",
        "video_url": video_url,
        "post_info": {
            "title": title[:150],
            "privacy_level": "PUBLIC_TO_EVERYONE",
            "disable_duet": False,
            "disable_stitch": False,
            "disable_comment": False
        }
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code in [200, 201]:
            return {"success": True, "data": res.json()}
        else:
            return {"success": False, "error": res.text}
    except Exception as e:
        return {"success": False, "error": str(e)}
