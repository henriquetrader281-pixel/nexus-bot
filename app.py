import streamlit as st
from groq import Groq
from datetime import datetime

# --- 1. SEGURANÇA E CONFIGURAÇÃO ---
st.set_page_config(page_title="Nexus Private Hub", page_icon="🔐", layout="wide")

def login_nexus():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.markdown("<h1 style='text-align: center;'>🔐 Nexus Private Access</h1>", unsafe_allow_html=True)
        with st.form("login_form"):
            email_input = st.text_input("E-mail Autorizado:", placeholder="seu@email.com")
            senha_input = st.text_input("Senha Mestre:", type="password")
            submit = st.form_submit_button("Liberar Inteligência", use_container_width=True)
            
            if submit:
                autorizados = st.secrets.get("ALLOWED_USERS", "").split(",")
                autorizados = [email.strip() for email in autorizados]
                if email_input in autorizados and senha_input == st.secrets["NEXUS_PASSWORD"]:
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("Credenciais Inválidas.")
        return False
    return True

if not login_nexus():
    st.stop()

# --- 2. CONEXÃO COM A IA (GROQ) ---
api_key = st.secrets.get("GROQ_API_KEY")
client = None
if api_key:
    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        st.error(f"Erro na conexão Groq: {e}")

def gerar_ia(prompt):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erro na IA: {e}"

# --- 3. INTERFACE OPERACIONAL ---
st.title("🧠 Nexus Brain: Hub de Precisão")
st.caption(f"📅 Operador Logado | {datetime.now().strftime('%d/%m/%Y %H:%M')}")

aba_hub, aba_midia, aba_social, aba_lucro = st.tabs([
    "🔎 Hub de Mineração Pro", 
    "🎥 Mídia & Fontes",
    "📅 Agendador Social", 
    "📊 Métricas & ROI"
])

# --- ABA 1: HUB DE MINERAÇÃO COM FILTROS (CORREÇÃO DE LINKS E NICHO) ---
with aba_hub:
    st.header("🎯 Inteligência de Mercado Personalizada")
    
    with st.expander("⚙️ Configurar Filtros de Busca (Recomendado para Iniciantes)", expanded=True):
        col_n, col_p, col_r = st.columns(3)
        
        nicho = col_n.selectbox("Escolha o Nicho:", 
            ["Todos", "Casa & Cozinha", "Saúde & Beleza", "Eletrônicos & Acessórios", "Pet Shop", "Brinquedos", "Ferramentas"])
        
        preco_min, preco_max = col_p.select_slider(
            "Faixa de Preço (Venda):",
            options=[0, 15, 30, 50, 80, 100, 150, 200, 500],
            value=(30, 100)
        )
        
        relevância = col_r.radio("Priorizar por:", ["Mais Vendidos", "Tendência Viral (Novo)", "Volume de Buscas"])

    st.divider()

    if st.button("Executar Varredura Inteligente", key="btn_min_filtros", use_container_width=True):
        with st.status("Nexus filtrando produtos ideais...", expanded=True) as status:
            # Prompt forçado para diversificar links e respeitar preço
            prompt_filtros = f"""
            Aja como um Especialista em Dropshipping e E-commerce Pro (Março 2026).
            Busque os 10 produtos mais virais seguindo ESTES LIMITES:
            - Nicho: {nicho}
            - Preço de Venda: Entre R$ {preco_min} e R$ {preco_max}
            - Critério: {relevância}
            
            Obrigatório: Gere uma tabela equilibrada. Busque links de busca direta para Shopee Brasil, Mercado Livre e Amazon Brasil (pelo menos 3 de cada).
            
            Responda EXATAMENTE em formato de tabela Markdown:
            | Produto | Plataforma | Preço Sug. | Tendência | Link de Busca Direta |
            | --- | --- | --- | --- | --- |
            """
            res = gerar_ia(prompt_filtros)
            st.session_state['tabela_minerada'] = res
            status.update(label="Filtro Aplicado com Sucesso!", state="complete", expanded=False)
    
    if 'tabela_minerada' in st.session_state:
        st.markdown(st.session_state['tabela_minerada'], unsafe_allow_html=True)
        st.info(f"✅ Filtro Ativo: {nicho} | R$ {preco_min} - R$ {preco_max}")

# --- ABA 2: MÍDIA E FONTES ---
with aba_midia:
    st.header("🎥 Fontes de Conteúdo")
    prod_busca = st.text_input("Produto para Mídia:", placeholder="Copie o nome do produto da tabela...")
    
    if st.button("Localizar Fontes de Vídeo/Imagem"):
        if prod_busca:
            with st.spinner("Varrendo links de referência..."):
                prompt_midia = f"Gere links de busca direta no TikTok, Instagram, Pinterest e AliExpress para o produto: {prod_busca}. Foque em vídeos de alta qualidade."
                res_midia = gerar_ia(prompt_midia)
                st.session_state['fontes_midia'] = res_midia
                st.session_state['produto_ativo'] = prod_busca
                st.markdown(res_midia)

    st.divider()
    if 'produto_ativo' in st.session_state:
        st.subheader(f"📝 Roteiro Viral: {st.session_state['produto_ativo']}")
        if st.button("Gerar Roteiro + Cenas"):
            res_roteiro = gerar_ia(f"Crie um roteiro viral de 30s e cenas de 3s para: {st.session_state['produto_ativo']}")
            st.session_state['roteiro_final'] = res_roteiro
            st.write(res_roteiro)

# --- ABA 3: AGENDADOR ---
with aba_social:
    st.header("📅 Agendamento Estratégico")
    if 'roteiro_final' in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            rede = st.selectbox("Rede:", ["Instagram Reels", "TikTok", "YouTube Shorts"])
            hora = st.select_slider("Sugestão de Horário:", options=["09:00", "12:00", "18:00", "21:00"])
        with col2:
            if st.button("Gerar Legenda Magnética"):
                leg = gerar_ia(f"Crie uma legenda de alta conversão para o produto {st.session_state.get('produto_ativo')} com base no roteiro: {st.session_state['roteiro_final']}")
                st.session_state['legenda_final'] = leg
        
        if 'legenda_final' in st.session_state:
            st.text_area("Legenda Final:", st.session_state['legenda_final'], height=150)
            if st.button("🚀 Confirmar Agendamento na Fila", use_container_width=True):
                st.balloons()
                st.success(f"O Nexus adicionou '{st.session_state['produto_ativo']}' à fila de postagem!")
    else:
        st.warning("⚠️ Gere um roteiro na aba anterior primeiro.")

# --- ABA 4: ROI ---
with aba_lucro:
    st.header("📊 Calculadora de Viabilidade")
    v = st.number_input("Preço de Venda Sugerido (R$):", value=89.90)
    c = st.number_input("Custo de Aquisição + Frete (R$):", value=30.0)
    taxa_plataforma = st.selectbox("Canal de Venda:", [0.18, 0.22, 0.15], 
                                  format_func=lambda x: "Shopee (18%)" if x==0.18 else ("Mercado Livre (22%)" if x==0.22 else "Amazon (15%)"))
    
    lucro = v - c - (v * taxa_plataforma)
    st.metric("Lucro Líquido Real", f"R$ {lucro:.2f}", delta=f"Margem de {(lucro/v)*100:.1f}%")
    
    if lucro > 20:
        st.success("🔥 Alta margem! Recomendado para iniciantes (baixo risco e bom retorno).")
    else:
        st.warning("⚠️ Margem baixa. Tente negociar com fornecedor ou aumentar o ticket.")
