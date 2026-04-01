import streamlit as st
from groq import Groq
import urllib.parse, requests, os, re, json
import pandas as pd
from datetime import datetime

# --- 1. SETUP ---
st.set_page_config(page_title="Nexus V61", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

def carregar_dados():
    if not os.path.exists(DATA_PATH):
        cols = ["data", "produto", "preco", "roteiro", "status", "link_afiliado", "copy_funil"]
        pd.DataFrame(columns=cols).to_csv(DATA_PATH, index=False)
    return pd.read_csv(DATA_PATH)

client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

def gerar_ia(prompt):
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role":"user","content": prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Erro: {str(e)}"

# --- 2. INTERFACE ---
st.title("🔱 Nexus Brain V61")

tabs = st.tabs(["🔎 Busca", "🚀 Arsenal", "🕹️ Disparo"])

# Estados de sessão
for k in ['sel_nome', 'sel_link', 'sel_preco', 'res_busca']:
    if k not in st.session_state: st.session_state[k] = ""

with tabs[0]:
    nicho = st.text_input("Nicho:", value="Utilidades Domésticas")
    if st.button("🔄 Localizar Produtos", use_container_width=True):
        with st.status("Varrendo..."):
            p = f"Liste 5 produtos de {nicho}. Use: PRODUTO: [nome] | PRECO: [R$] | URL: [link]"
            st.session_state.res_busca = gerar_ia(p)
    
    if st.session_state.res_busca:
        items = re.findall(r"PRODUTO:\s*(.*?)\s*\|\s*PRECO:\s*(.*?)\s*\|\s*URL:\s*(https?://\S+)", st.session_state.res_busca)
        for nome, preco, link in items:
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"📦 {nome}")
            c2.write(f"💰 {preco}")
            if c3.button("Selecionar", key=f"s_{nome}"):
                st.session_state.sel_nome, st.session_state.sel_preco, st.session_state.sel_link = nome, preco, link
                st.toast("Selecionado!")

with tabs[1]:
    st.header("🚀 Gerador de Vídeos")
    if st.button("⚡ GERAR 4 VARIAÇÕES", use_container_width=True):
        if st.session_state.sel_nome:
            with st.status("Criando..."):
                aff = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
                link_f = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(st.session_state.sel_link)}&aff_id={aff}"
                rots = gerar_ia(f"Crie 4 roteiros de 15s para {st.session_state.sel_nome} ({st.session_state.sel_preco}). Separe por ###").split("###")
                
                df = carregar_dados()
                for i, r in enumerate(rots):
                    if len(r.strip()) > 10:
                        cp = gerar_ia(f"Legenda TikTok viral para: {r}")
                        novo = pd.DataFrame([{"data": datetime.now().strftime("%d/%m"), "produto": f"{st.session_state.sel_nome} V{i+1}", "preco": st.session_state.sel_preco, "roteiro": r.strip(), "copy_funil": cp.strip(), "link_afiliado": link_f, "status": "PRONTO"}])
                        df = pd.concat([df, novo], ignore_index=True)
                df.to_csv(DATA_PATH, index=False)
                st.success("✅ Arsenal Pronto!")

with tabs[2]:
    st.header("🕹️ Disparo Buffer")
    df_d = carregar_dados()
    fila = df_d[df_d["status"] == "PRONTO"]
    st.metric("Fila", len(fila))
    
    if not fila.empty:
        if st.button("🚀 ENVIAR TUDO", type="primary"):
            web = st.secrets.get("WEBHOOK_POSTAGEM")
            for i, row in fila.iterrows():
                # Texto formatado para o Buffer não recusar
                msg = f"{row['copy_funil']}\n\nProduto: {row['produto']}\nPreço: {row['preco']}\nLink: {row['link_afiliado']}"
                try:
                    res = requests.post(web, json={"text": msg}, timeout=15)
                    if res.status_code < 300:
                        df_d.at[i, "status"] = "ENVIADO"
                except: continue
            df_d.to_csv(DATA_PATH, index=False)
            st.rerun()
