import streamlit as st
import requests

# O cache faz 1 crédito durar 24 horas no seu navegador
@st.cache_data(ttl=86400)
def buscar_musicas_looter(api_key, api_host):
    # Endpoint de tendências da Instagram Looter (ajuste se o nome for diferente no painel)
    url = f"https://{api_host}/v1/reels/trending" 
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": api_host
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def exibir_trends():
    st.header("📈 Nexus Trends: Instagram Looter")
    st.write("Minerando áudios virais com limite de 150 requisições.")

    if "rapidapi" not in st.secrets:
        st.error("Configure a chave 'rapidapi' nos Secrets.")
        return

    # Botão para forçar a atualização (limpar o cache e gastar 1 crédito)
    if st.button("🔄 ATUALIZAR ONDAS VIRAIS (-1 Crédito)"):
        st.cache_data.clear()
        st.rerun()

    dados = buscar_musicas_looter(
        st.secrets["rapidapi"]["api_key"], 
        st.secrets["rapidapi"]["api_host"]
    )

    if dados:
        st.success("Tendências carregadas (em cache 🛡️)")
        # Lógica de exibição baseada no retorno da Looter
        # Ajuste as chaves ['items'] ou ['data'] conforme o JSON da API
        reels = dados.get('data', [])[:10]
        
        for reel in reels:
            with st.container(border=True):
                col1, col2 = st.columns([1, 4])
                # Imagem de capa ou ícone do Instagram
                col1.image("https://cdn-icons-png.flaticon.com/512/174/174855.png", width=60)
                with col2:
                    audio_nome = reel.get('audio_title', 'Áudio Viral')
                    st.markdown(f"**🎵 {audio_nome}**")
                    if st.button(f"🎯 Selecionar para Estúdio", key=audio_nome):
                        st.session_state.musica_selecionada = audio_nome
                        st.toast(f"Áudio '{audio_nome}' pronto para o Nexus!")
    else:
        st.info("Clique em 'Atualizar' para buscar as tendências do dia.")
