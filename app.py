import streamlit as st
from groq import Groq
from datetime import datetime
import urllib.parse
import requests
import pandas as pd
import os

# --- 1. SETUP & SEGURANÇA ---
st.set_page_config(page_title="Nexus Absolute V17.8", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

def init_dataset():
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=[
            "data", "post_id", "produto", "roteiro", "link_origem", 
            "views", "cliques", "ctr", "status", "score"
        ])
        df.to_csv(DATA_PATH, index=False)

init_dataset()

# --- 2. LOGIN SEGURO ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center;'>🔐 Nexus Private Access</h1>", unsafe_allow_html=True)
    with st.form("login"):
        e = st.text_input("E-mail Autorizado:")
        s = st.text_input("Senha Mestre:", type="password")
        if st.form_submit_button("Liberar Nexus", use_container_width=True):
            autorizados = st.secrets.get("ALLOWED_USERS", "").split(",")
            if e in [i.strip() for i in autorizados] and s == st.secrets["NEXUS_PASSWORD"]:
                st.session_state["autenticado"] = True
                st.session_state["user_email"] = e
                st.rerun()
            else: st.error("Acesso Negado.")
    st.stop()

# --- 3. MOTORES IA & NOTIFICAÇÕES ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def gerar_ia(prompt):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

def enviar_notificacao(msg):
    """Disparo automático para seu WhatsApp via Webhook"""
    url = st.secrets.get("WEBHOOK_WHATSAPP")
    if url: 
        try: requests.post(url, json={"texto": f"🔱 *NEXUS REPORT*:\n{msg}"})
        except: pass

def converter_afiliado(url_prod, post_id="GERAL"):
    id_aff = st.secrets.get("SHOPEE_ID", "SEM_ID")
    link_base = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(url_prod)}&aff_id={id_aff}"
    return f"{link_base}&src={post_id}"

# --- 4. INTELIGÊNCIA DE DADOS ---
def processar_inteligencia(df):
    df["views"] = pd.to_numeric(df["views"]).fillna(0)
    df["cliques"] = pd.to_numeric(df["cliques"]).fillna(0)
    df["ctr"] = (df["cliques"] / df["views"] * 100).fillna(0)
    df["score"] = (df["ctr"] * 0.7) + (df["views"] * 0.001)
    df.loc[df["ctr"] >= 3, "status"] = "ESCALA"
    df.loc[df["ctr"] < 1, "status"] = "DESCARTADO"
    return df

# --- 5. INTERFACE (Onde tudo aparece de novo) ---
st.title("🔱 Nexus Brain: Absolute System")
tabs = st.tabs(["🔎 Mineração", "🎥 Criativos", "💬 Funil", "📊 Dataset", "⚡ Automação"])

with tabs[0]: # MINERAÇÃO + LINKS
    st.header("🎯 Mineração Cruzada Shopee + Google")
    termo = st.text_input("O que buscar hoje?")
    if st.button("🔄 Rodar Cruzamento", use_container_width=True):
        with st.status("Minerando..."):
            res = gerar_ia(f"Identifique 5 produtos de {termo} na Shopee Brasil com alta tendência no Google. Retorne uma tabela com sugestão de links.")
            st.session_state['tabela_cruzada'] = res
            st.session_state['p_minerado'] = termo
    
    if 'tabela_cruzada' in st.session_state:
        st.markdown(st.session_state['tabela_cruzada'])

with tabs[1]: # CRIATIVOS + GERADOR DE LINK VISUAL
    prod = st.text_input("Produto alvo:", value=st.session_state.get('p_minerado', ""))
    link_raw = st.text_input("Link Original da Shopee:")
    
    if link_raw:
        link_aff = converter_afiliado(link_raw)
        st.success(f"🔗 Seu Link de Afiliado: {link_aff}")
        st.session_state["link_ativo"] = link_aff

    if st.button("🚀 Criar Arsenal (Aprendizado Contínuo)"):
        df_hist = pd.read_csv(DATA_PATH)
        top_vencedores = df_hist[df_hist["status"] == "ESCALA"].sort_values(by="ctr", ascending=False).head(3)
        
        prompt = f"Crie 5 roteiros TikTok de 15s para {prod}. Separe com ###"
        if not top_vencedores.empty:
            prompt = f"Baseado nestes roteiros que deram ROI: {top_vencedores['roteiro'].to_list()}, crie 5 novas variações para {prod}. Separe com ###"
            
        variacoes = [v.strip() for v in gerar_ia(prompt).split("###") if len(v) > 10]
        df = pd.read_csv(DATA_PATH)
        for v in variacoes:
            novo = {"data": datetime.now().strftime("%d/%m/%Y"), "post_id": "PENDENTE", "produto": prod, "roteiro": v, "link_origem": link_raw, "views": 0, "cliques": 0, "ctr": 0, "status": "TESTE", "score": 10}
            df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
        df.to_csv(DATA_PATH, index=False)
        st.balloons()
        enviar_notificacao(f"Arsenal Criado para {prod}. 5 novos roteiros no dataset.")

with tabs[2]: # O FUNIL QUE TINHA SAÍDO (Voltou!)
    st.header("💬 Funil de Respostas Automáticas")
    if "link_ativo" in st.session_state:
        if st.button("📦 Gerar Respostas 'Eu Quero'"):
            prompt_res = f"Crie 3 variações de respostas curtas e persuasivas para comentários de 'Eu quero' sobre o produto {prod}. Inclua o link: {st.session_state['link_ativo']}"
            respostas = gerar_ia(prompt_res)
            st.session_state["respostas_comentarios"] = respostas
        
        if "respostas_comentarios" in st.session_state:
            st.code(st.session_state["respostas_comentarios"])
            if st.button("📱 Enviar Respostas para WhatsApp"):
                enviar_notificacao(f"Copies de Resposta:\n{st.session_state['respostas_comentarios']}")
    else:
        st.warning("Gere um link na aba Criativos primeiro.")

with tabs[3]: # DATASET
    df_atual = pd.read_csv(DATA_PATH)
    edited = st.data_editor(df_atual[df_atual["status"] != "DESCARTADO"], num_rows="dynamic")
    if st.button("💾 Salvar & Processar Inteligência"):
        df_final = processar_inteligencia(edited)
        df_final.to_csv(DATA_PATH, index=False)
        st.rerun()

with tabs[4]: # AUTOMAÇÃO PLAY/STOP
    st.header("🕹️ Painel de Controle Play/Stop")
    if "nexus_active" not in st.session_state: st.session_state["nexus_active"] = False
    
    c1, c2 = st.columns(2)
    if c1.button("▶️ LIGAR (PLAY)", use_container_width=True, type="primary"):
        st.session_state["nexus_active"] = True
        enviar_notificacao("SISTEMA ONLINE - Automação Iniciada.")
    if c2.button("🛑 DESLIGAR (STOP)", use_container_width=True):
        st.session_state["nexus_active"] = False
        enviar_notificacao("SISTEMA OFFLINE - Automação Pausada.")
    
    if st.session_state["nexus_active"]:
        st.success("🤖 Nexus está trabalhando em segundo plano.")
