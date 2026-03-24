import streamlit as st
import google.generativeai as genai

# 1. PEGAR CHAVE DOS SECRETS
api_key = st.secrets.get("GEMINI_API_KEY")

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Nexus Bot 1.0", page_icon="🤖")
st.title("🤖 Nexus: Gerador de Posts Shopee")

# 3. CONECTAR AO MODELO CORRETO
if api_key:
    try:
        genai.configure(api_key=api_key)
        # Usando a chamada de modelo mais compatível para evitar erro 404
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    except Exception as e:
        st.error(f"Erro de configuração: {e}")
else:
    st.error("Chave API não encontrada!")

# 4. INTERFACE
nome_produto = st.text_input("📦 Nome do Produto:")
link_video = st.text_input("🔗 Link do Vídeo (.mp4):")

if st.button("🚀 Gerar Post Completo"):
    if nome_produto and api_key:
        try:
            with st.spinner("🧠 Criando legenda..."):
                prompt = f"Crie uma legenda viral para o produto {nome_produto}. Use emojis."
                response = model.generate_content(prompt)
                
                st.success("✅ Gerado!")
                st.subheader("📝 Legenda:")
                st.code(response.text)
                
                if link_video:
                    st.video(link_video)
        except Exception as e:
            st.error(f"Erro na IA: {e}")
            st.info("Verifique se sua chave API nos Secrets está correta.")
