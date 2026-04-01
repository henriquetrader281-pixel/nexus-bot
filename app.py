import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os
import re

# --- 1. CONFIGURAÇÃO DE SEGURANÇA ---
st.set_page_config(page_title="Nexus Absolute V66", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

def carregar_dados():
    if not os.path.exists(DATA_PATH):
        cols = ["data", "produto", "preco", "roteiro", "status", "link_afiliado", "copy_funil"]
        pd.DataFrame(columns=cols).to_csv(DATA_PATH, index=False)
    try:
        return pd.read_csv(DATA_PATH)
    except:
        return pd.DataFrame(columns=["data", "produto", "preco", "roteiro", "status", "link_afiliado", "copy_funil"])

client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

def gerar_ia(prompt):
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role":"user","content": prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Erro: {e}"

# --- 2. INTERFACE ---
st.title("🔱 Nexus Brain V66: Imparável")

tabs = st.tabs(["🔎 Sourcing & Termômetro", "🚀 Arsenal Automático", "🕹️ Central de Disparo"])

# Inicialização de estados
for k in ['sel_nome', 'sel_link', 'sel_preco', 'res_busca']:
    if k not in st.session_state: st.session_state[k] = ""

with tabs[0]:
    st.header("🎯 Inteligência de Mercado")
    nicho = st.text_input("Nicho Alvo:", value="Utilidades Domésticas")
    
    if st.button("🔄 Localizar Oportunidades", use_container_width=True):
        with st.status("Minerando tendências..."):
            # Prompt que força a nota de temperatura
            p = f"Liste 5 produtos de {nicho}. Formato: PRODUTO: [nome] | PRECO: [R$] | URL: [link] | TEMP: [Alta/Media]"
            st.session_state.res_busca = gerar_ia(p)
    
    if st.session_state.res_busca:
        # Regex robusto para capturar os campos
        items = re.findall(r"PRODUTO:\s*(.*?)\s*\|\s*PRECO:\s*(.*?)\s*\|\s*URL:\s*(https?://\S+)", st.session_state.res_busca)
        
        if items:
            for nome, preco, link in items:
                # Lógica de ícones que você pediu
                temp_icon = "🔥 Alta" if "Alta" in st.session_state.res_busca else "📉 Fraco"
                
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"📦 **{nome.strip()}** ({temp_icon})")
                c2.write(f"💰 {preco.strip()}")
                if c3.button("Selecionar", key=f"s_{nome[:10]}_{hash(link)}"):
                    st.session_state.sel_nome = nome.strip()
                    st.session_state.sel_preco = preco.strip()
                    st.session_state.sel_link = link.strip()
                    st.toast("Produto na agulha!")
        else:
            st.error("Erro na leitura dos dados. Tente novamente.")

with tabs[1]:
    st.header("🚀 Arsenal de Vendas")
    p_n = st.text_input("Produto:", value=st.session_state.sel_nome)
    p_l = st.text_input("Link:", value=st.session_state.sel_link)
    
    if st.button("⚡ GERAR 4 VARIAÇÕES", use_container_width=True):
        if p_n and p_l:
            with st.status("Criando conteúdo..."):
                aff = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
                link_f = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(p_l)}&aff_id={aff}"
                rots = gerar_ia(f"Crie 4 roteiros de 15s para {p_n}. Separe por ###").split("###")
                
                df = carregar_dados()
                for i, r in enumerate(rots):
                    if len(r.strip()) > 10:
                        cp = gerar_ia(f"Legenda TikTok viral para: {r}")
                        # Salvamento blindado
                        novo = pd.DataFrame([{"data": datetime.now().strftime("%d/%m"), "produto": f"{p_n} V{i+1}", "preco": st.session_state.sel_preco, "roteiro": r.strip(), "copy_funil": cp.strip(), "link_afiliado": link_f, "status": "PRONTO"}])
                        df = pd.concat([df, novo], ignore_index=True)
                df.to_csv(DATA_PATH, index=False)
                st.success("🔥 Arsenal pronto!")

with tabs[2]:
    st.header("🕹️ Disparo Buffer")
    df_d = carregar_dados()
    fila = df_d[df_d["status"] == "PRONTO"]
    st.metric("Aguardando Envio", len(fila))
    
    if not fila.empty:
        if st.button("🚀 DISPARAR AGORA", type="primary"):
            web = st.secrets.get("WEBHOOK_POSTAGEM")
            for i, row in fila.iterrows():
                # Payload simplificado para o Buffer (Print 11/12)
                payload = {"text": f"{row['copy_funil']}\n\nLink: {row['link_afiliado']}"}
                try:
                    res = requests.post(web, json=payload, timeout=15)
                    if res.status_code < 300:
                        df_d.at[i, "status"] = "ENVIADO"
                except: continue
            df_d.to_csv(DATA_PATH, index=False)
            st.rerun()
