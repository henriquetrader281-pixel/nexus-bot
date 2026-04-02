import streamlit as st
from groq import Groq
import pandas as pd
import os
import update  # Importa o seu novo módulo de SEO/Escala

st.set_page_config(page_title="Nexus Absolute V72", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

# Inicializa o banco se não existir
if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=["data", "produto", "preco", "roteiro", "status", "link_afiliado", "copy_funil", "horario_previsto"]).to_csv(DATA_PATH, index=False)

client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

def gerar_ia(prompt):
    try:
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content": prompt}])
        return res.choices[0].message.content
    except: return "Erro na conexão com a IA."

st.title("🔱 Nexus Brain V72: Painel de Controle")
tabs = st.tabs(["🔎 Mineração", "🚀 Arsenal de Elite", "📊 Performance"])

with tabs[0]:
    c1, c2 = st.columns([3, 1])
    nicho = c1.text_input("Nicho SEO:", value="Utilidades")
    ticket = c2.selectbox("Ticket:", ["Baixo", "Médio", "Alto"])
    
    if st.button("🔄 Iniciar Mineração de Escala", use_container_width=True):
        with st.status("Minerando tendências..."):
            p = f"Liste 15 produtos de {nicho} com ticket {ticket}. Responda: PRODUTO: [nome] | PRECO: [valor] | URL: [link]"
            st.session_state.res_busca = gerar_ia(p)
            st.write(st.session_state.res_busca)

with tabs[1]:
    st.header("🚀 Gerador de Escala 10x")
    p_nome = st.text_input("Produto Selecionado:")
    p_link = st.text_input("Link Original:")
    
    if st.button("⚡ GERAR 10 VARIAÇÕES COM SEO", type="primary"):
        # CHAMA O UPDATE EXTERNO PARA NÃO POLUIR O CÓDIGO FONTE
        sucesso = update.aplicar_seo_viral(p_nome, p_link, "Sob consulta", nicho)
        if sucesso:
            st.success(f"🔥 10 variações de '{p_nome}' injetadas no Agendador com Sub_ID!")
            st.balloons()

with tabs[2]:
    update.dashboard_performance_simples()
