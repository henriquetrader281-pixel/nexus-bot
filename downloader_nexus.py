import requests
import re
import os
import streamlit as st

def caçar_video_shopee(url_produto):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    try:
        # 1. Puxa o HTML da página do produto
        res = requests.get(url_produto, headers=headers, timeout=10)
        html = res.text
        
        # 2. Busca padrões de vídeo (MP4) no código da página
        # A Shopee costuma usar servidores como cv.shopee.com.br ou video.shopee.com.br
        padrao_video = re.findall(r'https://[^\s"]+\.mp4', html)
        
        if padrao_video:
            # Filtra para evitar links quebrados e pega o primeiro (geralmente o principal)
            video_url = padrao_video[0].replace('\\u002F', '/')
            return video_url
        
        return None
    except Exception as e:
        st.error(f"Erro na caça ao vídeo: {e}")
        return None

def baixar_video_temporario(url_video):
    try:
        res = requests.get(url_video, stream=True)
        path_temp = "video_bruto.mp4"
        with open(path_temp, "wb") as f:
            for chunk in res.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return path_temp
    except:
        return None
      
