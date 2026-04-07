import streamlit as st

def aplicar_id_afiliado(link, mkt):
    """
    Versão Recuperada e Blindada: 
    Limpa o lixo (extraParams, sp_atk) e crava o ID 18316451024
    """
    if not link or link == "#":
        return link
    
    ID_FIXO_SHOPEE = "18316451024"
    link = str(link).strip()
    
    if mkt == "Shopee":
        # 1. Se o link for de busca (search)
        if "search?keyword=" in link:
            # Extraímos a base até a interrogação e a keyword
            base_search = link.split("?")[0]
            try:
                keyword = link.split("keyword=")[1].split("&")[0]
                return f"{base_search}?keyword={keyword}&smtt={ID_FIXO_SHOPEE}"
            except:
                return f"https://shopee.com.br/search?keyword=produto&smtt={ID_FIXO_SHOPEE}"
        
        # 2. Se o link for de produto direto (como o do Espeto)
        # Cortamos tudo o que vem depois do '?' para eliminar o lixo eletrônico
        base_produto = link.split("?")[0]
        
        # SEGURANÇA: Se a base não tiver o domínio (erro comum de processamento), nós reinserimos
        if "shopee.com.br" not in base_produto:
            if base_produto.startswith("/"):
                base_produto = f"https://shopee.com.br{base_produto}"
            else:
                # Tenta pegar a parte final i.123.456
                path = base_produto.split("/")[-1]
                base_produto = f"https://shopee.com.br/{path}"
        
        # Retorna o link do produto limpo + o seu ID de afiliado
        return f"{base_produto}?smtt={ID_FIXO_SHOPEE}"
    
    return link

def exibir_arsenal(miny, motor_ia):
    """
    Interface do Arsenal que o app.py chama.
    Garante cópias agressivas (Nível CEO) e links com ID.
    """
    st.markdown(f"### 🔱 Nexus 3.1 Pro | Estratégia AIDA (Nível CEO)")
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        
        # PROCESSO DE BLINDAGEM DO LINK
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"📦 **Produto Selecionado:** {st.session_state.sel_nome}")
            st.markdown("#### 🔗 Link de Afiliado Blindado")
            # Exibe o link pronto para ser usado
            st.code(link_final, language="text")
            st.caption(f"Rastreio ativo para o ID: 18316451024")

        st.divider()

        # Botão para o Gemini 1.5 Pro gerar a copy
        if st.button(f"🔥 GERAR MUNIÇÃO DE ALTA PERSUASÃO", use_container_width=True):
            with st.spinner("Gemini 3.1 Pro processando gatilhos psicológicos..."):
                
                prompt = f"""
                Atue como um Copywriter Sênior e Estrategista de Venda Direta (Estilo CEO).
                Ignore listas genéricas e descrições chatas. 
                Produto: {st.session_state.sel_nome}.
                Use o MODELO AIDA (Atenção, Interesse, Desejo, Ação).
                
                REQUISITOS:
                - Hook agressivo para parar o scroll.
                - Foque no benefício imediato e status.
                - Use emojis de forma estratégica (não infantil).
                - PROIBIDO dizer "Aqui está sua copy". Vá direto ao texto.
                - Separe as 5 variações com ###.
                """
                
                resultado = miny.minerar_produtos(prompt, mkt, motor_ia)
                # Salva as variações na sessão
                st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 20]

        # EXIBIÇÃO DAS COPIES
        if "res_arsenal" in st.session_state:
            for i, copy in enumerate(st.session_state.res_arsenal):
                with st.container(border=True):
                    # Limpa possíveis números de lista (1., 2., etc)
                    v_limpa = copy.lstrip('0123456789. "').rstrip('"')
                    st.markdown(f"#### 💎 Estratégia de Elite V{i+1}")
                    st.markdown(v_limpa)
                    
                    if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_v_{i}"):
                        # Une a copy escolhida com o seu link blindado
                        st.session_state.copy_ativa = f"{v_limpa}\n\n🛒 **COMPRE AGORA:** {link_final}"
                        st.toast("Munição enviada ao Estúdio!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")
