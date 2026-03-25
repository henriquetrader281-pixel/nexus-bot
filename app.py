import streamlit as st
from groq import Groq # Precisará adicionar 'groq' no seu requirements.txt

# --- 1. CONFIGURAÇÕES E SECRETS ---
api_key = st.secrets.get("GROQ_API_KEY")
st.set_page_config(page_title="Nexus Bot: Groq Edition", page_icon="⚡", layout="wide")

# --- 2. CONEXÃO COM A IA (GROQ - 100% GRÁTIS E RÁPIDA) ---
client = None
if api_key:
    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        st.error(f"Erro na conexão Groq: {e}")
else:
    st.error("API Key da Groq não encontrada nos Secrets.")

# Função para chamar a IA sem erros de NotFound
def chamar_ia(prompt):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Modelo top de linha e grátis
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erro na chamada: {e}"

# --- 3. INTERFACE PRINCIPAL ---
st.title("⚡ Nexus Brain: Groq Turbo")
st.sidebar.header("Módulos de Automação")

# --- 4. [PATCH 10: MINERADOR] ---
st.header("🔎 Mineração de Tendências")
if st.button("Buscar Top 10 Mais Quentes", key="btn_min"):
    if client:
        with st.status("Minerando via Groq...", expanded=True) as status:
            res = chamar_ia("Liste 10 produtos virais Shopee 2026 com nota de 0-10.")
            st.session_state['lista_minerada'] = res
            status.update(label="Concluído!", state="complete", expanded=False)
    else:
        st.error("IA Offline.")

if 'lista_minerada' in st.session_state:
    st.info(st.session_state['lista_minerada'])

# --- 5. [PATCH 11: ROTEIRO] ---
st.divider()
st.header("📝 Remodelagem (Patch 11)")
prod = st.text_input("Produto:", placeholder="Ex: Mini Projetor")
if st.button("Gerar Roteiro Viral", key="btn_p11"):
    if client and prod:
        with st.spinner("Criando..."):
            res = chamar_ia(f"Crie um roteiro de 30s para {prod}. Hook + Problema + Solução + CTA.")
            st.session_state['roteiro_final'] = res
            st.write(res)

# --- 6. [PATCH 12: CENAS] ---
if 'roteiro_final' in st.session_state:
    st.divider()
    if st.button("Quebrar em Cenas", key="btn_p12"):
        res = chamar_ia(f"Divida em cenas de 3s: {st.session_state['roteiro_final']}")
        st.code(res)

# --- 7. [PATCH 04, 05 e 06: EXTRAS] ---
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.header("📥 Downloader (P04)")
    st.text_input("Link TikTok/IG:", key="dl")
    if st.button("Processar Link"): st.toast("Link na fila!")

with col2:
    st.header("📊 Lucro (P06)")
    v = st.number_input("Venda:", value=50.0)
    c = st.number_input("Custo:", value=20.0)
    if st.button("Calcular"):
        st.metric("Lucro", f"R$ {v-c-(v*0.15):.2f}")
