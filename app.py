import streamlit as st
import google.generativeai as genai
import os

# 1. PEGAR CHAVE DOS SECRETS
api_key = st.secrets.get("GEMINI_API_KEY")

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Nexus Bot 1.0", page_icon="🤖")
st.title("🤖 Nexus: Gerador de Posts Shopee")

# 3. CONEXÃO FORÇADA COM MODELO ESTÁVEL
if api_key:
    try:
        genai.configure(api_key=api_key)
        # Forçamos o modelo 1.5-flash que é gratuito e estável
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Erro de configuração: {e}")
else:
    st.error("Chave API não encontrada nos Secrets!")

# 4. INTERFACE
nome_produto = st.text_input("📦 Nome do Produto:", placeholder="Ex: Mini Processador")
link_video = st.text_input("🔗 Link do Vídeo (.mp4):", placeholder="https://...")

if st.button("🚀 Gerar Post Completo"):
    if nome_produto and api_key:
        try:
            with st.spinner("🧠 Criando legenda viral..."):
                # Chamada direta sem v1beta
                response = model.generate_content(f"Crie uma legenda curta e viral para o produto {nome_produto}. Use emojis.")
                
                st.success("✅ Gerado com sucesso!")
                st.subheader("📝 Legenda:")
                st.code(response.text)
                
                if link_video:
                    st.video(link_video)
        except Exception as e:
            st.error(f"Erro na IA: {e}")
            st.info("Verifique se você aceitou os termos no Google AI Studio.")
