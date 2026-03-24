import streamlit as st
import google.generativeai as genai
import requests
import os

# 1. CONFIGURAÇÃO DE SEGURANÇA DA IA
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Erro ao configurar IA: {e}")
else:
    st.error("Chave GEMINI_API_KEY não encontrada nos Secrets!")

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Nexus Bot 1.0", page_icon="🤖", layout="centered")

st.title("🤖 Nexus: Gerador de Posts Shopee")
st.markdown("---")

# 3. ENTRADA DE DADOS
col1, col2 = st.columns(2)
with col1:
    nome_produto = st.text_input("📦 Nome do Produto:", placeholder="Ex: Mini Processador")
with col2:
    link_video = st.text_input("🔗 Link Direto do Vídeo (.mp4):")

# 4. AÇÃO DO ROBÔ
if st.button("🚀 Gerar Post Completo"):
    if not nome_produto:
        st.warning("Por favor, digite o nome do produto.")
    elif not api_key:
        st.error("Sua chave API não está configurada.")
    else:
        try:
            with st.spinner("🧠 O cérebro está criando a legenda viral..."):
                # Chamada da IA
                prompt = f"Crie uma legenda curta e muito viral para Instagram Reels sobre o produto '{nome_produto}'. Use emojis, gatilhos de escassez e hashtags de achadinhos."
                response = model.generate_content(prompt)
                
                st.success("✅ Post Gerado com Sucesso!")
                
                # Exibe a Legenda
                st.subheader("📝 Legenda Sugerida:")
                st.code(response.text, language="text") # Facilita copiar
                
                # Exibe o Vídeo (se houver link)
                if link_video:
                    st.subheader("🎥 Prévia do Vídeo:")
                    st.video(link_video)
                else:
                    st.info("💡 Cole um link .mp4 para ver a prévia do vídeo aqui.")
                    
        except Exception as e:
            st.error(f"Erro técnico: {e}")
            st.info("Dica: Verifique se sua chave API no Streamlit está correta e sem espaços.")

st.markdown("---")
st.caption("Nexus Bot v1.0 - Automação de Achadinhos")
