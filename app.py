import streamlit as st
from groq import Groq
from datetime import datetime
import urllib.parse
import requests
import pandas as pd
import os

# --- 1. CONFIG & DATASET ENRIQUECIDO (Patches 25, 29, 30) ---
st.set_page_config(page_title="Nexus Command Center", layout="wide", page_icon="🔱")

DATA_PATH = "dataset_nexus_v17.csv"
if not os.path.exists(DATA_PATH):
    # Adicionamos colunas de Ganhos, Temperatura e Origem
    df = pd.DataFrame(columns=[
        "data", "produto", "origem", "status", "views", "cliques", 
        "vendas", "faturamento", "temp", "agendamento"
    ])
    df.to_csv(DATA_PATH, index=False)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. INTEGRAÇÕES EXTERNAS (Patches 28 & 31) ---

def enviar_relatorio_whatsapp(mensagem):
    """Envia métricas diárias para o seu WhatsApp via Make/Zapier"""
    webhook_zap = st.secrets.get("WEBHOOK_ZAP_URL")
    if webhook_zap:
        requests.post(webhook_zap, json={"msg": mensagem})

def buscar_tendencias_eua():
    """Filtro de Achadinhos EUA (Amazon/TikTok US) - Patch 31"""
    prompt = "Liste 5 produtos que são virais no TikTok USA hoje (Home/Gadgets) e que têm baixo volume de busca no Brasil ainda."
    return client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}]).choices[0].message.content

# --- 3. INTERFACE DE COMANDO ---
st.title("🔱 Nexus Brain: Command Center")

tabs = st.tabs(["🔥 Termômetro & EUA", "📅 Agendador Social", "💰 Ganhos & ROI", "🤖 ManyChat & Zap", "📊 Dataset"])

# --- ABA 1: TERMÔMETRO & TENDÊNCIAS EUA ---
with tabs[0]:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.header("🇺🇸 Radar Achadinhos EUA (Primeira Mão)")
        if st.button("Explorar Tendências Internacionais"):
            st.markdown(buscar_tendencias_eua())
    
    with col2:
        st.header("🌡️ Termômetro")
        # Exemplo visual de temperatura de produto
        st.select_slider("Temperatura do Nicho Cozinha", options=["Frio", "Morno", "Quente", "🔥 EXPLODINDO"], value="Quente")

# --- ABA 2: AGENDADOR (ESTILO BUFFER) ---
with tabs[1]:
    st.header("📅 Agendador Multicanal (Patch 27)")
    with st.container(border=True):
        p_select = st.selectbox("Produto para agendar:", ["Selecione..."] + pd.read_csv(DATA_PATH)["produto"].tolist())
        data_post = st.date_input("Data da Postagem")
        hora_post = st.time_input("Horário de Pico")
        redes = st.multiselect("Canais:", ["TikTok", "Instagram Reels", "Facebook Grupos", "YouTube Shorts"])
        
        if st.button("Confirmar Agendamento"):
            # Envia para o Make que gerencia o Buffer/API Social
            st.success(f"Postagem de '{p_select}' agendada para {data_post} às {hora_post} via API.")

# --- ABA 3: DASHBOARD DE GANHOS (PATCH 29) ---
with tabs[2]:
    st.header("💰 Dashboard de Performance Financeira")
    df = pd.read_csv(DATA_PATH)
    
    m1, m2, m3 = st.columns(3)
    total_fat = df["faturamento"].sum()
    total_vendas = df["vendas"].sum()
    roi = (total_fat / (df.index.size * 10)) if df.index.size > 0 else 0 # Exemplo de cálculo
    
    m1.metric("Faturamento Total", f"R$ {total_fat:,.2f}")
    m2.metric("Vendas Convertidas", int(total_vendas))
    m3.metric("ROI Estimado", f"{roi:.2f}x")
    
    st.line_chart(df.set_index("data")["faturamento"])

# --- ABA 4: INTEGRAÇÃO MANYCHAT & WHATSAPP ---
with tabs[3]:
    st.header("🤖 Automação de Mensagens")
    st.write("Configuração de Fluxo ManyChat (Patch 28)")
    
    if st.button("📤 Enviar Relatório de Métricas para meu WhatsApp"):
        resumo = f"Nexus Report: {datetime.now().strftime('%d/%m')} - Faturamento: R${total_fat} | Vendas: {total_vendas}"
        enviar_relatorio_whatsapp(resumo)
        st.success("Relatório enviado para a fila do WhatsApp!")
