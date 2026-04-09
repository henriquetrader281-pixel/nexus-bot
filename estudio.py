import streamlit as st
import requests
import re
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
import nexus_copy as nxcopy
import update

# --- 1. MOTOR DE CAÇA E DOWNLOAD ---
def caçar_video_shopee(url_produto):
    # Bloqueia links de busca que não funcionam para download
    if "/search" in url_produto or "keyword=" in url_produto:
        st.warning("⚠️ Isso é um link de busca. Entre no produto e copie o link real dele.")
        return None

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        res = requests.get(url_produto, headers=headers, timeout=10)
        # Procura por links .mp4 no código da página
        links = re.findall(r'https://[^\s"]+\.mp4', res.text)
        if links:
            return links[0].replace('\\u002F', '/')
        return None
    except: return None

def baixar_video(url_video):
    try:
        res = requests.get(url_video, stream=True)
        path = "video_bruto.mp4"
        with open(path, "wb") as f:
            for chunk in res.iter_content(chunk_size=1024):
                if chunk: f.write(chunk)
        return path
    except: return None

# --- 2. MOTOR DE EDIÇÃO ---
def criar_adesivo_legenda(texto, w, h):
    img = Image.new('RGBA', (w, h // 4), (0, 0, 0, 180))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 25)
    except: font = ImageFont.load_default()
    
    linhas = [texto[i:i+35] for i in range(0, len(texto), 35)]
    draw.text((20, 20), "\n".join(linhas[:3]), font=font, fill="white")
    return np.array(img)

def renderizar_final(video_path, texto):
    clip = VideoFileClip(video_path).subclip(0, 15)
    w, h = clip.size
    img_array = criar_adesivo_legenda(texto, w, h)
    legenda = ImageClip(img_array).set_duration(clip.duration).set_position(('center', 'bottom'))
    
    output = "reels_nexus_pronto.mp4"
    CompositeVideoClip([clip, legenda]).write_videofile(output, fps=24, codec="libx264")
    return output

# --- 3. INTERFACE DO ESTÚDIO ---
def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio Nexus Absolute: Automação de Vídeo")
    
    # --- PASSO 1: CAPTURA AUTOMÁTICA ---
    with st.expander("🔍 1. Rastrear Vídeo da Shopee", expanded=True):
        # Puxa o link que selecionaste no Scanner automaticamente
        link_memoria = st.session_state.get('sel_link', '')
        url_input = st.text_input("Link do Produto para Captura:", value=link_memoria)
        
        if st.button("🛰️ CAÇAR E BAIXAR VÍDEO", width='stretch'):
            with st.spinner("Rastreando vídeo nos servidores..."):
                link_mp4 = caçar_video_shopee(url_input)
                if link_mp4:
                    path = baixar_video(link_mp4)
                    if path:
                        st.session_state.video_local = path
                        st.success("Vídeo capturado com sucesso!")
                        st.video(path)
                else:
                    st.error("Não encontramos vídeo bruto neste link. Verifique se o produto tem vídeo ou tente outro vendedor.")

    # --- PASSO 2: REFINO E GATILHOS ---
    copy_ativa = st.session_state.get("copy_ativa", "")
    if copy_ativa:
        st.divider()
        with st.container(border=True):
            st.markdown("#### 📝 Refino de Legenda")
            legenda_editada = st.text_area("Ajuste sua legenda aqui:", value=copy_ativa, height=200)
            
            if st.button("💎 ADICIONAR GATILHO MANYCHAT", width='stretch'):
                gatilho = "\n\n🔥 Comenta 'EU QUERO' que te envio o link no seu Direct agora! 🚀"
                if gatilho not in legenda_editada:
                    legenda_editada += gatilho
                    st.session_state.copy_ativa = legenda_editada
                    st.rerun()
        
        # --- PASSO 3: RENDERIZAÇÃO ---
        if st.button("⚡ RENDERIZAR REELS AUTOMÁTICO", type="primary", width='stretch'):
            if "video_local" in st.session_state:
                with st.spinner("Editando vídeo com a sua copy..."):
                    video_pronto = renderizar_final(st.session_state.video_local, legenda_editada)
                    if video_pronto:
                        st.balloons()
                        with open(video_pronto, "rb") as f:
                            st.download_button("📥 BAIXAR VÍDEO PRONTO", f, file_name="reels_viral.mp4", width='stretch')
            else:
                st.warning("⚠️ Precisas de caçar o vídeo no Passo 1 primeiro!")

    # --- PASSO 4: REGISTRO NO DASHBOARD ---
    st.divider()
    if st.button("🚀 SALVAR NO RAIO-X E FINALIZAR", width='stretch'):
        # Limpeza do nome para o Dashboard não ficar com lixo visual
        nome_cru = st.session_state.get('sel_nome', 'Produto')
        nome_limpo = nome_cru.split('|')[0].replace("NOME:", "").strip()
        link_final = st.session_state.get('sel_link', '#')
        
        if update.aplicar_seo_viral(nome_limpo, link_final, "Shopee"):
            st.success("✅ Salvo no Dashboard com sucesso!")
            st.toast("Dados enviados para o Raio-X")
