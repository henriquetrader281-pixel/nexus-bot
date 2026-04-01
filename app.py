import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os
import re

# --- 1. CONFIGURAÇÃO SEGURA ---
st.set_page_config(page_title="Nexus Absolute V55", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

def carregar_dados():
    if not os.path.exists(DATA_PATH):
        cols = ["data", "produto", "preco", "roteiro", "status", "link_afiliado", "copy_funil"]
        pd.DataFrame(columns=cols).to_csv(DATA_PATH, index=False)
    return pd.read_csv(DATA_PATH)

def salvar_progresso(df):
    """Garante que o CSV seja fechado corretamente"""
    df.to_csv(DATA_PATH, index=False)

client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

def gerar_ia(prompt):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role":"user","content": prompt}]
    ).choices[0].message.content

# --- 2. INTERFACE ---
st.title("🔱 Nexus Brain V55: Safe-Flow")

tabs = st.tabs(["🔎 Mineração", "🚀 Arsenal Automático", "🕹️ Central de Disparo"])

if 'sel_nome' not in st.session_state: st.session_state.sel_nome = ""
if 'sel_link' not in st.session_state: st.session_state.sel_link = ""
if 'sel_preco' not in st.session_state: st.session_state.sel_preco = ""

with tabs[0]:
    st.header("🎯 Inteligência de Sourcing")
    nicho = st.text_input("Nicho:", value="Utilidades Domésticas")
    if st.button("🔄 Localizar Oportunidades", use_container_width=True):
        with st.status("Minerando..."):
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
                st.toast("Produto Selecionado!")

with tabs[1]:
    st.header("🚀 Arsenal Automático")
    p_n = st.text_input("Produto:", value=st.session_state.sel_nome)
    p_l = st.text_input("Link:", value=st.session_state.sel_link)
    
    if st.button("⚡ GERAR 4 VÍDEOS (Safe-Mode)", use_container_width=True):
        if p_n and p_l:
            with st.status("Processando..."):
                aff_id = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
                link_f = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(p_l)}&aff_id={aff_id}"
                roteiros = gerar_ia(f"Crie 4 roteiros de 15s para {p_n}. Use {st.session_state.sel_preco}. Separe por ###").split("###")
                
                df = carregar_dados()
                for i, rot in enumerate(roteiros):
                    if len(rot) > 10:
                        copy = gerar_ia(f"Crie legenda para: {rot}")
                        novo = pd.DataFrame([{
                            "data": datetime.now().strftime("%d/%m"),
                            "produto": f"{p_n} (V{i+1})", "preco": st.session_state.sel_preco,
                            "roteiro": rot.strip(), "copy_funil": copy,
                            "link_afiliado": link_f, "status": "PRONTO"
                        }])
                        df = pd.concat([df, novo], ignore_index=True)
                salvar_progresso(df)
                st.success("✅ Arsenal Pronto!")

with tabs[2]:
    st.header("🕹️ Disparo (Limpeza de Fila)")
    df_d = carregar_dados()
    fila = df_d[df_d["status"] == "PRONTO"]
    
    st.metric("Vídeos na Fila", len(fila))
    
    if not fila.empty:
        if st.button("🚀 ENVIAR TUDO E LIMPAR FILA", type="primary"):
            webhook = st.secrets.get("WEBHOOK_POSTAGEM")
            progresso = st.progress(0)
            
            for idx, (i, row) in enumerate(fila.iterrows()):
                try:
                    # Envio robusto
                    payload = row.to_dict()
                    r = requests.post(webhook, json=payload, timeout=15)
                    
                    if r.status_code in [200, 201, 202]:
                        df_d.at[i, "status"] = "ENVIADO"
                    else:
                        st.warning(f"Erro no item {i}: Status {r.status_code}")
                except Exception as e:
                    st.error(f"Falha crítica no envio: {e}")
                
                progresso.progress((idx + 1) / len(fila))
            
            salvar_progresso(df_d) # Salva o status "ENVIADO" de uma vez
            st.success("🔥 Fila processada!")
            st.rerun()
