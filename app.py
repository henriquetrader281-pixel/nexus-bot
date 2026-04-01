import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os

# --- 1. SETUP & BANCO DE DADOS (Com Inteligência de Performance) ---
st.set_page_config(page_title="Nexus Absolute V44.0", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

# Colunas para o Ciclo de Validação (Postagens e Performance)
COL_MESTRE = ["data", "produto", "roteiro", "copy", "link", "status", "views", "cliques", "ctr", "postagens_cont", "score_v"]

def carregar_dados():
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame(columns=COL_MESTRE)
    df = pd.read_csv(DATA_PATH)
    for col in COL_MESTRE:
        if col not in df.columns:
            df[col] = 0 if col in ["views", "cliques", "ctr", "postagens_cont", "score_v"] else ""
    return df

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def gerar_ia(prompt):
    return client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content": prompt}]).choices[0].message.content

# --- 2. INTERFACE OPERACIONAL ---
st.title("🔱 Nexus Absolute: Ciclo de Validação TikTok")
tabs = st.tabs(["🌎 Sourcing & ROI", "🎥 Marketing & Viral Reference", "🕹️ Central de Postagem", "📊 Validação de Score"])

with tabs[0]: # MINERAÇÃO E PRECIFICAÇÃO
    st.header("🔎 Radar Shopee & Cálculo de Margem")
    nicho = st.text_input("Nicho Alvo:", value="Utilidades")
    c1, c2 = st.columns([2, 1])
    
    with c1:
        if st.button("🇧🇷 Minerar Shopee Brasil (Tendências Reais)", use_container_width=True):
            st.session_state['m_shopee'] = gerar_ia(f"Liste 10 produtos de {nicho} que estão no topo de vendas na Shopee Brasil hoje. Tabela: Produto, Preço e Por que é quente.")
        if 'm_shopee' in st.session_state: st.markdown(st.session_state['m_shopee'])
        
    with c2:
        v_venda = st.number_input("Preço Venda (R$):", value=99.0)
        v_custo = st.number_input("Custo (R$):", value=35.0)
        lucro = v_venda - v_custo - (v_venda * 0.14)
        st.metric("Lucro p/ Unidade", f"R$ {lucro:.2f}", f"{(lucro/v_venda)*100:.1f}% Margem")

with tabs[1]: # MARKETING REVERSIVO (O QUE VOCÊ LEMBROU)
    st.header("🚀 Sourcing de Vídeos Quentes & Funil")
    p_nome = st.text_input("Produto Escolhido:")
    p_link = st.text_input("Link Shopee:")
    
    if st.button("🔥 Buscar Referência Viral & Gerar Arsenal", use_container_width=True):
        with st.status("Minerando o TikTok por hooks que já funcionam..."):
            # Sourcing Reversivo: O que está quente agora para esse produto?
            ref_viral = gerar_ia(f"Busque no TikTok: Quais os vídeos mais virais de {p_nome}? Liste 3 hooks (ganchos) de alta retenção e o estilo de edição (ASMR, Demonstração, Narrado).")
            
            # Geração de 4 variações (para o teste de 4 publicações dia)
            roteiros = gerar_ia(f"Baseado na referência viral: {ref_viral}, crie 4 roteiros curtos de 15s para {p_nome}. Use hooks diferentes em cada um. Separe por ###")
            
            aff_id = st.secrets.get("SHOPEE_ID", "SEM_ID")
            link_f = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(p_link)}&aff_id={aff_id}"
            
            df = carregar_dados()
            for i, rot in enumerate(roteiros.split("###")):
                if len(rot) > 10:
                    copy_v = gerar_ia(f"Crie uma legenda viral e 1 resposta de funil para o roteiro: {rot}. Use o link {link_f}")
                    novo = {
                        "data": datetime.now().strftime("%d/%m"), "produto": p_nome,
                        "roteiro": rot.strip(), "copy": copy_v, "link": link_f,
                        "status": "VALIDAÇÃO", "postagens_cont": 0, "score_v": 0
                    }
                    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
            df.to_csv(DATA_PATH, index=False)
            st.success("4 Variações enviadas para a fila de validação!")

with tabs[2]: # CENTRAL DE DISPARO
    st.header("🕹️ Comando de Postagem Diária")
    df_v = carregar_dados()
    fila = df_v[df_v["status"].isin(["VALIDAÇÃO", "ESCALA"])]
    
    if not fila.empty:
        item = fila.iloc[0]
        st.info(f"🚀 Próximo na Fila: {item['produto']} | Status: {item['status']}")
        
        c1, c2 = st.columns(2)
        with c1: st.text_area("Roteiro Escolhido:", item['roteiro'], height=150)
        with c2: st.text_area("Legenda & Funil:", item['copy'], height=150)
        
        if st.button("▶️ DISPARAR PARA O TIKTOK (Webhook)", type="primary", use_container_width=True):
            payload = {"comando": "POSTAR", "roteiro": item['roteiro'], "copy": item['copy'], "link": item['link']}
            requests.post(st.secrets["WEBHOOK_POSTAGEM"], json=payload)
            
            # Incrementa o contador de postagens para validação
            idx = fila.index[0]
            df_v.at[idx, "postagens_cont"] += 1
            df_v.at[idx, "data"] = datetime.now().strftime("%d/%m %H:%M")
            df_v.to_csv(DATA_PATH, index=False)
            st.success(f"Postagem nº {df_v.at[idx, 'postagens_cont']} realizada!")
            st.rerun()

with tabs[3]: # VALIDAÇÃO VIA SCORE (O PONTO CHAVE)
    st.header("📊 Analisador de Score & Métricas TikTok")
    df_val = carregar_dados()
    
    st.write("Insira as métricas das últimas postagens para o Nexus decidir:")
    edited = st.data_editor(df_val[df_val["status"] == "VALIDAÇÃO"])
    
    if st.button("💾 Validar Sobrevivência do Produto"):
        # Lógica de Validação: 4 publicações dia
        for i, row in edited.iterrows():
            # Cálculo de Score Simples: CTR (Cliques/Views)
            try:
                ctr = (float(row['cliques']) / float(row['views']) * 100) if float(row['views']) > 0 else 0
            except: ctr = 0
            
            # Critério de Decisão (Pach 33)
            if row['postagens_cont'] >= 4:
                if ctr >= 3.0: # Se manteve bom enganchamento (3% CTR)
                    edited.at[i, "status"] = "ESCALA"
                    st.success(f"🔥 PRODUTO APROVADO: {row['produto']} subiu para MODO ESCALA!")
                else:
                    edited.at[i, "status"] = "DESCARTADO"
                    st.error(f"❌ PRODUTO REPROVADO: {row['produto']} teve baixo enganchamento.")
            
            edited.at[i, "ctr"] = ctr
            
        # Mescla de volta ao banco principal
        df_val.update(edited)
        df_val.to_csv(DATA_PATH, index=False)
        st.rerun()
