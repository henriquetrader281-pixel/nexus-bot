import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os

# --- 1. SETUP & SISTEMA DE PATCH (Injeção de Funcionalidades) ---
st.set_page_config(page_title="Nexus Absolute V47.0", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

def aplicar_patches(df):
    updates = {
        "copy_funil": "", 
        "ref_viral": "",        # Patch 18: Referência de vídeo quente
        "postagens_cont": 0, 
        "status": "VALIDAÇÃO",
        "link_afiliado": "",
        "views": 0, "cliques": 0, "score_v": 0
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

def gerar_ia(prompt):
    return client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content": prompt}]).choices[0].message.content

# --- 2. INTERFACE ---
st.title("🔱 Nexus Brain: Sourcing & Marketing")
tabs = st.tabs(["🔎 Minerador Shopee/TikTok", "💰 ROI", "🚀 Gerador de Funil", "🕹️ Central de Disparo", "📊 Validação"])

# --- TAB 1: MINERADOR (O QUE TINHA SUMIDO) ---
with tabs[0]:
    st.header("🎯 Minerador de Produtos e Vídeos Quentes")
    nicho_busca = st.text_input("Nicho para caça (ex: Cozinha, Pet, Tech):", value="Utilidades")
    
    col_btn1, col_btn2 = st.columns(2)
    
    if col_btn1.button("🇧🇷 Minerar Shopee Brasil (Vendas Reais)", use_container_width=True):
        with st.spinner("Acedendo a dados da Shopee..."):
            prompt = f"Aja como um especialista em mineração. Liste os 10 produtos mais vendidos de {nicho_busca} na Shopee Brasil. Forneça: Nome, Preço Estimado e o 'Fator Viral'."
            st.session_state['res_shopee'] = gerar_ia(prompt)

    if col_btn2.button("🔥 Buscar Vídeos Quentes (TikTok References)", use_container_width=True):
        with st.spinner("Rastreando tendências no TikTok..."):
            prompt = f"Para o nicho {nicho_busca}, quais os 5 estilos de vídeos que estão a gerar mais visualizações agora? (Ex: ASMR de limpeza, Teste de resistência). Liste ganchos (hooks) reais."
            st.session_state['res_viral'] = gerar_ia(prompt)

    st.divider()
    res_c1, res_c2 = st.columns(2)
    with res_c1:
        if 'res_shopee' in st.session_state: st.markdown(st.session_state['res_shopee'])
    with res_c2:
        if 'res_viral' in st.session_state: st.markdown(st.session_state['res_viral'])

# --- TAB 2: ROI ---
with tabs[1]:
    st.header("📊 Calculadora de Viabilidade")
    v_venda = st.number_input("Preço de Venda (R$):", value=97.0)
    v_custo = st.number_input("Custo Total (R$):", value=30.0)
    lucro = v_venda - v_custo - (v_venda * 0.14)
    st.metric("Lucro Líquido", f"R$ {lucro:.2f}", f"{(lucro/v_venda)*100:.1f}% Margem")

# --- TAB 3: MARKETING (GERAÇÃO COM BASE NO VIRAL) ---
with tabs[2]:
    st.header("🚀 Construção do Arsenal de Guerrilha")
    p_nome = st.text_input("Produto Escolhido:")
    p_link = st.text_input("Link Shopee Original:")
    
    if st.button("🔥 Gerar 4 Roteiros + Funil de Respostas"):
        with st.status("Processando inteligência de marketing..."):
            # Aqui ele usa a referência viral buscada na Tab 1
            ref = st.session_state.get('res_viral', 'Ganchos de curiosidade e unboxing rápido.')
            roteiros = gerar_ia(f"Baseado nesta tendência viral: {ref}. Crie 4 roteiros de 15s para {p_nome}. Separe por ###")
            
            aff_id = st.secrets.get("SHOPEE_ID", "SEM_ID")
            link_f = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(p_link)}&aff_id={aff_id}"
            
            df = carregar_dados()
            for rot in roteiros.split("###"):
                if len(rot) > 10:
                    copy = gerar_ia(f"Crie uma legenda TikTok e uma resposta de funil para quem comentar 'Eu quero' usando o link {link_f}. Roteiro base: {rot}")
                    novo = {
                        "data": datetime.now().strftime("%d/%m"), "produto": p_nome,
                        "ref_viral": ref[:200], "roteiro": rot.strip(), "copy_funil": copy,
                        "link_afiliado": link_f, "status": "VALIDAÇÃO", "post
