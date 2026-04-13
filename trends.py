import streamlit as st
import requests

# Cache de 24h para economizar seus 150 créditos
@st.cache_data(ttl=86400)
def buscar_trends_insta_120(api_key, api_host):
    url = f"https://{api_host}/v1/trending_reels" # Verifique se o endpoint é este no painel
    
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": api_host
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

def exibir_trends():
    st.header("📈 Nexus Trends: Instagram 120")
    
    if "rapidapi" not in st.secrets:
        st.error("Chave 'rapidapi' não encontrada nos Secrets.")
        return

    # Botão de emergência para resetar o cache
    if st.sidebar.button("🔄 Resetar Trends (-1 Crédito)"):
        st.cache_data.clear()
        st.rerun()

    dados = buscar_trends_insta_120(
        st.secrets["rapidapi"]["api_key"], 
        st.secrets["rapidapi"]["api_host"]
    )

    if dados:
        st.success("Dados carregados via Instagram 120 (Cache Ativo 🛡️)")
        
        # O JSON dessa API costuma vir em 'data' ou 'reels'
        items = dados.get('data', [])[:10]
        
        for item in items:
            with st.container(border=True):
                col1, col2 = st.columns([1, 4])
                # Tenta pegar a capa do vídeo ou usa um ícone
                capa = item.get('display_url', "https://cdn-icons-png.flaticon.com/512/174/174855.png")
                col1.image(capa, width=80)
                
                with col2:
                    # Extrai info da música
                    music = item.get('music_info', {})
                    titulo = music.get('title', 'Áudio Viral')
                    st.markdown(f"**🎵 {titulo}**")
                    
                    if st.button(f"🎯 Usar no Estúdio", key=f"sel_{titulo}"):
                        st.session_state.musica_selecionada = titulo
                        st.toast(f"Áudio '{titulo}' pronto para o vídeo!")
    else:
        st.warning("Nenhum dado retornado. Verifique se o endpoint está correto na RapidAPI.")
