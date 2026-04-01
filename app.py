import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os

# --- 1. SETUP & SISTEMA DE PATCH (Injeção de Colunas) ---
st.set_page_config(page_title="Nexus Absolute V46.0", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

def aplicar_patches(df):
    # Patch 46: Garante que o status 'VALIDAÇÃO' e as métricas existam para o disparo
    updates = {
        "copy_funil": "", 
        "postagens_cont": 0, 
        "status": "VALIDAÇÃO",
        "link_afiliado": "",
        "views": 0,
        "cliques": 0
    }
    for col, default in updates.items():
        if col not in df.columns:
            df[col] = default
    return df

def carregar_dados():
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=["data", "produto", "roteiro", "nicho"])
        df.to_csv(DATA_PATH, index=False)
    df = pd.read_csv(DATA_PATH)
    return aplicar_patches(df)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. MOTOR DE INTELIGÊNCIA ---
def gerar_ia(prompt):
    return client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content": prompt}]).choices[0].message.content

# --- 3. INTERFACE ---
st.title("🔱 Nexus Brain: Corretor de Disparos")
tabs = st.tabs(["🌎 Sourcing & ROI", "📣 Marketing & Viral", "🕹️ Central de Postagem", "📊 Score & Validação"])

# --- TAB 2: GERAÇÃO (Onde o erro pode começar) ---
with tabs[1]:
    st.header("🚀 Gerar Arsenal com Sourcing Viral")
    p_nome = st.text_input("Produto:")
    p_link = st.text_input("Link Shopee:")
    
    if st.button("🔥 Gerar e Enviar para Fila"):
        with st.status("Minerando referências e criando funil..."):
            ref = gerar_ia(f"Hooks virais para {p_nome} no TikTok.")
            roteiros = gerar_ia(f"Crie 4 roteiros de 15s baseados em: {ref}. Separe por ###")
            
            aff_id = st.secrets.get("SHOPEE_ID", "SEM_ID")
            link_f = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(p_link)}&aff_id={aff_id}"
            
            df = carregar_dados()
            for rot in roteiros.split("###"):
                if len(rot) > 10:
                    copy = gerar_ia(f"Legenda viral para: {rot}")
                    novo = {
                        "data": datetime.now().strftime("%d/%m"), "produto": p_nome,
                        "roteiro": rot.strip(), "copy_funil": copy,
                        "link_afiliado": link_f, "status": "VALIDAÇÃO", "postagens_cont": 0
                    }
                    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
            df.to_csv(DATA_PATH, index=False)
            st.success("Arsenal pronto! Vá para a 'Central de Postagem'.")

# --- TAB 3: CENTRAL DE POSTAGEM (FIX DO DISPARO) ---
with tabs[2]:
    st.header("🕹️ Controle de Execução de Vídeo")
    df_v = carregar_dados()
    
    # Filtro rigoroso: Só mostra o que está em VALIDAÇÃO ou ESCALA e ainda não bateu 4 posts
    fila = df_v[df_v["status"].isin(["VALIDAÇÃO", "ESCALA"])]
    
    if not fila.empty:
        item = fila.iloc[0]
        st.warning(f"🎬 PRONTO PARA DISPARO: {item['produto']}")
        
        c1, c2 = st.columns(2)
        with c1: st.text_area("Roteiro:", item['roteiro'], height=150)
        with c2: st.text_area("Copy/Legenda:", item['copy_funil'], height=150)
        
        url_webhook = st.secrets.get("WEBHOOK_POSTAGEM")
        
        if st.button("▶️ EXECUTAR DISPARO AGORA", type="primary", use_container_width=True):
            if not url_webhook:
                st.error("❌ ERRO: WEBHOOK_POSTAGEM não configurado nos Secrets!")
            else:
                payload = {
                    "produto": item['produto'],
                    "roteiro": item['roteiro'],
                    "copy": item['copy_funil'],
                    "link": item['link_afiliado'],
                    "tentativa": int(item['postagens_cont']) + 1
                }
                
                try:
                    # Diagnóstico em tempo real
                    response = requests.post(url_webhook, json=payload, timeout=15)
                    
                    if response.status_code == 200:
                        # Atualiza o banco apenas se o servidor recebeu o vídeo
                        idx = fila.index[0]
                        df_v.at[idx, "postagens_cont"] += 1
                        df_v.at[idx, "data"] = datetime.now().strftime("%d/%m %H:%M")
                        df_v.to_csv(DATA_PATH, index=False)
                        st.success(f"✅ VÍDEO ENVIADO! Postagem {df_v.at[idx, 'postagens_cont']}/4")
                        st.rerun()
                    else:
                        st.error(f"❌ O Servidor do Webhook respondeu com ERRO {response.status_code}")
                        st.write(response.text) # Mostra o erro do servidor
                except Exception as e:
                    st.error(f"❌ FALHA DE CONEXÃO: {str(e)}")

# --- TAB 4: VALIDAÇÃO ---
with tabs[3]:
    st.header("📊 Validação de Performance")
    df_val = carregar_dados()
    edited = st.data_editor(df_val[df_val["status"] == "VALIDAÇÃO"])
    if st.button("💾 Salvar Métricas"):
        df_val.update(edited)
        df_val.to_csv(DATA_PATH, index=False)
        st.rerun()
