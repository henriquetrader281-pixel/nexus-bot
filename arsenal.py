import streamlit as st

def aplicar_id_afiliado(link, mkt):
    """Gera o link final injetando o ID de forma agressiva e correta"""
    if not link or link == "#":
        return link
        
    # Puxa os IDs dos Secrets
    id_shopee = st.secrets.get("SHOPEE_ID", "seu_id_padrao")
    id_meli = st.secrets.get("MELI_ID", "seu_id_meli")
    id_amz = st.secrets.get("AMAZON_ID", "seu_tag-20")

    link = str(link).strip()
    
    # RESOLVE O PROBLEMA DO SEARCH: Se já tem '?', usa '&'. Se não, usa '?'
    conector = "&" if "?" in link else "?"

    if mkt == "Shopee":
        return f"{link}{conector}smtt={id_shopee}"
    elif mkt == "Mercado Livre":
        return f"{link}{conector}utm_source=afiliado&utm_id={id_meli}"
    elif mkt == "Amazon":
        return f"{link}{conector}tag={id_amz}"
    
    return link

def exibir_arsenal(miny, motor_ia):
    st.markdown("### 🔱 Arsenal de Elite: Estratégia AIDA (Nível CEO)")
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        
        # O LINK É PROCESSADO AQUI - PÁGINA INTEIRA
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.info(f"📦 **Produto Selecionado:** {st.session_state.sel_nome}")
            st.write("**Link de Afiliado (Validado):**")
            # Isso garante que você veja o ID no final do link de search
            st.code(link_final, language="text")

        st.divider()

        if st.button(f"🚀 GERAR CÓPIAS DE ALTA PERSUASÃO", use_container_width=True):
            with st.spinner("IA Sênior formatando modelo AIDA..."):
                # PROMPT CEO / ALTA PERSUASÃO - FOCADO EM VENDA DIRETA
                prompt = f"""
                Ignore todas as instruções genéricas. Você é um Diretor de Marketing especialista em Direct Response.
                Crie 5 variações de copy extremamente persuasivas para o produto: {st.session_state.sel_nome}.
                
                ESTRUTURA OBRIGATÓRIA AIDA:
                - ATENÇÃO: Um gancho (hook) agressivo para parar o scroll no TikTok/Reels.
                - INTERESSE: Conecte o produto a um desejo de status ou solução de dor.
                - DESEJO: Mostre o valor exclusivo e o gatilho de 'oportunidade única'.
                - AÇÃO: CTA curto e direto para o link abaixo.
                
                REGRAS:
                - Use linguagem de alto nível (Estilo CEO/Sofisticado).
                - Use emojis de luxo e poder.
                - Separe cada uma das 5 variações estritamente com o símbolo ###.
                - PROIBIDO introduções ou listas de outros produtos.
                """
                resultado = miny.minerar_produtos(prompt, mkt, motor_ia)
                # Limpa a resposta para pegar apenas o que importa
                st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 20]

        # EXIBIÇÃO ORGANIZADA
        if "res_arsenal" in st.session_state:
            for i, copy in enumerate(st.session_state.res_arsenal):
                with st.container(border=True):
                    # Limpa resíduos de texto da IA
                    copy_limpa = copy.lstrip('0123456789. "').rstrip('"')
                    
                    st.markdown(f"#### 💎 Versão Black {i+1}")
                    st.markdown(copy_limpa)
                    
                    if st.button(f"🎬 Carregar no Estúdio (V{i+1})", key=f"btn_v_{i}"):
                        # Envia a copy + o link já com o seu ID
                        st.session_state.copy_ativa = f"{copy_limpa}\n\n👉 **ADQUIRA AQUI:** {link_final}"
                        st.toast("Munição enviada ao Estúdio!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner para gerar as cópias de elite.")
