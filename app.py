import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os

# --- 1. SETUP & INFRAESTRUTURA ---
st.set_page_config(page_title="Nexus Absolute V29.0", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

cols = ["data", "produto", "roteiro", "link", "status", "hook_tipo", "nicho", "ticket"]
if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=cols).to_csv(DATA_PATH, index=False)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. MOTORES DE INTELIGÊNCIA (PATCHES 01-25) ---

def log_nexus(msg):
    if 'logs' not in st.session_state: st.session_state.logs = []
    st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M')}] {msg}")

def limpar_e_converter_link(url):
    link_limpo = url.split('?')[0]
    my_id = st.secrets.get("SHOPEE_ID", "AGUARDANDO")
    return f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(link_limpo)}&aff_id={my_id}"

def aplicar_gatilhos_v25(texto, nicho, cta, escassez):
    tags = f"\n\n#achadinhos #shopee #viral #{nicho.lower().replace(' ', '')}"
    gatilho_perda = " 🔥 ÚLTIMAS UNIDADES NO ESTOQUE!" if escassez else ""
    return f"{texto.strip()}{gatilho_perda}\n\n{cta}{tags}"

# --- 3. INTERFACE ---
st.sidebar.title("🔱 Nexus Auditoria")
if st.sidebar.button("Limpar Histórico"): st.session_state.logs = []
if 'logs' in st.session_state:
    for l in reversed(st.session_state.logs[-12:]): st.sidebar.caption(l)

st.title("🔱 Nexus Brain: Absolute System V29.0")
tabs = st.tabs(["🌎 Inteligência Global", "🎥 Arsenal de Guerra", "⚡ Central & Visualizador"])

with tabs[0]:
    st.header("🎯 Termômetro de Tendências")
    col1, col2 = st.columns([2, 1])
    with col1: nicho_atual = st.text_input("Nicho:", value="Cozinha")
    with col2: v_max = st.slider("Preço Máximo (R$):", 5, 250, 47)
    
    if st.button("🔥 Escanear Trends (BR/EUA)"):
        p = f"Sugira 5 produtos de {nicho_atual} virais na Shopee Brasil e 3 tendências dos EUA abaixo de R${v_max}."
        st.markdown(client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":p}]).choices[0].message.content)

with tabs[1]:
    st.header("🚀 Gerador de Arsenal")
    col_a, col_b = st.columns(2)
    with col_a:
        p_nome = st.text_input("Produto:")
        p_link = st.text_input("Link Shopee:")
    with col_b:
        hook_tipo = st.selectbox("Gancho (Hook):", ["Urgência", "Curiosidade", "Problema/Solução"])
        escassez_on = st.checkbox("Ativar Gatilho de Escassez", value=True)
    
    cta_user = st.text_input("CTA:", value="Comenta 'EU QUERO' para o link!")

    if st.button("🔥 Gerar Arsenal Completo"):
        if p_nome and p_link:
            link_final = limpar_e_converter_link(p_link)
            prompt = f"Crie 5 roteiros curtos (15s) para TikTok sobre {p_nome}. Estilo: {hook_tipo}. Separe por '---'."
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":prompt}]).choices[0].message.content
            
            df = pd.read_csv(DATA_PATH)
            for r in res.split("---"):
                if len(r) > 15:
                    roteiro_full = aplicar_gatilhos_v25(r, nicho_atual, cta_user, escassez_on)
                    novo = {"data": datetime.now().strftime("%d/%m %H:%M"), "produto": p_nome, "roteiro": roteiro_full, "link": link_final, "status": "FILA", "hook_tipo": hook_tipo, "nicho": nicho_atual, "ticket": v_max}
                    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
            df.to_csv(DATA_PATH, index=False)
            st.success("✅ Arsenal salvo!")

with tabs[2]:
    st.header("🕹️ Central de Postagem & Visualizador")
    df_v = pd.read_csv(DATA_PATH)
    
    # --- NOVO VISUALIZADOR DE STATUS ---
    col_m1, col_m2 = st.columns(2)
    fila = df_v[df_v["status"] == "FILA"]
    postados = df_v[df_v["status"] == "POSTADO"]
    
    col_m1.metric("📦 NA FILA", len(fila), delta_color="normal")
    col_m2.metric("✅ POSTADOS", len(postados), delta=len(postados))
    
    st.divider()
    
    col_btn, col_view = st.columns([1, 2])
    
    with col_btn:
        st.subheader("Ações")
        if not fila.empty:
            if st.button("▶️ DISPARAR PRÓXIMO", type="primary", use_container_width=True):
                item = fila.iloc[0]
                payload = {"texto": f"{item['roteiro']}\n\n🛒 LINK: {item['link']}", "produto": item["produto"]}
                resp = requests.post(st.secrets["WEBHOOK_POSTAGEM"], json=payload)
                
                if resp.status_code == 200:
                    df_v.loc[fila.index[0], "status"] = "POSTADO"
                    df_v.to_csv(DATA_PATH, index=False)
                    st.rerun() # Atualiza o visualizador na hora
        else:
            st.info("Nada na fila para postar.")

    with col_view:
        st.subheader("Histórico Recente")
        if not postados.empty:
            # Mostra os últimos 3 postados de forma elegante
            for i, row in postados.tail(3).iterrows():
                with st.expander(f"✅ {row['produto']} - {row['data']}"):
                    st.write(row['roteiro'])
                    st.caption(f"Link enviado: {row['link']}")
        else:
            st.caption("Nenhuma postagem realizada ainda.")

# --- SEÇÃO DE PATCHES (05-10 LIVRES) ---
def patch_05(): pass
def patch_06(): pass
def patch_07(): pass
def patch_08(): pass
def patch_09(): pass
def patch_10(): pass
