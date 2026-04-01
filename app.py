import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os
import re

# --- 1. CONFIGURAÇÃO E BANCO ---
st.set_page_config(page_title="Nexus Absolute V56", layout="wide", page_icon="🔱")
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
st.title("🔱 Nexus Brain V56: Fluxo Anti-Travamento")

tabs = st.tabs(["🔎 Mineração Ultra", "🚀 Arsenal Automático", "🕹️ Central de Disparo"])

# Inicialização de estados
for key in ['sel_nome', 'sel_link', 'sel_preco', 'res_busca']:
    if key not in st.session_state: st.session_state[key] = ""

with tabs[0]:
    st.header("🎯 Inteligência de Sourcing")
    nicho = st.text_input("Nicho para busca:", value="Utilidades Domésticas")
    
    if st.button("🔄 Localizar Oportunidades Agora", use_container_width=True):
        with st.status("Varrendo mercado..."):
            prompt = (
                f"Liste 5 produtos virais para {nicho} na Shopee Brasil. "
                f"Formato obrigatório por linha: PRODUTO: [nome] | PRECO: [valor] | URL: [link]"
            )
            st.session_state.res_busca = gerar_ia(prompt)
    
    if st.session_state.res_busca:
        # Regex melhorada para pegar variações de texto da IA
        padrao = r"PRODUTO:\s*(.*?)\s*\|\s*PRECO:\s*(.*?)\s*\|\s*URL:\s*(https?://\S+)"
        matches = re.findall(padrao, st.session_state.res_busca)
        
        if matches:
            st.markdown("### ✅ Produtos Identificados:")
            for nome, preco, link in matches:
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"📦 **{nome}**")
                c2.write(f"💰 {preco}")
                if c3.button("Selecionar", key=f"sel_{nome}"):
                    st.session_state.sel_nome = nome
                    st.session_state.sel_preco = preco
                    st.session_state.sel_link = link
                    st.toast("Produto enviado para o Arsenal!")
        else:
            st.warning("A IA não usou o formato correto. Veja a resposta abaixo e copie manualmente se necessário:")
            st.info(st.session_state.res_busca)

with tabs[1]:
    st.header("🚀 Arsenal Automático (4 Vídeos)")
    p_n = st.text_input("Produto Selecionado:", value=st.session_state.sel_nome)
    p_l = st.text_input("Link Original:", value=st.session_state.sel_link)
    
    if st.button("⚡ GERAR ARSENAL COMPLETO", use_container_width=True):
        if p_n and p_l:
            with st.status("Criando ganchos e roteiros..."):
                aff_id = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
                link_f = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(p_l)}&aff_id={aff_id}"
                
                # Gera 4 variações
                prompt_rot = f"Crie 4 roteiros de 15s para {p_n} ({st.session_state.sel_preco}). Varie os estilos: 1. ASMR, 2. Problema/Solução, 3. Curiosidade, 4. Oferta. Separe por ###"
                roteiros = gerar_ia(prompt_rot).split("###")
                
                df = carregar_dados()
                for i, rot in enumerate(roteiros):
                    if len(rot.strip()) > 10:
                        copy = gerar_ia(f"Crie uma legenda de TikTok viral para este roteiro: {rot}")
                        novo_item = pd.DataFrame([{
                            "data": datetime.now().strftime("%d/%m"),
                            "produto": f"{p_n} (V{i+1})",
                            "preco": st.session_state.sel_preco,
                            "roteiro": rot.strip(),
                            "copy_funil": copy.strip(),
                            "link_afiliado": link_f,
                            "status": "PRONTO"
                        }])
                        df = pd.concat([df, novo_item], ignore_index=True)
                df.to_csv(DATA_PATH, index=False)
                st.success("✅ Arsenal carregado com sucesso!")
        else:
            st.error("Selecione um produto na aba de Mineração primeiro.")

with tabs[2]:
    st.header("🕹️ Central de Disparo")
    df_d = carregar_dados()
    fila = df_d[df_d["status"] == "PRONTO"]
    
    st.metric("Vídeos aguardando envio", len(fila))
    
    if not fila.empty:
        if st.button("🚀 DISPARAR TUDO AGORA", type="primary"):
            webhook = st.secrets.get("WEBHOOK_POSTAGEM")
            for i, row in fila.iterrows():
                try:
                    res = requests.post(webhook, json=row.to_dict(), timeout=15)
                    if res.status_code in [200, 201, 202]:
                        df_d.at[i, "status"] = "ENVIADO"
                except:
                    st.error(f"Falha ao enviar: {row['produto']}")
            
            df_d.to_csv(DATA_PATH, index=False)
            st.success("🔥 Fila processada!")
            st.rerun()
