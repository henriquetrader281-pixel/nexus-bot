import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os
import re

# --- 1. CONFIGURAÇÃO E ENGINE ---
st.set_page_config(page_title="Nexus Absolute V58", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

def carregar_dados():
    if not os.path.exists(DATA_PATH):
        cols = ["data", "produto", "preco", "roteiro", "status", "link_afiliado", "copy_funil"]
        pd.DataFrame(columns=cols).to_csv(DATA_PATH, index=False)
    return pd.read_csv(DATA_PATH)

client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

def gerar_ia(prompt):
    try:
        return client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role":"user","content": prompt}]
        ).choices[0].message.content
    except Exception as e:
        return f"Erro na IA: {e}"

# --- 2. INTERFACE ---
st.title("🔱 Nexus Brain V58: Varredura Blindada")

tabs = st.tabs(["🔎 Mineração Real-Time", "🚀 Arsenal Automático", "🕹️ Central de Disparo"])

# Reset de estados se necessário
for key in ['sel_nome', 'sel_link', 'sel_preco', 'res_busca']:
    if key not in st.session_state: st.session_state[key] = ""

with tabs[0]:
    st.header("🎯 Sourcing Estratégico")
    nicho = st.text_input("Defina o Nicho:", value="Utilidades Domésticas")
    
    if st.button("🔄 Localizar Oportunidades Agora", use_container_width=True):
        with st.status("Varrendo mercado..."):
            # Prompt ultra-rígido para não dar erro de leitura
            prompt = (
                f"Liste 5 produtos virais de {nicho} na Shopee Brasil. "
                f"Siga EXATAMENTE este formato: "
                f"PRODUTO: [nome] | PRECO: [valor] | URL: [link]"
            )
            st.session_state.res_busca = gerar_ia(prompt)
    
    if st.session_state.res_busca:
        # Busca por padrões no texto da IA
        padrao = r"PRODUTO:\s*(.*?)\s*\|\s*PRECO:\s*(.*?)\s*\|\s*URL:\s*(https?://\S+)"
        matches = re.findall(padrao, st.session_state.res_busca)
        
        if matches:
            st.markdown("### ✅ Resultados Encontrados:")
            for nome, preco, link in matches:
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"📦 **{nome}**")
                c2.write(f"💰 {preco}")
                if c3.button("Selecionar", key=f"btn_{nome}"):
                    st.session_state.sel_nome = nome
                    st.session_state.sel_preco = preco
                    st.session_state.sel_link = link
                    st.toast(f"{nome} selecionado!")
        else:
            st.error("Não consegui extrair os links. Tente novamente ou mude o nicho.")
            st.info("Resposta da IA: " + st.session_state.res_busca)

with tabs[1]:
    st.header("🚀 Arsenal & Copywriting")
    col1, col2 = st.columns(2)
    p_n = col1.text_input("Produto:", value=st.session_state.sel_nome)
    p_l = col2.text_input("Link Original:", value=st.session_state.sel_link)
    
    if st.button("⚡ GERAR 4 Variações (Buffer Format)", use_container_width=True):
        if p_n and p_l:
            with st.status("Processando IA..."):
                aff_id = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
                link_f = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(p_l)}&aff_id={aff_id}"
                
                # Gera as variações
                roteiros = gerar_ia(f"Crie 4 roteiros de 15s para {p_n} ({st.session_state.sel_preco}). Separe por ###").split("###")
                
                df = carregar_dados()
                for i, rot in enumerate(roteiros):
                    if len(rot.strip()) > 10:
                        copy = gerar_ia(f"Crie legenda viral para TikTok: {rot}")
                        # Salvamento em DataFrame para evitar erro de sintaxe
                        novo_item = pd.DataFrame([{
                            "data": datetime.now().strftime("%d/%m"),
                            "produto": f"{p_n} (V{i+1})", "preco": st.session_state.sel_preco,
                            "roteiro": rot.strip(), "copy_funil": copy.strip(),
                            "link_afiliado": link_f, "status": "PRONTO"
                        }])
                        df = pd.concat([df, novo_item], ignore_index=True)
                df.to_csv(DATA_PATH, index=False)
                st.success("🔥 Arsenal pronto!")

with tabs[2]:
    st.header("🕹️ Central de Disparo (Fila Buffer)")
    df_d = carregar_dados()
    fila = df_d[df_d["status"] == "PRONTO"]
    st.metric("Itens na Fila", len(fila))
    
    if not fila.empty:
        if st.button("🚀 ENVIAR TUDO AGORA", type="primary"):
            webhook = st.secrets.get("WEBHOOK_POSTAGEM")
            for i, row in fila.iterrows():
                try:
                    # Formato otimizado para o Make/Buffer
                    payload = {
                        "text": f"{row['copy_funil']}\n\nLink: {row['link_afiliado']}",
                        "meta": {"produto": row['produto'], "preco": row['preco']}
                    }
                    requests.post(webhook, json=payload, timeout=15)
                    df_d.at[i, "status"] = "ENVIADO"
                except: continue
            df_d.to_csv(DATA_PATH, index=False)
            st.rerun()
