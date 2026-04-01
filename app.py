import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os

# --- 1. SETUP & DATASET PERSISTENTE ---
st.set_page_config(page_title="Nexus Absolute V20.1", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

# Garante que o dataset exista e mantenha os dados
if not os.path.exists(DATA_PATH):
    df_init = pd.DataFrame(columns=["data", "produto", "roteiro", "link", "status"])
    df_init.to_csv(DATA_PATH, index=False)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def gerar_ia(prompt):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

# --- 2. INTERFACE ---
st.title("🔱 Nexus Brain: Absolute System V20.1")
tabs = st.tabs(["🌎 Termômetro Global", "🎥 Criar Arsenal", "⚡ Automação"])

with tabs[0]:
    st.header("🎯 Inteligência de Mercado (BR & EUA)")
    col1, col2 = st.columns([2, 1])
    with col1:
        nicho = st.text_input("Nicho Alvo:", placeholder="Ex: Cozinha, Tech, Casa")
    with col2:
        v_max = st.slider("Preço Máximo (R$):", 5, 250, 47)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔥 Quentes no BRASIL", use_container_width=True):
            res = gerar_ia(f"Liste 5 produtos de {nicho} virais na Shopee Brasil hoje (Abril 2026) até R${v_max}. Retorne em tabela.")
            st.markdown(res)
    with c2:
        if st.button("🇺🇸 Quentes nos EUA", use_container_width=True):
            res = gerar_ia(f"Liste 5 tendências de {nicho} no TikTok USA hoje (Abril 2026) que custam menos de 20 dólares.")
            st.markdown(res)

with tabs[1]:
    st.header("🚀 Gerador de Arsenal (Dataset)")
    p_nome = st.text_input("Nome do Produto:")
    p_link_original = st.text_input("Link Original da Shopee:")
    
    if st.button("🔥 Gerar 5 Roteiros e Link"):
        if p_nome and p_link_original:
            with st.spinner("Processando..."):
                # Lógica de Link de Afiliado
                my_id = st.secrets.get("SHOPEE_ID", "AGUARDANDO")
                link_pronto = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(p_link_original)}&aff_id={my_id}"
                
                # Geração de Roteiros
                prompt = f"Crie 5 roteiros curtos de TikTok para {p_nome}. Estilo 'achadinho' barato. Separe por '---'."
                roteiros = gerar_ia(prompt).split("---")
                
                # Salva no CSV sem apagar o anterior
                df_atual = pd.read_csv(DATA_PATH)
                novos_dados = []
                for r in roteiros:
                    if len(r) > 10:
                        novos_dados.append({
                            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "produto": p_nome,
                            "roteiro": r.strip(),
                            "link": link_pronto,
                            "status": "FILA"
                        })
                
                if novos_dados:
                    df_novo = pd.concat([df_atual, pd.DataFrame(novos_dados)], ignore_index=True)
                    df_novo.to_csv(DATA_PATH, index=False)
                    st.success(f"✅ Link Gerado e 5 Roteiros salvos!")
                    st.info(f"Link: {link_pronto}")
        else:
            st.error("Preencha o nome e o link do produto!")

with tabs[2]:
    st.header("🕹️ Controle de Disparo (Buffer)")
    df_ver = pd.read_csv(DATA_PATH)
    fila = df_ver[df_ver["status"] == "FILA"]
    
    st.metric("Vídeos aguardando no Arsenal", len(fila))
    
    if not fila.empty:
        if st.button("▶️ DISPARAR PRÓXIMO PARA O TIKTOK", type="primary"):
            item = fila.iloc[0]
            payload = {
                "texto": f"{item['roteiro']}\n\n🛒 Link: {item['link']}",
                "produto": item["produto"]
            }
            
            # Envio para o Webhook do Make
            resp = requests.post(st.secrets["WEBHOOK_POSTAGEM"], json=payload)
            
            if resp.status_code == 200:
                df_ver.loc[fila.index[0], "status"] = "POSTADO"
                df_ver.to_csv(DATA_PATH, index=False)
                st.success(f"🚀 Sucesso! {item['produto']} enviado para o Buffer.")
            else:
                st.error("Erro no Webhook. Verifique se o cenário no Make está ativo.")
    
    if st.checkbox("Ver Dataset Completo"):
        st.dataframe(df_ver)

# --- 3. SEÇÃO DE PATCHES (MELHORIAS FUTURAS) ---
# Adicione suas melhorias nas funções abaixo sem alterar o código acima.

def patch_01():
    pass

def patch_02():
    pass

def patch_03():
    pass

def patch_04():
    pass

def patch_05():
    pass

def patch_06():
    pass

def patch_07():
    pass

def patch_08():
    pass

def patch_09():
    pass

def patch_10():
    pass
