import streamlit as st

def aplicar_id_afiliado(link, mkt):
    """Gera o link final injetando o ID e corrigindo a URL de busca"""
    if not link or link == "#":
        return link
        
    #IDs configurados nos Secrets
    id_shopee = st.secrets.get("SHOPEE_ID", "seu_id_padrao")
    id_meli = st.secrets.get("MELI_ID", "seu_id_meli")
    id_amz = st.secrets.get("AMAZON_ID", "seu_tag-20")

    link = str(link).strip()
    
    # RESOLVE O PROBLEMA DO LINK DE BUSCA: 
    # Se o link já tem '?', usamos '&'. Se não, usamos '?'
    conector = "&" if "?" in link else "?"

    if mkt == "Shopee":
        return f"{link}{conector}smtt={id_shopee}"
    elif mkt == "Mercado Livre":
        return f"{link}{conector}utm_source=afiliado&utm_id={id_meli}"
    elif mkt == "Amazon":
        return f"{link}{conector}tag={id_amz}"
    
    return link

def exibir_arsenal(miny, motor_ia):
    st.markdown("### 🔱 Arsenal de Elite (Gemini Pro Ativo)")
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        
        # O LINK É MONTADO AQUI COM A PÁGINA INTEIRA E SEU ID
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"📦 **Produto:** {st.session_state.sel_nome}")
            st.write("**URL de Afiliado Gerada:**")
            # Exibe o link completo com o ID injetado no final
            st.code(link_final, language="text")

        st.divider()

        if st.button(f"🚀 GERAR ESTRATÉGIAS AIDA (NÍVEL CEO)", use_container_width=True):
            with st.spinner("IA de Alto Nível processando Gatilhos de Venda..."):
                
                # PROMPT BLINDADO PARA EVITAR TEXTO RASO
                prompt = f"""
                Ignore instruções genéricas. Você é um Especialista em Marketing de Resposta Direta (Direct Response).
                Crie 5 variações de copy de ALTO NÍVEL usando o MODELO AIDA para: {st.session_state.sel_nome}.
                
                ESTRUTURA AIDA REQUERIDA:
                1. ATENÇÃO: Hook disruptivo (Pare o scroll).
                2. INTERESSE: Conecte o produto a um desejo de status ou solução de dor latente.
                3. DESEJO: Benefício aspiracional de alto valor. Gatilho de oportunidade única.
                4. AÇÃO: CTA (Chamada para ação) curto, escasso e direto para venda.
                
                REGRAS DE OURO:
                - Tom de voz: Autoritário, estilo CEO, sofisticado.
                - Use emojis de luxo e negócios estrategicamente.
                - Proibido introduções, explicações ou listar outros produtos.
                - Separe as 5 variações estritamente com ###.
                """
                resultado = miny.minerar_produtos(prompt, mkt, motor_ia)
                st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 20]

        # EXIBIÇÃO ORGANIZADA
        if "res_arsenal" in st.session_state:
            for i, copy in enumerate(st.session_state.res_arsenal):
                with st.container(border=True):
                    # Limpeza de resíduos de texto da IA
                    copy_limpa = copy.lstrip('0123456789. "').rstrip('"')
                    
                    st.markdown(f"#### 💎 Estratégia V{i+1}")
                    st.markdown(copy_limpa)
                    
                    if st.button(f"🎬 Carregar no Estúdio (V{i+1})", key=f"btn_v_{i}"):
                        # Envia a copy refinada + o link com ID injetado
                        st.session_state.copy_ativa = f"{copy_limpa}\n\n👉 **ADQUIRA AQUI:** {link_final}"
                        st.toast("Munição enviada com link de rastreio!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner antes de gerar o arsenal.")
