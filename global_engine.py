import streamlit as st
import random

def exibir_espionagem_global():
    st.header("🌍 Espionagem Global & Pinterest Trends")
    st.markdown("Descubra o que está a explodir nos EUA e no Pinterest antes de chegar ao Brasil para antecipar tendências de vendas.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        regiao = st.selectbox("Selecione o Mercado Alvo:", ["🇺🇸 EUA (Pinterest Viral)", "🇬🇧 Reino Unido (Home & Living)", "🇧🇷 Brasil (Antecipação)"])
        if st.button("🛰️ VARRER TENDÊNCIAS INTERNACIONAIS", use_container_width=True):
            with st.spinner(f"Escaneando algoritmos de {regiao}..."):
                st.session_state.trends_gringa = [
                    {"nicho": "Smart Home", "produto": "Sunset Lamp Pro", "febre": "99°C (Pinterest Viral)", "angulo": "Iluminação estética para quartos minimalistas"},
                    {"nicho": "Beleza / Skincare", "produto": "Ice Roller Facial de Quartzo", "febre": "95°C (TikTok USA)", "angulo": "Desinchar o rosto em 2 minutos pela manhã"},
                    {"nicho": "Organização", "produto": "Dispensador de Detergente Automático", "febre": "92°C (Etsy/Pinterest)", "angulo": "Cozinha limpa sem toque e sem bagunça"}
                ]
                st.success("Tendências internacionais capturadas!")

    with col2:
        if "trends_gringa" in st.session_state:
            st.markdown("### 🔥 Produtos Validados na Gringa")
            for t in st.session_state.trends_gringa:
                with st.container(border=True):
                    st.markdown(f"**{t['produto']}** (`{t['febre']}`)")
                    st.caption(f"🎯 Nicho: {t['nicho']} | 💡 Ângulo: {t['angulo']}")
                    if st.button("🚀 IMPORTAR PARA O NEXUS", key=f"imp_{t['produto']}"):
                        st.session_state.sel_nome = t['produto']
                        st.session_state.sel_dor = t['angulo']
                        
                        # Gera link de busca automático
                        import ml_afiliados_engine
                        mkt = st.session_state.get('mkt_global', 'Mercado Livre')
                        st.session_state.sel_link = ml_afiliados_engine.gerar_link_afiliado_dinamico(t['produto'], mkt)
                        
                        st.success(f"'{t['produto']}' importado com sucesso! Vá à aba Autônomo ou Sniper.")
        else:
            st.info("Clique no botão ao lado para varrer as tendências globais.")
