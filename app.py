import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURAÇÕES E SECRETS ---
api_key = st.secrets.get("GEMINI_API_KEY")

st.set_page_config(page_title="Nexus Bot: Minerador", page_icon="🔥", layout="wide")

# --- 2. CONEXÃO COM A IA (PATCH DE ESTABILIDADE) ---
model = None
if api_key:
    try:
        genai.configure(api_key=api_key)
        # Usando o modelo flash padrão (mais estável para automação)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Erro na IA: {e}")

# --- 3. INTERFACE PRINCIPAL ---
st.title("🔥 Nexus: Mineração e Estratégia")
st.sidebar.header("Painel de Controle")

# --- 4. [PATCH 01: MINERADOR DE PRODUTOS] ---
st.header("🔎 Mineração de Tendências")
if st.button("Buscar Top 10 Mais Quentes (Shopee)"):
    # Espaço reservado para a lógica de busca/scraping
    st.warning("Patch de Mineração Ativo: Buscando dados em tempo real...")
    
    # Exemplo de como os dados aparecerão:
    col1, col2 = st.columns(2)
    with col1:
        st.info("📦 Produto: Luminária Projetora USB")
    with col2:
        st.success("🔥 Status: Viralizando no TikTok/Shopee")

# --- 5. [PATCH 02: ADAPTADOR DE CONTEÚDO IA] ---
st.header("🧠 Inteligência e Legenda")
nome_produto = st.text_input("Confirme o nome do produto para a IA:", value="Luminária de Pôr do Sol USB")

if st.button("Gerar Estratégia de Venda"):
    if model and nome_produto:
        try:
            with st.spinner("IA criando estratégia..."):
                prompt = f"Crie uma legenda de venda curta para {nome_produto} focada em conversão Shopee."
                response = model.generate_content(prompt)
                st.code(response.text, language='text')
        except Exception as e:
            st.error(f"IA Offline: {e}")

# --- 6. [PATCH 03: VISUALIZAÇÃO DE MÍDIA] ---
st.header("🎥 Mídia do Produto")
link_video = st.text_input("Link do Vídeo Minerado:", value="https://www.w3schools.com/html/mov_bbb.mp4")

if link_video:
    st.video(link_video)

# --- [PATCH 10: RADAR DE TENDÊNCIA] ---
# Esta função analisa por que um conteúdo funcionou para replicarmos a lógica
def analisar_tendencia(texto_viral):
    if api_key:
        prompt_trend = f"""
        Analise a estrutura deste conteúdo viral: "{texto_viral}"
        1. Qual é o Gancho (Hook) inicial?
        2. Qual é o desejo ou dor que ele explora?
        3. Por que as pessoas comentariam nele?
        Responda de forma curta e técnica para o Nexus Brain.
        """
        response = model.generate_content(prompt_trend)
        return response.text
    return "Erro: API Key não configurada para análise de tendência."

# --- INTERFACE DO PATCH 10 ---
st.divider()
st.subheader("🕵️ Radar de Tendência (Patch 10)")
input_viral = st.text_area("Cole aqui a descrição ou transcrição de um vídeo VIRAL que você quer copiar:")

if st.button("Analisar DNA do Vídeo"):
    if input_viral:
        with st.spinner("Minerando padrões de viralização..."):
            analise = analisar_tendencia(input_viral)
            st.session_state['analise_sucesso'] = analise
            st.info("Padrão de Sucesso Identificado:")
            st.write(analise)
    else:
        st.warning("Por favor, cole algum texto para eu analisar!")
        # --- 7. [FUTUROS PATCHES] ---
# PATCH 04: DOWNLOADER AUTOMÁTICO (YT-DLP)
# PATCH 05: EDITOR DE VÍDEO (MOVIEPY)
# PATCH 06: DASHBOARD DE LUCRO ESTIMADO
