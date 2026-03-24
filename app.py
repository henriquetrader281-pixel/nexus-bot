import streamlit as st
import google.generativeai as genai
from google.api_core import client_options

# 1. BUSCAR A CHAVE DOS SECRETS
api_key = st.secrets.get("GEMINI_API_KEY")

st.set_page_config(page_title="Nexus Bot", page_icon="🤖")
st.title("🤖 Nexus Bot: Shopee")

# 2. CONFIGURAÇÃO PARA MATAR O ERRO 404
if api_key:
    try:
        # FORÇA A VERSÃO V1 (A v1beta é a que está dando erro nos seus prints)
        options = client_options.ClientOptions(api_version="v1")
        genai.configure(api_key=api_key, client_options=options)
        
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Erro na configuração: {e}")
else:
    st.error("Chave não encontrada nos Secrets!")

# 3. INTERFACE (O LINK VOLTOU!)
nome_produto = st.text_input("📦 Nome do Produto:", placeholder="Ex: Mop Giratório")
link_video = st.text_input("🔗 Link do Vídeo (.mp4):", placeholder="https://...")

if st.button("🚀 Gerar Post Completo"):
    if nome_produto:
        try:
            with st.spinner("🧠 IA Criando legenda..."):
                # Gera a legenda
                response = model.generate_content(f"Crie uma legenda viral para: {nome_produto}")
                st.success("✅ Conectado!")
                st.subheader("📝 Legenda:")
                st.code(response.text)
                
                # MOSTRAR O VÍDEO (Mesmo se a IA falhar, ele tenta mostrar)
                if link_video:
                    st.subheader("🎥 Prévia do Vídeo:")
                    st.video(link_video)
        except Exception as e:
            st.error(f"Erro técnico: {e}")
            # Se a IA falhar, ainda mostramos o vídeo para você não ficar na mão
            if link_video:
                st.subheader("🎥 Prévia do Vídeo (IA offline):")
                st.video(link_video)
