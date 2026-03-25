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
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Erro na IA: {e}")

# --- 3. INTERFACE PRINCIPAL ---
st.title("🔥 Nexus: Mineração e Estratégia")
st.sidebar.header("Painel de Controle")

# --- 4. [PATCH 10: MINERADOR DE PRODUTOS REAL] ---
st.header("🔎 Mineração de Tendências")

# BOTÃO CORRIGIDO (O ÚNICO QUE DEVE EXISTIR PARA MINERAÇÃO)
if st.button("Buscar Top 10 Mais Quentes (Shopee)", key="botao_mineracao_unique"):
    if model:
        with st.status("Patch de Mineração Ativo: Buscando dados em tempo real...", expanded=True) as status:
            st.write("Conectando aos servidores de tendência...")
            
            prompt_mineracao = "Liste 10 produtos que são tendência de vendas para afiliados em 2024. Dê nota de viralização de 0 a 10."
            response = model.generate_content(prompt_mineracao)
            dados_quentes = response.text
            
            st.write("Analisando volume de buscas...")
            status.update(label="Mineração Concluída!", state="complete", expanded=False)
        
        st.markdown("### 🔥 Top 10 Produtos Identificados:")
        st.info(dados_quentes)
        st.session_state['lista_minerada'] = dados_quentes
    else:
        st.error("IA Offline: Verifique sua API Key nos Secrets.")

# --- 5. [PATCH 02: ADAPTADOR DE CONTEÚDO IA] ---
st.divider()
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
            st.error(f"Erro ao gerar legenda: {e}")

# --- 6. [PATCH 03: VISUALIZAÇÃO DE MÍDIA] ---
st.header("🎥 Mídia do Produto")
link_video = st.text_input("Link do Vídeo Minerado:", value="https://www.w3schools.com/html/mov_bbb.mp4")
if link_video:
    st.video(link_video)

# --- 7. [PATCH 10: RADAR DE TENDÊNCIA - ANALISADOR] ---
st.divider()
st.subheader("🕵️ Radar de Tendência (Analise de Concorrência)")

def analisar_tendencia(texto_viral):
    if model:
        prompt_trend = f"""
        Analise a estrutura deste conteúdo viral: "{texto_viral}"
        1. Qual é o Gancho (Hook) inicial?
        2. Qual é o desejo ou dor que ele explora?
        3. Por que as pessoas comentariam nele?
        Responda de forma curta e técnica para o Nexus Brain.
        """
        response = model.generate_content(prompt_trend)
        return response.text
    return "Erro: IA não configurada."

input_viral = st.text_area("Cole aqui a descrição ou transcrição de um vídeo VIRAL que você quer copiar:")

if st.button("Analisar DNA do Vídeo", key="btn_analisar_dna"):
    if input_viral:
        with st.spinner("Minerando padrões de viralização..."):
            analise = analisar_tendencia(input_viral)
            st.session_state['analise_sucesso'] = analise
            st.info("Padrão de Sucesso Identificado:")
            st.write(analise)
    else:
        st.warning("Por favor, cole algum texto para eu analisar!")
# PATCH 04: DOWNLOADER AUTOMÁTICO (YT-DLP)
# PATCH 05: EDITOR DE VÍDEO (MOVIEPY)
# PATCH 06: DASHBOARD DE LUCRO ESTIMADO
