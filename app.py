import streamlit as st
from groq import Groq
from datetime import datetime
import urllib.parse
import requests
import pandas as pd
import os

# --- 1. CONFIGURAÇÃO E SEGURANÇA (Resgate app 1 & 2) ---
st.set_page_config(page_title="Nexus Absolute V34.0", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center;'>🔐 Nexus Private Access</h1>", unsafe_allow_html=True)
    with st.form("login"):
        e = st.text_input("E-mail Autorizado:")
        s = st.text_input("Senha Mestre:", type="password")
        if st.form_submit_button("Liberar Nexus"):
            autorizados = st.secrets.get("ALLOWED_USERS", "").split(",")
            if e in [i.strip() for i in autorizados] and s == st.secrets["NEXUS_PASSWORD"]:
                st.session_state["autenticado"] = True
                st.session_state["user_email"] = e
                st.rerun()
            else: st.error("Acesso Negado.")
    st.stop()

# --- 2. MOTORES IA & DATABASE (Resgate V16 & V17.5) ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def init_dataset():
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=["data","produto","roteiro","link","views","cliques","ctr","status","score"])
        df.to_csv(DATA_PATH, index=False)

init_dataset()

def gerar_ia(prompt):
    return client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}]).choices[0].message.content

def ad_scorer(roteiro): # FUNÇÃO RESGATADA DA V16 (app 3)
    prompt = f"Dê uma nota de 0 a 100 para este roteiro de TikTok Ads (Retenção e CTA): {roteiro}. Retorne apenas o número."
    try:
        nota = gerar_ia(prompt)
        return int(''.join(filter(str.isdigit, nota)))
    except: return 75

def zap_notifica(msg): # PATCH WHATSAPP
    webhook = st.secrets.get("WEBHOOK_WHATSAPP")
    if webhook: requests.post(webhook, json={"texto": f"🔱 *NEXUS REPORT*\n{msg}"})

# --- 3. INTERFACE COMPLETA (FUSÃO DE TODOS OS APPS) ---
st.title("🔱 Nexus Brain: Absolute System V34.0")
st.caption(f"Operador: {st.session_state.get('user_email')} | Cruzamento Shopee + Google 2026 Ativo")

tabs = st.tabs(["🔎 Mineração Cruzada", "📈 SEO & Sourcing", "🎥 Arsenal & Scoring", "💬 Funil de Comentários", "📊 Escala & ROI", "🕹️ Central"])

with tabs[0]: # MINERAÇÃO CRUZADA (Resgate app 2)
    st.header("🎯 Os 10 Mais Buscados (Shopee vs Google)")
    if st.button("🔄 Rodar Cruzamento de Dados de Hoje", use_container_width=True):
        with st.status("Nexus acessando tendências Shopee e cruzando com Google Search..."):
            prompt = "Identifique os 10 produtos mais buscados na Shopee Brasil hoje. Cruze com o volume Google (🚀 Alta, 📈 Estável). Gere uma Tabela Markdown."
            st.session_state['tabela_cruzada'] = gerar_ia(prompt)
    if 'tabela_cruzada' in st.session_state: st.markdown(st.session_state['tabela_cruzada'])

with tabs[1]: # SEO & SOURCING (Resgate app 1)
    st.header("📈 Inteligência de Busca")
    nicho_seo = st.selectbox("Nicho:", ["Cozinha", "Saúde", "Tech", "Pets"])
    if st.button("Mapear Oportunidades"):
        st.markdown(gerar_ia(f"Aja como Especialista SEO 2026 para o nicho '{nicho_seo}'. Liste Palavras-Passe e Títulos Magnéticos."))

with tabs[2]: # ARSENAL & SCORING (Resgate V16 / app 3)
    st.header("🚀 Criador de Arsenal (Com Nota de Qualidade)")
    col_p, col_l = st.columns(2)
    p_nome = col_p.text_input("Produto:")
    p_link = col_l.text_input("Link Shopee Original:")
    
    if st.button("🔥 Gerar & Avaliar 5 Roteiros"):
        link_limpo = p_link.split('?')[0]
        aff_id = st.secrets.get("SHOPEE_ID", "SEM_ID")
        link_final = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(link_limpo)}&aff_id={aff_id}"
        st.session_state['link_ativo'] = link_final
        
        res = gerar_ia(f"Crie 5 roteiros curtos para {p_nome}. Separe por ###")
        variacoes = [v.strip() for v in res.split("###") if len(v) > 10]
        
        df = pd.read_csv(DATA_PATH)
        for v in variacoes:
            nota = ad_scorer(v) # Função V16 ativa
            st.subheader(f"Score: {nota}")
            st.write(v)
            novo = {"data": datetime.now().strftime("%d/%m"), "produto": p_nome, "roteiro": v, "link": link_final, "views": 0, "cliques": 0, "ctr": 0, "status": "TESTE", "score": nota}
            df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
        df.to_csv(DATA_PATH, index=False)
        st.success("Arsenal salvo no Dataset!")

with tabs[3]: # FUNIL DE COMENTÁRIOS (Resgate V16 / app 3)
    st.header("💬 Automação de Resposta (O 'Fecha-Venda')")
    if "link_ativo" in st.session_state:
        if st.button("📦 Gerar Respostas para 'Eu Quero'"):
            respostas = gerar_ia(f"Crie 3 respostas amigáveis para quem comentou 'Eu quero' no produto {p_nome}. Link: {st.session_state['link_ativo']}")
            st.markdown(respostas)
    else: st.warning("Gere um link de afiliado na aba 'Arsenal' primeiro.")

with tabs[4]: # ESCALA & ROI (Resgate app 1 & 4)
    st.header("📊 Painel de Performance")
    df_atual = pd.read_csv(DATA_PATH)
    edited = st.data_editor(df_atual[df_atual["status"] != "DESCARTADO"])
    if st.button("💾 Salvar & Processar Escala"):
        edited["ctr"] = (edited["cliques"] / edited["views"] * 100).fillna(0)
        edited.loc[edited["ctr"] >= 3, "status"] = "ESCALA"
        edited.to_csv(DATA_PATH, index=False)
        st.rerun()

with tabs[5]: # CENTRAL DE DISPARO (Resgate app 4)
    st.header("🕹️ Automação de Postagem")
    df_v = pd.read_csv(DATA_PATH)
    fila = df_v[df_v["status"].isin(["TESTE", "ESCALA"])]
    if not fila.empty and st.button("▶️ DISPARAR AGORA"):
        item = fila.iloc[0]
        requests.post(st.secrets["WEBHOOK_POSTAGEM"], json={"texto": item['roteiro'], "link": item['link']})
        zap_notifica(f"✅ POSTADO: {item['produto']}")
        st.success(f"Enviado para o Buffer: {item['produto']}")
