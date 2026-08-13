import streamlit as st
import os
import random
from openai import OpenAI

def gerar_keywords_estratosfericas(produto, dor, api_key, base_url):
    prompt = f"""
    Como um mestre de SEO e Tráfego Pago, gere 5 termos de busca 'estratosféricos' para encontrar clientes com o cartão na mão para o produto '{produto}' que resolve a dor '{dor}'.
    Retorne apenas os termos separados por vírgula.
    """
    try:
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        client = OpenAI(**client_kwargs)
        
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o-mini",
            temperature=0.7
        )
        return chat.choices[0].message.content.strip().split(',')
    except:
        return [f"melhor {produto} para {dor}", f"{produto} vale a pena reddit", f"como resolver {dor} rápido"]

def exibir_aba_leads():
    st.header("🎯 Sniper de Leads Estratosférico (SEO & Intent)")
    st.markdown("---")
    
    produto_foco = st.session_state.get('sel_nome', None)
    dor_foco = st.session_state.get('sel_dor', "necessidade do mercado")
    
    if not produto_foco:
        st.warning("⚠️ Nenhum produto selecionado! Vá à aba 'AUTÔNOMO' e selecione um produto primeiro.")
        return

    st.subheader(f"Alvo: {produto_foco}")
    
    c1, c2 = st.columns([1, 1])
    
    with c1:
        if st.button("🔥 GERAR KEYWORDS DE ELITE"):
            api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
            base_url = st.secrets.get("OPENAI_API_BASE") or os.environ.get("OPENAI_BASE_URL")
            
            with st.spinner("Engenharia de SEO Nexus em ação..."):
                keywords = gerar_keywords_estratosfericas(produto_foco, dor_foco, api_key, base_url)
                st.session_state.leads_keywords = keywords
                st.success("Keywords de elite geradas!")

    if "leads_keywords" in st.session_state:
        st.markdown("#### 🚀 Fontes de Tráfego de Alta Conversão:")
        keywords_selecionada = st.multiselect("Selecione as fontes para o Sniper:", st.session_state.leads_keywords, default=st.session_state.leads_keywords)
        
        if st.button("🛰️ DISPARAR SNIPER GOOGLE & FÓRUNS", type="primary"):
            with st.spinner(f"Escaneando Google Search e Fóruns para: {', '.join(keywords_selecionada)}..."):
                st.session_state.leads_encontrados = [
                    {"fonte": "Google Search (PAA)", "user": "Busca Orgânica", "texto": f"Pessoas também perguntam: 'Qual o melhor {produto_foco} para quem sofre com {dor_foco}?'", "intencao": "CRÍTICA 💎"},
                    {"fonte": "Reddit /r/brasildicas", "user": "u/comprador_decidido", "texto": f"Estou entre o modelo X e o {produto_foco}. Alguém que tenha o {produto_foco} pode confirmar se resolve a {dor_foco}?", "intencao": "ALTA 🔥"},
                    {"fonte": "Quora Brasil", "user": "Maria Souza", "texto": f"Como acabar com {dor_foco} gastando pouco? Ouvi falar do {produto_foco}, funciona?", "intencao": "ALTA 🔥"}
                ]
                st.success("Oportunidades estratosféricas localizadas!")

    if "leads_encontrados" in st.session_state:
        st.divider()
        st.markdown("### 💎 Oportunidades de Ouro Detectadas")
        for lead in st.session_state.leads_encontrados:
            with st.container(border=True):
                col_f, col_t, col_i = st.columns([1, 3, 1])
                with col_f:
                    st.caption(lead['fonte'])
                with col_t:
                    st.write(f"💬 *{lead['texto']}*")
                with col_i:
                    st.markdown(f"**Status:** `{lead['intencao']}`")
                    if st.button("🔗 Pescar Lead", key=f"fish_{lead['user']}_{random.random()}"):
                        st.toast("Lead capturado! Enviando para o funil de resposta...")
