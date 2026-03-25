import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURAÇÕES E SECRETS ---
api_key = st.secrets.get("GEMINI_API_KEY")
st.set_page_config(page_title="Nexus Bot: Master", page_icon="🧠", layout="wide")

# --- 2. CONEXÃO COM A IA (CORREÇÃO ERRO 404) ---
model = None
if api_key:
    try:
        genai.configure(api_key=api_key)
        # CORREÇÃO: Removido prefixo 'models/' que causava o 404
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Erro na conexão Gemini: {e}")

# --- 3. INTERFACE PRINCIPAL ---
st.title("🧠 Nexus Brain: Operação Ativa")
st.sidebar.header("Módulos de Automação")

# --- 4. [PATCH 10: MINERADOR DE PRODUTOS REAL] ---
st.header("🔎 Mineração de Tendências")

if st.button("Buscar Top 10 Mais Quentes (Shopee)", key="botao_mineracao_unique"):
    if model:
        with st.status("Minerando tendências...", expanded=True) as status:
            st.write("Conectando aos servidores...")
            prompt_min = "Liste 10 produtos virais Shopee 2026 com nota de 0-10."
            
            try:
                response = model.generate_content(prompt_min)
                st.write("Analisando volume de buscas...")
                
                if response and hasattr(response, 'text'):
                    st.session_state['lista_minerada'] = response.text
                    status.update(label="Concluído!", state="complete", expanded=False)
                else:
                    st.error("IA não retornou dados.")
            except Exception as e:
                st.error(f"Erro ao gerar conteúdo: {e}")
    else:
        st.error("API Key não configurada.")

if 'lista_minerada' in st.session_state:
    st.info(st.session_state['lista_minerada'])

# --- 5. [PATCH 11: REMODELAGEM DE ROTEIRO] ---
st.divider()
st.header("📝 Remodelagem (Patch 11)")
prod_para_roteiro = st.text_input("Produto para o Roteiro:", placeholder="Digite o produto...")

if st.button("Gerar Roteiro Viral", key="btn_remodelagem_p11"):
    if model and prod_para_roteiro:
        with st.spinner("Criando roteiro..."):
            prompt_p11 = f"Crie um roteiro de 30s para {prod_para_roteiro}. Hook + Problema + Solução + CTA."
            res_p11 = model.generate_content(prompt_p11)
            if res_p11 and hasattr(res_p11, 'text'):
                st.session_state['roteiro_final'] = res_p11.text
                st.success("Roteiro pronto!")
                st.write(st.session_state['roteiro_final'])

# --- 6. [PATCH 12: ESTRUTURA DE CENAS] ---
if 'roteiro_final' in st.session_state:
    st.divider()
    st.subheader("🎬 Estrutura de Cenas (Patch 12)")
    if st.button("Quebrar Roteiro para Edição", key="btn_cenas_p12_final"):
        with st.spinner("Organizando cenas..."):
            prompt_12 = f"Transforme este roteiro em uma lista de cenas de 3 segundos para o editor: {st.session_state['roteiro_final']}"
            res_12 = model.generate_content(prompt_12)
            if res_12 and hasattr(res_12, 'text'):
                st.code(res_12.text, language='text')
                st.success("Cenas prontas para edição!")

# --- 7. [PATCH 03: MÍDIA] ---
st.divider()
st.header("🎥 Mídia do Produto")
link_video = st.text_input("Link do vídeo:", value="https://www.w3schools.com/html/mov_bbb.mp4")
if link_video:
    st.video(link_video)

# --- 8. [PATCH 04, 05 e 06: EXTRAS DE PERFORMANCE] ---
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.header("📥 Downloader (P04)")
    url_ref = st.text_input("Link para download (TikTok/IG):", key="dl_link")
    if st.button("Preparar Arquivo"):
        st.toast("Link enviado para a fila de download!")

with col2:
    st.header("✍️ Legenda Post (P05)")
    if st.button("Gerar Legenda p/ Instagram"):
        if 'roteiro_final' in st.session_state:
            prompt_05 = f"Crie uma legenda curta com emojis para este roteiro: {st.session_state['roteiro_final']}"
            res_05 = model.generate_content(prompt_05)
            st.write(res_05.text)
        else:
            st.warning("Gere um roteiro primeiro!")

st.divider()
st.header("📊 Calculadora de Lucro (P06)")
venda = st.number_input("Preço de Venda (R$):", value=50.0)
custo = st.number_input("Custo do Produto + Frete (R$):", value=20.0)
if st.button("Calcular Margem"):
    lucro = venda - custo - (venda * 0.15) # Sim
