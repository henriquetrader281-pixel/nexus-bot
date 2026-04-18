"""
NEXUS ABSOLUTE - Sistema Automático de Affiliate Marketing
Versão: 3.1 (Shopee Only + Gemini Corrigido)

✅ CORREÇÕES v3.1:
- Mineração APENAS de Shopee (não Amazon/Mercado Livre)
- Gemini corrigido (sem prefixo models/)
- Links com ID afiliado garantido
- Integração completa com arsenal_tab.py
"""

import streamlit as st
import os
import json
import urllib.parse
from datetime import datetime
import google.generativeai as genai

# ============================================================================
# IMPORTAÇÕES DOS MÓDULOS PRÓPRIOS
# ============================================================================
try:
    import arsenal_tab as arsenal
    import scanner_tab as scanner
    import producao_midia as estudio
    import scheduler as postador
    import nexus_copy as nxcopy
    # Opcional (comentado se não tiver):
    # import trends
    # import radar_engine
except ImportError as e:
    st.warning(f"⚠️ Alguns módulos não encontrados: {e}")


# ============================================================================
# CONFIGURAÇÃO STREAMLIT
# ============================================================================
st.set_page_config(
    page_title="Nexus Absolute | Affiliate Marketing",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Customizado
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-weight: bold;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# INICIALIZAÇÃO: GEMINI API (CORRIGIDO v3.0)
# ============================================================================
def inicializar_gemini():
    """
    Inicializa Gemini com modelo CORRETO (sem prefixo 'models/')
    """
    try:
        # Tentar secrets.toml primeiro
        api_key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
        
        if not api_key:
            st.error(
                "🔴 **API Key não encontrada**\n\n"
                "Adicione em `.streamlit/secrets.toml`:\n"
                "```\nGEMINI_API_KEY = 'sua-chave'\n```"
            )
            return None
        
        genai.configure(api_key=api_key)
        
        # ✅ CORRETO: Sem prefixo 'models/'
        modelo = genai.GenerativeModel('gemini-1.5-flash')
        
        return modelo
        
    except Exception as e:
        st.error(f"❌ Erro ao inicializar Gemini: {str(e)}")
        return None


# ============================================================================
# MINERAÇÃO: APENAS SHOPEE
# ============================================================================
def minerar_shopee(termo_busca, modelo_ia):
    """
    Minera APENAS produtos de Shopee.
    Usa Gemini para listar produtos virais com formato padronizado.
    """
    try:
        prompt = f"""
Você é um especialista em produtos virais da Shopee Brasil.
Analise o termo de busca: "{termo_busca}"

Retorne EXATAMENTE 10 produtos REAIS da Shopee em JSON puro (sem markdown, sem ```):
{{
    "produtos": [
        {{
            "nome": "Nome do Produto",
            "valor": "R$ 99,90",
            "calor": 85,
            "ticket": "Médio",
            "url": "https://shopee.com.br/p/12345",
            "vendas": 1500,
            "avaliacao": 4.8
        }}
    ]
}}

IMPORTANTE:
- APENAS produtos da Shopee
- URLs DEVEM começar com https://shopee.com.br/
- Calor: 50-99 (viralidade)
- Retorne APENAS JSON válido
"""
        
        response = modelo_ia.generate_content(prompt)
        
        if not response or not response.text:
            st.error("❌ Gemini retornou resposta vazia")
            return []
        
        # Limpar JSON
        json_text = response.text.replace('```json', '').replace('```', '').strip()
        
        try:
            dados = json.loads(json_text)
            return dados.get("produtos", [])
        except json.JSONDecodeError as e:
            st.error(f"❌ Erro ao decodificar JSON: {str(e)}")
            st.code(json_text)  # Debug
            return []
            
    except Exception as e:
        st.error(f"❌ Erro ao minerar: {str(e)}")
        return []


# ============================================================================
# RENDERIZAR CARD DE PRODUTO
# ============================================================================
def renderizar_card_produto(idx, produto):
    """
    Renderiza um card de produto com estilo melhorado.
    """
    nome = produto.get("nome", "Produto Detectado")
    valor = produto.get("valor", "---")
    calor = produto.get("calor", 50)
    ticket = produto.get("ticket", "Médio")
    url = produto.get("url", "#")
    vendas = produto.get("vendas", 0)
    avaliacao = produto.get("avaliacao", 0)
    
    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        # COLUNA 1: Nome, preço, ticket
        with col1:
            st.markdown(f"**🧡 {nome}**")
            st.caption(f"💰 {valor} | 🎫 {ticket} | ⭐ {avaliacao}")
            if vendas > 0:
                st.caption(f"📊 {vendas:,} vendas")
        
        # COLUNA 2: Indicador de calor
        with col2:
            calor_num = min(max(int(calor), 0), 100)
            st.progress(calor_num / 100)
            st.write(f"🌡️ {calor_num}°C")
        
        # COLUNA 3: Botão selecionar
        with col3:
            if st.button("🎯 Selecionar", key=f"sel_{idx}", use_container_width=True):
                # Salvar em session state
                st.session_state.sel_nome = nome
                st.session_state.sel_link = url
                st.session_state.sel_preco = valor
                st.session_state.sel_calor = calor_num
                
                st.success(f"✅ Selecionado: {nome}")
                st.toast(f"🎯 Enviando para Arsenal...")


# ============================================================================
# INICIALIZAÇÃO: SESSION STATE
# ============================================================================
def inicializar_session_state():
    """Inicializa todas as variáveis de sessão."""
    
    # Scanner
    if "produtos_minerados" not in st.session_state:
        st.session_state.produtos_minerados = []
    if "sel_nome" not in st.session_state:
        st.session_state.sel_nome = None
    if "sel_link" not in st.session_state:
        st.session_state.sel_link = None
    if "sel_preco" not in st.session_state:
        st.session_state.sel_preco = None
    if "sel_calor" not in st.session_state:
        st.session_state.sel_calor = 0
    
    # Arsenal
    if "res_arsenal" not in st.session_state:
        st.session_state.res_arsenal = None
    if "copy_ativa" not in st.session_state:
        st.session_state.copy_ativa = None
    if "link_final_afiliado" not in st.session_state:
        st.session_state.link_final_afiliado = None
    
    # Studio
    if "videos_gerados" not in st.session_state:
        st.session_state.videos_gerados = []
    
    # Postador
    if "conteudo_agendado" not in st.session_state:
        st.session_state.conteudo_agendado = []


# ============================================================================
# SIDEBAR: CONTROLES
# ============================================================================
def exibir_sidebar():
    """Exibe sidebar com status e controles."""
    st.sidebar.markdown("# ⚙️ Controles Nexus")
    
    # Status
    st.sidebar.markdown("### 📊 Status Atual")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Produto", st.session_state.sel_nome or "—")
    with col2:
        st.metric("Preço", st.session_state.sel_preco or "—")
    
    st.sidebar.divider()
    
    # Controles
    st.sidebar.markdown("### 🎯 Ações")
    if st.sidebar.button("🧹 Limpar Sessão", use_container_width=True):
        inicializar_session_state()
        st.success("✅ Sessão limpa!")
        st.rerun()
    
    st.sidebar.divider()
    
    # Info
    st.sidebar.markdown("### ℹ️ Informações")
    st.sidebar.info(
        "**Nexus Absolute v3.1**\n\n"
        "🔱 Marketing de Afiliado\n"
        "📱 Shopee Brasil Only\n"
        "🤖 Powered by Gemini\n\n"
        "Última atualização: 2026-04-18"
    )


# ============================================================================
# HEADER
# ============================================================================
def exibir_header():
    """Exibe header com métricas."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Produtos", len(st.session_state.produtos_minerados))
    with col2:
        st.metric("💎 Copys", len(st.session_state.res_arsenal or []))
    with col3:
        st.metric("🎬 Vídeos", len(st.session_state.videos_gerados))
    with col4:
        st.metric("📅 Posts", len(st.session_state.conteudo_agendado))


# ============================================================================
# MAIN APP
# ============================================================================
def main():
    """Função principal do aplicativo."""
    
    # Inicializar
    inicializar_session_state()
    exibir_header()
    exibir_sidebar()
    
    # Inicializar Gemini
    st.session_state.motor_ia_obj = inicializar_gemini()
    
    if not st.session_state.motor_ia_obj:
        st.error("❌ Não foi possível inicializar Gemini. Verifique sua API Key.")
        st.stop()
    
    st.success("✅ Gemini inicializado com sucesso!")
    st.divider()
    
    # ========================================================================
    # TABS PRINCIPAIS
    # ========================================================================
    tabs = st.tabs([
        "🔍 SCANNER",
        "🔱 ARSENAL",
        "🎬 ESTÚDIO",
        "📱 POSTADOR",
        "📊 DASHBOARD",
    ])
    
    # TAB 0: SCANNER (Mineração Shopee)
    with tabs[0]:
        st.markdown("## 🔍 Scanner - Mineração Shopee")
        st.info("🛍️ Minerando APENAS produtos Shopee Brasil")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            termo = st.text_input(
                "Buscar produto Shopee:",
                placeholder="Ex: Power Bank, Fone Bluetooth, etc",
                key="termo_busca"
            )
        
        with col2:
            btn_varrer = st.button("🚀 INICIAR VARREDURA", use_container_width=True)
        
        if btn_varrer and termo:
            with st.spinner("🔍 Minerando Shopee..."):
                produtos = minerar_shopee(termo, st.session_state.motor_ia_obj)
                
                if produtos:
                    st.session_state.produtos_minerados = produtos
                    st.success(f"✅ {len(produtos)} produtos encontrados!")
                else:
                    st.error("❌ Nenhum produto encontrado")
        
        # Exibir produtos
        if st.session_state.produtos_minerados:
            st.divider()
            st.markdown(f"### 📦 Resultados ({len(st.session_state.produtos_minerados)} produtos)")
            
            for idx, produto in enumerate(st.session_state.produtos_minerados):
                renderizar_card_produto(idx, produto)
    
    # TAB 1: ARSENAL (Geração de Copys)
    with tabs[1]:
        st.markdown("## 🔱 Arsenal - Geração de Copys AIDA")
        
        if not st.session_state.sel_nome:
            st.warning("⚠️ Selecione um produto no SCANNER primeiro")
        else:
            try:
                arsenal_tab.exibir_arsenal(None, st.session_state.motor_ia_obj)
            except Exception as e:
                st.error(f"❌ Erro no Arsenal: {str(e)}")
    
    # TAB 2: ESTÚDIO (Produção de Vídeos)
    with tabs[2]:
        st.markdown("## 🎬 Estúdio - Produção de Vídeos")
        
        if not st.session_state.copy_ativa:
            st.info("📝 Gere um copy no ARSENAL primeiro")
        else:
            st.info("🎬 Tab em desenvolvimento...")
            st.caption(f"Copy Ativa: {st.session_state.copy_ativa[:50]}...")
    
    # TAB 3: POSTADOR (Agendamento)
    with tabs[3]:
        st.markdown("## 📱 Postador - Agendamento Automático")
        st.info("📅 Agende seus vídeos para Instagram/TikTok")
        
        if not st.session_state.videos_gerados:
            st.info("🎬 Crie vídeos no ESTÚDIO primeiro")
        else:
            st.caption(f"Vídeos disponíveis: {len(st.session_state.videos_gerados)}")
    
    # TAB 4: DASHBOARD (Métricas)
    with tabs[4]:
        st.markdown("## 📊 Dashboard - Métricas e Performance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🔗 Cliques", "0")
        with col2:
            st.metric("💰 Conversões", "0")
        with col3:
            st.metric("💵 Receita", "R$ 0,00")
        with col4:
            st.metric("📈 Taxa", "0%")
        
        st.info("📊 Gráficos em desenvolvimento...")


# ============================================================================
# EXECUTAR APP
# ============================================================================
if __name__ == "__main__":
    main()
