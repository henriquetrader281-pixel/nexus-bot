import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os
import re

# --- 1. CONFIGURAÇÃO DE SEGURANÇA MÁXIMA ---
st.set_page_config(page_title="Nexus Absolute V65", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

def carregar_dados():
    if not os.path.exists(DATA_PATH):
        cols = ["data", "produto", "preco", "roteiro", "status", "link_afiliado", "copy_funil"]
        pd.DataFrame(columns=cols).to_csv(DATA_PATH, index=False)
    # Proteção contra erro de leitura do CSV
    try: return pd.read_csv(DATA_PATH)
    except: return pd.DataFrame(columns=["data", "produto", "preco", "roteiro", "status", "link_afiliado", "copy_funil"])

client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

def gerar_ia(prompt):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role":"user","content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erro Crítico IA: {e}"

# --- 2. INTERFACE COM ÍCONES ---
st.title("🔱 Nexus Brain V65: Fluxo de Aço")

tabs = st.tabs(["🔎 Mineração Real-Time", "🚀 Arsenal Automático", "🕹️ Central de Disparo"])

# Inicialização segura dos estados de sessão
for key in ['sel_nome', 'sel_link', 'sel_preco', 'res_busca']:
    if key not in st.session_state: st.session_state[key] = ""

with tabs[0]:
    st.header("🎯 Inteligência de Sourcing")
    nicho = st.text_input("Defina o Nicho:", value="Utilidades Domésticas")
    
    if st.button("🔄 Localizar Oportunidades", use_container_width=True):
        with st.status("Varrendo mercado..."):
            prompt = (
                f"Liste 5 produtos virais de {nicho} na Shopee Brasil. "
                "Responda EXATAMENTE assim: PRODUTO: [nome] | PRECO: [valor] | URL: [link]"
            )
            st.session_state.res_busca = gerar_ia(prompt)
    
    if st.session_state.res_busca:
        # Regex blindada: captura mesmo se a IA colocar emojis ou texto extra
        matches = re.findall(r"PRODUTO:\s*(.*?)\s*\|\s*PRECO:\s*(.*?)\s*\|\s*URL:\s*(https?://\S+)", st.session_state.res_busca)
        
        if matches:
            st.markdown("### ✅ Produtos Em Alta (Boa Oportunidade)")
            for nome, preco, link in matches:
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"📦 **{nome.strip()}**")
                c2.write(f"💰 {preco.strip()}")
                if c3.button("Selecionar", key=f"sel_{nome[:15]}"):
                    st.session_state.sel_nome, st.session_state.sel_preco, st.session_state.sel_link = nome.strip(), preco.strip(), link.strip()
                    st.toast(f"Selecionado!")
        else:
            st.warning("IA gerou formato inválido. Tentando novamente...")
            st.info(st.session_state.res_busca)

with tabs[1]:
    st.header("🚀 Arsenal de Conteúdo")
    p_n = st.text_input("Produto Selecionado:", value=st.session_state.sel_nome)
    p_l = st.text_input("URL Original:", value=st.session_state.sel_link)
    
    if st.button("⚡ GERAR 4 VARIAÇÕES PARA BUFFER", use_container_width=True):
        if p_n and p_l:
            with st.status("Processando vídeos e copies..."):
                aff_id = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
                link_f = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(p_l)}&aff_id={aff_id}"
                
                # Divisão resiliente por marcadores
                roteiros = gerar_ia(f"Crie 4 roteiros de 15s para {p_n}. Separe por ###").split("###")
                
                df = carregar_dados()
                for i, rot in enumerate(roteiros):
                    if len(rot.strip()) > 10:
                        copy = gerar_ia(f"Crie legenda viral curta com hashtags para: {rot}")
                        # Criação de DataFrame temporário para salvar sem SyntaxError
                        novo = pd.DataFrame([{
                            "data": datetime.now().strftime("%d/%m"),
                            "produto": f"{p_n} V{i+1}", "preco": st.session_state.sel_preco,
                            "roteiro": rot.strip(), "copy_funil": copy.strip(),
                            "link_afiliado": link_f, "status": "PRONTO"
                        }])
                        df = pd.concat([df, novo], ignore_index=True)
                df.to_csv(DATA_PATH, index=False)
                st.success("🔥 Arsenal pronto!")

with tabs[2]:
    st.header("🕹️ Disparo Final (Make ➔ Buffer)")
    df_d = carregar_dados()
    fila = df_d[df_d["status"] == "PRONTO"]
    st.metric("📦 Itens na Fila", len(fila)) #
    
    if not fila.empty:
        if st.button("🚀 ENVIAR TUDO AGORA", type="primary", use_container_width=True):
            webhook = st.secrets.get("WEBHOOK_POSTAGEM")
            for i, row in fila.iterrows():
                try:
                    # Payload "limpo" focado no que o Buffer exige no campo 'text'
                    payload = {
                        "text": f"{row['copy_funil']}\n\nProduto: {row['produto']}\nPreço: {row['preco']}\nLink: {row['link_afiliado']}"
                    }
                    res = requests.post(webhook, json=payload, timeout=15)
                    if res.status_code < 300:
                        df_d.at[i, "status"] = "ENVIADO"
                except: continue
            df_d.to_csv(DATA_PATH, index=False)
            st.success("✅ Enviados para o Fluxo!")
            st.rerun()
