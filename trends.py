import streamlit as st
import requests

def buscar_trends_instagram():
    try:
        # Puxa as credenciais da RapidAPI que você configurou nos Secrets
        api_key = st.secrets["rapidapi"]["api_key"]
        api_host = st.secrets["rapidapi"]["api_host"]
        
        # Endpoint para Reels em alta (Verifique o nome exato na aba Endpoints da RapidAPI)
        url = f"https://{api_host}/trending_reels" 
        
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": api_host
        }

        # Faz a chamada para a RapidAPI
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            dados = response.json()
            
            # Mapeamento dos dados do Instagram para o formato do seu Nexus
            # Nota: A estrutura do JSON varia por API, ajuste as chaves se necessário
            musicas = []
            
            # Geralmente as APIs de Instagram retornam uma lista em 'data' ou 'reels'
            items = dados.get('data', [])[:10] 
            
            for item in items:
                # Extraindo informações de áudio/música do Reel
                music_info = item.get('music_info', {})
                
                musicas.append({
                    "nome": music_info.get('title', 'Áudio Original Viral'),
                    "autor": music_info.get('display_artist', 'Instagram Trends'),
                    "url": f"https://www.instagram.com/reels/audio/{music_info.get('music_id', '')}",
                    "capa": item.get('display_url', 'https://www.instagram.com/static/images/ico/favicon-192.png/ed97e42dca57.png')
                })
            return musicas
        else:
            st.error(f"Erro na API ({response.status_code}). Verifique sua cota na RapidAPI.")
            return []
    except Exception as e:
        st.error(f"Falha técnica: {str(e)}")
        return []

def exibir_trends():
    st.markdown("## 📈 Trends: Instagram Reels")
    st.write("Identificando os áudios que estão dominando o algoritmo agora.")

    # Se não houver segredos configurados
    if "rapidapi" not in st.secrets:
        st.warning("Configure 'api_key' e 'api_host' na categoria [rapidapi] nos Secrets.")
        return

    if st.button("🚀 SCANNER DE TENDÊNCIAS", width='stretch'):
        musicas = buscar_trends_instagram()

        if musicas:
            for m in musicas:
                with st.container(border=True):
                    col1, col2 = st.columns([1, 4])
                    with col1: 
                        st.image(m['capa'], width=80)
                    with col2:
                        st.markdown(f"**{m['nome']}**")
                        st.caption(f"👤 {m['autor']}")
                        
                        c1, c2 = st.columns(2)
                        c1.link_button("🔗 Ver Trend", m['url'], use_container_width=True)
                        
                        if c2.button(f"🎯 Usar no Estúdio", key=f"trend_{m['nome']}", use_container_width=True):
                            st.session_state.musica_selecionada = m['nome']
                            st.success(f"Áudio selecionado para o Nexus!")
        else:
            st.info("Nenhuma tendência encontrada no momento. Tente novamente em instantes.")
