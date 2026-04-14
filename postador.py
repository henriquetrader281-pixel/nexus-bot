import streamlit as st
import requests

def disparar_postagem_automatica(legenda, video_url):
    # Usando requests para postar via API do Ayrshare sem precisar da biblioteca
    url_api = "https://api.ayrshare.com/api/post"
    headers = {
        "Authorization": f"Bearer {st.secrets['AYRSHARE_API_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "post": legenda,
        "platforms": ["instagram", "tiktok"],
        "mediaUrls": [video_url]
    }
    
    response = requests.post(url_api, json=payload, headers=headers)
    return response.status_code

# No seu botão do Postador:
if st.button("🚀 EXECUTAR POSTAGEM"):
    status = disparar_postagem_automatica(st.session_state.copy_final_pronta, "link_do_video")
    if status == 200:
        st.success("Post agendado com sucesso!")
