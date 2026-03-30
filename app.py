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

# --- 2. MOTORES IA ---
# Busca a chave nos secrets ou pede se não encontrar
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Erro: Configure a GROQ_API_KEY no arquivo .streamlit/secrets.toml")
    st.stop()

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

def gerar_copy_resposta(produto, link):
    prompt = f"Crie 3 variações de respostas curtas e amigáveis para quem comentou 'Eu quero' no vídeo do produto {produto}. Inclua o link {link} de forma natural. Use emojis."
    return gerar_ia(prompt)

# --- 3. INTERFACE ---
st.title("🔱 Nexus Brain: Absolute Decision System")
st.caption("Automação de Funil Completa: Mineração -> Copy -> Escala -> Acompanhamento")

tabs = st.tabs(["🎥 Criativos", "🔗 Afiliado", "📊 Dataset", "🧠 Decisão", "💬 Funil", "⚡ Escala"])

with tabs[0]: # CRIATIVOS
    prod_nome = st.text_input("Produto alvo:", placeholder="Ex: Mini Processador USB")
    if st.button("🚀 Gerar Arsenal de Vendas"):
        with st.spinner("Criando ganchos de alta retenção..."):
            res = gerar_ia(f"Crie 5 roteiros de 15s para TikTok do produto {prod_nome}. Separe cada um com ###")
            variacoes = [v.strip() for v in res.split("###") if len(v) > 10]
            
            df = pd.read_csv(DATA_PATH)
            for i, v in enumerate(variacoes):
                nota = ad_scorer(v)
                st.subheader(f"V{i+1} | Score: {nota}")
                st.write(v)
                
                novo = {
                    "data": datetime.now().strftime("%d/%m/%Y"), 
                    "produto": prod_nome, 
                    "roteiro": v, 
                    "variacao": f"V{i+1}", 
                    "views": 0, "cliques": 0, "ctr": 0, 
                    "status": "TESTE", "score": nota
                }
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

with tabs[2]: # DATASET (ACOMPANHAMENTO)
    st.header("📊 Gestão de Performance")
    df_editor = pd.read_csv(DATA_PATH)
    
    st.write("Insira as Views e Cliques das redes sociais abaixo:")
    edited_df = st.data_editor(
        df_editor,
        column_config={
            "ctr": st.column_config.NumberColumn("CTR (%)", format="%.2f%%", disabled=True),
            "status": st.column_config.SelectboxColumn("Status", options=["TESTE", "ESCALA", "PAUSADO"])
        },
        num_rows="dynamic"
    )

    if st.button("💾 Salvar e Calcular Métricas"):
        # Garante que números sejam válidos
        edited_df["views"] = pd.to_numeric(edited_df["views"]).fillna(0)
        edited_df["cliques"] = pd.to_numeric(edited_df["cliques"]).fillna(0)
        
        # Calcula CTR evitando divisão por zero
        edited_df["ctr"] = (edited_df["cliques"] / edited_df["views"] * 100).replace([float('inf'), -float('inf')], 0).fillna(0)
        
        edited_df.to_csv(DATA_PATH, index=False)
        st.success("Dados atualizados!")
        st.rerun()

with tabs[3]: # DECISÃO (O CÉREBRO)
    st.header("🧠 Inteligência de Escala")
    df_decisao = pd.read_csv(DATA_PATH)
    
    if not df_decisao.empty:
        for index, row in df_decisao.iterrows():
            with st.expander(f"Análise: {row['produto']} ({row['variacao']})"):
                c1, c2, c3 = st.columns(3)
                c1.metric("Views", int(row['views']))
                c2.metric("CTR", f"{row['ctr']:.2f}%")
                c3.metric("Score IA", row['score'])
                
                if row['views'] > 500:
                    if row['ctr'] >= 2.0:
                        st.success("🔥 VEREDITO: ESCALAR. Alta conversão detectada!")
                    elif row['ctr'] < 0.8:
                        st.error("🚫 VEREDITO: PAUSAR. O público não está clicando.")
                    else:
                        st.warning("⚖️ VEREDITO: MANTER. Continue testando.")
                else:
                    st.info("Aguardando mais dados para análise precisa.")
    else:
        st.info("Nenhum dado para analisar.")

with tabs[4]: # FUNIL
    st.header("💬 Automação de Resposta")
    if "link_ativo" in st.session_state:
        if st.button("📦 Gerar Respostas"):
            respostas = gerar_copy_resposta(prod_nome if prod_nome else "Produto", st.session_state["link_ativo"])
            st.session_state["respostas_comentarios"] = respostas
        
        if "respostas_comentarios" in st.session_state:
            st.markdown(st.session_state["respostas_comentarios"])
            if st.button("🔥 Enviar ao Webhook"):
                webhook = st.secrets.get("WEBHOOK_POST_URL")
                payload = {"tipo": "RESPOSTA", "conteudo": st.session_state["respostas_comentarios"]}
                requests.post(webhook, json=payload)
                st.success("Enviado!")
    else:
        st.warning("Gere o link na aba 'Afiliado' primeiro.")

with tabs[5]: # ESCALA
    st.header("⚡ Comando de Escala")
    if st.button("🚀 Disparar Orçamento para Vencedores"):
        webhook_esc = st.secrets.get("WEBHOOK_ESCALA_URL")
        requests.post(webhook_esc, json={"comando": "ESCALAR_VENCEDORES"})
        st.success("Sinal de escala enviado!")
