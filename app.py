import streamlit as st
from groq import Groq
import pandas as pd
import os
import update  # Módulo de SEO e Escala

st.set_page_config(page_title="Nexus Absolute V71-72", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

# Inicialização do Banco de Dados
if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=["data", "produto", "preco", "link_afiliado", "status", "copy_funil", "horario_previsto"]).to_csv(DATA_PATH, index=False)

client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

def gerar_ia(prompt):
    try:
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content": prompt}])
        return res.choices[0].message.content
    except: return "Erro na conexão com a IA."

st.title("🔱 Nexus Absolute: Monitor de Tendências & Escala")
tabs = st.tabs(["🔎 Scanner V71 (BR/EUA)", "🚀 Arsenal SEO 10x", "📊 Performance"])

with tabs[0]:
    st.header("Monitor de Produtos Quentes")
    c1, c2 = st.columns([3, 1])
    nicho = c1.text_input("Nicho para Scanner:", value="Utilidades Domésticas")
    ticket = c2.selectbox("Ticket:", ["Baixo", "Médio", "Alto"])
    
    if st.button("🚀 Escanear Shopee & TikTok Trends", use_container_width=True):
        with st.status("Consultando tendências globais..."):
            p = f"""Aja como Analista de E-commerce. Liste 10 produtos de {nicho} ({ticket}). 
            Retorne EXATAMENTE: PRODUTO: [nome] | TENDENCIA: [% cresc. BR/EUA] | CALOR: [0-100] | URL: [link]"""
            st.session_state.res_busca = gerar_ia(p)

    if "res_busca" in st.session_state:
        for item in st.session_state.res_busca.split("\n"):
            if "|" in item:
                parts = item.split("|")
                nome = parts[0].replace("PRODUTO:", "").strip()
                tend = parts[1].replace("TENDENCIA:", "").strip()
                calor = int(''.join(filter(str.isdigit, parts[2])))
                link_orig = parts[3].replace("URL:", "").strip()

                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"📦 **{nome}**")
                        st.caption(f"🌍 Tendência: {tend}")
                    with col2:
                        cor = "red" if calor > 80 else "orange"
                        st.write(f"🌡️ Termômetro: :{cor}[{calor}°C]")
                        st.progress(calor / 100)
                    with col3:
                        if st.button("Selecionar", key=f"sel_{nome}"):
                            st.session_state.sel_nome = nome
                            st.session_state.sel_link = link_orig
                            st.toast("Enviado para o Arsenal!")

with tabs[1]:
    st.header("🚀 Gerador de Escala (10 Vídeos)")
    if "sel_nome" in st.session_state:
        st.info(f"Produto Ativo: {st.session_state.sel_nome}")
        if st.button("⚡ INJETAR 10 VARIAÇÕES COM SEO", type="primary"):
            if update.aplicar_seo_viral(st.session_state.sel_nome, st.session_state.sel_link, nicho):
                st.success("🔥 Escala 10x injetada no Agendador!")
                st.balloons()
    else:
        st.warning("Selecione um produto no Scanner primeiro.")

with tabs[2]:
    update.dashboard_performance_simples()
