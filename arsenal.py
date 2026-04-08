import streamlit as st

def aplicar_id_afiliado(link, mkt):
    if not link or link == "#":
        return link
    ID_FIXO_SHOPEE = "18316451024"
    link = str(link).strip()
    if mkt == "Shopee":
        if "search?keyword=" in link:
            try:
                keyword = link.split("keyword=")[1].split("&")[0]
                return f"https://shopee.com.br/search?keyword={keyword}&smtt={ID_FIXO_SHOPEE}"
            except:
                return f"https://shopee.com.br/search?keyword=produto&smtt={ID_FIXO_SHOPEE}"
        base_link = link.split("?")[0]
        if "shopee.com.br" not in base_link:
            path = base_link.split("/")[-1]
            base_link = f"https://shopee.com.br/{path}"
        return f"{base_link}?smtt={ID_FIXO_SHOPEE}"
    return link

def exibir_arsenal(miny, motor_ia):
    st.markdown(f"### 🔱 Nexus 3.1 Pro | Estratégia AIDA (Nível CEO)")
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        
        # Limpamos o nome do produto de qualquer lixo técnico antes de enviar ao Gemini
        produto_limpo = st.session_state.sel_nome.split('|')[0].replace("NOME:", "").strip()
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"📦 **Produto Selecionado:** {produto_limpo}")
            st.markdown("#### 🔗 Link de Afiliado Blindado")
            st.code(link_final, language="text")

        st.divider()

        # Atualizado: use_container_width -> width='stretch'
        if st.button(f"🔥 GERAR MUNIÇÃO DE ALTA PERSUASÃO", width='stretch'):
            with st.spinner("Gemini Pro processando gatilhos psicológicos..."):
                
                # --- PROMPT BLINDADO E REESTRUTURADO ---
                prompt = f"""
                [COMANDO PRIORITÁRIO]: ESQUEÇA TODA E QUALQUER LISTA DE PRODUTOS ANTERIOR. 
                NÃO mencione "30 produtos" ou categorias genéricas.
                
                PRODUTO ÚNICO PARA TRABALHAR: {produto_limpo}
                
                TAREFA: Gere 5 variações de Copywriting usando o MODELO AIDA.
                
                ESTILO: Direto, agressivo, focado em vendas (Estilo CEO).
                - Use gatilhos de escassez e exclusividade.
                - Sem introduções gentis. Comece direto no Hook.
                - Separe cada uma das 5 variações APENAS com o símbolo ###.
                """
                
                try:
                    # 🛑 TRAVA ABSOLUTA: Forçando o Gemini para evitar o erro 429 da Groq
                    resultado = miny.minerar_produtos(prompt, mkt, "gemini-1.5-pro")
                    
                    # Limpeza de segurança caso a IA ainda tente mandar a lista
                    if "1. NOME:" in resultado:
                        resultado = resultado.split("###")[-5:] # Pega só as últimas 5 partes (as copies)
                        st.session_state.res_arsenal = [c.strip() for c in resultado if len(c) > 20]
                    else:
                        st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 20]
                except Exception as e:
                    st.error(f"Erro na IA: {e}")

        # EXIBIÇÃO
        if "res_arsenal" in st.session_state:
            for i, copy in enumerate(st.session_state.res_arsenal):
                with st.container(border=True):
                    # Limpeza visual para remover restos de numeração ou tags que a IA solta
                    v_limpa = copy.replace("[ATENÇÃO]", "🚨").replace("[INTERESSE]", "💡").replace("[DESEJO]", "✨").replace("[AÇÃO]", "🛒")
                    st.markdown(f"#### 💎 Estratégia de Elite V{i+1}")
                    st.markdown(v_limpa)
                    
                    # Atualizado: key dinâmico e width='stretch'
                    if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_v_{i}", width='stretch'):
                        st.session_state.copy_ativa = f"{v_limpa}\n\n🛒 **COMPRE AGORA:** {link_final}"
                        st.toast("Munição enviada com sucesso!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")
