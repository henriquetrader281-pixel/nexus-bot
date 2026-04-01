import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os

# --- 1. SETUP & INFRA (Patches 01-37) ---
st.set_page_config(page_title="Nexus Absolute V37.0", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

# Colunas que mantêm todo o histórico e inteligência
cols = ["data", "produto", "roteiro", "link", "status", "nicho", "score", "views", "cliques", "ctr"]
if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=cols).to_csv(DATA_PATH, index=False)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. MOTORES RECUPERADOS (Pente Fino) ---

def ad_scorer(roteiro): # Patch 30 (Resgate V16)
    prompt = f"Avalie de 0 a 100 a retenção e copy deste roteiro: {roteiro}. Retorne APENAS o número."
    try:
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":prompt}]).choices[0].message.content
        return int(''.join(filter(str.isdigit, res)))
    except: return 75

def limpar_e_converter_link(url): # Patch 17 & 27
    link_limpo = url.split('?')[0]
    my_id = st.secrets.get("SHOPEE_ID", "AGUARDANDO")
    return f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(link_limpo)}&aff_id={my_id}"

# --- 3. INTERFACE COMPLETA ---
st.title("🔱 Nexus Absolute V37.0")
tabs = st.tabs(["🌎 Mineração Global", "🎥 Arsenal & Scoring", "💰 Precificação & ROI", "📊 Escala", "🕹️ Central"])

with tabs[0]: # MINERAÇÃO (BR + EUA)
    st.header("🎯 Inteligência de Mercado")
    nicho_atual = st.text_input("Nicho:", value="Utilidades")
    c1, c2 = st.columns(2)
    if c1.button("🇧🇷 Escanear Brasil"):
        prompt = f"10 produtos virais de {nicho_atual} na Shopee Brasil. Tabela com Link de Busca."
        st.session_state['res_br'] = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":prompt}]).choices[0].message.content
    if c2.button("🇺🇸 Escanear EUA"):
        prompt = f"10 produtos virais no TikTok Shop EUA de {nicho_atual}. Tabela com Link de Busca Shopee."
        st.session_state['res_usa'] = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":prompt}]).choices[0].message.content
    
    col_r1, col_r2 = st.columns(2)
    with col_r1: 
        if 'res_br' in st.session_state: st.markdown(st.session_state['res_br'])
    with col_r2: 
        if 'res_usa' in st.session_state: st.markdown(st.session_state['res_usa'])

with tabs[1]: # ARSENAL (V16 Scorer)
    st.header("🚀 Gerador de Criativos")
    p_nome = st.text_input("Produto:")
    p_link = st.text_input("Link Original:")
    if st.button("🔥 Gerar 5 Roteiros"):
        link_final = limpar_e_converter_link(p_link)
        res_ia = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Crie 5 roteiros para {p_nome}. Separe por ###"}]).choices[0].message.content
        df = pd.read_csv(DATA_PATH)
        for r in res_ia.split("###"):
            if len(r) > 10:
                score = ad_scorer(r)
                novo = {"data": datetime.now().strftime("%d/%m"), "produto": p_nome, "roteiro": r.strip(), "link": link_final, "status": "FILA", "nicho": nicho_atual, "score": score, "views": 0, "cliques": 0, "ctr": 0}
                df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
        df.to_csv(DATA_PATH, index=False)
        st.success("Arsenal Salvo!")

with tabs[2]: # [NOVO: RESGATE DA PRECIFICAÇÃO DO APP 1]
    st.header("📊 Calculadora de Viabilidade (ROI)")
    c1, c2, c3 = st.columns(3)
    venda = c1.number_input("Preço de Venda (R$):", value=89.90)
    custo = c2.number_input("Custo do Produto (R$):", value=35.00)
    imposto = c3.slider("Taxa Shopee/Canal (%):", 0, 20, 14)
    
    lucro_bruto = venda - custo - (venda * (imposto/100))
    margem = (lucro_bruto / venda) * 100
    
    st.divider()
    m1, m2 = st.columns(2)
    m1.metric("Lucro Líquido p/ Unidade", f"R$ {lucro_bruto:.2f}")
    m2.metric("Margem de Lucro", f"{margem:.1f}%")
    
    if lucro_bruto > 20: st.success("✅ Produto Viável para Escala!")
    else: st.warning("⚠️ Margem Apertada. Cuidado com o custo do anúncio.")

with tabs[3]: # ESCALA (V17.5)
    st.header("📊 Métricas de Performance")
    df_p = pd.read_csv(DATA_PATH)
    edited = st.data_editor(df_p)
    if st.button("💾 Salvar & Processar Inteligência"):
        edited["ctr"] = (pd.to_numeric(edited["cliques"]) / pd.to_numeric(edited["views"]) * 100).fillna(0)
        edited.loc[edited["ctr"] >= 3, "status"] = "ESCALA"
        edited.to_csv(DATA_PATH, index=False)
        st.rerun()

with tabs[4]: # CENTRAL (V29)
    st.header("🕹️ Comando Central")
    df_v = pd.read_csv(DATA_PATH)
    fila = df_v[df_v["status"].isin(["FILA", "ESCALA"])]
    if not fila.empty:
        if st.button("▶️ DISPARAR PRÓXIMO"):
            item = fila.iloc[0]
            requests.post(st.secrets["WEBHOOK_POSTAGEM"], json={"texto": item['roteiro'], "link": item['link']})
            df_v.loc[fila.index[0], "status"] = "POSTADO"
            df_v.to_csv(DATA_PATH, index=False)
            st.success(f"Postado: {item['produto']}")
