import streamlit as st
from pytrends.request import TrendReq
import pandas as pd

def exibir_trends():
    st.header("📈 Google Trends Brasil: Termos em Tempo Real")
    st.markdown("Extraindo dores e palavras-passe de alta conversão diretamente do Google Trends.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🔍 VARRER TENDÊNCIAS REAIS AGORA", use_container_width=True):
            with st.spinner("Conectando ao Google Trends Brasil..."):
                try:
                    pytrends = TrendReq(hl='pt-BR', tz=180)
                    # Busca as tendências diárias do Brasil
                    df = pytrends.trending_searches(pn='brazil')
                    trends_list = df[0].tolist()[:10] # Top 10
                    st.session_state.real_trends = trends_list
                    st.success("Tendências capturadas com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao conectar ao Google Trends: {e}")
                    # Fallback para não travar
                    st.session_state.real_trends = ["organizador de cozinha", "luminaria led", "fone bluetooth", "mop giratorio"]

        if "real_trends" in st.session_state:
            termo_escolhido = st.selectbox("Selecione um termo para o funil:", st.session_state.real_trends)
            
            if st.button("🚀 INJETAR NO MOTOR NEXUS", type="primary", use_container_width=True):
                nome_limpo = termo_escolhido.title()
                st.session_state.sel_nome = nome_limpo
                st.session_state.sel_dor = f"Busca em alta no Google Trends: {termo_escolhido}"
                
                import ml_afiliados_engine
                mkt = st.session_state.get('mkt_global', 'Mercado Livre')
                st.session_state.sel_link = ml_afiliados_engine.gerar_link_afiliado_dinamico(nome_limpo, mkt)
                
                st.success(f"'{nome_limpo}' injetado em todas as abas!")
                st.rerun()

    with col2:
        st.subheader("💡 Inteligência de Mercado")
        st.info("O Nexus analisa o que o Brasil está a pesquisar agora para garantir que o seu produto tenha demanda imediata.")
        st.link_button("🌐 Ver no Google Trends", "https://trends.google.com.br/trends/")
