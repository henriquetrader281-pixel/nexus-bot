import streamlit as st
from groq import Groq
from datetime import datetime
import urllib.parse

# --- 1. SEGURANÇA E PRIVACIDADE ---
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
st.title("🧠 Nexus Brain: Hub de Inteligência 2026")
st.caption(f"📅 Operação Ativa | {datetime.now().strftime('%d/%m/%Y %H:%M')}")

aba_hub, aba_midia, aba_social, aba_lucro = st.tabs([
    "🔎 Hub de Mineração & Google", 
    "🎥 Mídia & Fontes",
    "📅 Agendador Social", 
    "📊 Métricas & ROI"
])

# --- ABA 1: HUB DE MINERAÇÃO PRO (CORRIGIDO) ---
with aba_hub:
    st.header("🎯 Mineração com Termômetro Google")
    
    with st.expander("⚙️ Filtros de Precisão de Mercado", expanded=True):
        col_n, col_p, col_r = st.columns(3)
        nicho = col_n.selectbox("Nicho Alvo:", ["Todos", "Cozinha Criativa", "Saúde & Beleza", "Eletrônicos/Tech", "Pet Shop", "Ferramentas Smart"])
        
        # --- CORREÇÃO DO ERRO VALUEERROR ---
        # Garantindo que value=(40, 100) existam na lista options
        lista_precos = [0, 20, 40, 60, 80, 100, 150, 200, 500]
        preco_min, preco_max = col_p.select_slider(
            "Faixa de Preço Sugerida (Venda):", 
            options=lista_precos, 
            value=(40, 100) 
        )
        
        relevancia = col_r.radio("Prioridade de Busca:", ["🚀 Hype Google (Crescente)", "📈 Volume de Vendas", "📉 Baixa Concorrência"])

    st.divider()

    if st.button("🚀 Executar Varredura Inteligente Multicanal", use_container_width=True):
        with st.status("Nexus analisando Google Search + Marketplaces...", expanded=True) as status:
            prompt_google = f"""
            Aja como um Analista de Big Data Senior em Março de 2026.
            Filtre 10 produtos no nicho {nicho} com preço final entre R$ {preco_min} e R$ {preco_max}.
            Identifique o volume de buscas no GOOGLE BRASIL.
            Retorne EXATAMENTE uma tabela Markdown com:
            | Produto | Plataforma Recomendada | Status Google Search | Link de Busca (Direto) |
            | --- | --- | --- | --- |
            No 'Status Google Search', use: 🚀 (Crescente), 📈 (Estável), ⚠️ (Saturando).
            Force links de busca para Shopee, Mercado Livre ou Amazon Brasil.
            """
            res = gerar_ia(prompt_google)
            st.session_state['tabela_minerada'] = res
            status.update(label="Análise de Tendências Concluída!", state="complete", expanded=False)
    
    if 'tabela_minerada' in st.session_state:
        st.markdown(st.session_state['tabela_minerada'], unsafe_allow_html=True)
        st.info(f"✅ Filtro Ativo: {nicho} | R$ {preco_min} - R$ {preco_max}")

    # --- VALIDADOR RÁPIDO ---
    st.divider()
    st.subheader("🔗 Validador Externo em Tempo Real")
    prod_check = st.text_input("Cole o nome do produto para validar no Google real:", placeholder="Ex: Mini Selador a Vácuo")
    if prod_check:
        c1, c2 = st.columns(2)
        q_encoded = urllib.parse.quote(prod_check)
        link_trends = f"https://trends.google.com.br/trends/explore?date=now%207-d&geo=BR&q={q_encoded}"
        link_shopping = f"https://www.google.com.br/search?tbm=shop&q={q_encoded}+preço+shopee"
        c1.link_button(f"🔍 Ver '{prod_check}' no Google Trends", link_trends, use_container_width=True)
        c2.link_button(f"🛒 Ver Preços no Google Shopping", link_shopping, use_container_width=True)

# --- ABA 2: MÍDIA E FONTES ---
with aba_midia:
    st.header("🎥 Central de Mídia")
    prod_busca = st.text_input("Produto para Mídia:", key="media_input")
    if st.button("Localizar Fontes de Vídeo"):
        with st.spinner("Varrendo links de referência..."):
            res_midia = gerar_ia(f"Gere links de busca direta no TikTok, Instagram e Pinterest para: {prod_busca}.")
            st.session_state['fontes_midia'] = res_midia
            st.session_state['produto_ativo'] = prod_busca
            st.markdown(res_midia)

    if 'produto_ativo' in st.session_state:
        st.divider()
        if st.button("Gerar Roteiro Viral + Cenas"):
            res_roteiro = gerar_ia(f"Crie um roteiro de 30s e cenas de 3s para: {st.session_state['produto_ativo']}")
            st.session_state['roteiro_final'] = res_roteiro
            st.write(res_roteiro)

# --- ABA 3: AGENDADOR ---
with aba_social:
    st.header("📅 Agendador Estratégico")
    if 'roteiro_final' in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            rede = st.selectbox("Rede:", ["Instagram Reels", "TikTok", "YouTube Shorts"])
            hora = st.select_slider("Hora:", options=["09:00", "12:00", "18:00", "21:00"])
        if st.button("Gerar Legenda Magnética"):
            st.session_state['legenda_final'] = gerar_ia(f"Crie uma legenda viral para: {st.session_state['roteiro_final']}")
        
        if 'legenda_final' in st.session_state:
            st.text_area("Legenda:", st.session_state['legenda_final'])
            if st.button("🚀 Confirmar Agendamento"):
                st.balloons()
                st.success("Post adicionado à fila!")
    else:
        st.warning("⚠️ Gere um roteiro primeiro.")

# --- ABA 4: ROI ---
with aba_lucro:
    st.header("📊 Calculadora de Lucro")
    v = st.number_input("Preço Venda (R$):", value=89.90)
    c = st.number_input("Custo Total (R$):", value=30.0)
    taxa = st.selectbox("Canal:", [0.18, 0.22, 0.15], format_func=lambda x: "Shopee" if x==0.18 else ("ML" if x==0.22 else "Amazon"))
    
    lucro = v - c - (v * taxa)
    st.metric("Lucro Líquido", f"R$ {lucro:.2f}", delta=f"{(lucro/v)*100:.1f}% Margem")
