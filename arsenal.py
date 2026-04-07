import streamlit as st

def aplicar_id_afiliado(link, mkt):
    """Gera o link final injetando o ID de forma agressiva e correta"""
    if not link or link == "#":
        return link
        
    # Puxa os IDs dos Secrets (Certifique-se que estão configurados no Streamlit)
    id_shopee = st.secrets.get("SHOPEE_ID", "seu_id_padrao")
    id_meli = st.secrets.get("MELI_ID", "seu_id_meli")
    id_amz = st.secrets.get("AMAZON_ID", "seu_tag-20")

    link = str(link).strip()
    
    # RESOLVE O PROBLEMA DO ID NO SEARCH: 
    # Se o link já tem '?', usamos '&'. Se não, usamos '?'
    conector = "&" if "?" in link else "?"

    if mkt == "Shopee":
        # Injeta o smtt no final da URL de busca ou produto
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
        
        # O LINK É PROCESSADO IMEDIATAMENTE - PÁGINA INTEIRA COM ID
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.info(f"📦 **Produto Selecionado:** {st.session_state.sel_nome}")
            st.write("**Link de Venda Direta (Com seu Tracking):**")
            # Isso força a exibição do link completo para você conferir o ID
            st.code(link_final, language="text")

        st.divider()

        if st.button(f"🚀 GERAR MUNIÇÃO DE ALTA PERSUASÃO", use_container_width=True):
            with st.spinner("IA Sênior formatando modelo AIDA..."):
                # PROMPT CEO / ALTA PERSUASÃO - FOCADO EM VENDA DIRETA
                prompt = f"""
                Atue como um Diretor de Marketing (CMO) especialista em Direct Response e Persuasão.
                Gere 5 variações de copy de ALTO NÍVEL para o produto: {st.session_state.sel_nome}.
                
                ESTRUTURA OBRIGATÓRIA AIDA:
                - ATENÇÃO: Hook (gancho) disruptivo e agressivo para parar o scroll.
                - INTERESSE: Conecte o produto a um desejo de status, poder ou solução de dor latente.
                - DESEJO: Benefício aspiracional de alto valor. Gatilho de oportunidade única.
                - AÇÃO: CTA (Chamada para ação) curto, escasso e direto para o link.
                
                REGRAS:
                - Use linguagem autoritária, "Estilo CEO", sofisticada e direta.
                - Use emojis de luxo e negócios.
                - Separe cada uma das 5 variações estritamente com o símbolo ###.
                - PROIBIDO introduções, explicações ou listar outros produtos.
                """
                resultado = miny.minerar_produtos(prompt, mkt, motor_ia)
                # Limpa a resposta para garantir que pegamos apenas as copies
                st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 20]

        # EXIBIÇÃO ORGANIZADA
        if "res_arsenal" in st.session_state:
            for i, copy in enumerate(st.session_state.res_arsenal):
                with st.container(border=True):
                    # Limpeza de resíduos de texto da IA
                    copy_limpa = copy.lstrip('0123456789. "').rstrip('"')
                    
                    st.markdown(f"#### 💎 Versão Black {i+1}")
                    st.markdown(copy_limpa)
                    
                    if st.button(f"🎬 Carregar no Estúdio (V{i+1})", key=f"btn_v_{i}"):
                        # Envia a copy + o link já blindado com seu ID
                        st.session_state.copy_ativa = f"{copy_limpa}\n\n👉 **ADQUIRA AQUI:** {link_final}"
                        st.toast("Estratégia enviada ao Estúdio com Link de Afiliado!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner para desbloquear o Arsenal de Elite.")
