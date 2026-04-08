import streamlit as st
import arsenal 
import estudio
import pandas as pd
import update
import radar_engine 
import os
import urllib.parse
from datetime import datetime
import mineracao as miny

# --- 1. CONFIGURAÇÃO DE TELA (Obrigatório ser a primeira linha) ---
st.set_page_config(page_title="Nexus Absolute V101", layout="wide", page_icon="🔱")

# --- 2. FUNÇÃO DE RENDERIZAÇÃO DE CARDS (Scanner) ---
def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt_alvo):
    icones = {"Shopee": "🧡", "Mercado Livre": "💛", "Amazon": "💙"}
    ico = icones.get(mkt_alvo, "🛍️")
    
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            st.markdown(f"**{ico} {nome}**")
            st.caption(f"💰 {valor} | 🎫 {ticket}")
        
        with c2:
            calor_num = min(max(int(calor), 0), 100)
            st.progress(calor_num / 100)
            st.write(f"🌡️ {calor_num}°C")
        
        # O Padrão 2026: width='stretch'
        if c3.button("🎯 Selecionar", key=f"sel_{idx}_{mkt_alvo}", width='stretch'):
            st.session_state.sel_nome = nome
            st.session_state.sel_link = link
            st.toast(f"Alvo Selecionado: {nome}")

# --- 3. SISTEMA DE ACESSO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

def login():
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Absolute</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha_mestra = st.secrets.get("NEXUS_PASSWORD", "Bru2024!")
        senha = st.text_input("Acesso:", type="password")
        if st.button("AUTENTICAR", width='stretch'):
            if senha == senha_mestra:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    st.stop()

if not st.session_state.autenticado:
    login()

# --- 4. ESTADO DA SESSÃO ---
if "res_busca" not in st.session_state: st.session_state.res_busca = ""
if "sel_nome" not in st.session_state: st.session_state.sel_nome = ""
if "sel_link" not in st.session_state: st.session_state.sel_link = ""
if "mkt_global" not in st.session_state: st.session_state.mkt_global = "Shopee"

# --- 5. INTERFACE PRINCIPAL ---
st.sidebar.title("🔱 Nexus Control")
st.session_state.mkt_global = st.sidebar.selectbox(
    "Marketplace Ativo:", 
    ["Shopee", "Mercado Livre", "Amazon"], 
    index=["Shopee", "Mercado Livre", "Amazon"].index(st.session_state.mkt_global)
)

# Motor configurado para Gemini Pro Estável (Lido pelo mineracao.py)
motor_ia = "gemini-1.5-pro" 

tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "🌍 RADAR", "🎥 ESTÚDIO", "📊 DASHBOARD"])

# --- ABA 0: SCANNER ---
with tabs[0]:
    st.header(f"🔍 Scanner Nexus: {st.session_state.mkt_global}")
    
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        qtd_produtos = st.selectbox("Volume de Mineração:", [15, 30, 45], index=1)
    
    with col_sel2:
        foco_nicho = st.text_input("🎯 Nicho da Operação:", value="Cozinha Criativa", key="nicho_input")

    if st.button(f"🔥 INICIAR VARREDURA {st.session_state.mkt_global.upper()}", width='stretch'):
        with st.spinner(f"Nexus minerando produtos virais em '{foco_nicho}'..."):
            prompt_scanner = f"""
            Liste {qtd_produtos} produtos físicos da {st.session_state.mkt_global} para o nicho '{foco_nicho}'.
            Formato por linha: NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo/Médio/Alto] | URL: [link]
            """
            # mineracao.py usará Groq aqui para evitar limites do Gemini
            resultado = miny.minerar_produtos(prompt_scanner, st.session_state.mkt_global, motor_ia)
            st.session_state.res_busca = resultado
    
# --- DENTRO DA ABA 0: SCANNER (Logo após o st.session_state.res_busca) ---
    if st.session_state.res_busca:
        st.divider()
        filtro_ticket = st.multiselect("Filtrar por Ticket:", ["Baixo", "Médio", "Alto"], default=["Baixo", "Médio", "Alto"])
        
        linhas = st.session_state.res_busca.split('\n')
       # --- Dentro do loop de linhas do Scanner no seu app.py ---
for idx, linha in enumerate(linhas):
    linha_limpa = linha.replace("**", "").replace("*", "").strip()
    
    if "|" in linha_limpa:
        try:
            # Divide a linha por |
            partes = [p.strip() for p in linha_limpa.split('|')]
            
            # Pega o nome: Se não achar "NOME:", pega a primeira parte da linha
            nome_final = "Produto"
            for p in partes:
                if "NOME:" in p.upper():
                    nome_final = p.split(':', 1)[1].strip()
                    break
            if nome_final == "Produto" and len(partes) > 0:
                nome_final = partes[0].replace("NOME:", "").strip()

            # Pega o Valor
            valor_final = "R$ 0,00"
            for p in partes:
                if "VALOR:" in p.upper():
                    valor_final = p.split(':', 1)[1].strip()
                    break

            # Renderiza o Card
            renderizar_card_produto(
                idx, nome_final, valor_final, 95, "Médio", "#", st.session_state.mkt_global
            )
        except:
            continue
                    
                    # 3. LÓGICA DE NOME BLINDADA:
                    # Tenta achar a chave que CONTÉM "NOME" (ex: "1. NOME" ou "NOME")
                    nome_final = "Produto Desconhecido"
                    for k in dados.keys():
                        if "NOME" in k:
                            nome_final = dados[k]
                            break
                    
                    # Se ainda for o padrão, pega a primeira parte da linha (geralmente o nome)
                    if nome_final == "Produto Desconhecido" and partes_brutas:
                        nome_final = partes_brutas[0].replace("NOME:", "").strip()

                    # 4. Captura os outros dados com fallbacks
                    ticket_val = "Médio"
                    for k in dados.keys():
                        if "TICKET" in k: ticket_val = dados[k]; break
                    
                    if ticket_val in filtro_ticket:
                        # Extrai apenas os números do Calor
                        c_num = "".join(filter(str.isdigit, str(dados.get("CALOR", "0"))))
                        
                        renderizar_card_produto(
                            idx, 
                            nome_final, 
                            dados.get("VALOR", "R$ ---"), 
                            int(c_num) if c_num else 0, 
                            ticket_val, 
                            dados.get("URL", "#"), 
                            st.session_state.mkt_global
                        )
                except Exception as e:
                    continue # Pula linhas que derem erro de formato

# --- ABA 1: ARSENAL ---
with tabs[1]:  
    arsenal.exibir_arsenal(miny, motor_ia)

# --- ABA 2: RADAR ---
with tabs[2]:
    st.header("🌍 Inteligência Radar")
    c_eua, c_br = st.columns(2)
    if c_eua.button("🇺🇸 Scanner TikTok USA", width='stretch'): 
        st.info("Buscando tendências internacionais...")
    if c_br.button(f"🇧🇷 Trends {st.session_state.mkt_global}", width='stretch'): 
        st.success("Analisando volume de buscas Brasil...")

# --- ABA 3: ESTÚDIO ---
with tabs[3]:
    estudio.exibir_estudio(miny, motor_ia)

# --- ABA 4: DASHBOARD ---
with tabs[4]:
    update.dashboard_performance_simples()
