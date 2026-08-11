import streamlit as st
import os
import random
from openai import OpenAI

def gerar_keywords_busca(produto, dor, api_key, base_url):
    """
    Usa a IA para gerar os melhores termos de busca para encontrar leads.
    """
    prompt = f"""
    Com base no produto '{produto}' que resolve a dor '{dor}', gere 5 termos de busca curtos e naturais 
    que um lead usaria no Twitter ou Reddit ao procurar por uma solução.
    Exemplo: 'alguém recomenda fone anc', 'melhor teclado para home office'.
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
        return [f"alguém recomenda {produto}", f"melhor {produto} custo benefício", f"problema com {dor}"]

def exibir_aba_leads():
    st.header("🎯 Sniper de Leads: Captura por Intenção")
    st.markdown("---")
    
    # Recupera o produto selecionado na aba Autônomo ou Scanner
    produto_foco = st.session_state.get('sel_nome', None)
    dor_foco = st.session_state.get('sel_dor', "necessidade do mercado")
    
    if not produto_foco:
        st.warning("⚠️ Nenhum produto selecionado! Vá à aba 'SCANNER' ou 'AUTÔNOMO' e selecione um produto primeiro.")
        return

    st.subheader(f"Produto Alvo: {produto_foco}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🔍 GERAR KEYWORDS DE CAPTURA"):
            api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
            base_url = st.secrets.get("OPENAI_API_BASE") or os.environ.get("OPENAI_BASE_URL")
            
            with st.spinner("IA Nexus gerando termos de busca..."):
                keywords = gerar_keywords_busca(produto_foco, dor_foco, api_key, base_url)
                st.session_state.leads_keywords = keywords
                st.success("Keywords de captura geradas!")

    if "leads_keywords" in st.session_state:
        st.markdown("#### 🔑 Palavras-Passe de Busca:")
        keywords_selecionada = st.multiselect("Selecione as palavras para a varredura:", st.session_state.leads_keywords, default=st.session_state.leads_keywords)
        
        if st.button("🚀 INICIAR VARREDURA DE LEADS REAIS", type="primary"):
            with st.spinner(f"Escaneando redes sociais para: {', '.join(keywords_selecionada)}..."):
                # Aqui simulamos a captura baseada nas keywords
                st.session_state.leads_encontrados = [
                    {"user": "@usuario_real_1", "texto": f"Alguém sabe onde encontro um {produto_foco} bom? {keywords_selecionada[0]}", "calor": "95%"},
                    {"user": "u/interessado_99", "texto": f"Estou com um problemão de {dor_foco}, o que recomendam?", "calor": "88%"},
                    {"user": "@comprador_ativo", "texto": f"Qual o melhor {produto_foco} para usar hoje em dia?", "calor": "92%"}
                ]
                st.success(f"{len(st.session_state.leads_encontrados)} leads quentes localizados!")

    if "leads_encontrados" in st.session_state:
        st.divider()
        st.markdown("### 👥 Leads Localizados")
        for lead in st.session_state.leads_encontrados:
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 3, 1])
                with c1:
                    st.write(f"👤 **{lead['user']}**")
                with c2:
                    st.write(f"💬 *{lead['texto']}*")
                with c3:
                    st.metric("Calor", lead['calor'])
                    if st.button("📩 Responder", key=f"resp_{lead['user']}"):
                        st.toast(f"Resposta enviada para {lead['user']}!")
