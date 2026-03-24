import streamlit as st
import google.generativeai as genai

# --- CONFIGURAÇÃO INICIAL ---
# Tenta carregar a chave dos Secrets do Streamlit
api_key = st.secrets.get("GEMINI_API_KEY")

st.set_page_config(page_title="Nexus Bot 1.0", page_icon="🤖", layout="centered")

# --- CONEXÃO COM A IA ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        # Ajuste para evitar o erro 404: usamos o identificador padrão estável
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Erro ao configurar a IA: {e}")
else:
    st.error("Chave 'GEMINI_API_KEY' não encontrada nos Secrets!")

# --- INTERFACE DO SITE ---
st.title("🤖 Nexus: Gerador de Posts Shopee")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    nome_produto = st.text_input("📦 Nome do Produto:", placeholder="Ex: Mop Giratório")
with col2:
    link_video = st.text_input("🔗 Link Direto do Vídeo (.mp4):", placeholder="https://exemplo.com/video.mp4")

# --- LÓGICA DE GERAÇÃO ---
if st.button("🚀 Gerar Post Completo"):
    if not nome_produto:
        st.warning("Por favor, digite o nome do produto.")
    elif not api_key:
        st.error("Configure sua API Key nos Secrets primeiro.")
    else:
        try:
            with st.spinner("🧠 O Nexus está pensando na melhor legenda..."):
                # Criando o prompt para a IA
                prompt = f"Crie uma legenda de 3 linhas para o produto '{nome_produto}' focada em vendas no Instagram. Use emojis e hashtags."
                response = model.generate_content(prompt)
                
                st.success("✅ Legenda Criada!")
                st.subheader("📝 Sugestão de Legenda:")
                st.code(response.text, language="text") # Caixa de texto fácil de copiar
                
                if link_video:
                    if link_video.endswith(".mp4"):
                        st.subheader("🎥 Prévia do Vídeo Original:")
                        st.video(link_video)
                    else:
                        st.info("💡 Para ver a prévia aqui, o link precisa terminar em .mp4")
        except Exception as e:
            st.error(f"Erro técnico na IA: {e}")
            st.info("Dica: Verifique se sua chave API não tem aspas extras ou espaços.")

st.markdown("---")
st.caption("Nexus Bot v1.0 - Automação Inteligente")

# ---------------------------------------------------------
# PATCH DE UPDATE (Próxima Etapa: Edição de Vídeo Automática)
# ---------------------------------------------------------
# Quando ativarmos a edição, adicionaremos abaixo:
# import moviepy.editor as mp
# def processar_video(url):
#     ... lógica de download e "carimbo" de texto no vídeo ...
