import streamlit as st
import requests
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import update

# --- 1. INTELIGÊNCIA DE CONVERSÃO & SCRAPING AVANÇADO ---
def extrair_dados_shopee(url):
    padrao = r'i\.(\d+)\.(\d+)'
    resultado = re.search(padrao, url)
    if resultado:
        shop_id = resultado.group(1)
        product_id = resultado.group(2)
        link_afiliado = f"https://shopee.com.br/product/{shop_id}/{product_id}"
        return shop_id, product_id, link_afiliado
    return None, "N/A", url

def super_scraper_video(url):
    """Simula a lógica do copiarlink para achar o vídeo escondido"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        conteudo = res.text
        
        # Tentativa 1: Link direto .mp4 (Padrão simples)
        links_diretos = re.findall(r'https://[^\s"\'\\]+?\.mp4', conteudo.replace('\\/', '/'))
        if links_diretos:
            return links_diretos[0]
            
        # Tentativa 2: Buscar por video_id (Onde os sites de download focam)
        # A Shopee guarda os vídeos em servidores MMS
        v_id_match = re.search(r'"video_id":"([^"]+)"', conteudo)
        if v_id_match:
            v_id = v_id_match.group(1)
            # URL padrão dos servidores de mídia da Shopee
            return f"https://video.shopee.com.br/api/v4/1111/mms/{v_id}.mp4"
            
        return None
    except:
        return None

# --- 2. TRENDS DO SPOTIFY (Mantido igual) ---
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

# --- 3. MOTOR DE RENDERIZAÇÃO (Mantido igual) ---
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
def exibir_estudio(miny=None, motor_ia=None):
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
        else: st.warning("Conecte o Spotify nos Secrets.")

    with aba_video:
        with st.container(border=True):
            link_auto = st.session_state.get('sel_link', '')
            url_input = st.text_input("🔗 Link da Shopee:", value=link_auto)
            
            # Extração Automática de ID
            s_id, p_id, link_limpo = extrair_dados_shopee(url_input)
            if p_id != "N/A":
                st.caption(f"🆔 ID Detectado: {p_id} | 🔗 Link Limpo Gerado")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🛰️ CAPTURAR VÍDEO (Super Scraper)", width='stretch'):
                    with st.spinner("Nexus minerando o vídeo..."):
                        video_url = super_scraper_video(url_input)
                        if video_url:
                            st.session_state.video_path = video_url
                            st.success("🎯 Vídeo localizado com sucesso!")
                        else:
                            st.error("❌ Não foi possível extrair automaticamente. Tente o upload manual.")
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
           # update.aplicar_seo_viral(nome, link_limpo, f"ID:{p_id} | {st.session_state.get('musica_selecionada', 'Trend')}")
st.success("SEO Viral preparado para o Postador!")
            st.success(f"✅ Registrado para o Afiliado 18316451024!")
