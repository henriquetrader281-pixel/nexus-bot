import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os
import json

# --- 1. SETUP & ENGINE ---
st.set_page_config(page_title="Nexus Absolute V50", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

def carregar_dados():
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=["data", "produto", "roteiro", "status", "link_afiliado"])
        df.to_csv(DATA_PATH, index=False)
    return pd.read_csv(DATA_PATH)

client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

def gerar_ia(prompt):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role":"user","content": prompt}]
    ).choices[0].message.content

# --- 2. LOGICA DE FLUXO AUTOMÁTICO (MINERAÇÃO -> ARSENAL) ---
st.title("🔱 Nexus Brain V50: Automação de Fluxo")

tabs = st.tabs(["🔎 Mineração & Escolha", "🚀 Arsenal & Processamento", "🕹️ Central de Disparo"])

with tabs[0]:
    st.header("🎯 Escolha o Produto para Processamento Automático")
    nicho = st.text_input("Nicho:", value="Utilidades")
    
    if st.button("🔄 Buscar Oportunidades"):
        with st.status("Minerando..."):
            res = gerar_ia(f"Liste 5 produtos virais de {nicho} na Shopee Brasil com links de busca.")
            st.session_state['lista_produtos'] = res

    if 'lista_produtos' in st.session_state:
        st.markdown(st.session_state['lista_produtos'])
        st.divider()
        
        # INPUTS PARA O FLUXO AUTOMÁTICO
        c1, c2 = st.columns(2)
        prod_escolhido = c1.text_input("Nome do Produto Selecionado:")
        link_orig = c2.text_input("URL Original do Produto:")
        
        if st.button("⚡ INICIAR FLUXO TOTAL (Arsenal + Vídeos + Links)"):
            with st.status("Processando Arsenal e Modificações de Vídeo..."):
                # 1. Gerar ID de Afiliado (P-27)
                aff_id = st.secrets.get("SHOPEE_ID", "ID_PADRAO")
                link_final = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(link_orig)}&aff_id={aff_id}"
                
                # 2. Gerar 4 Roteiros Modificados (Anti-Plágio)
                roteiros = gerar_ia(f"Crie 4 roteiros de 15s para {prod_escolhido}. Mude a ordem dos ganchos e a narração para não ficar igual ao original. Separe por ###")
                
                df = carregar_dados()
                for rot in roteiros.split("###"):
                    if len(rot) > 10:
                        copy = gerar_ia(f"Crie legenda viral e resposta de funil para o link {link_final}")
                        novo = {
                            "data": datetime.now().strftime("%d/%m"),
                            "produto": prod_escolhido,
                            "roteiro": rot.strip(),
                            "copy_funil": copy,
                            "link_afiliado": link_final,
                            "status": "PRONTO PARA POSTAGEM"
                        }
                        df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                df.to_csv(DATA_PATH, index=False)
                st.success("✅ VÍDEOS MODIFICADOS E ARSENAL PRONTO!")

with tabs[1]:
    st.header("📦 Status do Arsenal")
    df_check = carregar_dados()
    # Layout de confirmação visual
    prontos = df_check[df_check["status"] == "PRONTO PARA POSTAGEM"]
    if not prontos.empty:
        for idx, row in prontos.iterrows():
            st.success(f"🎬 Vídeo OK: {row['produto']} | Link: {row['link_afiliado']}")
    else:
        st.info("Aguardando processamento na aba de Mineração.")

# --- 3. FIX DO WEBHOOK (JSON E HEADERS PARA MAKE/BUFFER) ---
with tabs[2]:
    st.header("🕹️ Central de Disparo (Fix Make/TikTok)")
    df_disparo = carregar_dados()
    fila = df_disparo[df_disparo["status"] == "PRONTO PARA POSTAGEM"]
    
    if not fila.empty:
        if st.button("🚀 DISPARAR TUDO PARA MAKE/BUFFER", type="primary"):
            url_webhook = st.secrets.get("WEBHOOK_POSTAGEM")
            headers = {"Content-Type": "application/json"}
            
            sucessos = 0
            for i, row in fila.iterrows():
                # Payload estruturado para o Make.com reconhecer
                payload = {
                    "event": "new_post",
                    "data": {
                        "produto": row['produto'],
                        "video_script": row['roteiro'],
                        "caption": row['copy_funil'],
                        "affiliate_link": row['link_afiliado'],
                        "timestamp": datetime.now().isoformat()
                    }
                }
                try:
                    r = requests.post(url_webhook, data=json.dumps(payload), headers=headers, timeout=15)
                    if r.status_code == 200:
                        df_disparo.at[i, "status"] = "ENVIADO"
                        sucessos += 1
                except Exception as e:
                    st.error(f"Erro no envio: {e}")
            
            df_disparo.to_csv(DATA_PATH, index=False)
            st.success(f"🔥 {sucessos} itens enviados com sucesso para o seu fluxo!")
