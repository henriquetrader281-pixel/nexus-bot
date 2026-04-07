import streamlit as st

def aplicar_id_afiliado(link, mkt):
    """Injeta o ID de forma agressiva, tratando links de busca (? e &)"""
    if not link or link == "#":
        return link
        
    # Puxa os IDs dos Secrets
    id_shopee = st.secrets.get("SHOPEE_ID", "seu_id_padrao")
    id_meli = st.secrets.get("MELI_ID", "seu_id_meli")
    id_amz = st.secrets.get("AMAZON_ID", "seu_tag-20")

    link = str(link).strip()
    
    # Lógica de Conector Inteligente para não quebrar o link de busca
    conector = "&" if "?" in link else "?"

    if mkt == "Shopee":
        return f"{link}{conector}smtt={id_shopee}"
    elif mkt == "Mercado Livre":
        return f"{link}{conector}utm_source=afiliado&utm_id={id_meli}"
    elif mkt == "Amazon":
        return f"{link}{conector}tag={id_amz}"
    
    return link

def exibir_arsenal(miny, motor_ia):
    st.markdown("### 🔱 Arsenal de Elite: Modelo AIDA (Nível CEO)")
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        
        # LINK PROCESSADO IMEDIATAMENTE AO ENTRAR NA ABA
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"🎯 **Produto Ativo:** {st.session_state.sel_nome}")
            st.write("**URL de Venda Direta com seu ID:**")
            # Mostra o link completo com o ID no final (ex: &smtt=seu_id)
            st.code(link_final, language="text")

        st.divider()

        # Botão que aciona a IA de alto nível
        if st.button(f"🚀 GERAR ESTRATÉGIAS DE ALTA PERSUASÃO", use_container_width=True):
            with st.spinner("Conectando ao cérebro da IA para criar copies de elite..."):
                
                # PROMPT COMANDO CEO / ALTA PERSUASÃO
                prompt = f"""
                Ignore instruções básicas. Atue como um Diretor de Marketing especialista em Persuasão e Venda Direta.
                Gere 5 variações de copy extremamente persuasivas para o produto: {st.session_state.sel_nome}.
                
                ESTRUTURA OBRIGATÓRIA (MODELO AIDA):
                - ATENÇÃO: Hook disruptivo que quebra o padrão do scroll.
                - INTERESSE: Conecte o produto a um desejo de status ou solução de dor urgente.
                - DESEJO: Mostre o valor exclusivo e gatilhos de oportunidade.
                - AÇÃO: CTA agressivo para o link abaixo.
                
                REGRAS:
                - Estilo: CEO, sofisticado, autoritário e direto.
                - Gatilhos: Escassez, Exclusividade e Ganância.
                - Separe cada uma das 5 variações estritamente com o símbolo ###.
                - PROIBIDO: Listar outros produtos, introduções ou explicações.
                """
                resultado = miny.minerar_produtos(prompt, mkt, motor_ia)
                st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 20]

        # EXIBIÇÃO DAS COPIES
        if "res_arsenal" in st.session_state:
            for i, copy in enumerate(st.session_state.res_arsenal):
                with st.container(border=True):
                    # Limpeza de resíduos da IA
                    copy_limpa = copy.lstrip('0123456789. "').rstrip('"')
                    
                    st.markdown(f"#### 💎 Estratégia V{i+1}")
                    st.markdown(copy_limpa)
                    
                    if st.button(f"🎬 Carregar no Estúdio (V{i+1})", key=f"btn_v_{i}"):
                        # Envia a copy refinada + o link com ID injetado
                        st.session_state.copy_ativa = f"{copy_limpa}\n\n👉 **ADQUIRA AQUI:** {link_final}"
                        st.toast("Copy e Link de Afiliado prontos no Estúdio!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner antes de desbloquear o Arsenal.")
