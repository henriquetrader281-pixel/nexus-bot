import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os

# --- 1. INFRAESTRUTURA & PERSISTÊNCIA (Pach 34) ---
st.set_page_config(page_title="Nexus Absolute V39.0", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

# Colunas que guardam toda a inteligência dos Pachs 01-39
cols = ["data", "produto", "roteiro", "copy", "link", "status", "nicho", "score", "views", "cliques", "ctr"]
if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=cols).to_csv(DATA_PATH, index=False)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. MOTORES DE INTELIGÊNCIA REATIVADOS ---

def gerar_ia(prompt):
    return client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":prompt}]).choices[0].message.content

def ad_scorer(roteiro): # Motor V16 [Pach 30]
    try:
        res = gerar_ia(f"Nota 0-100 para retenção deste roteiro: {roteiro}. Retorne apenas o número.")
        return int(''.join(filter(str.isdigit, res)))
    except: return 75

def converter_link(url): # DeepLink [Pach 27]
    link_limpo = url.split('?')[0]
    my_id = st.secrets.get("SHOPEE_ID", "AGUARDANDO")
    return f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(link_limpo)}&aff_id={my_id}"

# --- 3. INTERFACE OPERACIONAL ---
st.title("🔱 Nexus Absolute: Full Integration")
tabs = st.tabs(["🌎 Mineração Global", "💰 ROI & Preço", "🎥 Arsenal & Copy", "🕹️ Central de Vídeo", "📊 Escala"])

with tabs[0]: # MINERAÇÃO (Pach 31/32)
    st.header("🎯 Tendências Shopee & EUA")
    nicho = st.text_input("Nicho:", value="Cozinha")
    c1, c2 = st.columns(2)
    if c1.button("🇧🇷 Buscar no Brasil"):
        st.session_state['m_br'] = gerar_ia(f"10 produtos virais Shopee Brasil de {nicho}. Tabela com Link de Busca.")
    if c2.button("🇺🇸 Buscar nos EUA"):
        st.session_state['m_usa'] = gerar_ia(f"10 virais TikTok Shop EUA de {nicho}. Tabela com Link de Busca Shopee.")
    
    res1, res2 = st.columns(2)
    with res1: 
        if 'm_br' in st.session_state: st.markdown(st.session_state['m_br'])
    with res2: 
        if 'm_usa' in st.session_state: st.markdown(st.session_state['m_usa'])

with tabs[1]: # PRECIFICAÇÃO [Pach 37 - Resgatado]
    st.header("📊 Viabilidade Financeira")
    col1, col2, col3 = st.columns(3)
    v_venda = col1.number_input("Preço de Venda (R$):", value=99.00)
    v_custo = col2.number_input("Custo Produto (R$):", value=30.00)
    v_taxa = col3.slider("Taxa Canal (%):", 0, 20, 14)
    lucro = v_venda - v_custo - (v_venda * (v_taxa/100))
    st.metric("Lucro Líquido por Venda", f"R$ {lucro:.2f}", delta=f"{(lucro/v_venda)*100:.1f}% Margem")

with tabs[2]: # ARSENAL & COPY [Pach 26/30/38]
    st.header("🚀 Geração de Conteúdo Viral")
    p_nome = st.text_input("Nome do Produto:")
    p_link = st.text_input("Link Shopee:")
    
    if st.button("🔥 Gerar Arsenal Completo (Roteiro + Copy)"):
        link_f = converter_link(p_link)
        res_roteiros = gerar_ia(f"Crie 3 roteiros TikTok para {p_nome}. Separe por ###")
        df = pd.read_csv(DATA_PATH)
        
        for rot in res_roteiros.split("###"):
            if len(rot) > 10:
                score = ad_scorer(rot)
                copy = gerar_ia(f"Crie uma legenda viral com emojis e hashtags para: {rot}")
                novo = {
                    "data": datetime.now().strftime("%d/%m"), "produto": p_nome,
                    "roteiro": rot.strip(), "copy": copy, "link": link_f,
                    "status": "FILA", "nicho": nicho, "score": score,
                    "views": 0, "cliques": 0, "ctr": 0
                }
                df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                st.write(f"✅ **Score: {score}** - {rot[:50]}...")
        df.to_csv(DATA_PATH, index=False)
        st.success("Arsenal pronto!")

with tabs[3]: # CENTRAL DE VÍDEO [Pach 38 - Resgatado]
    st.header("🕹️ Central de Comando Nexus")
    df_v = pd.read_csv(DATA_PATH)
    fila = df_v[df_v["status"].isin(["FILA", "ESCALA"])]
    if not fila.empty:
        item = fila.iloc[0]
        st.info(f"Próximo: {item['produto']} | Score: {item['score']}")
        st.text_area("Copy Gerada:", item['copy'], height=100)
        
        if st.button("🎬 DISPARAR GERAÇÃO DE VÍDEO", type="primary", use_container_width=True):
            payload = {"comando": "GERAR_VIDEO", "roteiro": item['roteiro'], "copy": item['copy'], "link": item['link']}
            requests.post(st.secrets["WEBHOOK_POSTAGEM"], json=payload)
            df_v.loc[fila.index[0], "status"] = "POSTADO"
            df_v.to_csv(DATA_PATH, index=False)
            st.rerun()

with tabs[4]: # ESCALA [Pach 33]
    st.header("📊 Inteligência de Performance")
    df_e = pd.read_csv(DATA_PATH)
    edited = st.data_editor(df_e)
    if st.button("💾 Atualizar ROI"):
        edited["ctr"] = (pd.to_numeric(edited["cliques"]) / pd.to_numeric(edited["views"]) * 100).fillna(0)
        edited.loc[edited["ctr"] >= 3, "status"] = "ESCALA"
        edited.to_csv(DATA_PATH, index=False)
        st.rerun()
