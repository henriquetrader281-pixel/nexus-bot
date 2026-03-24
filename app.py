import streamlit as st
import google.generativeai as genai
import os

# 1. FORÇAR ROTA ESTÁVEL (Isso mata o erro 404)
os.environ["GOOGLE_API_USE_MTLS_ENDPOINT"] = "never"

# 2. PEGAR CHAVE DOS SECRETS
api_key = st.secrets.get("GEMINI_API_KEY")

st.set_page_config(page_title="Nexus Bot", page_icon="🤖")
st.title("🤖 Nexus Bot: Shopee")

# 3. CONEXÃO MANUAL
if api_key:
    try:
        genai.configure(api_key=api_key)
        # Usamos o flash-8b: ele é o mais rápido e menos propenso a erros de região
        model = genai.GenerativeModel('gemini-1.5-flash-8b')
    except Exception as e:
        st.error(f"Erro ao configurar: {e}")
else:
    st.error("Configure a chave nos Secrets!")

# 4. INTERFACE
nome = st.text_input("📦 Nome do Produto:")

if st.button("🚀 Gerar"):
    if nome:
        try:
            with st.spinner("IA Processando..."):
                # Chamada de teste
                response = model.generate_content(f"Legenda curta para {nome}")
                st.success("✅ Funcionou!")
                st.write(response.text)
        except Exception as e:
            st.error(f"Erro persistente: {e}")
            st.info("💡 Tente ir no Google AI Studio e clicar em 'Create API Key in NEW Project'.")
