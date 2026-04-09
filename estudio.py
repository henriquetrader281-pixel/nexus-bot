import streamlit as st
import requests
import re
import os
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import update

# --- 1. INTELIGÊNCIA DE TRENDS (API) ---
def buscar_sugestoes_musica():
    """
    Simula a busca de tendências. Para produção real, 
    conecte aqui sua API do Spotify ou TikTok via RapidAPI.
    """
    # Exemplo de retorno vindo de uma lógica de API (Viral 50 Brasil)
    trends = [
        "🎵 No Ritmo do Nexus (Slowed + Reverb)",
        "🎵 Viral Trend 2026 - Phonk Edition",
        "🎵 Chill Lofi Beats para Achadinhos",
        "🎵 Bass Boosted - Gancho de Atenção"
    ]
    return trends

# --- 2. MOTOR DE CAÇA (SCRAPER) ---
def pegar_video_shopee(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        # Limpa escapes de JSON para encontrar o link real
        links = re.findall(r'https://[^\s"\'\\]+?\.mp4', res.text.replace('\\/', '/'))
        return links[0] if links else None
    except: return None

# --- 3. MOTOR DE EDIÇÃO (PILLOW + MOVIEPY) ---
def renderizar_reels(video_path, texto):
    try:
        clip = VideoFileClip(video_path).subclip(0, 15)
        w, h = clip.size
        
        # Cria a tarja preta semi-transparente
        img = Image.new('RGBA', (w, h // 4), (0, 0, 0, 180))
        draw = ImageDraw.Draw(img)
        
        # Tenta carregar fonte padrão do Linux/Streamlit ou fallback
        try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 25)
        except: font = ImageFont.load_default()
        
        # Quebra de linha para a legenda não vazar
        linhas = [texto[i:i+35] for i in range(0, len(texto), 35)]
        draw.text((20, 20), "\n".join(linhas[:3]), font=font, fill="white")
        
        legenda_img = ImageClip(np.array(img)).set_duration(clip.duration).set_position(('center', 'bottom'))
        
        output = "reels_finalizado.mp4"
        CompositeVideoClip([clip, legenda_img]).write_videofile(output, fps=24, codec="libx264", audio_codec="aac")
        return output
    except Exception as e:
        st.error(f"Erro na edição: {e}")
        return None

# --- 4. INTERFACE DO ESTÚDIO ---
def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio Nexus: Produção de Elite")

    # --- BLOCO 1: CAPTURA DO BRUTO ---
    with st.container(border=True):
        st.markdown("#### 🛰️ Passo 1: Obter Vídeo do Produto")
        link_auto = st.session_state.get('sel_link', '')
        url_input = st.text_input("🔗 Link da Shopee:", value=link_auto)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🛰️ CAPTURAR PELO LINK", width='stretch'):
                with st.spinner("Rastreando..."):
                    link_video = pegar_video_shopee(url_input)
                    if link_video:
                        st.session_state.video_path = link_video
                        st.success("🎯 Vídeo localizado!")
                    else:
                        st.error("❌ Link protegido. Use o Upload abaixo.")
        
        with col2:
            arquivo_manual = st.file_uploader("📤 Ou faça Upload Manual:", type=["mp4"])
            if arquivo_manual:
                with open("temp_upload.mp4", "wb") as f:
                    f.write(arquivo_manual.getbuffer())
                st.session_state.video_path = "temp_upload.mp4"

    # --- BLOCO 2: INTELIGÊNCIA DE TRENDS ---
    st.divider()
    with st.expander("🎵 Consultar Músicas Virais (Trends do Dia)", expanded=False):
        st.write("Use estas músicas no Instagram/TikTok para aumentar o alcance:")
        for trend in buscar_sugestoes_musica():
            st.info(trend)

    # --- BLOCO 3: EDIÇÃO E RENDER ---
    if "video_path" in st.session_state:
        st.video(st.session_state.video_path)
        
        copy_base = st.session_state.get("copy_ativa", "🔥 Confira essa oferta incrível!")
        
        with st.container(border=True):
            st.markdown("#### 📝 Refino da Legenda")
            legenda = st.text_area("Texto que aparecerá no vídeo:", value=copy_base, height=150)
            
            if st.button("💎 ADICIONAR GATILHO MANYCHAT"):
                gatilho = "\n\n🔥 Comenta 'EU QUERO' que te envio o link agora! 🚀"
                if gatilho not in legenda:
                    legenda += gatilho
                    st.session_state.copy_ativa = legenda
                    st.rerun()

        if st.button("⚡ GERAR REELS FINAL COM LEGENDA", type="primary", width='stretch'):
            with st.spinner("O Nexus está editando seu vídeo..."):
                final = renderizar_reels(st.session_state.video_path, legenda)
                if final:
                    st.balloons()
                    with open(final, "rb") as f:
                        st.download_button("📥 BAIXAR REELS PRONTO", f, file_name="reels_viral_nexus.mp4", width='stretch')

    # --- BLOCO 4: DASHBOARD ---
    st.divider()
    if st.button("🚀 SALVAR NO RAIO-X E FINALIZAR", width='stretch'):
        nome = st.session_state.get('sel_nome', 'Produto').split('|')[0]
        update.aplicar_seo_viral(nome, url_input, "Shopee")
        st.success("✅ Salvo no Dashboard com sucesso!")
