import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os
import re

# --- 1. CONFIGURAÇÃO (Base V58 Estável) ---
st.set_page_config(page_title="Nexus Absolute V69", layout="wide", page_icon="🔱")
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
st.title("🔱 Nexus Brain V69: Estratégia de Ticket")

tabs = st.tabs(["🔎 Mineração Por Ticket", "🚀 Arsenal Automático", "🕹️ Central de Disparo"])

for k in ['sel_nome', 'sel_link', 'sel_preco', 'res_busca']:
    if k not in st.session_state: st.session_state[k] = ""

with tabs[0]:
    st.header("🎯 Sourcing Inteligente")
    c1, c2 = st.columns([2, 1])
    nicho = c1.text_input("Nicho:", value="Utilidades")
    ticket = c2.selectbox("Ticket Médio:", ["Baixo (Até R$50)", "Médio (R$50-R$150)", "Alto (Acima de R$150)"])
    
    if st.button("🔄 Localizar Oportunidades", use_container_width=True):
        with st.status(f"Buscando produtos de ticket {ticket}..."):
            # Prompt reforçado para não quebrar a busca
            p = (
                f"Aja como especialista em Shopee Brasil. Liste 5 produtos de {nicho} "
                f"com preço {ticket}. "
                f"Responda APENAS: PRODUTO: [nome] | PRECO: [valor] | URL: [link]"
            )
            st.session_state.res_busca = gerar_ia(p)
    
    if st.session_state.res_busca:
        items = re.findall(r"PRODUTO:\s*(.*?)\s*\|\s*PRECO:\s*(.*?)\s*\|\s*URL:\s*(https?://\S+)", st.session_state.res_busca)
        if items:
            for nome, preco, link in items:
                # Ícones por valor
                icon = "🛒" if "Baixo" in ticket else "⭐" if "Médio" in ticket else "💎"
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.write(f"{icon} **{nome.strip()}**")
                col2.write(f"💰 {preco.strip()}")
                if col3.button("Selecionar", key=f"s_{hash(nome)}"):
                    st.session_state.sel_nome, st.session_state.sel_preco, st.session_state.sel_link = nome.strip(), preco.strip(), link.strip()
                    st.toast("Selecionado!")
        else:
            st.error("Busca quebrou. Tente novamente.")

with tabs[1]:
    st.header("🚀 Arsenal de Vendas")
    p_n = st.text_input("Produto:", value=st.session_state.sel_nome)
    p_l = st.text_input("Link:", value=st.session_state.sel_link)
    
    if st.button("⚡ GERAR 4 VARIAÇÕES", use_container_width=True):
        if p_n and p_l:
            with st.status("IA em ação..."):
                aff = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
                link_f = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(p_l)}&aff_id={aff}"
                # FIX: Linha 88 corrigida para não dar SyntaxError
                rots = gerar_ia(f"Crie 4 roteiros de 15s para vender {p_n}. Separe por ###").split("###")
                
                df = carregar_dados()
                for i, r in enumerate(rots):
                    if len(r.strip()) > 10:
                        cp = gerar_ia(f"Legenda viral curta para TikTok: {r}")
                        # Salvamento blindado
                        novo = pd.DataFrame([{"data": datetime.now().strftime("%d/%m"), "produto": f"{p_n} V{i+1}", "preco": st.session_state.sel_preco, "roteiro": r.strip(), "copy_funil": cp.strip(), "link_afiliado": link_f, "status": "PRONTO"}])
                        df = pd.concat([df, novo], ignore_index=True)
                df.to_csv(DATA_PATH, index=False)
                st.success("🔥 Arsenal pronto!")

with tabs[2]:
    st.header("🕹️ Central de Disparo")
    df_d = carregar_dados()
    fila = df_d[df_d["status"] == "PRONTO"]
    st.metric("Fila", len(fila))
    
    if not fila.empty:
        if st.button("🚀 ENVIAR TUDO", type="primary"):
            web = st.secrets.get("WEBHOOK_POSTAGEM")
            for i, row in fila.iterrows():
                # Payload otimizado para o Buffer (Print d5fb71)
                payload = {"text": f"{row['copy_funil']}\n\nLink: {row['link_afiliado']}"}
                try:
                    requests.post(web, json=payload, timeout=15)
                    df_d.at[i, "status"] = "ENVIADO"
                except: continue
            df_d.to_csv(DATA_PATH, index=False)
            st.rerun()
