import streamlit as st
import random
import time

# ── Base de Dados do Radar (Expansível) ──
TRENDS_USA = [
    {"nome": "Projetor Estelar 4K Astronauto", "nicho": "Decoração/Tech", "calor": "98°C", "status": "Explodindo 🔥"},
    {"nome": "Mini Seladora a Vácuo Portátil", "nicho": "Cozinha", "calor": "92°C", "status": "Alta Conversão 🚀"},
    {"nome": "Liquidificador Portátil FreshJuice", "nicho": "Fitness/Saúde", "calor": "88°C", "status": "Viral TikTok 📱"},
    {"nome": "Umidificador Chama de Fogo", "nicho": "Decoração", "calor": "85°C", "status": "Escalando 📈"},
    {"nome": "Smartwatch Militar Indestrutível", "nicho": "Eletrônicos", "calor": "95°C", "status": "Oceano Azul 🌊"}
]

TRENDS_BR = [
    {"nome": "Mop Giratório Slim", "nicho": "Casa/Limpeza", "calor": "99°C", "status": "Top 1 Shopee 🏆"},
    {"nome": "Fone Bluetooth Lenovo XT88", "nicho": "Eletrônicos", "calor": "96°C", "status": "Alta Conversão 🔥"},
    {"nome": "Triturador de Alho Elétrico", "nicho": "Cozinha", "calor": "93°C", "status": "Problema/Solução 🎯"}
]

def renderizar_lista_radar(produtos):
    for p in produtos:
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**{p['nome']}**")
                st.caption(f"🏷️ Nicho: {p['nicho']} | 📊 {p['status']}")
            with c2:
                st.markdown(f"### {p['calor']}")

def exibir_radar():
    st.header("🌍 Inteligência Radar: Espionagem Global")
    col_eua, col_br = st.columns(2)
    
    with col_eua:
        st.subheader("🇺🇸 Radar TikTok USA")
        if st.button("🔍 Iniciar Varredura EUA", use_container_width=True):
            with st.spinner("Conectando aos servidores internacionais..."):
                time.sleep(1.5)
                produtos = random.sample(TRENDS_USA, min(len(TRENDS_USA), 5))
                renderizar_lista_radar(produtos)
                
    with col_br:
        st.subheader("🇧🇷 Radar Brasil")
        if st.button("🔍 Iniciar Varredura Brasil", use_container_width=True):
            with st.spinner("Analisando volume de buscas local..."):
                time.sleep(1.5)
                produtos = random.sample(TRENDS_BR, min(len(TRENDS_BR), 5))
                renderizar_lista_radar(produtos)
