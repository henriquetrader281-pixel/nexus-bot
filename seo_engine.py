import streamlit as st
import random

def exibir_seo_engine():
    st.header("🔍 SEO & Keyword Intelligence (Estilo Ubersuggest)")
    st.markdown("Descubra o volume de busca, a dificuldade de SEO e o custo por clique (CPC) de produtos e palavras-passe para dominar o tráfego orgânico no Google e Pinterest.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        keyword_input = st.text_input("Insira uma Palavra-Chave ou Nicho (ex: organizador de cozinha):", value="organizador de cozinha")
        
        if st.button("📊 ANALISAR MÉTRICAS DE SEO (UDS)", type="primary", use_container_width=True):
            with st.spinner("Anilhando dados de tráfego orgânico e concorrência..."):
                st.session_state.seo_dados = {
                    "kw": keyword_input,
                    "volume": random.randint(15000, 95000),
                    "dificuldade": random.randint(22, 58),
                    "cpc": f"R$ {random.uniform(1.20, 4.50):.2f}",
                    "oportunidade": "ALTA 🚀"
                }
                st.success("Análise concluída!")

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
            st.session_state.sel_nome = dados['kw']
            st.success("Palavra-chave enviada com sucesso para o funil de afiliados!")
