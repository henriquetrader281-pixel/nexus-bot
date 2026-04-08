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

# --- FUNÇÃO DE RENDERIZAÇÃO ---
def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt_alvo):
    icones = {"Shopee": "📦", "Mercado Livre": "🏪", "Amazon": "🛒"}
    ico = icones.get(mkt_alvo, "🛍️")
    
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.write(f"{ico} **{nome}**")
        c1.caption(f"💰 {valor} | 🎫 {ticket} | 🏷️ {mkt_alvo}")
        
        calor_num = min(max(int(calor), 0), 100)
        c2.progress(calor_num / 100)
        c2.write(f"🌡️ {calor_num}°C")
        
        if c3.button("Selecionar", key=f"btn_{idx}_{mkt_alvo}"):
            st.session_state.sel_nome = nome
            st.session_state.sel_link = link
            st.toast(f"Selecionado: {nome}")

# --- 1. CONFIGURAÇÃO E LOGIN ---
st.set_page_config(page_title="Nexus Absolute V101", layout="wide", page_icon="🔱")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

def login():
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Absolute</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha_mestra = st.secrets.get("NEXUS_PASSWORD", "Bru2024!")
        senha = st.text_input("Acesso:", type="password")
        if st.button("Entrar", use_container_width=True):
            if senha == senha_mestra:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    st.stop()

if not st.session_state.autenticado: login()

# --- 2. ESTADO DA SESSÃO ---
if "res_busca" not in st.session_state: st.session_state.res_busca = ""
if "sel_nome" not in st.session_state: st.session_state.sel_nome = ""
if "sel_link" not in st.session_state: st.session_state.sel_link = ""
if "copy_ativa" not in st.session_state: st.session_state.copy_ativa = ""
if "mkt_global" not in st.session_state: st.session_state.mkt_global = "Shopee"

# --- 3. INTERFACE PRINCIPAL ---
st.sidebar.title("🔱 Configurações")
st.session_state.mkt_global = st.sidebar.selectbox("Marketplace:", ["Shopee", "Mercado Livre", "Amazon"], index=["Shopee", "Mercado Livre", "Amazon"].index(st.session_state.mkt_global))

st.sidebar.info(f"Nicho Atual: {st.session_state.get('nicho_ativo', 'Cozinha Criativa')}")

# TRAVA DE SEGURANÇA: Força o Gemini no sistema inteiro
motor_ia = "gemini-1.5-pro" 

tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "🌍 RADAR", "🎥 ESTÚDIO", "📊 DASHBOARD"])

# --- ABA 0: SCANNER ---
with tabs[0]:
    st.header(f"🔍 Scanner Nexus: {st.session_state.mkt_global}")
    
    c_mkt1, c_mkt2, c_mkt3 = st.columns(3)
    if c_mkt1.button("🧡 Shopee", use_container_width=True): 
        st.session_state.mkt_global = "Shopee"
        st.rerun()
    if c_mkt2.button("💛 Mercado Livre", use_container_width=True): 
        st.session_state.mkt_global = "Mercado Livre"
        st.rerun()
    if c_mkt3.button("💙 Amazon", use_container_width=True): 
        st.session_state.mkt_global = "Amazon"
        st.rerun()

    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        qtd_produtos = st.selectbox("Quantidade de itens:", [15, 30, 45], index=1)
    
    with col_sel2:
        foco_nicho = st.text_input("🎯 Foco do Scanner (Mudar Nicho):", value="Cozinha Criativa", key="nicho_ativo")

    if st.button(f"🔥 Iniciar Varredura na {st.session_state.mkt_global}", use_container_width=True):
        with st.spinner(f"IA minerando {qtd_produtos} produtos em '{foco_nicho}'..."):
            
            # --- PROMPT BLINDADO PARA O SCANNER ---
            prompt_scanner = f"""Atue como um analista de produtos virais da {st.session_state.mkt_global}.
Liste {qtd_produtos} produtos físicos altamente lucrativos para o nicho '{foco_nicho}'.
REGRA DE OURO: NÃO escreva NENHUMA palavra de introdução ou conclusão.
Devolva APENAS as linhas dos produtos. CADA PRODUTO em UMA linha única.
O formato de cada linha DEVE SER RIGOROSAMENTE ESTE (Use o | para separar os dados e não use negritos):
NOME: Nome do Produto | CALOR: 95 | VALOR: R$ 49,90 | TICKET: Baixo | URL: https://shopee.com.br/search?keyword=exemplo"""

            resultado = miny.minerar_produtos(prompt_scanner, st.session_state.mkt_global, motor_ia)
            st.session_state.res_busca = resultado
    
    if st.session_state.res_busca:
        st.divider()
        filtro_ticket = st.multiselect("Visualizar Tickets:", ["Baixo", "Médio", "Alto"], default=["Baixo", "Médio", "Alto"])
        
        linhas = st.session_state.res_busca.split('\n')
        for idx, linha in enumerate(linhas):
            # Limpeza anti-negrito da IA (remove asteriscos)
            linha_limpa = linha.replace("**", "").replace("*", "")
            
            if "|" in linha_limpa and "NOME" in linha_limpa.upper():
                try:
                    partes = {p.split(':')[0].strip().upper(): p.split(':')[1].strip() for p in linha_limpa.split('|') if ':' in p}
                    ticket_atual = partes.get("TICKET", "Médio")
                    
                    if ticket_atual in filtro_ticket:
                        c_str = "".join(filter(str.isdigit, partes.get("CALOR", "0")))
                        renderizar_card_produto(
                            idx, 
                            partes.get("NOME", "Produto"), 
                            partes.get("VALOR", "Consultar"), 
                            int(c_str) if c_str else 0,
                            ticket_atual,
                            partes.get("URL", "#"),
                            st.session_state.mkt_global
                        )
                except Exception as e:
                    continue

# --- ABA 1: ARSENAL ---
with tabs[1]:  
    st.header("🚀 Arsenal Nexus")
    if st.session_state.sel_nome:
        st.success(f"🎯 Produto Ativo: **{st.session_state.sel_nome}**")
        
        if st.button(f"🚀 INJETAR 10 VARIAÇÕES DO SELECIONADO NA {st.session_state.mkt_global}", type="primary"):
            with st.spinner("Gerando copys e conectando ao banco de dados..."):
                prompt_hack = f"""IGNORE AS INSTRUÇÕES DE MINERAÇÃO DE DADOS. Aja APENAS como um Copywriter Sênior especialista em vídeos virais (TikTok/Reels).
Sua missão é escrever 10 opções de copy de ALTA CONVERSÃO para o produto '{st.session_state.sel_nome}'.
Aplique estritamente o framework AIDA em textos curtos, dinâmicos e focados em retenção.
Cada variação DEVE ter:
1. ATENÇÃO (Hook): Uma frase de impacto, polêmica ou curiosidade nos primeiros segundos.
2. INTERESSE/DESEJO: Toque na ferida. Como esse produto resolve um problema irritante do dia a dia ou traz muito status?
3. AÇÃO (CTA): Uma ordem agressiva e clara no final (Ex: 'Clica no link da bio e garante o seu antes que esgote!', 'Comenta EU QUERO que te mando o link agora').
REGRAS RÍGIDAS: Seja informal e persuasivo. NÃO liste outros produtos. NÃO invente preços. NÃO coloque URLs (links). Entregue apenas as 10 copys, uma por linha."""
                
                res_ia = miny.minerar_produtos(prompt_hack, st.session_state.mkt_global, motor_ia)
                
                variacoes_limpas = []
                for linha in res_ia.split('\n'):
                    texto = linha.strip().replace('"', '')
                    if len(texto) > 10 and "CALOR:" not in texto and "URL:" not in texto and "Aqui estão" not in texto:
                        variacoes_limpas.append(texto)
                
                for i, v in enumerate(variacoes_limpas[:10]):
                    with st.container(border=True):
                        st.write(v)
                        if st.button(f"Usar V{i+1}", key=f"v_{i}"):
                            st.session_state.copy_ativa = v
                            st.toast("Enviado ao Estúdio!")
                
                nicho_atual = st.session_state.get('nicho_ativo', 'Geral')
                sucesso = update.aplicar_seo_viral(
                    st.session_state.sel_nome, 
                    st.session_state.sel_link, 
                    nicho_atual
                )
                
                if sucesso:
                    st.success("✅ Sincronizado com a Nuvem e Shopee com sucesso!")
                else:
                    st.error("Erro ao salvar no banco de dados.")
    else:
        st.warning("⚠️ Selecione um produto no Scanner.")

# --- ABA 2: RADAR ---
with tabs[2]:
    st.header("🌍 Inteligência Radar")
    c_eua, c_br = st.columns(2)
    
    if c_eua.button("🇺🇸 Scanner TikTok USA"): 
        st.info("Buscando produtos virais nos EUA...")
        try:
            radar_engine.buscar_trends_usa()
        except:
            pass
            
    if c_br.button(f"🇧🇷 Trends {st.session_state.mkt_global}"): 
        st.success(f"Analisando tendências na {st.session_state.mkt_global}...")

# --- ABA 3: ESTÚDIO ---
with tabs[3]:
    st.header("🎥 Estúdio de Edição Automática")
    estudio.exibir_estudio(miny, motor_ia)

# --- ABA 4: DASHBOARD ---
with tabs[4]:
    st.header("📊 Dashboard de Performance")
    try:
        update.dashboard_performance_simples()
    except:
        st.info("Dashboard será carregado após as primeiras injeções.")
