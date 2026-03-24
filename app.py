import streamlit as st
import google.generativeai as genai

# --- CONFIGURAÇÃO INICIAL ---
api_key = st.secrets.get("GEMINI_API_KEY")

st.set_page_config(page_title="Nexus Bot 1.0", page_icon="🤖")

# --- CONEXÃO COM A IA ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        # O nome 'gemini-pro' funciona no seu plano gratuito!
        model = genai.GenerativeModel('gemini-pro')
    except Exception as e:
        st.error(f"Erro na configuração: {e}")
else:
    st.error("Chave API não encontrada nos Secrets!")

st.title("🤖 Nexus: Gerador de Posts Shopee")

nome_produto = st.text_input("📦 Nome do Produto:")
link_video = st.text_input("🔗 Link do Vídeo (.mp4):")

if st.button("🚀 Gerar Post Completo"):
    if nome_produto and api_key:
        try:
            with st.spinner("🧠 Criando legenda viral..."):
                prompt = f"Crie uma legenda curta e viral para: {nome_produto}. Use emojis e hashtags."
                response = model.generate_content(prompt)
                
                st.success("✅ Legenda Gerada!")
                st.code(response.text) # Caixa para copiar
                
                if link_video:
                    st.video(link_video)
        except Exception as e:
            st.error(f"Erro na IA: {e}")
            st.info("Recomendo gerar uma NOVA chave no Google AI Studio e colar nos Secrets.")

# --- PATCH DE UPDATE (FUTURO) ---
# Em breve adicionaremos as linhas abaixo para a edição automática:
# import moviepy.editor as mp
# def editar_video():
#     pass
