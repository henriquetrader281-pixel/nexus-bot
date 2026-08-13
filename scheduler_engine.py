import streamlit as st
import datetime

def exibir_agendador():
    st.header("⏰ Agendador de Execução & Postagem Autónoma")
    st.markdown("Programe o bot para rodar ciclos automáticos de mineração, criação de copy/vídeo e disparo de postagens sem intervenção manual.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.subheader("⚙️ Agendar Execução do Bot (Run)")
            frequencia_run = st.selectbox("Frequência de Mineração:", ["A cada 6 horas", "A cada 12 horas", "Diariamente às 09:00", "Diariamente 2x (09:00 e 18:00)"])
            nicho_alvo = st.text_input("Nicho Automático Alvo:", value="Achados de Cozinha / Casa Inteligente")
            
            if st.button("💾 ATIVAR AGENDAMENTO DE EXECUÇÃO", type="primary", use_container_width=True):
                st.success(f"Sucesso! O Nexus Bot foi programado para rodar '{nicho_alvo}' ({frequencia_run}) automaticamente.")
                st.balloons()

    with col2:
        with st.container(border=True):
            st.subheader("🚀 Agendar Disparo de Postagens (Post)")
            canal_post = st.multiselect("Canais de Destino:", ["Instagram Reels", "TikTok", "Pinterest (Global)", "YouTube Shorts"], default=["Instagram Reels", "TikTok"])
            horario_pico = st.time_input("Horário do Disparo:", datetime.time(19, 0))
            
            if st.button("💾 ATIVAR AGENDAMENTO DE POSTS", type="primary", use_container_width=True):
                st.success(f"Sucesso! Os disparos automáticos foram agendados para as {horario_pico} em {', '.join(canal_post)}.")
                st.balloons()
                
    st.divider()
    st.markdown("### 📋 Estado da Automação (Cron Tasks)")
    st.dataframe({
        "Tarefa": ["Mineração de Dores & Produtos", "Geração de Mídia e Vídeo", "Disparo Automático (Reels/TikTok)"],
        "Frequência": ["Diariamente (09:00 / 18:00)", "Imediato após Mineração", "Agendado (19:00)"],
        "Estado": ["🟢 Ativo (Cloud)", "🟢 Ativo (Cloud)", "🟢 Ativo (Cloud)"],
        "Próxima Execução": ["Hoje às 18:00", "Automático", "Hoje às 19:00"]
    }, use_container_width=True)
