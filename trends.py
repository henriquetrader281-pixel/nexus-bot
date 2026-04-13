import streamlit as st
import requests

@st.cache_data(ttl=86400) # Cache de 24 horas
def buscar_trends_insta_120():
    if "rapidapi" not in st.secrets:
        return None
        
    api_key = st.secrets["rapidapi"]["api_key"]
    api_host = st.secrets["rapidapi"]["api_host"]
    url = f"https://{api_host}/v1/trending_reels"

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": api_host
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def exibir_trends():
    st.header("📈 Nexus Trends: Instagram 120")
    
    if st.sidebar.button("🔄 Forçar Atualização (-1 Crédito)"):
        st.cache_data.clear()
        st.rerun()

    dados = buscar_trends_insta_120()

    if dados:
        st.caption("🛡️ Cache Ativo (Dados atualizados nas últimas 24h)")
        items = dados.get('data', [])[:10]
        
        for item in items:
            with st.container(border=True):
                c1, c2 = st.columns([1, 4])
                capa = item.get('display_url', "")
                if capa: c1.image(capa, width=80)
                
                with c2:
                    music = item.get('music_info', {})
                    titulo = music.get('title', 'Áudio Viral')
                    st.markdown(f"**🎵 {titulo}**")
                    if st.button(f"🎯 Usar Áudio", key=f"trend_{titulo}"):
                        st.session_state.musica_selecionada = titulo
                        st.toast("Áudio marcado para o próximo vídeo!")
    else:
        st.error("Erro ao conectar com a API. Verifica as chaves nos Secrets.")
