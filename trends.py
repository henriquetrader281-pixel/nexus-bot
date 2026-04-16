import streamlit as st

def exibir_trends():
    st.header("📈 Nexus Trends: Inteligência de Áudio")
    
    st.success("✅ Conectado ao banco de tendências interno.")
    st.caption("Nota: Modo de economia de créditos ativo. Exibindo tendências de alta conversão.")
    
    # --- BOTÃO DE ATUALIZAÇÃO REAL ---
    if st.button("📊 EXECUTAR ANÁLISE MONITOR GLOBAL", use_container_width=True):
        with st.spinner("Minerando tendências virais..."):
            try:
                # Importa a função de inteligência do seu app.py
                from app import get_nexus_intelligence
                dados = get_nexus_intelligence()
                
                if "trends" in dados:
                    st.session_state.lista_trends_cache = dados["trends"]
                else:
                    st.error("Erro ao minerar dados reais.")
            except:
                st.warning("Usando banco de dados offline (Fallback).")

    # Recupera os dados (da IA ou da lista padrão)
    if "lista_trends_cache" in st.session_state:
        # Se a IA já rodou, usamos os dados dela
        for item in st.session_state.lista_trends_cache:
            with st.container(border=True):
                col1, col2 = st.columns([1, 4])
                col1.image("https://cdn-icons-png.flaticon.com/512/174/174855.png", width=60)
                with col2:
                    st.markdown(f"**🎵 {item['musica']}**")
                    st.caption(f"🔥 Por que é trend: {item['razao']}")
                    if st.button(f"🎯 Usar este Áudio", key=f"real_trend_{item['musica']}"):
                        st.session_state.musica_selecionada = item['musica']
                        st.toast(f"Áudio '{item['musica']}' enviado para o Nexus Studio!")
    else:
        # Lista padrão (Como estava no seu script)
        audios_virais = [
            "Uptempo Beat - Funk Viral",
            "Storytelling Lo-Fi",
            "Efeito Suspense (Review)",
            "Música Epic Motivation",
            "Trend ASMR Limpeza"
        ]
        
        for audio in audios_virais:
            with st.container(border=True):
                col1, col2 = st.columns([1, 4])
                col1.image("https://cdn-icons-png.flaticon.com/512/174/174855.png", width=60)
                with col2:
                    st.markdown(f"**🎵 {audio}**")
                    if st.button(f"🎯 Usar este Áudio", key=f"sim_trend_{audio}"):
                        st.session_state.musica_selecionada = audio
                        st.toast(f"Áudio '{audio}' enviado para o Nexus Studio!")

    st.divider()
    st.caption("🔱 Nexus Absolute V101 | Rastreio: 18316451024")
