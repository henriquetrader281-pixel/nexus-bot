import streamlit as st
import google.generativeai as genai
import mineracao as miny
import arsenal, trends, postador, studio_tab, update

# --- CONFIGURAÇÃO ---
ID_AFILIADO = "18316451024"
st.set_page_config(page_title="Nexus Absolute V101", layout="wide", page_icon="🔱")

def renderizar_card_produto(idx, nome, valor, calor, ticket, url_bruta, mkt_alvo):
    # Limpeza e Injeção de ID (Lógica que você gostava)
    link_final = url_bruta.replace(" ", "+").replace("]", "").replace("[", "")
    if "shopee" in link_final.lower():
        link_final = f"{link_final}&smtt=0.0.{ID_AFILIADO}"

    with st.container(border=True):
        col_img, col_txt, col_btn = st.columns([1, 4, 1.5])
        with col_img: 
            st.markdown(f"<h1 style='text-align: center;'>{'🧡' if mkt_alvo == 'Shopee' else '💙'}</h1>", unsafe_allow_html=True)
        with col_txt:
            st.markdown(f"### {nome}")
            st.markdown(f"💰 **Valor:** {valor} | 🏷️ **Ticket:** {ticket}")
            st.caption(f"🔗 {link_final[:65]}...")
        with col_btn:
            st.metric("🔥 CALOR", f"{calor}°C")
            st.link_button("👁️ VER PRODUTO", link_final, use_container_width=True)
            if st.button("🎯 SELECIONAR", key=f"sel_{idx}", use_container_width=True):
                st.session_state.sel_nome, st.session_state.sel_link = nome, link_final
                st.success("Capturado!")

# --- LOGIN E MOTOR ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    senha = st.text_input("Senha Master:", type="password")
    if st.button("ACESSAR"):
        if senha == st.secrets["NEXUS_PASSWORD"]: st.session_state.autenticado = True; st.rerun()
    st.stop()

if "motor_ia_obj" not in st.session_state:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    st.session_state.motor_ia_obj = genai.GenerativeModel('gemini-1.5-flash')

# --- INTERFACE ---
tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "🛰️ POSTADOR"])

with tabs[0]:
    mkt = st.sidebar.selectbox("Marketplace:", ["Shopee", "Amazon", "Mercado Livre"])
    qtd = st.slider("Quantidade:", 5, 20, 10)
    
    if st.button("🚀 INICIAR VARREDURA DE ELITE", use_container_width=True):
        with st.spinner("Minerando..."):
            prompt = f"Busque {qtd} produtos virais da {mkt}. Separe por ###"
            resultado = miny.minerar_produtos(prompt, mkt, st.session_state.motor_ia_obj)
            if resultado:
                st.session_state.lista_produtos = [p.strip() for p in resultado.split("###") if "NOME:" in p.upper()]
                st.rerun()

    if st.session_state.get("lista_produtos"):
        for i, bloco in enumerate(st.session_state.lista_produtos):
            try:
                # O FATIADOR: Agora busca URL em vez de LINK
                d = {item.split(":")[0].strip().upper(): item.split(":")[1].strip() for item in bloco.split("|") if ":" in item}
                renderizar_card_produto(
                    i, 
                    d.get("NOME", "Produto"), 
                    d.get("VALOR", "R$ ---"), 
                    d.get("CALOR", "50"), 
                    d.get("TICKET", "Médio"), 
                    d.get("URL", "#"), # BUSCA POR URL
                    mkt
                )
            except: continue
