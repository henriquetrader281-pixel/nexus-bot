import streamlit as st
import google.generativeai as genai

# --- CONFIGURAÇÃO INICIAL ---
api_key = st.secrets.get("GEMINI_API_KEY")

st.set_page_config(page_title="Nexus Bot 1.0", page_icon="🤖")

# --- CONEXÃO COM A IA (VERSÃO UNIVERSAL) ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        # Usando o nome completo que o Google exige nas versões novas
        model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
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
                # O prompt corrigido
                prompt = f"Crie uma legenda curta e viral para: {nome_produto}. Use emojis."
                response = model.generate_content(prompt)
                
                st.success("✅ Sucesso!")
                st.subheader("📝 Legenda:")
                st.code(response.text)
                
                if link_video:
                    st.video(link_video)
        except Exception as e:
            # Se ainda der erro, o código vai tentar o modelo alternativo automaticamente
            st.error(f"Erro na IA: {e}")
            st.info("Tentando conexão alternativa...")
            try:
                model_alt = genai.GenerativeModel('gemini-1.5-flash')
                response = model_alt.generate_content(f"Legenda para {nome_produto}")
                st.code(response.text)
            except:
                st.warning("Ainda há um problema com a versão da API. Verifique sua chave.")

# --- PATCH DE UPDATE FINAL ---
# [Aqui entrarão os códigos de edição de vídeo em breve]
