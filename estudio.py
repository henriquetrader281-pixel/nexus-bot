import streamlit as st
import requests
import re
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
import nexus_copy as nxcopy
import update

# --- 1. MOTOR DE CAPTURA ---
def caçar_video_shopee(url_produto):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        res = requests.get(url_produto, headers=headers, timeout=10)
        # Tenta localizar MP4 no código (limpa escapes de JSON)
        links = re.findall(r'https://[^\s"\'\\]+?\.mp4', res.text.replace('\\/', '/'))
        if links: return links[0]
        return None
    except: return None

# --- 2. MOTOR DE EDIÇÃO (Aura de Viral) ---
def renderizar_final(video_path, texto):
    try:
        clip = VideoFileClip(video_path).subclip(0, 15) # Limita a 15s para Reels
        w, h = clip.size
        
        # Cria a tarja preta semi-transparente
        img = Image.new('RGBA', (w, h // 4), (0, 0, 0, 180))
        draw = ImageDraw.Draw(img)
        try: 
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
        except: 
            font = ImageFont.load_default()
        
        # Quebra de linha automática para o texto
        linhas = [texto[i:i+35] for i in range(0, len(texto), 35)]
        draw.text((20, 20), "\n".join(linhas[:3]), font=font, fill="white")
        
        legenda_img = ImageClip(np.array(img)).set_duration(clip.duration).set_position(('center', 'bottom'))
        
        output = "reels_final_nexus.mp4"
        CompositeVideoClip([clip, legenda_img]).write_videofile(output, fps=24, codec="libx264", audio_codec="aac")
        return output
    except Exception as e:
        st.error(f"Erro na renderização: {e}")
        return None

# --- 3. INTERFACE (O QUE MUDOU AFINAL) ---
def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio Nexus: Captura & Edição")

    # 💡 NOVA MELHORIA: Selector de Método
    metodo = st.radio("Como queres o vídeo do produto?", ["🛰️ Automático (URL)", "📤 Upload Manual (PC/Telemóvel)"], horizontal=True)

    caminho_video = None

    if metodo == "🛰️ Automático (URL)":
        # Puxa o link do Scanner automaticamente
        link_origem = st.session_state.get('sel_link', '')
        url_input = st.text_input("Link do Produto:", value=link_origem)
        
        if st.button("🛰️ INICIAR CAÇA"):
            with st.spinner("Rastreando..."):
                link_mp4 = caçar_video_shopee(url_input)
                if link_mp4:
                    st.session_state.video_ativo = link_mp4
                    st.success("🎯 Vídeo localizado!")
                else:
                    st.error("A Shopee bloqueou o robô. Usa o 'Upload Manual' abaixo.")

    else:
        # 💡 NOVA MELHORIA: Upload de arquivo que tu baixaste
        arquivo = st.file_uploader("Sobe o vídeo bruto que descarregaste:", type=["mp4", "mov"])
        if arquivo:
            with open("temp_video.mp4", "wb") as f:
                f.write(arquivo.getbuffer())
            st.session_state.video_ativo = "temp_video.mp4"
            st.success("✅ Vídeo pronto para edição!")

    # --- ÁREA DE EDIÇÃO ---
    if "video_ativo" in st.session_state:
        st.video(st.session_state.video_ativo)
        
        # Puxa a copy do Arsenal
        copy_base = st.session_state.get("copy_ativa", "")
        
        with st.container(border=True):
            st.markdown("#### 📝 Ajuste de Legenda")
            legenda_final = st.text_area("Texto que aparecerá no vídeo:", value=copy_base, height=150)
            
            if st.button("💎 ADICIONAR GATILHO MANYCHAT"):
                gatilho = "\n\n🔥 Comenta 'EU QUERO' que te envio o link! 🚀"
                if gatilho not in legenda_final:
                    legenda_final += gatilho
                    st.session_state.copy_ativa = legenda_final
                    st.rerun()

        if st.button("⚡ RENDERIZAR REELS FINAL", type="primary", width='stretch'):
            with st.spinner("O Nexus está a criar o teu Reels..."):
                resultado = renderizar_final(st.session_state.video_ativo, legenda_final)
                if resultado:
                    st.balloons()
                    with open(resultado, "rb") as f:
                        st.download_button("📥 DESCARREGAR REELS PRONTO", f, file_name="reels_nexus.mp4", width='stretch')

    # --- SALVAR NO DASHBOARD ---
    st.divider()
    if st.button("🚀 SALVAR NO RAIO-X E FINALIZAR", width='stretch'):
        nome = st.session_state.get('sel_nome', 'Produto').split('|')[0]
        link = st.session_state.get('sel_link', '#')
        if update.aplicar_seo_viral(nome, link, "Shopee"):
            st.success("✅ Registado no Dashboard de Performance!")
