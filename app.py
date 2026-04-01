import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os
import re

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Nexus Absolute V67", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

def carregar_dados():
    if not os.path.exists(DATA_PATH):
        cols = ["data", "produto", "preco", "roteiro", "status", "link_afiliado", "copy_funil"]
        pd.DataFrame(columns=cols).to_csv(DATA_PATH, index=False)
    try: return pd.read_csv(DATA_PATH)
    except: return pd.DataFrame(columns=["data", "produto", "preco", "roteiro", "status", "link_afiliado", "copy_funil"])

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
st.title("🔱 Nexus Brain V67: High Profit Edition")

tabs = st.tabs(["🔎 Mineração High-Ticket", "🚀 Arsenal Automático", "🕹️ Central de Disparo"])

for k in ['sel_nome', 'sel_link', 'sel_preco', 'res_busca']:
    if k not in st.session_state: st.session_state[k] = ""

with tabs[0]:
    st.header("🎯 Sourcing de Alta Conversão")
    nicho = st.text_input("Nicho:", value="Eletrônicos e Casa Inteligente")
    
    if st.button("🔄 Localizar Produtos Premium", use_container_width=True):
        with st.status("Minerando Shopee (Foco em Ticket Alto)..."):
            # Ajuste no Prompt para Precificação Alta e Formato Rígido
            p = (
                f"Aja como um especialista em afiliados Shopee. Liste 5 produtos de {nicho} "
                f"que tenham PREÇO ALTO (acima de R$ 150) e alta busca. "
                f"Responda APENAS seguindo este padrão: "
                f"PRODUTO: [nome] | PRECO: [R$] | URL: [link]"
            )
            st.session_state.res_busca = gerar_ia(p)
    
    if st.session_state.res_busca:
        # Regex blindada para não "quebrar a busca"
        items = re.findall(r"PRODUTO:\s*(.*?)\s*\|\s*PRECO:\s*(.*?)\s*\|\s*URL:\s*(https?://\S+)", st.session_state.res_busca)
        
        if items:
            st.markdown("### 🔥 Oportunidades de Lucro Alto")
            for nome, preco, link in items:
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"💎 **{nome.strip()}**")
                c2.write(f"💰 {preco.strip()}")
                if c3.button("Selecionar", key=f"s_{hash(nome)}"):
                    st.session_state.sel_nome, st.session_state.sel_preco, st.session_state.sel_link = nome.strip(), preco.strip(), link.strip()
                    st.toast("Produto Selecionado!")
        else:
            st.error("A IA não seguiu o formato. Tente minerar novamente.")
            st.info("Resposta bruta: " + st.session_state.res_busca)

with tabs[1]:
    st.header("🚀 Arsenal & Copy")
    p_n = st.text_input("Produto:", value=st.session_state.sel_nome)
    p_l = st.text_input("Link:", value=st.session_state.sel_link)
    
    if st.button("⚡ GERAR 4 VARIAÇÕES", use_container_width=True):
        if p_n and p_l:
            with st.status("Criando arsenal..."):
                aff = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
                link_f = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(p_l)}&aff_id={aff}"
                rots = gerar_ia(f"Crie 4 roteiros de 15s para vender {p_n}. Separe por ###").split("###")
                
                df = carregar_dados()
                for i, r in enumerate(rots):
                    if len(r.strip()) > 10:
                        cp = gerar_ia(f"Legenda TikTok viral (use gatilhos de luxo/valor) para: {r}")
                        novo = pd.DataFrame([{"data": datetime.now().strftime("%d/%m"), "produto": f"{p_n} V{i+1}", "preco": st.session_state.sel_preco, "roteiro": r.strip(), "copy_funil": cp.strip(), "link_afiliado": link_f, "status": "PRONTO"}])
                        df = pd.concat([df, novo], ignore_index=True)
                df.to_csv(DATA_PATH, index=False)
                st.success("🔥 Arsenal pronto!")

with tabs[2]:
    st.header("🕹️ Central de Disparo")
    df_d = carregar_dados()
    fila = df_d[df_d["status"] == "PRONTO"]
    st.metric("Fila de Postagem", len(fila))
    
    if not fila.empty:
        if st.button("🚀 ENVIAR PARA O BUFFER", type="primary"):
            web = st.secrets.get("WEBHOOK_POSTAGEM")
            for i, row in fila.iterrows():
                # Payload otimizado para o Make/Buffer
                payload = {"text": f"{row['copy_funil']}\n\nLink: {row['link_afiliado']}"}
                try:
                    requests.post(web, json=payload, timeout=15)
                    df_d.at[i, "status"] = "ENVIADO"
                except: continue
            df_d.to_csv(DATA_PATH, index=False)
            st.rerun()
