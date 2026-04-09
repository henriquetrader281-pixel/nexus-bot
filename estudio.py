import streamlit as st
import requests
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import update

# --- 1. INTELIGÊNCIA DE TRENDS (API SPOTIFY) ---
def buscar_sugestoes_musica():
    try:
        client_id = st.secrets["spotify"]["client_id"]
        client_secret = st.secrets["spotify"]["client_secret"]
        
        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        # Playlist Viral 50 Brasil
        results = sp.playlist_tracks('37i9dQZEVXbMOYmS0tVvbi', limit=5)
        
        lista_musicas = []
        for item in results['items']:
            track = item['track']
            lista_musicas.append({
                "nome": f"🎵 {track['name']} - {track['artists'][0]['name']}",
                "url": track['external_urls']['spotify']
            })
        return lista_musicas
    except:
        return [{"nome": "🎵 Música Viral (Verificar Manual)", "url": "#"}]

# --- 2. MOTOR DE EDIÇÃO (GERADOR DE REELS) ---
def renderizar_reels(video_path, texto):
    try:
        clip = VideoFileClip(video_path).subclip(0, 15)
        w, h = clip.size
        # Tarja de legenda
        img = Image.new('RGBA', (w, h // 4), (0, 0, 0, 180))
        draw = ImageDraw.Draw(img)
        try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 25)
        except: font = ImageFont.load_default()
        
        linhas = [texto[i:i+35] for i in range(0, len(texto), 35)]
        draw.text((20, 20), "\n".join(linhas[:3]), font=font, fill="white")
        
        legenda = ImageClip(np.array(img)).set_duration(clip.duration).set_position(('center', 'bottom'))
        output = "reels_final.mp4"
        CompositeVideoClip([clip, legenda]).write_videofile(output, fps=24, codec="libx264")
        return output
    except Exception as e:
        st.error(f"Erro na edição: {e}")
        return None

# --- 3. INTERFACE DO ESTÚDIO ---
def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio de Produção Automática")

    # PASSO 1: CAPTURA
    with st.container(border=True):
        st.markdown("#### 🔍 1. Obter Vídeo Bruto")
        link_origem = st.session_state.get('sel_link', '')
        url_input = st.text_input("Link do Produto:", value=link_origem)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🛰️ CAPTURAR PELO LINK", width='stretch'):
                headers = {"User-Agent": "Mozilla/5.0"}
                res = requests.get(url_input, headers=headers)
                links = re.findall(r'https://[^\s"\'\\]+?\.mp4', res.text.replace('\\/', '/'))
                if links:
                    st.session_state.video_path = links[0]
                    st.success("🎯 Vídeo localizado!")
                else: st.error("❌ Link bloqueado. Use o upload manual.")
        
        with col2:
            arq = st.file_uploader("📤 Ou faça Upload:", type=["mp4"])
            if arq:
                with open("temp.mp4", "wb") as f: f.write(arq.getbuffer())
                st.session_state.video_path = "temp.mp4"

    # PASSO 2: TRENDS
    st.divider()
    with st.expander("🎵 Escolher Trilha Viral", expanded=True):
        musicas = buscar_sugestoes_musica()
        escolha = st.selectbox("Selecione a música:", [m['nome'] for m in musicas])
        url_ouvir = next(m['url'] for m in musicas if m['nome'] == escolha)
        if url_ouvir != "#": st.link_button(f"🎧 OUVIR: {escolha}", url_ouvir)
        st.session_state.musica_atual = escolha

    # PASSO 3: EDIÇÃO E DOWNLOAD
    if "video_path" in st.session_state:
        st.video(st.session_state.video_path)
        copy_base = st.session_state.get("copy_ativa", "🔥 Confira essa oferta!")
        legenda_final = st.text_area("Texto no vídeo:", value=copy_base)

        if st.button("⚡ GERAR REELS FINAL", type="primary", width='stretch'):
            with st.spinner("Editando..."):
                final = renderizar_reels(st.session_state.video_path, legenda_final)
                if final:
                    st.balloons()
                    with open(final, "rb") as f:
                        st.download_button("📥 BAIXAR VÍDEO PRONTO", f, file_name="reels_viral.mp4")

    # PASSO 4: REGISTRO
    st.divider()
    if st.button("🚀 SALVAR NO RAIO-X E FINALIZAR"):
        nome = st.session_state.get('sel_nome', 'Produto').split('|')[0]
        musica = st.session_state.get('musica_atual', 'Nenhuma')
        update.aplicar_seo_viral(nome, url_input, f"Música: {musica}")
        st.success("✅ Registrado com sucesso!")
