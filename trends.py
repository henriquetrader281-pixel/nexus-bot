import streamlit as st
from pytrends.request import TrendReq
import pandas as pd
import time

def exibir_trends():
    st.header("📈 Google Trends Brasil: Inteligência em Tempo Real")
    st.markdown("Extraindo as dores e desejos mais quentes do mercado brasileiro agora.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🔍 VARRER TENDÊNCIAS AGORA", use_container_width=True, type="primary"):
            with st.spinner("Conectando aos servidores do Google Trends..."):
                try:
                    # Configuração robusta com retries e timeout
                    pytrends = TrendReq(hl='pt-BR', tz=180, retries=2, backoff_factor=0.1, timeout=(10,25))
                    df = pytrends.trending_searches(pn='brazil')
                    if df is not None and not df.empty:
                        trends_list = df[0].tolist()[:10]
                        st.session_state.real_trends = trends_list
                        st.success("✅ Tendências capturadas com sucesso!")
                    else:
                        raise Exception("Google retornou lista vazia.")
                except Exception as e:
                    st.error(f"⚠️ Limite de requisições ou erro de conexão: {str(e)}")
                    st.info("Usando Radar de Contingência (Termos quentes validados):")
                    st.session_state.real_trends = [
                        "Organizador de Cozinha Inteligente", 
                        "Luminária LED Monitor Anti-Reflexo", 
                        "Mini Pistola de Massagem Profissional",
                        "Mop Giratório Slim 2026",
                        "Fone Bluetooth Cancelamento Ruído"
                    ]

        if "real_trends" in st.session_state:
            termo_escolhido = st.selectbox("Selecione o alvo para o funil:", st.session_state.real_trends)
            
            if st.button("🚀 INJETAR NO MOTOR NEXUS", use_container_width=True):
                nome_limpo = termo_escolhido.title()
                st.session_state.sel_nome = nome_limpo
                st.session_state.sel_dor = f"Tendência em alta detectada: {termo_escolhido}"
                
                import ml_afiliados_engine
                mkt = st.session_state.get('mkt_global', 'Mercado Livre')
                st.session_state.sel_link = ml_afiliados_engine.gerar_link_afiliado_dinamico(nome_limpo, mkt)
                
                st.success(f"'{nome_limpo}' injetado! Vá ao Agente ou Arsenal.")
                time.sleep(1)
                st.rerun()

    with col2:
        st.subheader("💡 Por que usar Trends?")
        st.markdown("""
        1. **Demanda Validada:** Você só vende o que as pessoas já estão procurando.
        2. **SEO Nativo:** O Nexus usa estes termos exatos para que o seu post apareça no topo das buscas.
        3. **ROI Elevado:** Menor custo por clique em anúncios.
        """)
        st.link_button("🌐 Abrir Google Trends", "https://trends.google.com.br/trends/")
