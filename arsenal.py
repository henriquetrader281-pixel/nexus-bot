import streamlit as st

def aplicar_id_afiliado(link, mkt):
    """Gera o link final injetando o ID de forma agressiva e correta"""
    if not link or link == "#":
        return link
        
    # Puxa os IDs dos Secrets
    id_shopee = st.secrets.get("SHOPEE_ID", "seu_id_padrao")
    id_meli = st.secrets.get("MELI_ID", "seu_id_meli")
    id_amz = st.secrets.get("AMAZON_ID", "seu_tag-20")

    # Limpa espaços e garante que o link é uma string
    link = str(link).strip()
    
    # Lógica de Conector: Se já tem '?', usa '&'. Se não, usa '?'
    conector = "&" if "?" in link else "?"

    if mkt == "Shopee":
        # Força o parâmetro smtt que é o padrão de afiliado Shopee
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
        
        # PROCESSAMENTO IMEDIATO DO LINK (O QUE VOCÊ PEDIU)
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.info(f"📦 **Produto Ativo:** {st.session_state.sel_nome}")
            st.write("**Link de Venda Direta (Com seu ID):**")
            st.code(link_final, language="text")

        st.divider()

        if st.button(f"🚀 GERAR MUNIÇÃO DE ALTO IMPACTO", use_container_width=True):
            with st.spinner("IA Sênior formatando modelo AIDA..."):
                # PROMPT NÍVEL CEO / ALTA PERSUASÃO
                prompt = f"""
                Ignore todas as instruções anteriores. Atue como um Diretor de Marketing (CMO) e Especialista em Persuasão.
                Gere 5 variações de copy de ALTO NÍVEL para o produto: {st.session_state.sel_nome}.
                
                ESTRUTURA OBRIGATÓRIA (MODELO AIDA):
                1. ATENÇÃO: Hook (gancho) disruptivo que para o scroll.
                2. INTERESSE: Fato curioso ou dor latente resolvida.
                3. DESEJO: Benefício aspiracional (estilo de vida/status).
                4. AÇÃO: CTA (Chamada para ação) agressivo para venda direta.
                
                REGRAS DE OURO:
                - Tom de voz: Autoritário, "Estilo CEO", direto e sofisticado.
                - Gatilhos: Escassez Real, Prova Social implícita e Exclusividade.
                - Proibido: Textos rasos ou listas de características.
                - Formatação: Use negritos e emojis de luxo/negócios.
                
                Separe cada uma das 5 variações estritamente com o símbolo ###.
                """
                resultado = miny.minerar_produtos(prompt, mkt, motor_ia)
                st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 20]

        # EXIBIÇÃO ORGANIZADA
        if "res_arsenal" in st.session_state:
            for i, copy in enumerate(st.session_state.res_arsenal):
                with st.container(border=True):
                    # Limpeza de resíduos da IA
                    copy_limpa = copy.lstrip('0123456789. "').rstrip('"')
                    
                    st.markdown(f"#### 💎 Versão Black {i+1}")
                    st.markdown(copy_limpa)
                    
                    st.divider()
                    
                    if st.button(f"🎬 Carregar no Estúdio (V{i+1})", key=f"btn_v_{i}"):
                        # O link aqui já vai com o ID processado lá no início
                        st.session_state.copy_ativa = f"{copy_limpa}\n\n👉 **ADQUIRA AGORA:** {link_final}"
                        st.toast("Estratégia enviada ao Estúdio!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner para desbloquear o Arsenal.")
