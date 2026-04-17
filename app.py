import streamlit as st
import google.generativeai as genai
import mineracao as miny
import arsenal, trends, postador, studio_tab, update

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Nexus Absolute V101", layout="wide", page_icon="🔱")

def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt_alvo):
    # Limpeza final do link (remove espaços e caracteres de erro)
    link_final = str(link).replace(" ", "+").replace("]", "").replace("[", "").strip()
    
    with st.container(border=True):
        col_img, col_txt, col_btn = st.columns([1, 4, 1.5])
        with col_img: 
            st.markdown(f"<h1 style='text-align: center;'>{'🧡' if mkt_alvo == 'Shopee' else '💙'}</h1>", unsafe_allow_html=True)
        with col_txt:
            st.markdown(f"### {nome}")
            st.markdown(f"💰 **Preço:** {valor} | 🏷️ **Ticket:** {ticket}")
            st.caption(f"📍 Link: {link_final[:60]}...")
        with col_btn:
            st.metric("🔥 CALOR", f"{calor}°C")
            st.link_button("👁️ VER PRODUTO", link_final, use_container_width=True)
            if st.button("🎯 SELECIONAR", key=f"sel_{idx}", use_container_width=True):
                st.session_state.sel_nome, st.session_state.sel_link = nome, link_final
                st.success("✅ CAPTURADO!")

# --- MOTOR IA ---
if "motor_ia_obj" not in st.session_state:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    st.session_state.motor_ia_obj = genai.GenerativeModel('gemini-1.5-flash')

if "lista_produtos" not in st.session_state: st.session_state.lista_produtos = []

# --- INTERFACE ---
st.sidebar.title("🔱 Nexus Control")
mkt = st.sidebar.selectbox("Marketplace:", ["Shopee", "Amazon", "Mercado Livre"])
st.session_state.mkt_global = mkt
filtro_ticket = st.sidebar.multiselect("Tickets:", ["Baixo", "Médio", "Alto"], default=["Baixo", "Médio", "Alto"])

tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "🛰️ POSTADOR"])

with tabs[0]:
    st.header(f"🔍 Scanner de Oportunidades - {mkt}")
    qtd = st.slider("Quantidade:", 5, 20, 10)
    
    if st.button("🚀 INICIAR VARREDURA", use_container_width=True):
        with st.spinner("Minerando..."):
            prompt = f"Busque {qtd} produtos virais da {mkt} com ticket {filtro_ticket}. Separe por ###"
            resultado = miny.minerar_produtos(prompt, mkt, st.session_state.motor_ia_obj)
            if resultado:
                # Limpeza de asteriscos que a IA coloca
                res_clean = resultado.replace("**", "").replace("`", "")
                st.session_state.lista_produtos = [p.strip() for p in res_clean.split("###") if "NOME:" in p.upper()]
                st.rerun()

    if st.session_state.lista_produtos:
        for i, bloco in enumerate(st.session_state.lista_produtos):
            try:
                # Fatiador Universal: Busca URL em vez de LINK
                d = {item.split(":")[0].strip().upper(): item.split(":")[1].strip() for item in bloco.split("|") if ":" in item}
                renderizar_card_produto(i, d.get("NOME", "Produto"), d.get("VALOR", "---"), d.get("CALOR", "50"), d.get("TICKET", "Médio"), d.get("URL", "#"), mkt)
            except: continue

# Conexão com módulos
with tabs[1]: arsenal.exibir_arsenal(miny, st.session_state.motor_ia_obj)
with tabs[2]: trends.exibir_trends()
