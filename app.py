import streamlit as st
from groq import Groq

# --- 1. CONFIGURAÇÕES E SECRETS ---
# Certifique-se de que o nome no Secrets é GROQ_API_KEY
api_key = st.secrets.get("GROQ_API_KEY")
st.set_page_config(page_title="Nexus Bot: Groq Turbo", page_icon="⚡", layout="wide")

# --- 2. CONEXÃO COM A IA ---
client = None
if api_key:
    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        st.error(f"Erro na conexão Groq: {e}")
else:
    st.error("API Key da Groq não encontrada nos Secrets.")

# Função mestre para evitar repetição de código
def gerar_resposta(prompt):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Modelo potente e gratuito
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erro na IA: {e}"

# --- 3. INTERFACE ---
st.title("⚡ Nexus Brain: Operação Turbo (Groq)")

# --- 4. [PATCH 10: MINERADOR] ---
st.header("🔎 Mineração de Tendências")
if st.button("Buscar Top 10 Mais Quentes", key="btn_min"):
    if client:
        with st.status("Minerando em alta velocidade...", expanded=True) as status:
            res = gerar_resposta("Liste 10 produtos virais Shopee 2026 com nota de 0-10 de potencial de venda.")
            st.session_state['lista_minerada'] = res
            status.update(label="Mineração Concluída!", state="complete", expanded=False)
    else:
        st.error("Configure a API Key da Groq primeiro.")

if 'lista_minerada' in st.session_state:
    st.info(st.session_state['lista_minerada'])

# --- 5. [PATCH 11: ROTEIRO] ---
st.divider()
st.header("📝 Remodelagem (Patch 11)")
prod = st.text_input("Produto alvo:", placeholder="Ex: Luminária Projetora")
if st.button("Gerar Roteiro Viral", key="btn_p11"):
    if client and prod:
        with st.spinner("Criando roteiro magnético..."):
            res = gerar_resposta(f"Crie um roteiro de 30s para {prod}. Hook + Problema + Solução + CTA.")
            st.session_state['roteiro_final'] = res
            st.success("Roteiro Gerado!")
            st.write(res)

# --- 6. [PATCH 12: CENAS] ---
if 'roteiro_final' in st.session_state:
    st.divider()
    st.subheader("🎬 Estrutura de Cenas")
    if st.button("Quebrar em Cenas", key="btn_p12"):
        res = gerar_resposta(f"Divida esse roteiro em cenas de 3 segundos para edição: {st.session_state['roteiro_final']}")
        st.code(res)

# --- 7. [PATCHES EXTRAS 04, 05, 06] ---
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.header("📥 Downloader (P04)")
    st.text_input("Link para baixar:", key="dl")
    if st.button("Processar Link"): st.toast("Link enviado!")

with col2:
    st.header("📊 Lucro (P06)")
    v = st.number_input("Venda (R$):", value=50.0)
    c = st.number_input("Custo (R$):", value=20.0)
    if st.button("Calcular"):
        st.metric("Lucro Líquido", f"R$ {v-c-(v*0.15):.2f}")
