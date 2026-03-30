import streamlit as st
from groq import Groq
from datetime import datetime
import urllib.parse
import requests
import pandas as pd
import os

# --- 1. SETUP & SEGURANÇA ---
st.set_page_config(page_title="Nexus Brain ABSOLUTE V16", layout="wide", page_icon="🔱")

DATA_PATH = "dataset_nexus.csv"
def init_dataset():
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=[
            "data","produto","roteiro","variacao",
            "views","cliques","ctr","status","score"
        ])
        df.to_csv(DATA_PATH, index=False)

init_dataset()

# --- 2. MOTORES IA (Patches 14, 18, 20, 26) ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def gerar_ia(prompt):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

def ad_scorer(roteiro):
    prompt = f"Dê uma nota de 0 a 100 para este roteiro de TikTok Ads (Retenção e CTA): {roteiro}. Retorne apenas o número."
    try:
        nota = gerar_ia(prompt)
        return int(''.join(filter(str.isdigit, nota)))
    except: return 70

# --- 3. FUNIL & COPY (A Lógica por trás do código) ---
def gerar_copy_resposta(produto, link):
    prompt = f"Crie 3 variações de respostas curtas e amigáveis para quem comentou 'Eu quero' no vídeo do produto {produto}. Inclua o link {link} de forma natural. Use emojis."
    return gerar_ia(prompt)

# --- 4. INTERFACE ABSOLUTE ---
st.title("🔱 Nexus Brain: Absolute Decision System")
st.caption("Automação de Funil Completa: Mineração -> Copy -> Escala -> Resposta Automática")

tabs = st.tabs(["🎥 Criativos", "🔗 Afiliado", "📊 Dataset", "🧠 Decisão", "💬 Funil de Comentários", "⚡ Escala"])

with tabs[0]: # CRIATIVOS
    prod_nome = st.text_input("Produto alvo:")
    if st.button("🚀 Gerar Arsenal de Vendas (5 Variações)"):
        with st.spinner("Criando ganchos de alta retenção..."):
            res = gerar_ia(f"Crie 5 roteiros de 15s para TikTok do produto {prod_nome} (Curiosidade, Dor, Medo, Prova, Transformação). Separe com ###")
            variacoes = [v.strip() for v in res.split("###") if len(v) > 10]
            for i, v in enumerate(variacoes):
                nota = ad_scorer(v)
                st.subheader(f"V{i+1} | Score: {nota}")
                st.write(v)
                # Salva no Dataset Proprietário (Patch 25)
                df = pd.read_csv(DATA_PATH)
                novo = {"data": datetime.now().strftime("%d/%m/%Y"), "produto": prod_nome, "roteiro": v, "variacao": f"V{i+1}", "views": 0, "cliques": 0, "ctr": 0, "status": "TESTE", "score": nota}
                df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                df.to_csv(DATA_PATH, index=False)
        st.success("Salvo no Dataset!")

with tabs[1]: # AFILIADO
    link_shopee = st.text_input("Link Shopee Original:")
    if link_shopee:
        aff_id = st.secrets.get("SHOPEE_ID", "SEM_ID")
        link_final = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(link_shopee)}&aff_id={aff_id}"
        st.success(f"Link de Afiliado Gerado: {link_final}")
        st.session_state["link_ativo"] = link_final

with tabs[4]: # PATCH 26: FUNIL DE COMENTÁRIOS (NOVO!)
    st.header("💬 Automação de Resposta (O 'Fecha-Venda')")
    if "link_ativo" in st.session_state:
        if st.button("📦 Gerar Respostas para 'Eu Quero'"):
            respostas = gerar_copy_resposta(prod_nome if prod_nome else "Produto", st.session_state["link_ativo"])
            st.session_state["respostas_comentarios"] = respostas
        
        if "respostas_comentarios" in st.session_state:
            st.info("Copie e configure no seu bot de automação (ManyChat/Make):")
            st.markdown(st.session_state["respostas_comentarios"])
            
            if st.button("🔥 Enviar Respostas para Webhook de Resposta"):
                webhook = st.secrets.get("WEBHOOK_POST_URL")
                payload = {"tipo": "RESPOSTA_COMENTARIO", "respostas": st.session_state["respostas_comentarios"]}
                requests.post(webhook, json=payload)
                st.success("Configuração de resposta enviada ao Make.com!")
    else:
        st.warning("Gere um link de afiliado na Aba 1 primeiro para criar as respostas.")

# --- AS OUTRAS ABAS (DATASET, DECISÃO, ESCALA) CONTINUAM COM A LÓGICA ANTERIOR ---
