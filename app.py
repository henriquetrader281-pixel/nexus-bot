import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURAÇÕES E SECRETS ---
api_key = st.secrets.get("GEMINI_API_KEY")
st.set_page_config(page_title="Nexus Bot: Master", page_icon="🧠", layout="wide")

# --- 2. CONEXÃO COM A IA (CORREÇÃO DEFINITIVA ERRO 404) ---
# Se o erro 404 persistir, o Google mudou o nome da versão. 
# Usaremos 'gemini-1.5-flash' que é o padrão universal.
if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Erro na conexão Gemini: {e}")
        model = None
else:
    st.error("API Key não encontrada nos Secrets.")
    model = None

# --- 3. INTERFACE PRINCIPAL ---
st.title("🧠 Nexus Brain: Operação Ativa")
st.sidebar.header("Módulos de Automação")

# --- 4. [PATCH 10: MINERADOR DE PRODUTOS] ---
st.header("🔎 Mineração de Tendências")

if st.button("Buscar Top 10 Mais Quentes (Shopee)", key="btn_min_vfinal"):
    if model:
        with st.status("Minerando tendências...", expanded=True) as status:
            try:
                prompt_min = "Liste 10 produtos virais Shopee 2026 com nota de 0-10."
                response = model.generate_content(prompt_min)
                if response and hasattr(response, 'text'):
                    st.session_state['lista_minerada'] = response.text
                    status.update(label="Concluído!", state="complete", expanded=False)
                else:
                    st.error("Resposta vazia da IA.")
            except Exception as e:
                st.error(f"Erro na Mineração: {e}")
    else:
        st.error("IA Offline.")

if 'lista_minerada' in st.session_state:
    st.info(st.session_state['lista_minerada'])

# --- 5. [PATCH 11: REMODELAGEM DE ROTEIRO] ---
st.divider()
st.header("📝 Remodelagem (Patch 11)")
prod_para_roteiro = st.text_input("Produto para o Roteiro:", placeholder="Digite o produto...")

if st.button("Gerar Roteiro Viral", key="btn_p11_vfinal"):
    if model and prod_para_roteiro:
        with st.spinner("Criando roteiro..."):
            try:
                prompt_p11 = f"Crie um roteiro de 30s para {prod_para_roteiro}. Hook + Problema + Solução + CTA."
                res_p11 = model.generate_content(prompt_p11)
                if res_p11 and hasattr(res_p11, 'text'):
                    st.session_state['roteiro_final'] = res_p11.text
                    st.success("Roteiro pronto!")
                    st.write(st.session_state['roteiro_final'])
            except Exception as e:
                st.error(f"Erro no Patch 11: {e}")

# --- 6. [PATCH 12: ESTRUTURA DE CENAS] ---
if 'roteiro_final' in st.session_state:
    st.divider()
    st.subheader("🎬 Estrutura de Cenas (Patch 12)")
    if st.button("Quebrar Roteiro para Edição", key="btn_p12_vfinal"):
        try:
            prompt_12 = f"Divida em cenas de 3s para edição: {st.session_state['roteiro_final']}"
            res_12 = model.generate_content(prompt_12)
            st.code(res_12.text, language='text')
        except Exception as e:
            st.error(f"Erro no Patch 12: {e}")

# --- 7. [PATCH 04, 05 e 06: EXTRAS] ---
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.header("📥 Downloader (P04)")
    url_ref = st.text_input("Link para download (TikTok/IG):", key="dl_link_final")
    if st.button("Preparar Arquivo", key="btn_dl_p04"):
        st.toast("Link enviado para processamento!")

with col2:
    st.header("✍️ Legenda Post (P05)")
    if st.button("Gerar Legenda", key="btn_leg_p05"):
        if 'roteiro_final' in st.session_state and model:
            res_05 = model.generate_content(f"Crie uma legenda para: {st.session_state['roteiro_final']}")
            st.write(res_05.text)
        else:
            st.warning("Gere um roteiro primeiro!")

st.divider()
st.header("📊 Calculadora de Lucro (P06)")
venda = st.number_input("Preço de Venda (R$):", value=50.0, key="val_venda")
custo = st.number_input("Custo Total (R$):", value=20.0, key="val_custo")
if st.button("Calcular Lucro", key="btn_p06_calc"):
    lucro = venda - custo - (venda * 0.15)
    st.metric("Lucro Líquido", f"R$ {lucro:.2f}", delta=f"{(lucro/venda)*100:.1f}%")
