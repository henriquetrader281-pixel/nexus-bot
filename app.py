import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os

# --- 1. SETUP & INFRA (SISTEMA DE PATCH POR LINHA) ---
st.set_page_config(page_title="Nexus Absolute V45.0", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

def patch_system(df):
    """Adiciona melhorias e colunas novas sem quebrar o banco de dados"""
    updates = {
        "copy_funil": "",      # Patch 38: Funil de vendas
        "ref_viral": "",       # Patch 18: Referência de vídeos quentes
        "postagens_cont": 0,   # Patch 33: Contador para validação (4/dia)
        "score_v": 0,          # Patch 34: Score de retenção real
        "link_afiliado": "",   # Patch 27: Link pronto para uso
        "status": "VALIDAÇÃO"  # Patch 40: Status inicial de teste
    }
    for col, default in updates.items():
        if col not in df.columns:
            df[col] = default
    return df

def carregar_dados():
    if not os.path.exists(DATA_PATH):
        cols = ["data", "produto", "roteiro", "nicho", "views", "cliques", "ctr"]
        df = pd.DataFrame(columns=cols)
        df.to_csv(DATA_PATH, index=False)
    df = pd.read_csv(DATA_PATH)
    return patch_system(df) # Aplica os patches linha por linha

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. MOTORES DE INTELIGÊNCIA ---
def gerar_ia(prompt):
    return client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content": prompt}]).choices[0].message.content

# --- 3. INTERFACE (ORGANIZADA POR FUNCIONALIDADE PENSADA) ---
st.title("🔱 Nexus Brain: Absolute V45.0")
tabs = st.tabs(["🌎 Sourcing & ROI", "📣 Marketing de Guerrilha", "🕹️ Central de Postagem", "📊 Score & Validação"])

# --- TAB 1: MINERAÇÃO (Shopee + EUA + Lucro) ---
with tabs[0]:
    st.header("🔎 Mineração de Produtos Quentes")
    nicho = st.text_input("Nicho:", value="Cozinha")
    c1, c2, c3 = st.columns([1,1,1])
    
    if c1.button("🇧🇷 Shopee Brasil"):
        st.session_state['m_br'] = gerar_ia(f"Top 10 produtos {nicho} Shopee BR. Tabela: Nome, Preço, Link Busca.")
    if c2.button("🇺🇸 Trends EUA"):
        st.session_state['m_usa'] = gerar_ia(f"Virais TikTok Shop EUA {nicho}. Tabela: Produto e Motivo do Viral.")
    
    with c3:
        st.subheader("💰 Calculadora ROI")
        venda = st.number_input("Preço Venda:", value=99.0)
        custo = st.number_input("Custo:", value=35.0)
        st.metric("Lucro Líquido", f"R$ {venda - custo - (venda*0.14):.2f}")

    r1, r2 = st.columns(2)
    with r1: 
        if 'm_br' in st.session_state: st.markdown(st.session_state['m_br'])
    with r2: 
        if 'm_usa' in st.session_state: st.markdown(st.session_state['m_usa'])

# --- TAB 2: MARKETING (VÍDEOS QUENTES + FUNIL + LEGENDAS) ---
with tabs[1]:
    st.header("🚀 Marketing Reversivo (Hooks & Funil)")
    p_nome = st.text_input("Produto para Validar:")
    p_link = st.text_input("Link Shopee para Afiliar:")
    
    if st.button("🔥 Gerar 4 Variações de Teste (TikTok Sourcing)"):
        with st.status("Minerando vídeos quentes e criando roteiros..."):
            ref = gerar_ia(f"Quais vídeos são virais para {p_nome} no TikTok? Liste 3 hooks.")
            roteiros = gerar_ia(f"Baseado no viral {ref}, crie 4 roteiros curtos (15s) para {p_nome}. Separe por ###")
            
            aff_id = st.secrets.get("SHOPEE_ID", "SEM_ID")
            link_f = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(p_link)}&aff_id={aff_id}"
            
            df = carregar_dados()
            for rot in roteiros.split("###"):
                if len(rot) > 10:
                    copy = gerar_ia(f"Crie legenda viral e resposta de funil para: {rot}")
                    novo = {
                        "data": datetime.now().strftime("%d/%m"), "produto": p_nome,
                        "ref_viral": ref, "roteiro": rot.strip(), "copy_funil": copy,
                        "link_afiliado": link_f, "status": "VALIDAÇÃO", "postagens_cont": 0
                    }
                    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
            df.to_csv(DATA_PATH, index=False)
            st.success("Arsenal pronto com 4 variações de teste!")

# --- TAB 3: CENTRAL DE COMANDO (AGENDAMENTO & DISPARO) ---
with tabs[2]:
    st.header("🕹️ Disparo e Agendamento Diário")
    df_v = carregar_dados()
    fila = df_v[df_v["status"] == "VALIDAÇÃO"]
    
    if not fila.empty:
        item = fila.iloc[0]
        st.info(f"🎥 Próximo Post: {item['produto']} (Teste {item['postagens_cont']+1}/4)")
        col_rot, col_cop = st.columns(2)
        with col_rot: st.text_area("Roteiro p/ Edição:", item['roteiro'], height=150)
        with col_cop: st.text_area("Legenda & Hashtags:", item['copy_funil'], height=150)
        
        if st.button("▶️ DISPARAR WEBHOOK (Edição/Post)", type="primary"):
            payload = {"produto": item['produto'], "roteiro": item['roteiro'], "copy": item['copy_funil'], "link": item['link_afiliado']}
            requests.post(st.secrets["WEBHOOK_POSTAGEM"], json=payload)
            df_v.at[fila.index[0], "postagens_cont"] += 1
            df_v.to_csv(DATA_PATH, index=False)
            st.rerun()

# --- TAB 4: VALIDAÇÃO (SCORE & SOBREVIVÊNCIA) ---
with tabs[3]:
    st.header("📊 Validação de Score (4 Posts/Dia)")
    df_val = carregar_dados()
    
    st.write("Insira os dados do TikTok abaixo. Se após 4 posts o CTR > 3%, o Nexus escala.")
    edited = st.data_editor(df_val[df_val["status"] == "VALIDAÇÃO"])
    
    if st.button("💾 Validar e Atualizar"):
        for i, row in edited.iterrows():
            if row['postagens_cont'] >= 4:
                ctr = (float(row['cliques'])/float(row['views'])*100) if float(row['views']) > 0 else 0
                edited.at[i, "status"] = "ESCALA" if ctr >= 3 else "DESCARTADO"
        
        df_val.update(edited)
        df_val.to_csv(DATA_PATH, index=False)
        st.success("Status de validação atualizado!")
        st.rerun()
