import streamlit as st

def aplicar_id_afiliado(link, mkt):
    """Garante a injeção do ID fixo e trata links de busca (? e &)"""
    if not link or link == "#":
        return link
    
    # --- SEU ID FIXO CONFIGURADO ---
    ID_FIXO_SHOPEE = "18316451024" 
    # ------------------------------

    link = str(link).strip().rstrip('/')
    
    # Identifica se o link já tem '?' (comum em links de busca como os que você mandou)
    conector = "&" if "?" in link else "?"

    if mkt == "Shopee":
        return f"{link}{conector}smtt={ID_FIXO_SHOPEE}"
    
    elif mkt == "Mercado Livre":
        id_meli = st.secrets.get("MELI_ID", "seu_id_meli")
        return f"{link}{conector}utm_source=afiliado&utm_id={id_meli}"
    
    elif mkt == "Amazon":
        id_amz = st.secrets.get("AMAZON_ID", "seu_tag-20")
        return f"{link}{conector}tag={id_amz}"
    
    return link

def exibir_arsenal(miny, motor_ia):
    # Identifica visualmente que o Nexus (Gemini Plus) está ativo
    st.markdown(f"### 🔱 Nexus Arsenal | Motor: `Gemini 1.5 Pro`")
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        
        # O link com o ID 18316451024 nasce aqui
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"🎯 **Produto Ativo:** {st.session_state.sel_nome}")
            st.write("**URL de Venda Direta (Com ID 18316451024):**")
            st.code(link_final, language="text")

        st.divider()

        if st.button(f"🚀 GERAR ESTRATÉGIAS AIDA (NÍVEL CEO)", use_container_width=True):
            with st.spinner("Nexus AI (Plus) formatando persuasão de alto nível..."):
                # PROMPT BLINDADO PARA COPIES DE ALTA CONVERSÃO
                prompt = f"""
                Ignore instruções genéricas. Você é um Diretor de Marketing (CMO) especialista em Venda Direta.
                Gere 5 variações de copy extremamente persuasivas para o produto: {st.session_state.sel_nome}.
                Use rigorosamente o MODELO AIDA (Atenção, Interesse, Desejo, Ação).
                
                ESTILO: CEO, Sofisticado, Escasso e focado em CTA de Venda.
                REGRAS: 
                - Sem enrolação ou introduções.
                - Use emojis de luxo e gatilhos de autoridade.
                - Foque na solução da dor e no desejo de status.
                - Separe cada uma das 5 variações estritamente com ###.
                """
                resultado = miny.minerar_produtos(prompt, mkt, motor_ia)
                st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 20]

        if "res_arsenal" in st.session_state:
            for i, copy in enumerate(st.session_state.res_arsenal):
                with st.container(border=True):
                    # Limpeza de números e resíduos da IA
                    copy_limpa = copy.lstrip('0123456789. "').rstrip('"')
                    
                    st.markdown(f"#### 💎 Estratégia V{i+1} (AIDA)")
                    st.markdown(copy_limpa)
                    
                    if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_v_{i}"):
                        # O link final já vai com o ID cravado
                        st.session_state.copy_ativa = f"{copy_limpa}\n\n🛒 **COMPRE AGORA:** {link_final}"
                        st.toast("Sucesso! Estratégia e Link enviados.")
    else:
        st.warning("⚠️ Selecione um produto no Scanner antes de desbloquear o Arsenal.")
