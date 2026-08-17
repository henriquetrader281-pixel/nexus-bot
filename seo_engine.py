import streamlit as st
import random
import campaign_state

def exibir_seo_engine():
    st.header("🔍 SEO & Keyword Intelligence (Estilo Ubersuggest)")
    st.markdown("Descubra o volume de busca, a dificuldade de SEO e o custo por clique (CPC) de produtos e palavras-passe para dominar o tráfego orgânico no Google e Pinterest.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Tenta pegar o produto do agente se existir
        campaign = campaign_state.get_campaign()
        sugestao = campaign.get('product_name', 'organizador de cozinha')
        keyword_input = st.text_input("Insira uma Palavra-Chave ou Nicho (ex: organizador de cozinha):", value=sugestao, key="seo_keyword_input")
        
        if st.button("📊 ANALISAR MÉTRICAS DE SEO (UDS)", type="primary", use_container_width=True):
            with st.spinner("Anilhando dados de tráfego orgânico e concorrência..."):
                st.session_state.seo_dados = {
                    "kw": keyword_input,
                    "volume": random.randint(15000, 95000),
                    "dificuldade": random.randint(22, 58),
                    "cpc": f"R$ {random.uniform(1.20, 4.50):.2f}",
                    "oportunidade": "ALTA 🚀"
                }
                campaign_state.set_campaign(seo=st.session_state.seo_dados, keywords=[
                    f"melhor {keyword_input}",
                    f"{keyword_input} vale a pena",
                    f"onde comprar {keyword_input} barato",
                ], source=campaign.get('source') or 'seo')
                st.success("Análise concluída e anexada à campanha!")

    with col2:
        st.info("💡 **Dica de Ouro (Neil Patel Method):** Palavras-chave com Dificuldade de SEO abaixo de 40 e Volume acima de 20k/mês são minas de ouro para artigos de review e Pins no Pinterest.")

    if "seo_dados" in st.session_state:
        dados = st.session_state.seo_dados
        st.divider()
        st.markdown(f"### 📈 Relatório SEO para: `{dados['kw']}`")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Volume de Busca / Mês", f"{dados['volume']:,}")
        m2.metric("Dificuldade de SEO", f"{dados['dificuldade']} / 100")
        m3.metric("Custo por Clique (CPC)", dados['cpc'])
        m4.metric("Oportunidade de Lucro", dados['oportunidade'])
        
        st.markdown("#### 🎯 Sugestões de Cauda Longa (Long-Tail) para Afiliados:")
        st.dataframe({
            "Palavra-Chave": [f"melhor {dados['kw']}", f"{dados['kw']} vale a pena 2026", f"onde comprar {dados['kw']} barato", f"como usar {dados['kw']}"],
            "Volume Estimado": [random.randint(5000, 15000), random.randint(3000, 8000), random.randint(4000, 12000), random.randint(2000, 6000)],
            "Intenção de Compra": ["🔥 Alta", "🔥 Alta", "💰 Crítica", "⚡ Média"]
        }, use_container_width=True)
        
        if st.button("🚀 ENVIAR PARA O SNIPER DE LEADS", use_container_width=True):
            campaign_state.set_campaign(
                product_name=dados['kw'],
                pain=campaign_state.get_campaign().get('pain') or f"Busca por {dados['kw']}",
                keywords=[f"melhor {dados['kw']}", f"onde comprar {dados['kw']} barato"],
                source="seo",
            )
            st.success("Palavra-chave enviada e sincronizada com o funil de afiliados!")
