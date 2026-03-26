import streamlit as st
from groq import Groq
from datetime import datetime

# --- 1. CONFIGURAÇÕES E SECRETS ---
api_key = st.secrets.get("GROQ_API_KEY")
st.set_page_config(page_title="Nexus Bot: Master", page_icon="🧠", layout="wide")

# --- 2. CONEXÃO COM A IA (GROQ TURBO) ---
client = None
if api_key:
    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        st.error(f"Erro na conexão Groq: {e}")
else:
    st.error("API Key da Groq não encontrada nos Secrets.")

def gerar_ia(prompt):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erro na IA: {e}"

# --- 3. NAVEGAÇÃO POR ABAS ---
st.title("🧠 Nexus Brain: Central de Comando")
aba_min, aba_social, aba_lucro = st.tabs(["🔎 Mineração & Roteiro", "📅 Agendador Social (P07/08)", "📊 Métricas & Lucro (P09)"])

# --- ABA 1: MINERAÇÃO E ROTEIRO ---
with aba_min:
    st.header("🔎 Inteligência de Mercado")
    if st.button("Minerar Top 10 Shopee 2026", key="btn_min_aba1"):
        with st.status("Varrendo tendências..."):
            res = gerar_ia("Liste 10 produtos virais Shopee 2026 com nota de potencial de 0-10.")
            st.session_state['lista_minerada'] = res
    
    if 'lista_minerada' in st.session_state:
        st.info(st.session_state['lista_minerada'])
    
    st.divider()
    st.header("📝 Criador de Conteúdo")
    prod = st.text_input("Produto alvo:", placeholder="Ex: Mini Selador Térmico")
    if st.button("Gerar Roteiro Viral + Cenas"):
        with st.spinner("O Nexus está redigindo..."):
            prompt_full = f"Crie um roteiro de 30s para {prod} (Hook, Problema, Solução, CTA) e divida em cenas de 3s para o editor."
            roteiro = gerar_ia(prompt_full)
            st.session_state['roteiro_final'] = roteiro
            st.success("Conteúdo pronto!")
            st.write(roteiro)

# --- ABA 2: AGENDADOR E CONEXÃO (PATCH 07 & 08) ---
with aba_social:
    st.header("📅 Agendamento Inteligente")
    
    if 'roteiro_final' in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            rede = st.selectbox("Destino do Post:", ["Instagram Reels", "TikTok", "YouTube Shorts"])
            horario = st.select_slider("Melhor Horário Sugerido:", options=["09:00", "12:00", "18:00", "21:00"])
        
        with col2:
            legenda_estilo = st.radio("Estilo da Legenda:", ["Urgência", "Curiosidade", "Engraçada"])
            if st.button("Gerar Legenda p/ Rede Social"):
                legenda = gerar_ia(f"Crie uma legenda {legenda_estilo} com hashtags para: {st.session_state['roteiro_final']}")
                st.session_state['legenda_final'] = legenda

        if 'legenda_final' in st.session_state:
            st.text_area("Legenda Gerada:", st.session_state['legenda_final'], height=100)

        if st.button("🚀 Confirmar Agendamento no Nexus", use_container_width=True):
            st.balloons()
            st.success(f"Post agendado com sucesso para {rede} às {horario}!")
            # Simulando a Fila de Postagem
            if 'fila' not in st.session_state: st.session_state['fila'] = []
            st.session_state['fila'].append({"Rede": rede, "Hora": horario, "Status": "Aguardando"})
    else:
        st.warning("⚠️ Gere um roteiro na aba anterior para habilitar o agendador.")

    if 'fila' in st.session_state:
        st.divider()
        st.subheader("📋 Fila de Postagens Ativa")
        st.table(st.session_state['fila'])

# --- ABA 3: MÉTRICAS E LUCRO (PATCH 09) ---
with aba_lucro:
    st.header("📊 Painel de Performance")
    m1, m2, m3 = st.columns(3)
    m1.metric("Alcance Estimado", "15.700", "+12%")
    m2.metric("Cliques no Link", "432", "5.2%")
    m3.metric("Conversão", "2.1%", "+0.4%")

    st.divider()
    st.subheader("💰 Calculadora de ROI")
    col_v, col_c = st.columns(2)
    venda = col_v.number_input("Preço de Venda (R$):", value=79.90)
    custo = col_c.number_input("Custo + Imposto (R$):", value=35.00)
    
    if st.button("Calcular Lucratividade"):
        # Cálculo: Venda - Custo - Taxa Shopee (estimada 18%)
        lucro_real = venda - custo - (venda * 0.18)
        st.metric("Lucro Líquido por Unidade", f"R$ {lucro_real:.2f}", delta=f"Margem: {(lucro_real/venda)*100:.1f}%")
        
        if lucro_real > 20:
            st.success("🔥 Produto Altamente Lucrativo! Escalar postagens.")
        else:
            st.warning("⚠️ Margem apertada. Considere aumentar o ticket.")
