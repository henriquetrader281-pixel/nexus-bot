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

# --- 3. LÓGICA AUTO-REFRESH DIÁRIO ---
hoje = datetime.now().strftime('%d/%m/%Y')
if "ultima_mineracao_data" not in st.session_state:
    st.session_state["ultima_mineracao_data"] = None

# --- 4. INTERFACE OPERACIONAL ---
st.title("🧠 Nexus Brain: Hub de Inteligência 2026")
st.caption(f"📅 Operação Ativa | Operador: {st.session_state.get('email_input', 'Privado')} | Data: {hoje}")

aba_hub, aba_seo, aba_midia, aba_social, aba_lucro = st.tabs([
    "🔎 Hub de Mineração", 
    "📈 SEO & Fornecedores",
    "🎥 Mídia & Fontes",
    "📅 Agendador Social", 
    "📊 ROI"
])

# --- ABA 1: HUB DE MINERAÇÃO (AUTO-REFRESH) ---
with aba_hub:
    st.header("🎯 Descoberta de Produtos (Shopee/ML/Amazon)")
    with st.expander("⚙️ Filtros de Precisão", expanded=True):
        col_n, col_p = st.columns(2)
        nicho_global = col_n.selectbox("Nicho Alvo:", ["Todos", "Cozinha Criativa", "Saúde & Beleza", "Eletrônicos/Tech", "Pet Shop", "Ferramentas Smart"])
        lista_precos = [0, 20, 40, 60, 80, 100, 150, 200, 500]
        preco_min, preco_max = col_p.select_slider("Faixa de Preço (Venda):", options=lista_precos, value=(40, 100))

    st.divider()

    def disparar_mineracao():
        with st.status("Nexus minerando tendências globais...", expanded=True):
            prompt = f"Analista 2026: Liste 10 produtos em {nicho_global} (R$ {preco_min}-{preco_max}). Tabela Markdown: Produto, Plataforma, Status Google Search (🚀, 📈, ⚠️) e Link de Busca Direta."
            res = gerar_ia(prompt)
            st.session_state['tabela_minerada'] = res
            st.session_state['ultima_mineracao_data'] = hoje
            st.toast("Mineração diária concluída automaticamente!")

    if st.session_state["ultima_mineracao_data"] != hoje:
        disparar_mineracao()

    if st.button("🔄 Atualizar Varredura Manualmente", use_container_width=True):
        disparar_mineracao()
    
    if 'tabela_minerada' in st.session_state:
        st.markdown(st.session_state['tabela_minerada'])

# --- ABA 2: SEO & FORNECEDORES (PATCH 14 + SUGESTÃO) ---
with aba_seo:
    st.header("📈 Inteligência de Busca & Sourcing")
    st.write("Analise palavras-chave e encontre os melhores caminhos para estoque.")
    
    col_s1, col_s2 = st.columns([2, 1])
    nicho_seo = col_s1.selectbox("Selecione o Nicho para Análise:", ["Cozinha Criativa", "Saúde & Beleza", "Eletrônicos", "Pet Shop", "Utilidades Domésticas"], key="n_seo")
    
    if col_s2.button("Mapear Oportunidades", use_container_width=True):
        with st.spinner(f"Analisando dados de {nicho_seo}..."):
            prompt_seo = f"""
            Aja como Especialista SEO/Sourcing 2026. Para o nicho '{nicho_seo}':
            1. Liste as 5 Palavras-Passe de maior volume no Google Brasil hoje.
            2. Sugira 3 Títulos de Anúncios magnéticos.
            3. Indique os 3 melhores tipos de fornecedores (ex: 1688, Fornecedor Local SP, Dropshipping Nacional).
            Responda em Markdown.
            """
            st.session_state['analise_seo'] = gerar_ia(prompt_seo)

    if 'analise_seo' in st.session_state:
        st.markdown(st.session_state['analise_seo'])

# --- ABA 3: MÍDIA & FONTES ---
with aba_midia:
    st.header("🎥 Central de Mídia")
    prod_busca = st.text_input("Produto para Mídia:", placeholder="Digite o produto selecionado...", key="media_in")
    
    if st.button("Localizar Fontes de Criativos"):
        with st.spinner("Buscando referências visuais..."):
            res_midia = gerar_ia(f"Links diretos de busca no TikTok, Instagram e Pinterest para o produto: {prod_busca}.")
            st.session_state['fontes_midia'] = res_midia
            st.session_state['produto_ativo'] = prod_busca
            st.markdown(res_midia)

    st.divider()
    if 'produto_ativo' in st.session_state:
        st.subheader(f"📝 Roteiro Estratégico: {st.session_state['produto_ativo']}")
        if st.button("Gerar Roteiro Viral + Cenas"):
            res_roteiro = gerar_ia(f"Crie um roteiro de 30s e descrição de cenas de 3s para: {st.session_state['produto_ativo']}")
            st.session_state['roteiro_final'] = res_roteiro
            st.write(res_roteiro)

# --- ABA 4: AGENDADOR SOCIAL ---
with aba_social:
    st.header("📅 Agendador de Postagens")
    if 'roteiro_final' in st.session_state:
        col1, col2 = st.columns(2)
        rede = col1.selectbox("Plataforma:", ["Instagram Reels", "TikTok", "YouTube Shorts"])
        hora = col2.select_slider("Horário Sugerido:", options=["09:00", "12:00", "18:00", "21:00"])
        
        if st.button("Gerar Legenda com SEO"):
            st.session_state['legenda_final'] = gerar_ia(f"Crie uma legenda viral com hashtags baseada neste roteiro: {st.session_state['roteiro_final']}")
        
        if 'legenda_final' in st.session_state:
            st.text_area("Legenda Final:", st.session_state['legenda_final'], height=150)
            if st.button("🚀 Confirmar Agendamento na Fila", use_container_width=True):
                st.balloons()
                st.success(f"Post de {st.session_state['produto_ativo']} agendado para {rede} às {hora}!")
    else:
        st.warning("⚠️ Gere um roteiro na aba de Mídia primeiro.")

# --- ABA 5: ROI (CALCULADORA) ---
with aba_lucro:
    st.header("📊 Calculadora de Viabilidade Financeira")
    c1, c2, c3 = st.columns(3)
    v = c1.number_input("Preço de Venda (R$):", value=89.90)
    c = c2.number_input("Custo do Produto (R$):", value=30.0)
    taxa = c3.selectbox("Taxa do Canal:", [0.18, 0.22, 0.15], format_func=lambda x: f"Taxa {int(x*100)}%")
    
    lucro = v - c - (v * taxa)
    st.metric("Lucro Líquido por Unidade", f"R$ {lucro:.2f}", delta=f"{(lucro/v)*100:.1f}% Margem")
    
    if lucro > 25:
        st.success("🔥 Produto com ótima margem para escala!")
    elif lucro < 15:
        st.warning("⚠️ Margem apertada. Cuidado com o custo de anúncio.")
