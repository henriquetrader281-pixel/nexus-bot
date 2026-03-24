import streamlit as st
import google.generativeai as genai
import requests
import os

# Configuração da IA (Pegando a chave que você vai salvar no Streamlit)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Configure sua chave API_KEY nos Secrets do Streamlit!")

st.set_page_config(page_title="Nexus Bot 1.0", layout="centered")
st.title("🤖 Nexus: Gerador de Posts Shopee")

# --- INTERFACE ---
link_video = st.text_input("Cole o link DIRETO do vídeo (terminado em .mp4):")
nome_produto = st.text_input("Nome do Produto:")

if st.button("🚀 Gerar Vídeo e Legenda"):
    if link_video and nome_produto:
        with st.spinner("O cérebro está criando o post..."):
            
            # 1. GERAR LEGENDA COM IA
            prompt = f"Crie uma legenda curta, engraçada e viral para um vídeo do TikTok/Reels sobre o produto: {nome_produto}. Use emojis e hashtags de achadinhos."
            response = model.generate_content(prompt)
            legenda = response.text
            
            # 2. MOSTRAR RESULTADOS
            st.subheader("✅ Legenda Sugerida:")
            st.write(legenda)
            
            st.subheader("🎥 Prévia do Vídeo:")
            st.video(link_video)
            
            st.info("Para este MVP Grátis, baixe o vídeo e a legenda acima para postar. A edição automática de texto sobre o vídeo será o próximo passo do nosso código!")
    else:
        st.warning("Por favor, preencha o link e o nome do produto.")
