import streamlit as st

def aplicar_id_afiliado(link, mkt):
    """Reconstrói o link garantindo o domínio e o ID 18316451024"""
    if not link or link == "#":
        return link
    
    ID_FIXO_SHOPEE = "18316451024"
    link = str(link).strip()
    
    if mkt == "Shopee":
        # Caso 1: Link de busca (Search)
        # Se o link contém "search?keyword=", limpamos os parâmetros extras da Shopee
        if "search?keyword=" in link:
            try:
                # Extraímos apenas o que vem depois de keyword= e antes de qualquer &
                keyword = link.split("keyword=")[1].split("&")[0]
                return f"https://shopee.com.br/search?keyword={keyword}&smtt={ID_FIXO_SHOPEE}"
            except:
                # Caso o split falhe, forçamos o domínio básico com a busca original
                return f"https://shopee.com.br/search?keyword=produto&smtt={ID_FIXO_SHOPEE}"
        
        # Caso 2: Link de Produto Direto
        # Pegamos a parte principal do link antes de qualquer interrogação (?)
        base_link = link.split("?")[0]
        
        # SEGURANÇA: Se por algum erro o link vier sem o domínio (como nas suas fotos), nós o reinserimos
        if "shopee.com.br" not in base_link:
            # Tenta pegar a parte final do link (ex: nome-do-produto-i.123.456)
            path = base_link.split("/")[-1]
            return f"https://shopee.com.br/{path}?smtt={ID_FIXO_SHOPEE}"
            
        return f"{base_link}?smtt={ID_FIXO_SHOPEE}"
    
    return link

def exibir_arsenal(miny, motor_ia):
    # Identificador de motor Gemini Plus
    st.markdown(f"### 🔱 Nexus 3.1 Pro | Estratégia AIDA (Nível CEO)")
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        
        # PROCESSO DE BLINDAGEM DO LINK
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"📦 **Produto Selecionado:** {st.session_state.sel_nome}")
            st.markdown("#### 🔗 Link de Afiliado Blindado")
            # Exibe o link reconstruído corretamente
            st.code(link_final, language="text")
            st.caption(f"Rastreio ativo para o ID: {ID_FIXO_SHOPEE if 'ID_FIXO_SHOPEE' in locals() else '18316451024'}")

        st.divider()

        # Botão para o Gemini 3.1 Pro gerar a copy CEO
        if st.button(f"🔥 GERAR MUNIÇÃO DE ALTA PERSUASÃO", use_container_width=True):
            with st.spinner("Gemini 3.1 Pro processando gatilhos psicológicos..."):
                prompt = f"""
                Atue como um Copywriter Sênior e Estrategista de Venda Direta (Estilo CEO).
                Ignore listas genéricas. Foque 100% no produto: {st.session_state.sel_nome}.
                Use o MODELO AIDA (Atenção, Interesse, Desejo, Ação).
                
                REQUISITOS:
                - Hook agressivo (Pare o scroll).
                - Linguagem autoritária e sofisticada.
                - Foque em status, facilidade e escassez.
                - PROIBIDO introduções ou explicações.
                - Separe as 5 variações com ###.
                """
                resultado = miny.minerar_produtos(prompt, mkt, motor_ia)
                st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 20]

        if "res_arsenal" in st.session_state:
            for i, copy in enumerate(st.session_state.res_arsenal):
                with st.container(border=True):
                    v_limpa = copy.lstrip('0123456789. "').rstrip('"')
                    st.markdown(f"#### 💎 Estratégia de Elite V{i+1}")
                    st.markdown(v_limpa)
                    
                    if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_v_{i}"):
                        st.session_state.copy_ativa = f"{v_limpa}\n\n🛒 **COMPRE AGORA:** {link_final}"
                        st.toast("Munição enviada com sucesso!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")
