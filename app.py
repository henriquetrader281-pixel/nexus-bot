import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os
import re

# --- 1. CONFIGURAÇÃO E ENGINE ---
st.set_page_config(page_title="Nexus Absolute V53", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

def carregar_dados():
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=["data", "produto", "roteiro", "status", "link_afiliado", "copy_funil"])
        df.to_csv(DATA_PATH, index=False)
    return pd.read_csv(DATA_PATH)

client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

def gerar_ia(prompt):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role":"user","content": prompt}]
    ).choices[0].message.content

# --- 2. INTERFACE E FLUXO ---
st.title("🔱 Nexus Brain V53: Mineração Ininterrupta")

tabs = st.tabs(["🔎 Busca & Seleção", "🚀 Arsenal Automático", "🕹️ Disparo"])

if 'sel_nome' not in st.session_state: st.session_state.sel_nome = ""
if 'sel_link' not in st.session_state: st.session_state.sel_link = ""

with tabs[0]:
    st.header("🎯 Inteligência de Sourcing")
    nicho = st.text_input("Qual o nicho de hoje?", value="Utilidades Domésticas")
    
    if st.button("🔄 Localizar Produtos e Links", use_container_width=True):
        with st.status("Varrendo API e tendências..."):
            # Prompt que obriga a entrega de links
            prompt = (
                f"Liste 5 produtos virais para {nicho}. "
                f"Obrigatório: Para cada item escreva EXATAMENTE assim: "
                f"PRODUTO: [nome] URL: [link de busca na shopee]"
            )
            st.session_state['res_busca'] = gerar_ia(prompt)

    if 'res_busca' in st.session_state:
        st.markdown("### 📦 Resultados da Mineração:")
        # Sistema de Extração por Regex (Garante que o link seja pego)
        padrao = r"PRODUTO:\s*(.*?)\s*URL:\s*(https?://\S+)"
        matches = re.findall(padrao, st.session_state['res_busca'])
        
        if matches:
            for nome, link in matches:
                col_info, col_acao = st.columns([4, 1])
                col_info.write(f"🔹 **{nome}**")
                if col_acao.button("Selecionar", key=f"btn_{nome}"):
                    st.session_state.sel_nome = nome
                    st.session_state.sel_link = link
                    st.success(f"{nome} pronto para o Arsenal!")
        else:
            st.warning("A IA não formatou os links corretamente. Tente minerar de novo ou ajuste o nicho.")
            st.info("Resposta bruta da IA para conferência:")
            st.code(st.session_state['res_busca'])

with tabs[1]:
    st.header("🚀 Arsenal e Modificações Anti-Plágio")
    c1, c2 = st.columns(2)
    p_nome = c1.text_input("Produto Confirmado:", value=st.session_state.sel_nome)
    p_link = c2.text_input("Link Confirmado:", value=st.session_state.sel_link)
    
    if st.button("⚡ GERAR 4 VÍDEOS OK (Com meu ID)", use_container_width=True):
        if p_nome and p_link:
            with st.status("Processando inteligência de vídeo..."):
                # Conversão com ID (Patch 27)
                aff_id = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
                link_final = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(p_link)}&aff_id={aff_id}"
                
                # Geração de 4 variações (Patch 33/49)
                roteiros = gerar_ia(f"Crie 4 roteiros de 15s para {p_nome}. Mude os ganchos. Separe por ###").split("###")
                
                df = carregar_dados()
                for i, rot in enumerate(roteiros):
                    if len(rot) > 10:
                        copy = gerar_ia(f"Crie legenda viral para: {rot}")
                        novo = {
                            "data": datetime.now().strftime("%d/%m"),
                            "produto": f"{p_nome} (V{i+1})",
                            "roteiro": rot.strip(),
                            "copy_funil": copy,
                            "link_afiliado": link_final,
                            "status": "PRONTO PARA POSTAGEM"
                        }
                        df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                df.to_csv(DATA_PATH, index=False)
                st.success("🎬 OS 4 VÍDEOS ESTÃO PRONTOS NO DISPARO!")

with tabs[2]:
    st.header("🕹️ Disparo para Make/Buffer")
    df_d = carregar_dados()
    fila = df_d[df_d["status"] == "PRONTO PARA POSTAGEM"]
    
    if not fila.empty:
        st.metric("Vídeos na Fila", len(fila))
        if st.button("🚀 ENVIAR TUDO AGORA", type="primary"):
            webhook = st.secrets.get("WEBHOOK_POSTAGEM")
            sucessos = 0
            for i, row in fila.iterrows():
                try:
                    r = requests.post(webhook, json=row.to_dict(), timeout=10)
                    if r.status_code in [200, 201]:
                        df_d.at[i, "status"] = "ENVIADO"
                        sucessos += 1
                except: continue
            df_d.to_csv(DATA_PATH, index=False)
            st.rerun()
