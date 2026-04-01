import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os
import re

# --- 1. CONFIGURAÇÃO DE SEGURANÇA ---
st.set_page_config(page_title="Nexus Absolute V64", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

def carregar_dados():
    if not os.path.exists(DATA_PATH):
        cols = ["data", "produto", "preco", "roteiro", "status", "link_afiliado", "copy_funil"]
        pd.DataFrame(columns=cols).to_csv(DATA_PATH, index=False)
    return pd.read_csv(DATA_PATH)

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
st.title("🔱 Nexus Brain V64: O Fluxo Imparável")

tabs = st.tabs(["🔎 Mineração & Seleção", "🚀 Arsenal (Auto-Process)", "🕹️ Central de Disparo"])

# Garantindo que os estados existam para não quebrar a busca
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
    
    # Processamento da busca com proteção contra falhas
    if st.session_state.res_busca:
        # Padrão regex ultra-sensível para encontrar os dados mesmo se a IA falar demais
        matches = re.findall(r"PRODUTO:\s*(.*?)\s*\|\s*PRECO:\s*(.*?)\s*\|\s*URL:\s*(https?://\S+)", st.session_state.res_busca)
        
        if matches:
            st.markdown("### ✅ Produtos Encontrados:")
            for nome, preco, link in matches:
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"📦 **{nome.strip()}**")
                c2.write(f"💰 {preco.strip()}")
                if c3.button("Selecionar", key=f"sel_{nome[:10]}"):
                    st.session_state.sel_nome = nome.strip()
                    st.session_state.sel_preco = preco.strip()
                    st.session_state.sel_link = link.strip()
                    st.toast(f"Selecionado: {nome[:20]}...")
        else:
            st.error("A busca falhou ao formatar. Tente novamente.")
            st.info("Log da IA: " + st.session_state.res_busca)

with tabs[1]:
    st.header("🚀 Arsenal de Conteúdo")
    col1, col2 = st.columns(2)
    p_n = col1.text_input("Nome do Produto Selecionado:", value=st.session_state.sel_nome)
    p_l = col2.text_input("URL Original do Produto:", value=st.session_state.sel_link)
    
    if st.button("⚡ INICIAR FLUXO TOTAL (Arsenal + Vídeos + Links)", use_container_width=True):
        if p_n and p_l:
            with st.status("Gerando variações..."):
                aff_id = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
                link_f = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(p_l)}&aff_id={aff_id}"
                
                # Gera roteiros e legendas
                roteiros = gerar_ia(f"Crie 4 roteiros de 15s para {p_n}. Separe por ###").split("###")
                
                df = carregar_dados()
                for i, rot in enumerate(roteiros):
                    if len(rot.strip()) > 10:
                        copy = gerar_ia(f"Crie legenda viral curta para TikTok: {rot}")
                        # Salvamento seguro usando DataFrame (evita SyntaxError)
                        novo = pd.DataFrame([{
                            "data": datetime.now().strftime("%d/%m"),
                            "produto": f"{p_n} (V{i+1})", "preco": st.session_state.sel_preco,
                            "roteiro": rot.strip(), "copy_funil": copy.strip(),
                            "link_afiliado": link_f, "status": "PRONTO"
                        }])
                        df = pd.concat([df, novo], ignore_index=True)
                df.to_csv(DATA_PATH, index=False)
                st.success("🔥 Arsenal pronto para disparo!")

with tabs[2]:
    st.header("🕹️ Central de Disparo (Fix Make/TikTok)")
    df_d = carregar_dados()
    fila = df_d[df_d["status"] == "PRONTO"]
    st.metric("Vídeos na Fila", len(fila))
    
    if not fila.empty:
        if st.button("🚀 DISPARAR TUDO PARA MAKE/BUFFER", type="primary", use_container_width=True):
            webhook = st.secrets.get("WEBHOOK_POSTAGEM")
            sucesso = 0
            for i, row in fila.iterrows():
                try:
                    # Payload que o seu Make já entende
                    payload = {
                        "text": f"{row['copy_funil']}\n\nLink: {row['link_afiliado']}",
                        "meta": {"produto": row['produto'], "preco": row['preco']}
                    }
                    requests.post(webhook, json=payload, timeout=15)
                    df_d.at[i, "status"] = "ENVIADO"
                    sucesso += 1
                except: continue
            df_d.to_csv(DATA_PATH, index=False)
            st.success(f"🔥 {sucesso} itens enviados com sucesso para o seu fluxo!")
            st.rerun()
