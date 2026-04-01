import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os

# --- 1. SETUP & ENGINE DE AUTO-CURA (PATCH 45, 48) ---
st.set_page_config(page_title="Nexus Absolute V49.0", layout="wide", page_icon="🔱")
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

# Conexão com Groq (Patch 16-17)
client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

def gerar_ia(prompt):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role":"user","content": prompt}]
    ).choices[0].message.content

# --- 2. INTERFACE DE ALTO NÍVEL (PENSANTE) ---
st.title("🔱 Nexus Brain Absolute: High-Level Marketing")
tabs = st.tabs([
    "🕵️ Sourcing Reversivo (P-18/23)", 
    "🧠 Arsenal Estratégico (P-33/49)", 
    "🚀 Disparo Webhook (P-46)", 
    "📈 Escala & Score (P-34/40)", 
    "⚙️ Config"
])

# --- JANELA 1: MINERAÇÃO (PATCH 18, 23, 30, 31) ---
with tabs[0]:
    st.header("🎯 Inteligência de Mercado & Tendências")
    nicho = st.text_input("Nicho de Atuação:", value="Utilidades Domésticas")
    
    if st.button("🔄 Escanear Big Data (Brasil + EUA)", use_container_width=True):
        with st.status("Nexus analisando tendências globais..."):
            # Patch 31: Cruzamento Global
            st.session_state['m_data'] = gerar_ia(f"Aja como CMO. Analise o nicho {nicho}. Liste 5 produtos com alta margem na Shopee Brasil e compare com virais do TikTok EUA.")
    
    if 'm_data' in st.session_state:
        st.markdown(st.session_state['m_data'])

# --- JANELA 2: ARSENAL (PATCH 27, 33, 38, 49) ---
with tabs[1]:
    st.header("🧠 Engine de Psicologia de Vendas")
    p_nome = st.text_input("Produto Selecionado:")
    p_link = st.text_input("Link Shopee (Original):")
    # Patch 49: Frameworks Psicológicos
    framework = st.selectbox("Framework Estratégico:", ["AIDA (Atenção/Ação)", "PAS (Problema/Solução)", "Storytelling Viral"])

    if st.button("🔥 Gerar Arsenal (4 Posts/Dia)"):
        with st.status("IA aplicando psicologia de retenção..."):
            ref_v = st.session_state.get('m_data', 'Hooks de curiosidade.')
            prompt = f"Crie 4 roteiros de 15s para {p_nome} usando {framework}. Baseie-se em: {ref_v}. Separe por ###"
            roteiros = gerar_ia(prompt)
            
            # Patch 27: DeepLink Automático
            aff_id = st.secrets.get("SHOPEE_ID", "SEM_ID")
            link_f = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(p_link)}&aff_id={aff_id}"
            
            df = carregar_dados()
            for rot in roteiros.split("###"):
                if len(rot) > 10:
                    # Patch 38: Funil de Resposta
                    copy_funil = gerar_ia(f"Crie: 1. Legenda TikTok; 2. Resposta de funil para o link {link_f}; 3. 15 Hashtags.")
                    novo = {
                        "data": datetime.now().strftime("%d/%m"), "produto": p_nome,
                        "roteiro": rot.strip(), "copy_funil": copy_funil, "link_afiliado": link_f,
                        "status": "VALIDAÇÃO", "estrategia_psico": framework, "postagens_cont": 0
                    }
                    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
            df.to_csv(DATA_PATH, index=False)
            st.success("✅ Arsenal Estratégico Gerado!")

# --- JANELA 3: AUTOMAÇÃO (PATCH 46, 48) ---
with tabs[2]:
    st.header("🚀 Central de Disparo")
    df_v = carregar_dados()
    fila = df_v[df_v["status"] == "VALIDAÇÃO"]
    
    if not fila.empty:
        item = fila.iloc[0]
        st.info(f"🎥 **Próximo:** {item['produto']} | Teste {int(item['postagens_cont'])+1}/4")
        
        c1, c2 = st.columns(2)
        with c1: st.text_area("Roteiro:", item['roteiro'], height=180)
        with c2: st.text_area("Funil:", item['copy_funil'], height=180)
        
        if st.button("▶️ EXECUTAR DISPARO", type="primary", use_container_width=True):
            # Patch 46: Diagnóstico de Webhook
            payload = {"produto": item['produto'], "roteiro": item['roteiro'], "copy": item['copy_funil'], "link": item['link_afiliado']}
            res = requests.post(st.secrets["WEBHOOK_POSTAGEM"], json=payload)
            if res.status_code == 200:
                df_v.at[fila.index[0], "postagens_cont"] += 1
                df_v.to_csv(DATA_PATH, index=False)
                st.success("Disparo realizado com sucesso!")
                st.rerun()
            else:
                st.error(f"Erro no Webhook: {res.status_code}")

# --- JANELA 4: SCORE & SOBREVIVÊNCIA (PATCH 34, 40) ---
with tabs[3]:
    st.header("📈 Dashboard de Escala Autônoma")
    df_p = carregar_dados()
    
    st.write("Insira as métricas para a IA decidir o futuro do produto:")
    # Patch 34: Cálculo de Score
    edited = st.data_editor(df_p[df_p["status"].isin(["VALIDAÇÃO", "ESCALA"])])
    
    if st.button("💾 Validar e Escalar"):
        for i, r in edited.iterrows():
            if int(r['postagens_cont']) >= 4:
                views = float(r['views']) if float(r['views']) > 0 else 1
                ctr = (float(r['cliques']) / views) * 100
                
                # Patch 40: Status de Sobrevivência
                if ctr >= 3.0:
                    edited.at[i, "status"] = "ESCALA"
                    st.success(f"🔥 {r['produto']} APROVADO PARA ESCALA (CTR: {ctr:.1f}%)")
                else:
                    edited.at[i, "status"] = "DESCARTADO"
                    st.error(f"❌ {r['produto']} DESCARTADO (Baixo Score)")
        
        df_p.update(edited)
        df_p.to_csv(DATA
