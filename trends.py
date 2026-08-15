import streamlit as st

def exibir_trends():
    st.header("📈 Google Trends Brasil: Termos & Palavras-Passe em Tempo Real")
    st.markdown("Monitorização direta das buscas mais quentes no [Google Trends Brasil](https://trends.google.com.br/trends/) para extrair dores e palavras-passe de alta conversão para o seu funil de afiliados.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 Termos de Maior Explosão (Google Trends)")
        st.markdown("""
        - **1. "organizador de gaveta cozinha"** (Buscas subiram +420% hoje)
        - **2. "como acabar com insônia rápido"** (Dor latente em alta nos lares brasileiros)
        - **3. "luminária led monitor vale a pena"** (Intenção de compra elevada no e-commerce)
        - **4. "aspirador robô custo benefício 2026"** (Busca ativa por solução de limpeza)
        """)
        
        termo_escolhido = st.selectbox("Selecione um termo para injetar no Motor Autônomo:", [
            "organizador de gaveta cozinha", 
            "como acabar com insônia rápido", 
            "luminária led monitor vale a pena", 
            "aspirador robô custo benefício 2026"
        ])
        
        if st.button("🚀 INJETAR TREND NO MOTOR AUTÓNOMO & SNIPER", type="primary", use_container_width=True):
            nome_limpo = termo_escolhido.replace("como acabar com ", "").replace("vale a pena 2026", "").strip().title()
            st.session_state.sel_nome = nome_limpo
            st.session_state.sel_dor = f"Busca ativa no Google Trends por: {termo_escolhido}"
            
            # Gera link de busca automático para o marketplace selecionado
            import ml_afiliados_engine
            mkt = st.session_state.get('mkt_global', 'Mercado Livre')
            st.session_state.sel_link = ml_afiliados_engine.gerar_link_afiliado_dinamico(nome_limpo, mkt)
            
            st.success(f"Termo '{termo_escolhido}' injetado com sucesso! Vá à aba Motor Autônomo ou Sniper de Leads.")

    with col2:
        st.subheader("💡 Sincronização com o Funil de Vendas")
        st.markdown("""
        1. **Captura:** O Google Trends mostra o que o Brasil está a digitar agora.
        2. **Palavras-Passe:** O Nexus extrai esses termos exatos para posicionar nos Pins do Pinterest e nas legendas.
        3. **Conversão:** O lead pesquisa o termo quente, encontra o seu post, comenta "QUERO" e recebe o link do Mercado Livre via ManyChat.
        """)
        
        st.link_button("🌐 Aceder ao Google Trends Oficial", "https://trends.google.com.br/trends/", use_container_width=True)
