import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os
import re

# --- 1. CONFIGURAÇÃO E ENGINE ---
st.set_page_config(page_title="Nexus Absolute V54", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

def carregar_dados():
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=["data", "produto", "preco", "roteiro", "status", "link_afiliado", "copy_funil"])
        df.to_csv(DATA_PATH, index=False)
    return pd.read_csv(DATA_PATH)

client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

def gerar_ia(prompt):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role":"user","content": prompt}]
    ).choices[0].message.content

# --- 2. INTERFACE E FLUXO ---
st.title("🔱 Nexus Brain V54: Mineração com Valor de Mercado")

tabs = st.tabs(["🔎 Busca & Seleção", "🚀 Arsenal Automático", "🕹️ Disparo"])

if 'sel_nome' not in st.session_state: st.session_state.sel_nome = ""
if 'sel_link' not in st.session_state: st.session_state.sel_link = ""
if 'sel_preco' not in st.session_state: st.session_state.sel_preco = ""

with tabs[0]:
    st.header("🎯 Inteligência de Sourcing & Preço")
    nicho = st.text_input("Qual o nicho de hoje?", value="Utilidades Domésticas")
    
    if st.button("🔄 Localizar Produtos, Preços e Links", use_container_width=True):
        with st.status("Varrendo mercado e analisando valores..."):
            # Prompt que obriga a entrega de nome, preço e link
            prompt = (
                f"Liste 5 produtos virais para {nicho}. "
                f"Obrigatório: Para cada item escreva EXATAMENTE assim: "
                f"PRODUTO: [nome] | PRECO: [valor em R$] | URL: [link de busca na shopee]"
            )
            st.session_state['res_busca'] = gerar_ia(prompt)

    if 'res_busca' in st.session_state:
        st.markdown("### 📦 Resultados da Mineração:")
        # Regex atualizado para capturar o preço também
        padrao = r"PRODUTO:\s*(.*?)\s*\|\s*PRECO:\s*(.*?)\s*\|\s*URL:\s*(https?://\S+)"
        matches = re.findall(padrao, st.session_state['res_busca'])
        
        if matches:
            for nome, preco, link in matches:
                col_info, col_preco, col_acao = st.columns([3, 1, 1])
                col_info.write(f"🔹 **{nome}**")
                col_preco.write(f"💰 **{preco}**")
                if col_acao.button("Selecionar", key=f"btn_{nome}"):
                    st.session_state.sel_nome = nome
                    st.session_state.sel_link = link
                    st.session_state.sel_preco = preco
                    st.success(f"{nome} ({preco}) pronto para o Arsenal!")
        else:
            st.warning("IA não formatou os dados. Tente novamente.")
            st.code(st.session_state['res_busca'])

with tabs[1]:
    st.header("🚀 Arsenal e Modificações Anti-Plágio")
    c1, c2, c3 = st.columns([2, 1, 2])
    p_nome = c1.text_input("Produto:", value=st.session_state.sel_nome)
    p_preco = c2.text_input("Preço Estimado:", value=st.session_state.sel_preco)
    p_link = c3.text_input("Link Confirmado:", value=st.session_state.sel_link)
    
    if st.button("⚡ GERAR 4 VÍDEOS OK (Com meu ID)", use_container_width=True):
        if p_nome and p_link:
            with st.status("Processando inteligência de vídeo e conversão de link..."):
                aff_id = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
                link_final = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(p_link)}&aff_id={aff_id}"
                
                # Roteiros que mencionam o valor para aumentar conversão
                prompt_rot = f"Crie 4 roteiros de 15s para {p_nome} que custa {p_preco}. Destaque o custo-benefício. Separe por ###"
                roteiros = gerar_ia(prompt_rot).split("###")
                
                df = carregar_dados()
                for i, rot in enumerate(roteiros):
                    if len(rot) > 10:
                        copy = gerar_ia(f"Crie legenda viral para {p_nome} por apenas {p_preco}. Use gatilhos de oferta.")
                        novo = {
                            "data": datetime.now().strftime("%d/%m"),
                            "produto": f"{p_nome} (V{i+1})",
                            "preco": p_preco,
                            "roteiro": rot.strip(),
                            "copy_funil": copy,
                            "link_afiliado": link_final,
                            "status": "PRONTO PARA POSTAGEM"
                        }
                        df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                df.to_csv(DATA_PATH, index=False)
                st.success("🎬 ARSENAL GERADO COM SUCESSO!")

with tabs[2]:
    st.header("🕹️ Central de Disparo")
    df_d = carregar_dados()
    fila = df_d[df_d["status"] == "PRONTO PARA POSTAGEM"]
    
    if not fila.empty:
        st.dataframe(fila[["produto", "preco", "status"]])
        if st.button("🚀 ENVIAR TUDO AGORA", type="primary"):
            webhook = st.secrets.get("WEBHOOK_POSTAGEM")
            for i, row in fila.iterrows():
                requests.post(webhook, json=row.to_dict(), timeout=10)
                df_d.at[i, "status"] = "ENVIADO"
            df_d.to_csv(DATA_PATH, index=False)
            st.rerun()
