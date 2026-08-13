import streamlit as st
import datetime

def exibir_agendador():
    st.header("⏰ Agendador Automático de Postagens")
    st.markdown("Programe os seus disparos para os horários de pico (09:00, 12:30 e 19:00) para maximizar o alcance orgânico.")
    
    with st.container(border=True):
        st.subheader("📅 Novo Agendamento")
        produto_auto = st.session_state.get('sel_nome', 'Produto Selecionado')
        st.write(f"**Produto na Fila:** {produto_auto}")
        
        col1, col2 = st.columns(2)
        with col1:
            data_post = st.date_input("Data do Disparo:", datetime.date.today())
        with col2:
            hora_post = st.time_input("Horário de Pico:", datetime.time(19, 0))
            
        plataforma = st.multiselect("Plataformas de Destino:", ["Instagram Reels", "TikTok", "Pinterest (Automático)", "YouTube Shorts"], default=["Instagram Reels"])
        
        if st.button("🚀 AGENDAR DISPARO AUTOMÁTICO", type="primary", use_container_width=True):
            st.success(f"Sucesso! O post para '{produto_auto}' foi agendado para {data_post} às {hora_post} em {', '.join(plataforma)}.")
            st.balloons()
            
    st.divider()
    st.markdown("### 📋 Fila de Agendamentos Ativos")
    st.dataframe({
        "Data/Hora": ["Hoje, 19:00", "Amanhã, 12:30", "Amanhã, 19:00"],
        "Produto": ["Luminária LED", "Smart Mask", "Sunset Lamp"],
        "Plataforma": ["Instagram / TikTok", "Instagram", "Pinterest / TikTok"],
        "Status": ["⏳ Agendado", "⏳ Agendado", "⏳ Agendado"]
    }, use_container_width=True)
