import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os

# --- [PATCH 34: DATASET PERSISTENTE] ---
st.set_page_config(page_title="Nexus Absolute V36.0", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

# Colunas consolidadas (Patches 25-36)
cols = ["data", "produto", "roteiro", "link", "status", "nicho", "score", "cliques", "views", "ctr"]
if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=cols).to_csv(DATA_PATH, index=False)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- [PATCH 30: AD SCORER ENGINE] ---
def ad_scorer(roteiro):
    prompt = f"Avalie a retenção e CTA deste roteiro (0-100): {roteiro}. Responda apenas o número."
    try:
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":prompt}]).choices[0].message.content
        return int(''.join(filter(str.isdigit, res)))
    except: return 75

# --- [PATCH 27: DEEPLINK TRACKING] ---
def converter_link(url):
    link_limpo = url.split('?')[0]
    my_id = st.secrets.get("SHOPEE_ID", "SEM_ID")
    return f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(link_limpo)}&aff_id={my_id}"

# --- [PATCH 25: GATILHOS DE RETENÇÃO] ---
def aplicar_gatilhos(texto, nicho):
    tags = f"\n\n#achadinhos #shopee #viral #{nicho.lower()}"
    return f"{texto.strip()}\n\nComenta 'EU QUERO' para o link! 🔥{tags}"

# --- INTERFACE ABSOLUTE ---
st.title("🔱 Nexus Absolute: Patches 25-36 Ativos")
tabs = st.tabs(["🌎 [31] Mineração Global", "🎥 [26] Arsenal & Funil", "📊 [33] Escala & ROI", "🕹️ [28] Central"])

with tabs[0]: # PATCH 31 & 32
    st.header("🎯 Tendências BR & EUA")
    nicho = st.text_input("Nicho Alvo:", value="Cozinha")
    c1, c2 = st.columns(2)
    
    if c1.button("🇧🇷 Escanear Brasil"):
        prompt = f"10 produtos buscados na Shopee Brasil de {nicho}. Tabela com Link de Busca Shopee."
        st.session_state['res_br'] = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":prompt}]).choices[0].message.content
    
    if c2.button("🇺🇸 Escanear EUA"):
        prompt = f"10 virais TikTok Shop EUA de {nicho}. Tabela com Link de Busca Shopee."
        st.session_state['res_usa'] = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":prompt}]).choices[0].message.content
    
    col_r1, col_r2 = st.columns(2)
    with col_r1: 
        if 'res_br' in st.session_state: st.markdown(st.session_state['res_br'])
    with col_r2: 
        if 'res_usa' in st.session_state: st.markdown(st.session_state['res_usa'])

with tabs[1]: # PATCH 26 & 30
    st.header("🚀 Arsenal de Guerra")
    p_nome = st.text_input("Produto:")
    p_link = st.text_input("Link Shopee:")
    
    if st.button("🔥 Gerar Arsenal (5 Variações)"):
        link_final = converter_link(p_link)
        res_ia = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Crie 5 roteiros TikTok para {p_nome}. Separe por '###' "}]).choices[0].message.content
        
        df = pd.read_csv(DATA_PATH)
        for r in res_ia.split("###"):
            if len(r) > 10:
                score = ad_scorer(r)
                roteiro_final = aplicar_gatilhos(r, nicho)
                # [PATCH 35: SYNTAX SHIELD]
                novo = {
                    "data": datetime.now().strftime("%d/%m"), "produto": p_nome,
                    "roteiro": roteiro_final, "link": link_final, "status": "TESTE",
                    "nicho": nicho, "score": score, "cliques": 0, "views": 0, "ctr": 0
                }
                df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
        df.to_csv(DATA_PATH, index=False)
        st.success("Salvo!")

with tabs[2]: # PATCH 33
    st.header("📊 Inteligência de Escala")
    df_perf = pd.read_csv(DATA_PATH)
    edited = st.data_editor(df_perf)
    if st.button("💾 Processar ROI"):
        edited["ctr"] = (pd.to_numeric(edited["cliques"]) / pd.to_numeric(edited["views"]) * 100).fillna(0)
        edited.loc[edited["ctr"] >= 3, "status"] = "ESCALA"
        edited.to_csv(DATA_PATH, index=False)
        st.rerun()

with tabs[3]: # PATCH 28
    st.header("🕹️ Comando Central")
    df_v = pd.read_csv(DATA_PATH)
    fila = df_v[df_v["status"].isin(["TESTE", "ESCALA"])]
    
    if not fila.empty:
        if st.button("▶️ DISPARAR PRÓXIMO"):
            item = fila.iloc[0]
            requests.post(st.secrets["WEBHOOK_POSTAGEM"], json={"texto": item['roteiro'], "link": item['link']})
            df_v.loc[fila.index[0], "status"] = "POSTADO"
            df_v.to_csv(DATA_PATH, index=False)
            st.success(f"Postado: {item['produto']}")
            st.rerun()
