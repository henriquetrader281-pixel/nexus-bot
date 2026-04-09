import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def buscar_musicas_reais():
    try:
        client_id = st.secrets["spotify"]["client_id"]
        client_secret = st.secrets["spotify"]["client_secret"]
        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        # Viral 50 Brasil
        results = sp.playlist_tracks('37i9dQZEVXbMOYmS0tVvbi', limit=10)
        
        musicas = []
        for item in results['items']:
            track = item['track']
            musicas.append({
                "nome": f"{track['name']} - {track['artists'][0]['name']}",
                "url": track['external_urls']['spotify'],
                "capa": track['album']['images'][0]['url']
            })
        return musicas
    except:
        return []

def exibir_trends():
    st.markdown("## 📈 Nexus Trends: Inteligência Viral")
    st.write("Selecione a música que está bombando para usar no seu vídeo.")

    musicas = buscar_musicas_reais()

    if musicas:
        for m in musicas:
            with st.container(border=True):
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.image(m['capa'], width=80)
                with col2:
                    st.markdown(f"**{m['nome']}**")
                    st.link_button("🎧 Ouvir no Spotify", m['url'])
                    
                    if st.button(f"🎯 Usar no Estúdio", key=m['nome']):
                        st.session_state.musica_selecionada = m['nome']
                        st.success(f"Pronto! A trilha '{m['nome']}' foi enviada para o Estúdio.")
    else:
        st.warning("Configure as chaves do Spotify nos Secrets para ver as tendências.")
