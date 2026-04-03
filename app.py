import streamlit as st
from groq import Groq
import pandas as pd
import os
import random
import update  # Módulo de SEO e Escala

st.set_page_config(page_title="Nexus Absolute V71-72", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

# Inicialização do Banco de Dados
if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=["data", "loja", "produto", "link_afiliado", "status", "copy_funil", "horario_previsto"]).to_csv(DATA_PATH, index=False)

client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

def gerar_ia(prompt):
    try:
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content": prompt}])
        return res.choices[0].message.content
    except: return "Erro na conexão com a IA."

st.title("🔱 Nexus Absolute: Monitor de Tendências & Escala")

# --- CRIAÇÃO DAS ABAS (Precisa vir antes de usar 'with tabs') ---
tabs = st.tabs(["🔎 Scanner V71 (BR/EUA)", "🚀 Arsenal SEO 10x", "📊 Performance"])

# --- ABA 0: SCANNER ---
with tabs[0]:
    st.header("Monitor de Produtos Quentes")
    c1, c2 = st.columns([3, 1])
    nicho = c1.text_input("Nicho para Scanner:", value="Utilidades Domésticas")
    ticket = c2.selectbox("Ticket:", ["Baixo", "Médio", "Alto"])
    
    if st.button("🚀 Escanear Shopee & TikTok Trends", use_container_width=True):
        with st.status("Minerando 30 tendências exclusivas Shopee..."):
            p = f"""Aja como um Expert em Shopee Affiliate. 
            Liste 30 produtos virais de {nicho} ({ticket}) que estão bombando no TikTok e Shopee Brasil.
            FORMATO OBRIGATÓRIO PARA CADA ITEM:
            PRODUTO: [nome do item] | TENDENCIA: [% cresc. BR] | CALOR: [0-100] | URL: https://shopee.com.br/exemplo
            Importante: Foque em produtos reais da Shopee Brasil."""
            st.session_state.res_busca = gerar_ia(p)

    if "res_busca" in st.session_state:
        for item in st.session_state.res_busca.split("\n"):
            if "|" in item and "PRODUTO:" in item:
                try:
                    parts = item.split("|")
                    nome = parts[0].replace("PRODUTO:", "").strip()
                    tend = parts[1].replace("TENDENCIA:", "").strip()
                    calor_str = ''.join(filter(str.isdigit, parts[2]))
                    calor = int(calor_str) if calor_str else 50
                    link_orig = parts[3].replace("URL:", "").strip()

                    # Lógica de Mercado Visual
                    is_shopee = "shopee" in link_orig.lower() or "shope.ee" in link_orig.lower()
                    mercado_tag = "Shopee 🟠" if is_shopee else "Outro ⚪"

                    with st.container(border=True):
                        col1, col2, col3 = st.columns([3, 2, 1])
                        with col1:
                            st.write(f"📦 **{nome}**")
                            st.caption(f"🌍 Tendência: {tend}")
                            st.markdown(f"🛒 **Mercado:** {mercado_tag}")
                        with col2:
                            cor = "red" if calor > 80 else "orange"
                            st.write(f"🌡️ Termômetro: :{cor}[{calor}°C]")
                            st.progress(calor / 100)
                        with col3:
                            if st.button("Selecionar", key=f"btn_{nome}_{random.randint(0,9999)}"):
                                st.session_state.sel_nome = nome
                                st.session_state.sel_link = link_orig
                                st.toast(f"✅ {nome} pronto para o Arsenal!")
                except:
                    continue

# --- ABA 1: ARSENAL ---
with tabs[1]:
    st.header("🚀 Gerador de Escala (10 Vídeos)")
    if "sel_nome" in st.session_state:
        st.info(f"Produto Selecionado: **{st.session_state.sel_nome}**")
        if st.button("⚡ INJETAR 10 VARIAÇÕES COM SEO", type="primary"):
            if update.aplicar_seo_viral(st.session_state.sel_nome, st.session_state.sel_link, nicho):
                st.success("🔥 Escala 10x injetada no Agendador!")
                st.balloons()
    else:
        st.warning("Vá ao Scanner e selecione um produto primeiro.")

# --- ABA 2: PERFORMANCE ---
with tabs[2]:
    update.dashboard_performance_simples()
