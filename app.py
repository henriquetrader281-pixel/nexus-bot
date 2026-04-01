import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os
import re
import json

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Nexus Absolute V57", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

def carregar_dados():
    if not os.path.exists(DATA_PATH):
        cols = ["data", "produto", "preco", "roteiro", "status", "link_afiliado", "copy_funil"]
        pd.DataFrame(columns=cols).to_csv(DATA_PATH, index=False)
    return pd.read_csv(DATA_PATH)

client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

def gerar_ia(prompt):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role":"user","content": prompt}]
    ).choices[0].message.content

# --- 2. INTERFACE ---
st.title("🔱 Nexus Brain V57: Conexão Buffer/TikTok")

tabs = st.tabs(["🔎 Mineração", "🚀 Arsenal Automático", "🕹️ Central de Disparo"])

if 'sel_nome' not in st.session_state: st.session_state.sel_nome = ""
if 'sel_link' not in st.session_state: st.session_state.sel_link = ""
if 'sel_preco' not in st.session_state: st.session_state.sel_preco = ""

with tabs[0]:
    st.header("🎯 Sourcing Estratégico")
    nicho = st.text_input("Nicho:", value="Utilidades Domésticas")
    if st.button("🔄 Localizar Oportunidades", use_container_width=True):
        with st.status("Varrendo mercado..."):
            prompt = f"Liste 5 produtos virais para {nicho}. Formato: PRODUTO: [nome] | PRECO: [R$] | URL: [link]"
            st.session_state['res_busca'] = gerar_ia(prompt)

    if 'res_busca' in st.session_state:
        padrao = r"PRODUTO:\s*(.*?)\s*\|\s*PRECO:\s*(.*?)\s*\|\s*URL:\s*(https?://\S+)"
        matches = re.findall(padrao, st.session_state['res_busca'])
        for nome, preco, link in matches:
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"🔹 {nome}")
            c2.write(f"💰 {preco}")
            if c3.button("Selecionar", key=f"s_{nome}"):
                st.session_state.sel_nome, st.session_state.sel_link, st.session_state.sel_preco = nome, link, preco

with tabs[1]:
    st.header("🚀 Arsenal & Copywriting")
    p_n = st.text_input("Produto:", value=st.session_state.sel_nome)
    p_l = st.text_input("Link:", value=st.session_state.sel_link)
    
    if st.button("⚡ GERAR 4 Variações para Buffer", use_container_width=True):
        if p_n and p_l:
            with st.status("IA Gerando Legendários..."):
                aff_id = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
                link_f = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(p_l)}&aff_id={aff_id}"
                roteiros = gerar_ia(f"Crie 4 roteiros de 15s para {p_n}. Preço: {st.session_state.sel_preco}. Separe por ###").split("###")
                
                df = carregar_dados()
                for i, rot in enumerate(roteiros):
                    if len(rot) > 10:
                        copy = gerar_ia(f"Crie uma legenda viral de TikTok com hashtags para: {rot}")
                        novo = pd.DataFrame([{
                            "data": datetime.now().strftime("%d/%m"),
                            "produto": f"{p_n} (V{i+1})", "preco": st.session_state.sel_preco,
                            "roteiro": rot.strip(), "copy_funil": copy.strip(),
                            "link_afiliado": link_f, "status": "PRONTO"
                        }])
                        df = pd.concat([df, novo], ignore_index=True)
                df.to_csv(DATA_PATH, index=False)
                st.success("✅ Arsenal Pronto para Disparo!")

with tabs[2]:
    st.header("🕹️ Disparo (Make ➔ Buffer)")
    df_d = carregar_dados()
    fila = df_d[df_d["status"] == "PRONTO"]
    
    st.metric("Vídeos na Fila para Buffer", len(fila))
    
    if not fila.empty:
        if st.button("🚀 ENVIAR TUDO AGORA", type="primary"):
            webhook = st.secrets.get("WEBHOOK_POSTAGEM")
            for i, row in fila.iterrows():
                try:
                    # Payload otimizado para o Buffer reconhecer
                    payload = {
                        "text": f"{row['copy_funil']}\n\nLink: {row['link_afiliado']}",
                        "product_name": row['produto'],
                        "script": row['roteiro'],
                        "price": row['preco']
                    }
                    r = requests.post(webhook, json=payload, timeout=15)
                    if r.status_code in [200, 201, 202]:
                        df_d.at[i, "status"] = "ENVIADO"
                except: continue
            df_d.to_csv(DATA_PATH, index=False)
            st.success("🔥 Enviado para o Make! Verifique o Buffer.")
            st.rerun()
