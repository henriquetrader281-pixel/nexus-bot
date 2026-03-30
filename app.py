import streamlit as st
from groq import Groq
from datetime import datetime
import urllib.parse
import requests
import pandas as pd
import os

# --- 1. CONFIG & DATASET (Patches 01-10, 25, 29) ---
st.set_page_config(page_title="Nexus Omega: Full Automation", layout="wide", page_icon="🔱")

DATA_PATH = "nexus_master_data.csv"
if not os.path.exists(DATA_PATH):
    df = pd.DataFrame(columns=[
        "data", "produto", "origem", "status", "views", "cliques", 
        "ctr", "vendas", "faturamento", "score", "agendamento"
    ])
    df.to_csv(DATA_PATH, index=False)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. MOTORES DE IA E CONECTIVIDADE (Patches 14, 15, 17, 18, 19, 26, 28, 31) ---

def gerar_ia(prompt):
    return client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}]).choices[0].message.content

def acionar_automacao_total(tipo, dados):
    """Ponte Webhook para Make.com (Patches 15, 17, 19, 21, 28)"""
    webhook = st.secrets.get("WEBHOOK_POST_URL")
    if webhook:
        payload = {"nexus_trigger": tipo, "timestamp": str(datetime.now()), "payload": dados}
        try: requests.post(webhook, json=payload, timeout=5)
        except: pass

# --- 3. INTERFACE DE COMANDO ABSOLUTO ---
st.title("🔱 Nexus Brain: Absolute Omega 2026")
st.caption("Central Única de Inteligência, Produção de Mídia, Escala e Gestão Financeira.")

tabs = st.tabs([
    "🔥 Radar & Termômetro", 
    "🎥 Estúdio de Mídia (IA)", 
    "📅 Agendador Social", 
    "💰 Dashboard Financeiro", 
    "🤖 Automações & Zap",
    "📊 Dataset Master"
])

# --- ABA 1: RADAR EUA & TERMÔMETRO BRASIL (Patches 23, 30, 31) ---
with tabs[0]:
    st.header("🎯 Inteligência de Mercado Global")
    c_eua, c_br = st.columns(2)
    
    with c_eua:
        st.subheader("🇺🇸 Radar Achadinhos EUA")
        if st.button("🔍 Escanear TikTok/Amazon USA"):
            res_eua = gerar_ia("Liste 5 produtos virais nos EUA hoje para dropshipping/afiliados que ainda não saturaram no Brasil.")
            st.info(res_eua)
            
    with c_br:
        st.subheader("🇧🇷 Termômetro Shopee Brasil")
        if st.button("🔥 Escanear Trends Shopee BR"):
            res_br = gerar_ia("Liste os 5 termos de produtos mais buscados na Shopee Brasil agora e dê a temperatura (0-100%).")
            st.success(res_br)

    st.divider()
    st.subheader("🌡️ Febre por Categoria (Brasil)")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Cozinha", "92%", "🔥")
    m2.metric("Tech", "85%", "🚀")
    m3.metric("Beleza", "70%", "📈")
    m4.metric("Pets", "45%", "❄️")

# --- ABA 2: ESTÚDIO DE MÍDIA (Patches 17, 18, 19, 20) ---
with tabs[1]:
    st.header("🎥 Produção de Criativos (Nano Banana 2 & Lyria 3)")
    prod_nome = st.text_input("Nome do Produto:")
    link_origem = st.text_input("Link Shopee Original:")

    if st.button("🚀 GERAR CRIATIVO COMPLETO (Voz + Imagem + Roteiro)"):
        with st.status("Processando motores de mídia..."):
            # DeepLink (Patch 20)
            aff_link = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(link_origem)}&aff_id={st.secrets['SHOPEE_ID']}"
            # Roteiro & Ad Scorer (Patch 18)
            roteiro = gerar_ia(f"Crie roteiro TikTok 15s para {prod_nome}. Use gatilho de curiosidade.")
            score = int(''.join(filter(str.isdigit, gerar_ia(f"Dê nota 0-100 para este roteiro: {roteiro}"))))
            
            # Disparo para Make (Patches 17, 19)
            dados_midia = {"produto": prod_nome, "roteiro": roteiro, "link": aff_link, "score": score}
            acionar_automacao_total("GERAR_MIDIA", dados_midia)
            
            st.write(f"**Roteiro (Score: {score}):** {roteiro}")
            st.caption(f"**Prompt Imagem (Nano Banana 2):** {prod_nome}, high resolution, cinematic product photo.")
            st.success("Comando de Voz (Lyria 3) e Imagem enviado ao Webhook!")

# --- ABA 3: AGENDADOR SOCIAL (Patch 21, 22, 27) ---
with tabs[2]:
    st.header("📅 Agendador Estilo Buffer")
    with st.container(border=True):
        p_agenda = st.text_input("Produto p/ Agendar:")
        data_p = st.date_input("Data")
        hora_p = st.time_input("Hora")
        redes = st.multiselect("Canais", ["TikTok", "Instagram", "Facebook", "WhatsApp Channel"])
        if st.button("Confirmar Agendamento Multicanal"):
            acionar_automacao_total("AGENDAR_POST", {"produto": p_agenda, "data": str(data_p), "hora": str(hora_p), "redes": redes})
            st.success("Postagem na fila de processamento!")

# --- ABA 4: DASHBOARD FINANCEIRO (Patch 29) ---
with tabs[3]:
    st.header("💰 Gestão de Ganhos & ROI")
    df_f = pd.read_csv(DATA_PATH)
    col1, col2, col3 = st.columns(3)
    col1.metric("Faturamento Total", f"R$ {df_f['faturamento'].sum():,.2f}")
    col2.metric("ROI Médio", f"{(df_f['faturamento'].sum() / (df_f['views'].sum() * 0.01) if df_f['views'].sum() > 0 else 0):.2f}x")
    col3.metric("Vendas", int(df_f['vendas'].sum()))
    st.line_chart(df_f.set_index("data")["faturamento"])

# --- ABA 5: AUTOMAÇÕES & ZAP (Patch 26, 28) ---
with tabs[4]:
    st.header("🤖 ManyChat & WhatsApp Connect")
    if st.button("📤 Enviar Relatório de Métricas p/ meu WhatsApp"):
        resumo = f"Nexus Report: Ganhos R$ {df_f['faturamento'].sum()} | Vendas: {df_f['vendas'].sum()}"
        acionar_automacao_total("RELATORIO_ZAP", {"msg": resumo})
        st.success("Relatório enviado!")
    
    st.divider()
    st.subheader("💬 Respostas ManyChat ('Eu Quero')")
    if st.button("Gerar Fluxo de Resposta"):
        res = gerar_ia(f"Crie 3 variações de resposta para o ManyChat sobre o produto {prod_nome} com link.")
        st.write(res)

# --- ABA 6: DATASET MASTER (Patch 24, 25) ---
with tabs[5]:
    st.header("📊 Base de Dados Proprietária")
    df_m = pd.read_csv(DATA_PATH)
    st.dataframe(df_m, use_container_width=True)
