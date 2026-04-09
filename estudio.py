import streamlit as st
import requests
import re
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import update

# --- 1. FUNÇÃO DE CAÇA (TENTA O LINK) ---
def pegar_video_shopee(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        links = re.findall(r'https://[^\s"\'\\]+?\.mp4', res.text.replace('\\/', '/'))
        return links[0] if links else None
    except: return None

# --- 2. FUNÇÃO DE EDIÇÃO (COLOCA A COPY NO VÍDEO) ---
def renderizar_reels(video_path, texto):
    clip = VideoFileClip(video_path).subclip(0, 15)
    w, h = clip.size
    # Cria a tarja preta com o texto
    img = Image.new('RGBA', (w, h // 4), (0, 0, 0, 180))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 25)
    except: font = ImageFont.load_default()
    
    linhas = [texto[i:i+35] for i in range(0, len(texto), 35)]
    draw.text((20, 20), "\n".join(linhas[:3]), font=font, fill="white")
    
    legenda = ImageClip(np.array(img)).set_duration(clip.duration).set_position(('center', 'bottom'))
    output = "reels_pronto.mp4"
    CompositeVideoClip([clip, legenda]).write_videofile(output, fps=24, codec="libx264")
    return output

# --- 3. INTERFACE SIMPLIFICADA ---
def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio Nexus: Link ➔ Vídeo")

    # Puxa o link do Scanner automaticamente
    link_automatico = st.session_state.get('sel_link', '')
    url_input = st.text_input("🔗 Link do Produto (ou use o Upload abaixo):", value=link_automatico)

    video_base = None

    # Tenta pegar pelo link
    if st.button("🛰️ CAPTURAR PELO LINK"):
        link_video = pegar_video_shopee(url_input)
        if link_video:
            st.session_state.video_path = link_video
            st.success("🎯 Vídeo capturado!")
        else:
            st.error("❌ Shopee bloqueou o link. Use o botão 'Upload' abaixo.")

    # Opção de Upload (O plano B para não travar)
    arquivo_manual = st.file_uploader("📤 Ou suba o vídeo aqui (se o link falhar):", type=["mp4"])
    if arquivo_manual:
        with open("video_temp.mp4", "wb") as f:
            f.write(arquivo_manual.getbuffer())
        st.session_state.video_path = "video_temp.mp4"

    # Se tiver um vídeo, mostra e permite renderizar
    if "video_path" in st.session_state:
        st.video(st.session_state.video_path)
        copy_base = st.session_state.get("copy_ativa", "🔥 Confira essa oferta!")
        
        legenda = st.text_area("📝 Legenda do Vídeo:", value=copy_base)

        if st.button("⚡ GERAR REELS FINAL", type="primary", width='stretch'):
            with st.spinner("Criando seu Reels..."):
                final = renderizar_reels(st.session_state.video_path, legenda)
                if final:
                    st.balloons()
                    with open(final, "rb") as f:
                        st.download_button("📥 BAIXAR REELS PRONTO", f, file_name="reels_viral.mp4")

    # Botão de salvar no Dashboard
    st.divider()
    if st.button("🚀 SALVAR NO RAIO-X"):
        nome = st.session_state.get('sel_nome', 'Produto').split('|')[0]
        update.aplicar_seo_viral(nome, url_input, "Shopee")
        st.success("✅ Salvo no Dashboard!")
