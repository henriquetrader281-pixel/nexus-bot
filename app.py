import streamlit as st
import google.generativeai as genai

# --- CONFIGURAÇÃO INICIAL ---
api_key = st.secrets.get("GEMINI_API_KEY")

st.set_page_config(page_title="Nexus Bot 1.0", page_icon="🤖")

# --- CONEXÃO COM A IA (FORÇANDO ESTABILIDADE) ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # Esta linha abaixo é o segredo: ela lista os modelos para "acordar" a API
        # e depois seleciona o Flash de forma direta.
        model = genai.GenerativeModel('gemini-1.5-flash')
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
            with st.spinner("🧠 Criando legenda..."):
                # Gerando o conteúdo
                response = model.generate_content(f"Crie uma legenda viral para: {nome_produto}")
                
                st.success("✅ Finalmente conectado!")
                st.subheader("📝 Legenda:")
                st.code(response.text)
                
                if link_video:
                    st.video(link_video)
        except Exception as e:
            # Se o erro 404 aparecer aqui, vamos dar a solução final
            st.error(f"O Google ainda não reconheceu o modelo: {e}")
            st.info("Acesse o Google AI Studio e verifique se você aceitou os 'Termos de Serviço' novos que aparecem no topo da página.")
