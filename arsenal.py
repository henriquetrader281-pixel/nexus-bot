import streamlit as st

def aplicar_id_afiliado(link, mkt):
    """
    Versão Master: Limpa 100% dos parâmetros inúteis e crava o ID 18316451024.
    Resolve os erros de 'link cortado' e 'https duplicado'.
    """
    if not link or link == "#":
        return link
    
    ID_FIXO_SHOPEE = "18316451024"
    link = str(link).strip()
    
    if mkt == "Shopee":
        # 1. Caso seja link de busca (search?keyword=...)
        if "search?keyword=" in link:
            try:
                # Extrai apenas a palavra-chave, ignorando o lixo posterior
                keyword = link.split("keyword=")[1].split("&")[0]
                return f"https://shopee.com.br/search?keyword={keyword}&smtt={ID_FIXO_SHOPEE}"
            except:
                return f"https://shopee.com.br/search?keyword=produto&smtt={ID_FIXO_SHOPEE}"
        
        # 2. Caso seja link de produto direto
        # Cortamos tudo após o '?' para eliminar o 'extraParams' e rastreios antigos
        base_link = link.split("?")[0]
        
        # Segurança: Garante que o domínio Shopee esteja presente e correto
        if "shopee.com.br" not in base_link:
            # Tenta recuperar o caminho final do produto (ex: nome-p.123.456)
            path = base_link.split("/")[-1]
            base_link = f"https://shopee.com.br/{path}"
        
        # 3. Retorna o link purificado com o seu ID
        return f"{base_link}?smtt={ID_FIXO_SHOPEE}"
    
    return link

def exibir_arsenal(miny, motor_ia):
    """Interface do Arsenal Nexus 3.1 Pro"""
    st.markdown(f"### 🔱 Nexus 3.1 Pro | Estratégia AIDA (Nível CEO)")
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        
        # GERA O LINK BLINDADO
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"📦 **Produto Selecionado:** {st.session_state.sel_nome}")
            st.markdown("#### 🔗 Link de Afiliado Blindado")
            # Exibe o link final limpo e funcional
            st.code(link_final, language="text")
            st.caption("Rastreio ativo para o ID: 18316451024")

        st.divider()

        # Botão para o Gemini 3.1 Pro gerar a copy estratégica
        if st.button(f"🔥 GERAR MUNIÇÃO DE ALTA PERSUASÃO", use_container_width=True):
            with st.spinner("Gemini 3.1 Pro processando gatilhos psicológicos..."):
                
                prompt = f"""
                Atue como um Copywriter Sênior e Estrategista de Venda Direta (Estilo CEO).
                Ignore listas genéricas. Foque 100% no produto: {st.session_state.sel_nome}.
                Use o MODELO AIDA (Atenção, Interesse, Desejo, Ação).
                
                REQUISITOS:
                - Hook agressivo (Pare o scroll).
                - Linguagem autoritária e sofisticada.
                - PROIBIDO introduções ou explicações.
                - Separe as 5 variações com ###.
                """
                
                resultado = miny.minerar_produtos(prompt, mkt, motor_ia)
                st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 20]

        # EXIBIÇÃO DAS COPIES PARA O ESTÚDIO
        if "res_arsenal" in st.session_state:
            for i, copy in enumerate(st.session_state.res_arsenal):
                with st.container(border=True):
                    v_limpa = copy.lstrip('0123456789. "').rstrip('"')
                    st.markdown(f"#### 💎 Estratégia de Elite V{i+1}")
                    st.markdown(v_limpa)
                    
                    if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_v_{i}"):
                        # Envia o texto + o link limpo para a copy ativa
                        st.session_state.copy_ativa = f"{v_limpa}\n\n🛒 **COMPRE AGORA:** {link_final}"
                        st.toast("Munição enviada com sucesso!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")
