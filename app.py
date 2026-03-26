import streamlit as st
from groq import Groq
from datetime import datetime

# --- 1. SISTEMA DE SEGURANÇA (DUPLA CONFIRMAÇÃO) ---
st.set_page_config(page_title="Nexus Private Hub", page_icon="🔐", layout="wide")

def login_nexus():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.markdown("<h1 style='text-align: center;'>🔐 Nexus Private Access</h1>", unsafe_allow_html=True)
        st.info("Sistema Restrito. Identifique-se para carregar a inteligência.")
        
        with st.form("login_form"):
            email_input = st.text_input("E-mail Autorizado:", placeholder="seu@email.com")
            senha_input = st.text_input("Senha Mestre:", type="password")
            submit = st.form_submit_button("Liberar Acesso", use_container_width=True)
            
            if submit:
                autorizados = st.secrets.get("ALLOWED_USERS", "").split(",")
                autorizados = [email.strip() for email in autorizados]
                
                if email_input in autorizados and senha_input == st.secrets["NEXUS_PASSWORD"]:
                    st.session_state["autenticado"] = True
                    st.success("Acesso Concedido. Sincronizando...")
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
st.title("🧠 Nexus Brain: Operação Privada")
st.caption(f"📅 Logged as Operator | {datetime.now().strftime('%d/%m/%Y %H:%M')}")

aba_hub, aba_midia, aba_social, aba_lucro = st.tabs([
    "🔎 Hub Multicanal", 
    "🎥 Mídia & Fontes",
    "📅 Agendador Social", 
    "📊 Métricas & ROI"
])

# --- ABA 1: HUB MULTICANAL ---
with aba_hub:
    st.header("🔎 Mineração Diária (Shopee, ML, Amazon)")
    if st.button("Executar Varredura Global Hoje", key="btn_min_global"):
        with st.status("Nexus rastreando tendências...", expanded=True) as status:
            prompt_hub = """
            Aja como um Meta-Scanner de E-commerce Pro (Março 2026). 
            Liste os 10 produtos mais virais do dia no Brasil (Shopee, Mercado Livre, Amazon). 
            Responda EXATAMENTE em formato de tabela Markdown:
            | Produto | Plataforma | Viralidade (0-10) | Link de Busca Sugerido |
            | --- | --- | --- | --- |
            """
            res = gerar_ia(prompt_hub)
            st.session_state['tabela_minerada'] = res
            status.update(label="Varredura Concluída!", state="complete", expanded=False)
    
    if 'tabela_minerada' in st.session_state:
        st.markdown(st.session_state['tabela_minerada'])

# --- ABA 2: MÍDIA E FONTES ---
with aba_midia:
    st.header("🎥 Fontes de Conteúdo")
    prod_busca = st.text_input("Produto para Mídia:", placeholder="Copie o nome da aba anterior...")
    
    if st.button("Localizar Fontes de Vídeo/Imagem"):
        with st.spinner("Buscando links de referência..."):
            prompt_midia = f"Gere links de busca direta no TikTok, Instagram, Pinterest e AliExpress para o produto: {prod_busca}. Organize em Markdown."
            res_midia = gerar_ia(prompt_midia)
            st.session_state['fontes_midia'] = res_midia
            st.session_state['produto_ativo'] = prod_busca
            st.markdown(res_midia)

    st.divider()
    if 'produto_ativo' in st.session_state:
        st.subheader(f"📝 Roteirização: {st.session_state['produto_ativo']}")
        if st.button("Gerar Roteiro + Cenas"):
            res_roteiro = gerar_ia(f"Crie um roteiro viral de 30s e cenas de 3s para: {st.session_state['produto_ativo']}")
            st.session_state['roteiro_final'] = res_roteiro
            st.write(res_roteiro)

# --- ABA 3: AGENDADOR ---
with aba_social:
    st.header("📅 Agendamento")
    if 'roteiro_final' in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            rede = st.selectbox("Rede:", ["Instagram", "TikTok", "YouTube"])
            hora = st.select_slider("Hora:", options=["09:00", "12:00", "18:00", "21:00"])
        with col2:
            if st.button("Gerar Legenda"):
                leg = gerar_ia(f"Crie uma legenda viral com hashtags para: {st.session_state['roteiro_final']}")
                st.session_state['legenda_final'] = leg
        
        if 'legenda_final' in st.session_state:
            st.text_area("Legenda:", st.session_state['legenda_final'])
            if st.button("🚀 Confirmar Postagem na Fila", use_container_width=True):
                st.success(f"Post de '{st.session_state['produto_ativo']}' agendado!")
    else:
        st.warning("⚠️ Gere um roteiro primeiro.")

# --- ABA 4: ROI ---
with aba_lucro:
    st.header("📊 Calculadora Pro")
    v = st.number_input("Preço Venda (R$):", value=97.0)
    c = st.number_input("Custo + Frete (R$):", value=40.0)
    taxa = st.selectbox("Plataforma (Taxa):", [0.18, 0.22, 0.15], format_func=lambda x: f"{x*100}%")
    
    lucro = v - c - (v * taxa)
    st.metric("Lucro Líquido", f"R$ {lucro:.2f}", delta=f"{(lucro/v)*100:.1f}% Margem")
