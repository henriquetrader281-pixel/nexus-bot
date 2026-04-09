import streamlit as st
import requests
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import update

# --- 1. INTELIGÊNCIA DE CONVERSÃO (Shopee ID) ---
def extrair_dados_shopee(url):
    """Extrai o ID do produto e prepara para o ID de Afiliado 18316451024"""
    padrao = r'i\.(\d+)\.(\d+)'
    resultado = re.search(padrao, url)
    if resultado:
        shop_id = resultado.group(1)
        product_id = resultado.group(2)
        # Gera um link de referência limpo para o Raio-X
        link_afiliado = f"https://shopee.com.br/product/{shop_id}/{product_id}"
        return product_id, link_afiliado
    return "N/A", url

# --- 2. TRENDS DO SPOTIFY ---
def buscar_trends_spotify():
    try:
        client_id = st.secrets["spotify"]["client_id"]
        client_secret = st.secrets["spotify"]["client_secret"]
        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(auth_manager=auth_manager)
        results = sp.playlist_tracks('37i9dQZEVXbMOYmS0tVvbi', limit=6)
        
        musicas = []
        for item in results['items']:
            track = item['track']
            musicas.append({
                "nome": f"{track['name']} - {track['artists'][0]['name']}",
                "url": track['external_urls']['spotify'],
                "capa": track['album']['images'][0]['url']
            })
        return musicas
    except: return []

# --- 3. MOTOR DE RENDERIZAÇÃO ---
def renderizar_reels(video_path, texto):
    clip = VideoFileClip(video_path).subclip(0, 15)
    w, h = clip.size
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

# --- 4. INTERFACE ---
def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Central de Produção Nexus Absolute")

    aba_video, aba_trends = st.tabs(["🎥 Criar Vídeo", "📈 Nexus Trends"])

    with aba_trends:
        st.markdown("#### 🔥 Músicas Virais Hoje")
        musicas = buscar_trends_spotify()
        if musicas:
            for m in musicas:
                with st.container(border=True):
                    col1, col2 = st.columns([1, 3])
                    with col1: st.image(m['capa'], width=70)
                    with col2:
                        st.markdown(f"**{m['nome']}**")
                        st.link_button("🎧 Ouvir", m['url'])
                        if st.button("🎯 Usar esta", key=m['nome']):
                            st.session_state.musica_selecionada = m['nome']
                            st.toast(f"Selecionada: {m['nome']}")
        else: st.warning("Conecte o Spotify nos Secrets para ver as trends.")

    with aba_video:
        with st.container(border=True):
            link_auto = st.session_state.get('sel_link', '')
            url_input = st.text_input("🔗 Link da Shopee:", value=link_auto)
            
            # Extração Automática de ID
            id_prod, link_limpo = extrair_dados_shopee(url_input)
            if id_prod != "N/A":
                st.caption(f"🆔 ID Detectado: {id_prod} | 🔗 Pronto para Afiliado: 18316451024")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🛰️ CAPTURAR VÍDEO", width='stretch'):
                    headers = {"User-Agent": "Mozilla/5.0"}
                    res = requests.get(url_input, headers=headers)
                    links = re.findall(r'https://[^\s"\'\\]+?\.mp4', res.text.replace('\\/', '/'))
                    if links:
                        st.session_state.video_path = links[0]
                        st.success("🎯 Vídeo localizado!")
                    else: st.error("❌ Link bloqueado. Use o upload manual.")
            with col_b:
                arq = st.file_uploader("📤 Upload Manual:", type=["mp4"])
                if arq:
                    with open("temp.mp4", "wb") as f: f.write(arq.getbuffer())
                    st.session_state.video_path = "temp.mp4"

        if "video_path" in st.session_state:
            st.video(st.session_state.video_path)
            musica = st.session_state.get('musica_selecionada', 'Selecione na aba Trends')
            st.info(f"🎵 **Trilha:** {musica}")
            
            copy_base = st.session_state.get("copy_ativa", "")
            legenda = st.text_area("📝 Legenda do Vídeo:", value=copy_base)

            if st.button("⚡ GERAR REELS FINAL", type="primary", width='stretch'):
                with st.spinner("Renderizando..."):
                    final = renderizar_reels(st.session_state.video_path, legenda)
                    if final:
                        st.balloons()
                        with open(final, "rb") as f:
                            st.download_button("📥 BAIXAR REELS PRONTO", f, file_name="reels_nexus.mp4")

        st.divider()
        if st.button("🚀 SALVAR NO RAIO-X"):
            nome = st.session_state.get('sel_nome', 'Produto').split('|')[0]
            # Salva já com o ID do produto e a tag de afiliado
            update.aplicar_seo_viral(nome, link_limpo, f"ID:{id_prod} | {st.session_state.get('musica_selecionada', 'Trend')}")
            st.success(f"✅ Registrado para o Afiliado 18316451024!")
