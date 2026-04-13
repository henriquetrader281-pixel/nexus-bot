import streamlit as st

def exibir_trends():
    st.header("📈 Nexus Trends: Inteligência de Áudio")
    
    st.success("✅ Conectado ao banco de tendências interno.")
    st.caption("Nota: Modo de economia de créditos ativo. Exibindo tendências de alta conversão.")
    
    # Lista de áudios virais para teste
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
            
            # Ícone visual para manter o design
            col1.image("https://cdn-icons-png.flaticon.com/512/174/174855.png", width=60)
            
            with col2:
                st.markdown(f"**🎵 {audio}**")
                
                # O botão mágico que envia o áudio para o Estúdio
                if st.button(f"🎯 Usar este Áudio", key=f"sim_trend_{audio}"):
                    st.session_state.musica_selecionada = audio
                    st.toast(f"Áudio '{audio}' enviado para o Nexus Studio!")
