import streamlit as st
from groq import Groq
from datetime import datetime
import urllib.parse
import requests
import pandas as pd
import os

# --- 1. SETUP E BANCO DE DADOS (Persistência de Dados) ---
st.set_page_config(page_title="Nexus Absolute V17.5", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

def init_dataset():
    """Inicializa o banco de dados para aprendizado contínuo"""
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=[
            "data", "post_id", "produto", "roteiro", "link_origem", 
            "views", "cliques", "ctr", "status", "score"
        ])
        df.to_csv(DATA_PATH, index=False)

init_dataset()

# --- 2. SEGURANÇA E ACESSO PRIVADO ---
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

# --- 3. MOTORES DE INTELIGÊNCIA ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def gerar_ia(prompt):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

def enviar_notificacao(msg):
    """Envia avisos de postagem diretamente para o WhatsApp"""
    url = st.secrets.get("WEBHOOK_WHATSAPP")
    if url: 
        try: requests.post(url, json={"texto": f"🔱 *NEXUS REPORT*:\n{msg}"})
        except: pass

def converter_afiliado(url_prod, post_id):
    """Gera link comissionado com rastreio de origem"""
    id_aff = st.secrets.get("SHOPEE_ID", "SEM_ID")
    link_base = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(url_prod)}&aff_id={id_aff}"
    return f"{link_base}&src={post_id}"

# --- 4. LÓGICA DE PERFORMANCE E ESCALA (Motor de Decisão) ---
def processar_inteligencia(df):
    """Atualiza métricas e define quem merece escala"""
    df["views"] = pd.to_numeric(df["views"]).fillna(0)
    df["cliques"] = pd.to_numeric(df["cliques"]).fillna(0)
    df["ctr"] = (df["cliques"] / df["views"] * 100).fillna(0)
    
    # Score de Sucesso: 70% CTR + Volume de Visualizações
    df["score"] = (df["ctr"] * 0.7) + (df["views"] * 0.001)
    
    # Classificação Automática de Campanha
    df.loc[df["ctr"] >= 3, "status"] = "ESCALA"
    df.loc[df["ctr"] < 1, "status"] = "DESCARTADO"
    return df

def disparar_ciclo_agendado():
    """Executa a postagem automática de 4 vídeos por dia"""
    df = pd.read_csv(DATA_PATH)
    # Seleciona prioridades: ESCALA primeiro, ignora score baixo (Stop Loss)
    candidatos = df[
        ((df["status"] == "ESCALA") | (df["status"] == "TESTE")) & (df["score"] >= 10)
    ].sort_values(by=["status", "ctr", "score"], ascending=False).head(4)
    
    horarios = ["08:00", "12:30", "18:00", "21:30"]
    for i, (idx, row) in enumerate(candidatos.iterrows()):
        p_id = f"NEXUS_{datetime.now().strftime('%d%m')}_{i}"
        link_final = converter_afiliado(row['link_origem'], p_id)
        
        payload = {
            "post_id": p_id, "produto": row['produto'], 
            "roteiro": row['roteiro'], "link": link_final, "hora": horarios[i]
        }
        # Envio para o Maverick/Ayrshare via Make.com
        requests.post(st.secrets["WEBHOOK_POSTAGEM"], json=payload)
        enviar_notificacao(f"🚀 Post Agendado: {row['produto']} às {horarios[i]}")
    
    st.success("Ciclo de postagem de hoje enviado para a fila!")

# --- 5. INTERFACE ABSOLUTE ---
st.title("🔱 Nexus Brain: Absolute Decision System")
st.caption(f"Operador: {st.session_state['user_email']} | Cruzamento Shopee + Google Ativo")

tabs = st.tabs(["🔎 Mineração", "🎥 Criativos", "📊 Dataset", "⚡ Automação"])

with tabs[0]: # MINERAÇÃO CRUZADA
    st.header("🎯 Inteligência de Mercado")
    termo = st.text_input("Buscar tendências para:")
    if st.button("🔄 Rodar Cruzamento de Dados", use_container_width=True):
        with st.status("Minerando produtos validados..."):
            res = gerar_ia(f"Identifique 5 produtos de {termo} na Shopee Brasil com alta tendência no Google. Retorne uma tabela com sugestão de links.")
            st.markdown(res)
            st.session_state['p_minerado'] = termo

with tabs[1]: # GERAÇÃO E CLONAGEM DE SUCESSO
    prod = st.text_input("Produto alvo:", value=st.session_state.get('p_minerado', ""))
    link_raw = st.text_input("Link Original da Shopee:")
    
    if st.button("🚀 Criar Arsenal (Baseado em Vencedores)"):
        df_hist = pd.read_csv(DATA_PATH)
        top_vencedores = df_hist[df_hist["status"] == "ESCALA"].sort_values(by="ctr", ascending=False).head(5)
        
        # Prompt de Aprendizado: Reclona o que já deu certo
        prompt = f"Crie 5 roteiros virais de 15s para o produto {prod}."
        if not top_vencedores.empty:
            prompt = f"Baseado nestes roteiros de sucesso: {top_vencedores['roteiro'].to_list()}, crie 5 novas variações para {prod} mantendo os mesmos gatilhos de clique."
            
        res_ia = gerar_ia(prompt)
        variacoes = [v.strip() for v in res_ia.split("###") if len(v) > 10]
        
        df = pd.read_csv(DATA_PATH)
        for v in variacoes:
            novo = {
                "data": datetime.now().strftime("%d/%m/%Y"), "post_id": "PENDENTE",
                "produto": prod, "roteiro": v, "link_origem": link_raw,
                "views": 0, "cliques": 0, "ctr": 0, "status": "TESTE", "score": 10
            }
            df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
        df.to_csv(DATA_PATH, index=False)
        st.success("5 novos roteiros adicionados ao Arsenal de teste!")

with tabs[2]: # GESTÃO DE PERFORMANCE
    st.header("📊 Painel de Controle de Métricas")
    df_atual = pd.read_csv(DATA_PATH)
    # Esconde os descartados para focar no lucro
    df_filtrado = df_atual[df_atual["status"] != "DESCARTADO"]
    
    edited = st.data_editor(df_filtrado, num_rows="dynamic")
    if st.button("💾 Salvar e Processar Inteligência"):
        df_final = processar_inteligencia(edited)
        df_final.to_csv(DATA_PATH, index=False)
        st.rerun()

with tabs[3]: # COMANDO CENTRAL PLAY/STOP
    st.header("🕹️ Automação de Postagem")
    if "nexus_active" not in st.session_state:
        st.session_state["nexus_active"] = False
        
    c1, c2 = st.columns(2)
    if c1.button("▶️ LIGAR NEXUS (PLAY)", use_container_width=True, type="primary"):
        st.session_state["nexus_active"] = True
        enviar_notificacao("SISTEMA ONLINE - Modo Escala Ativado.")
    
    if c2.button("🛑 DESLIGAR NEXUS (STOP)", use_container_width=True):
        st.session_state["nexus_active"] = False
        enviar_notificacao("SISTEMA OFFLINE - Operação Pausada.")
        
    st.divider()
    if st.session_state["nexus_active"]:
        st.success("🤖 Robô Operacional: Monitorando Dataset para as 4 postagens diárias.")
        if st.button("🚀 Forçar Disparo Imediato"):
            disparar_ciclo_agendado()
    else:
        st.error("⚠️ Sistema em PAUSE. Ligue o Nexus para habilitar postagens automáticas.")
