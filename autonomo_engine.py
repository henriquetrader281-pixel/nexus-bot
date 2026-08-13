import streamlit as st
import os
from real_marketplace_engine import obter_produto_real_validado

def exibir_aba_autonomo():
    st.header("🤖 Nexus Autônomo: Catálogo Real & Funil de Alta Retenção")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.info("💡 **Modo Real Validado:** O Nexus agora seleciona apenas produtos físicos reais e virais da Shopee, Amazon e Mercado Livre, eliminando 100% de alucinações.")
        
        provedor = st.radio("Selecione o Motor IA:", ["ChatGPT (OpenAI)", "Google Gemini", "Groq"], horizontal=True)
        
        if st.button("🚀 GERAR OPORTUNIDADE REAL", use_container_width=True):
            with st.spinner("Escaneando e-commerce e cruzando tendências..."):
                dados = obter_produto_real_validado(provedor)
                st.session_state.nexus_dados_reais = dados
                st.session_state.sel_nome = dados['produto']
                st.session_state.sel_dor = dados['dificuldade']
                st.session_state.nexus_media_url = dados['imagem']
                st.session_state.nexus_media_ready = True
                # Registrar no Dashboard
                import update
                update.registrar_mineracao(dados['produto'], dados['link_ml'], 99)
                st.success("Oportunidade real gerada e sincronizada com o Estúdio!")

    with col1:
        if "nexus_dados_reais" in st.session_state:
            dados = st.session_state.nexus_dados_reais
            
            with st.container(border=True):
                st.subheader(f"🎯 Nicho: {dados['nicho']}")
                st.warning(f"**DOR DETECTADA:** {dados['dificuldade']}")
                st.success(f"**PRODUTO REAL (SHOPEE/ML/AMAZON):** {dados['produto']}")
                
                st.markdown("### 📝 Copy de Alta Conversão (Com Hook, AIDA & CTA)")
                st.code(dados['copy'], language="text")
                
                st.markdown("### 🖼️ Mídia & Vídeo Sincronizados")
                st.image(dados['imagem'], caption=f"Produto Real: {dados['produto']}", use_container_width=True)
                st.info("🟢 Imagem e contexto enviados automaticamente para a aba **ESTÚDIO** para renderização do Reels.")
                
                st.markdown("### 🛒 Link de Afiliado Ativo")
                st.link_button("🛒 Comprar com Desconto (Afiliado)", dados['link_ml'], use_container_width=True)
        else:
            st.info("Clique no botão ao lado para gerar uma oportunidade de produto real e validado.")
