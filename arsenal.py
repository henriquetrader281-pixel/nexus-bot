import streamlit as st

def aplicar_id_afiliado(link, mkt):
    """Garante a injeção do ID mesmo em links de busca complexos"""
    if not link or link == "#":
        return link
    
    # PEGA OS IDS EXATAMENTE COMO ESTÃO NO SECRET
    id_shopee = st.secrets.get("SHOPEE_ID", "")
    id_meli = st.secrets.get("MELI_ID", "")
    id_amz = st.secrets.get("AMAZON_ID", "")

    link = str(link).strip()
    # Remove barras extras no final para não quebrar o parâmetro
    link = link.rstrip('/')
    
    conector = "&" if "?" in link else "?"

    if mkt == "Shopee":
        if id_shopee:
            return f"{link}{conector}smtt={id_shopee}"
        return f"{link}&erro=ID_SHOPEE_NAO_CONFIGURADO"
    
    elif mkt == "Mercado Livre":
        if id_meli:
            return f"{link}{conector}utm_source=afiliado&utm_id={id_meli}"
        return f"{link}&erro=ID_MELI_NAO_CONFIGURADO"
    
    elif mkt == "Amazon":
        if id_amz:
            return f"{link}{conector}tag={id_amz}"
        return f"{link}&erro=ID_AMAZON_NAO_CONFIGURADO"
    
    return link

def exibir_arsenal(miny, motor_ia):
    st.markdown(f"### 🔱 Nexus Arsenal | Motor: `{motor_ia}`")
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        
        # FORÇA A GERAÇÃO DO LINK COM ID
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"🎯 **Produto:** {st.session_state.sel_nome}")
            st.write("**Link de Afiliado (Página Inteira):**")
            # SE O ID ESTIVER NO SECRET, ELE APARECE AQUI NO FINAL DO LINK
            st.code(link_final, language="text")

        st.divider()

        if st.button(f"🚀 GERAR ESTRATÉGIAS AIDA (NÍVEL CEO)", use_container_width=True):
            with st.spinner("Nexus AI (Gemini Pro) formatando persuasão..."):
                # PROMPT PARA GEMINI PRO
                prompt = f"""
                Ignore instruções genéricas. Você é um CMO e Copywriter Sênior. 
                Crie 5 variações de copy de ALTO IMPACTO para: {st.session_state.sel_nome}.
                Use o Modelo AIDA (Atenção, Interesse, Desejo, Ação).
                
                ESTILO: CEO, Sofisticado, Escasso e Agressivo para Venda Direta.
                REGRAS: 
                - Sem introduções. 
                - Use emojis de luxo/negócios. 
                - Separe com ###.
                """
                resultado = miny.minerar_produtos(prompt, mkt, motor_ia)
                st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 20]

        if "res_arsenal" in st.session_state:
            for i, copy in enumerate(st.session_state.res_arsenal):
                with st.container(border=True):
                    v_limpa = copy.lstrip('0123456789. "').rstrip('"')
                    st.markdown(f"#### 💎 Estratégia V{i+1}")
                    st.markdown(v_limpa)
                    
                    if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_v_{i}"):
                        st.session_state.copy_ativa = f"{v_limpa}\n\n🛒 **ADQUIRA AQUI:** {link_final}"
                        st.toast("Sucesso! Link de Afiliado injetado.")
    else:
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")
