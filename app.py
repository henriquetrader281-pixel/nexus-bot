import streamlit as st
import google.generativeai as genai

# 1. CONFIGURAÇÃO DE SEGURANÇA
api_key = st.secrets.get("GEMINI_API_KEY")

st.set_page_config(page_title="Nexus Bot 1.0", page_icon="🤖")
st.title("🤖 Nexus: Gerador de Posts Shopee")

# 2. CONEXÃO COM A IA (FORÇANDO VERSÃO ESTÁVEL)
if api_key:
    try:
        genai.configure(api_key=api_key)
        # O segredo está aqui: usamos o nome técnico completo do modelo
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
    except Exception as e:
        st.error(f"Erro na configuração: {e}")
else:
    st.error("Chave API não encontrada nos Secrets!")

# 3. INTERFACE
nome_produto = st.text_input("📦 Nome do Produto:")
link_video = st.text_input("🔗 Link do Vídeo (.mp4):")

if st.button("🚀 Gerar Post Completo"):
    if nome_produto and api_key:
        try:
            with st.spinner("🧠 Criando legenda..."):
                # Chamada direta
                response = model.generate_content(f"Crie uma legenda viral para: {nome_produto}")
                
                st.success("✅ Conectado!")
                st.subheader("📝 Legenda:")
                st.code(response.text)
                
                if link_video:
                    st.video(link_video)
        except Exception as e:
            st.error(f"Erro técnico: {e}")
            st.info("Verifique se você clicou em 'Dismiss' ou 'Accept' no topo do Google AI Studio.")
