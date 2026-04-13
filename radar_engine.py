import streamlit as st
import random
import time

# ── Base de Dados do Radar (Expansível) ───────────────────────────────────
TRENDS_USA = [
    {"nome": "Projetor Estelar 4K Astronauto", "nicho": "Decoração/Tech", "calor": "98°C", "status": "Explodindo 🔥"},
    {"nome": "Mini Seladora a Vácuo Portátil", "nicho": "Cozinha", "calor": "92°C", "status": "Alta Conversão 🚀"},
    {"nome": "Liquidificador Portátil FreshJuice", "nicho": "Fitness/Saúde", "calor": "88°C", "status": "Viral TikTok 📱"},
    {"nome": "Umidificador Chama de Fogo", "nicho": "Decoração", "calor": "85°C", "status": "Escalando 📈"},
    {"nome": "Smartwatch Militar Indestrutível", "nicho": "Eletrónicos", "calor": "95°C", "status": "Oceano Azul 🌊"},
    {"nome": "Máscara de LED Terapia Facial", "nicho": "Beleza", "calor": "89°C", "status": "Alta Margem 💰"},
    {"nome": "Aspirador de Pó Portátil para Carro", "nicho": "Automóvel", "calor": "82°C", "status": "Estável 📊"},
    {"nome": "Corretor Postural Invisível", "nicho": "Saúde", "calor": "90°C", "status": "Alta Demanda 🎯"},
    {"nome": "Cinta Modeladora Térmica", "nicho": "Fitness", "calor": "87°C", "status": "Viral Reels 🎬"},
    {"nome": "Fita LED RGB Rítmica", "nicho": "Setup/Gaming", "calor": "84°C", "status": "Escalando 📈"}
]

TRENDS_BR = [
    {"nome": "Mop Giratório de Limpeza Slim", "nicho": "Casa/Limpeza", "calor": "99°C", "status": "Top 1 Shopee 🏆"},
    {"nome": "Organizador de Acrílico Giratório", "nicho": "Beleza", "calor": "91°C", "status": "Muito Viral 🚀"},
    {"nome": "Fone Bluetooth Lenovo XT88", "nicho": "Eletrónicos", "calor": "96°C", "status": "Alta Conversão 🔥"},
    {"nome": "Kit Utensílios de Silicone (12 Peças)", "nicho": "Cozinha", "calor": "89°C", "status": "Estável 📊"},
    {"nome": "Mini Câmera Espiã Magnética", "nicho": "Segurança", "calor": "94°C", "status": "Oceano Azul 🌊"},
    {"nome": "Depilador a Laser Portátil", "nicho": "Beleza", "calor": "88°C", "status": "Alta Margem 💰"},
    {"nome": "Lâmpada Caixa de Som Bluetooth", "nicho": "Decoração/Tech", "calor": "85°C", "status": "Escalando 📈"},
    {"nome": "Triturador de Alho Elétrico", "nicho": "Cozinha", "calor": "93°C", "status": "Problema/Solução 🎯"},
    {"nome": "Relógio Smartwatch D20", "nicho": "Acessórios", "calor": "97°C", "status": "Campeão de Vendas 🏅"},
    {"nome": "Tapete Mágico Super Absorvente", "nicho": "Casa", "calor": "90°C", "status": "Viral TikTok 📱"}
]

def renderizar_lista_radar(produtos):
    """Gera o visual de cada produto no radar"""
    for p in produtos:
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**{p['nome']}**")
                st.caption(f"🏷️ Nicho: {p['nicho']} | 📊 {p['status']}")
            with c2:
                st.markdown(f"### {p['calor']}")
                if st.button("Copiar", key=f"copy_{p['nome']}"):
                    st.toast(f"Nome copiado para o Scanner!")

def exibir_radar():
    st.header("🌍 Inteligência Radar: Espionagem Global")
    st.write("Varredura em tempo real dos produtos que estão a viralizar nas plataformas de vídeos curtos.")
    
    col_eua, col_br = st.columns(2)
    
    with col_eua:
        st.subheader("🇺🇸 Radar TikTok USA")
        st.caption("Foco: Produtos virais com potencial de importação.")
        
        if st.button("🔍 Iniciar Varredura USA", width='stretch'):
            with st.spinner("Conectando aos servidores internacionais..."):
                time.sleep(1.5) # Simula o tempo de busca
                produtos_selecionados = random.sample(TRENDS_USA, 5) # Escolhe 5 aleatórios
                st.success("✅ 5 Tendências quentes encontradas!")
                renderizar_lista_radar(produtos_selecionados)
                
    with col_br:
        st.subheader("🇧🇷 Radar Shopee/Mercado Livre")
        st.caption("Foco: Alto volume de buscas no mercado local.")
        
        if st.button("🔍 Iniciar Varredura Brasil", width='stretch'):
            with st.spinner("Analisando algoritmo de recomendação..."):
                time.sleep(1.5)
                produtos_selecionados = random.sample(TRENDS_BR, 5) # Escolhe 5 aleatórios
                st.success("✅ 5 Tendências locais encontradas!")
                renderizar_lista_radar(produtos_selecionados)
