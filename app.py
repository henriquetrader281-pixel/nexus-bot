import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os
import re

# --- 1. CONFIGURAÇÃO E SEGURANÇA (Base V58 Estável) ---
st.set_page_config(page_title="Nexus Absolute V68", layout="wide", page_icon="🔱")
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
st.title("🔱 Nexus Brain V68: Multi-Ticket Strategy")

tabs = st.tabs(["🔎 Mineração Estratégica", "🚀 Arsenal de Conteúdo", "🕹️ Central de Disparo"])

for k in ['sel_nome', 'sel_link', 'sel_preco', 'res_busca']:
    if k not in st.session_state: st.session_state[k] = ""

with tabs[0]:
    st.header("🎯 Filtro de Ticket e Sourcing")
    
    col_n, col_t = st.columns([2, 1])
    nicho = col_n.text_input("Nicho:", value="Utilidades")
    tipo_ticket = col_t.selectbox("Perfil do Produto:", ["Baixo (Até R$50)", "Médio (R$50 - R$150)", "Alto (Acima de R$150)"])
    
    if st.button("🔄 Localizar Oportunidades Shopee", use_container_width=True):
        with st.status(f"Minerando produtos de Ticket {tipo_ticket}..."):
            # Prompt reforçado para não quebrar a busca e respeitar o preço
            p = (
                f"Aja como especialista em Shopee Brasil. Liste 5 produtos de {nicho} "
                f"com preço {tipo_ticket}. Foque em itens que estão em alta no TikTok. "
                f"Responda EXATAMENTE neste formato, sem texto adicional: "
                f"PRODUTO: [nome] | PRECO: [valor] | URL: [link]"
            )
            st.session_state.res_busca = gerar_ia(p)
    
    if st.session_state.res_busca:
        # Regex blindada para extração limpa
        items = re.findall(r"PRODUTO:\s*(.*?)\s*\|\s*PRECO:\s*(.*?)\s*\|\s*URL:\s*(https?://\S+)", st.session_state.res_busca)
        
        if items:
            for nome, preco, link in items:
                # Ícones baseados no ticket selecionado
                icon = "🛒" if "Baixo" in tipo_ticket else "⭐" if "Médio" in tipo_ticket else "💎"
                
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"{icon} **{nome.strip()}**")
                c2.write(f"💰 {preco.strip()}")
                if c3.button("Selecionar", key=f"s_{hash(nome)}"):
                    st.session_state.sel_nome, st.session_state.sel_preco, st.session_state.sel_link = nome.strip(), preco.strip(), link.strip()
                    st.toast("Pronto para o Arsenal!")
        else:
            st.error("Falha na extração. A IA não seguiu o formato Shopee.")
            st.info("Resposta da IA: " + st.session_state.res_busca)

with tabs[1]:
    st.header("🚀 Personalização do Arsenal")
    p_n = st.text_input("Produto:", value=st.session_state.sel_nome)
    p_l = st.text_input("Link Original:", value=st.session_state.sel_link)
    
    if st.button("⚡ GERAR 4 VARIAÇÕES", use_container_width=True):
        if p_n and p_l:
            with st.status("Criando copies e roteiros..."):
                aff = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
                link_f = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(p_l)}&aff_id={aff}"
                rots = gerar_ia(f"Crie 4 roteiros curtos para {p_n}. Sep
