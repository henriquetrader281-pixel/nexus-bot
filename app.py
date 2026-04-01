import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os

# --- 1. SETUP & ENGINE DE AUTO-CURA (PATCH 45, 48) ---
st.set_page_config(page_title="Nexus Absolute V49.5", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

def aplicar_patches(df):
    """Garante a integridade de todos os 49 patches no banco de dados"""
    updates = {
        "copy_funil": "", "ref_viral": "", "postagens_cont": 0, 
        "status": "VALIDAÇÃO", "link_afiliado": "", "views": 0, 
        "cliques": 0, "cpa_estimado": 0.0, "estrategia_psico": ""
    }
    for col, default in updates.items():
        if col not in df.columns:
            df[col] = default
    return df

def carregar_dados():
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=["data", "produto", "roteiro"])
        df.to_csv(DATA_PATH, index=False)
    df = pd.read_csv(DATA_PATH)
    return aplicar_patches(df)

# Conexão com Groq
client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

def gerar_ia(prompt):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role":"user","content": prompt}]
    ).choices[0].message.content

# --- 2. INTERFACE OPERACIONAL ---
st.title("🔱 Nexus Brain Absolute: High-Level Marketing")
tabs = st.tabs([
    "🕵️ Sourcing Reversivo", 
    "🧠 Arsenal Estratégico", 
    "🚀 Disparo Webhook", 
    "📈 Escala & Score", 
    "⚙️ Config"
])

# --- JANELA 1: MINERAÇÃO ---
with tabs[0]:
    st.header("🎯 Inteligência de Mercado")
    nicho = st.text_input("Nicho de Atuação:", value="Utilidades Domésticas")
    
    if st.button("🔄 Escanear Big Data", use_container_width=True):
        with st.status("Nexus analisando tendências globais..."):
            st.session_state['m_data'] = gerar_ia(f"Analise o nicho {nicho}. Liste 5 produtos virais na Shopee Brasil e TikTok EUA.")
    
    if 'm_data' in st.session_state:
        st.markdown(st.session_state['m_data'])

# --- JANELA 2: ARSENAL (REVISADO PARA EVITAR CORTE DE CÓDIGO) ---
with tabs[1]:
    st.header("🧠 Arsenal de Guerra (4 Posts/Dia)")
    p_nome = st.text_input("Produto Selecionado:")
    p_link = st.text_input("Link Shopee Original:")
    framework = st.selectbox("Framework Estratégico:", ["AIDA", "PAS", "Storytelling"])

    if st.button("🔥 Gerar Arsenal Completo (Roteiro + Copy)"):
        if p_nome and p_link:
            with st.status("IA aplicando psicologia de retenção..."):
                ref_v = st.session_state.get('m_data', 'Hooks de curiosidade.')
                prompt = f"Crie 4 roteiros de 15s para {p_nome} usando {framework}. Separe por ###"
                roteiros = gerar_ia(prompt)
                
                aff_id = st.secrets.get("SHOPEE_ID", "SEM_ID")
                link_f = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(p_link)}&aff_id={aff_id}"
                
                df = carregar_dados()
                for rot in roteiros.split("###"):
                    if len(rot) > 10:
                        copy_funil = gerar_ia(f"Crie legenda TikTok e resposta de funil para o link {link_f}")
                        novo_item = {
                            "data": datetime.now().strftime("%d/%m"), 
                            "produto": p_nome,
                            "roteiro": rot.strip(), 
                            "copy_funil": copy_funil, 
                            "link_afiliado": link_f,
                            "status": "VALIDAÇÃO", 
                            "estrategia_psico": framework, 
                            "postagens_cont": 0
                        }
                        df = pd.concat([df, pd.DataFrame([novo_item])], ignore_index=True)
                df.to_csv(DATA_PATH, index=False)
                st.success("Arsenal pronto!")

# --- JANELA 3: DISPARO ---
with tabs[2]:
    st.header("🚀 Execução de Postagem")
    df_v = carregar_dados()
    fila = df_v[df_v["status"] == "VALIDAÇÃO"]
    
    if not fila.empty:
        item = fila.iloc[0]
        st.info(f"🎥 Próximo: {item['produto']} | Teste {int(item['postagens_cont'])+1}/4")
        if st.button("▶️ ENVIAR PARA WEBHOOK", type="primary"):
            payload = {"produto": item['produto'], "roteiro": item['roteiro'], "link": item['link_afiliado']}
            res = requests.post(st.secrets["WEBHOOK_POSTAGEM"], json=payload)
            if res.status_code == 200:
                df_v.at[fila.index[0], "postagens_cont"] += 1
                df_v.to_csv(DATA_PATH, index=False)
                st.success("Disparado!")
                st.rerun()

# --- JANELA 4: SCORE ---
with tabs[3]:
    st.header("📈 Dashboard de Escala")
    df_p = carregar_dados()
    edited = st.data_editor(df_p[df_p["status"].isin(["VALIDAÇÃO", "ESCALA"])])
    
    if st.button("💾 Salvar Métricas"):
        df_p.update(edited)
        df_p.to_csv(DATA_PATH, index=False)
        st.success("Dados atualizados!")
        st.rerun()

# --- JANELA 5: CONFIG ---
with tabs[4]:
    st.header("⚙️ Configurações")
    st.code(f"Webhook: {st.secrets.get('WEBHOOK_POSTAGEM', 'N/A')}")
