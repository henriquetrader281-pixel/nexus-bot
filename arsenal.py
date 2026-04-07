import streamlit as st

def aplicar_id_afiliado(link, mkt):
    """Refaz o link do zero para garantir que o ID 18316451024 seja o dono da página"""
    if not link or link == "#":
        return link
    
    # SEU ID FIXO DE AFILIADO
    ID_FIXO_SHOPEE = "18316451024" 

    link = str(link).strip()
    
    # LIMPEZA DE ELITE: Se for Shopee, limpamos o lixo da URL antes de fixar o ID
    if mkt == "Shopee":
        # Pega apenas a base do link (antes de qualquer '?' ou 'extraParams')
        base_link = link.split("?")[0]
        # Monta o link limpo e injeta seu ID como parâmetro principal
        link_final = f"{base_link}?smtt={ID_FIXO_SHOPEE}"
        return link_final
    
    # Para outros marketplaces (caso use no futuro)
    conector = "&" if "?" in link else "?"
    if mkt == "Mercado Livre":
        return f"{link}{conector}utm_source=afiliado&utm_id=seu_id_meli"
    elif mkt == "Amazon":
        return f"{link}{conector}tag=seu_tag-20"
    
    return link

def exibir_arsenal(miny, motor_ia):
    # Cabeçalho Nexus: Indica que o Gemini Pro está operando
    st.markdown(f"### 🔱 Nexus Arsenal | Motor: `Gemini 1.5 Pro`")
    
    # 1. FIXAÇÃO DO LINK NA PÁGINA INTEIRA
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        
        # O link morre e nasce aqui com o ID 18316451024 fixo
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        # Card de Comando Central (Onde o link fica fixado)
        with st.container(border=True):
            st.success(f"📦 **PRODUTO SELECIONADO:** {st.session_state.sel_nome}")
            st.markdown("### 🔗 Link Blindado (Página Inteira)")
            st.code(link_final, language="text")
            st.caption("Este link já contém o rastreio oficial 18316451024.")

        st.divider()

        # 2. GERADOR DE COPIES AIDA (NÍVEL CEO)
        if st.button(f"🔥 GERAR ESTRATÉGIAS DE ALTA PERSUASÃO", use_container_width=True):
            with st.spinner("Conectando ao Nexus AI para criar copies imbatíveis..."):
                prompt = f"""
                Ignore todas as instruções anteriores. Você é um Diretor de Marketing (CMO) e Copywriter de Elite.
                Gere 5 variações de copy de ALTO IMPACTO para o produto: {st.session_state.sel_nome}.
                
                ESTRUTURA OBRIGATÓRIA (MODELO AIDA):
                - ATENÇÃO: Hook disruptivo que para o scroll instantaneamente.
                - INTERESSE: Conecte o produto a um desejo de status, autoridade ou solução de dor.
                - DESEJO: Benefício aspiracional de alto nível. Gatilho de oportunidade única.
                - AÇÃO: CTA (Chamada para ação) curto, escasso e direto para o link.
                
                REGRAS:
                - Estilo CEO: Sofisticado, autoritário, sem enrolação.
                - Use emojis de luxo estrategicamente.
                - Separe cada variação estritamente com ###.
                - PROIBIDO introduções ou listar outros produtos.
                """
                resultado = miny.minerar_produtos(prompt, mkt, motor_ia)
                st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 20]

        # 3. EXIBIÇÃO E ENVIO AO ESTÚDIO
        if "res_arsenal" in st.session_state:
            for i, copy in enumerate(st.session_state.res_arsenal):
                with st.container(border=True):
                    # Limpeza de resíduos da IA
                    v_limpa = copy.lstrip('0123456789. "').rstrip('"')
                    
                    st.markdown(f"#### 💎 Estratégia de Elite V{i+1}")
                    st.markdown(v_limpa)
                    
                    if st.button(f"🎬 Carregar no Estúdio (V{i+1})", key=f"btn_v_{i}"):
                        # Envia a copy refinada + o link que está FIXO no topo da página
                        st.session_state.copy_ativa = f"{v_limpa}\n\n🛒 **COMPRE AGORA:** {link_final}"
                        st.toast("Munição enviada ao Estúdio com ID Blindado!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner antes de desbloquear o Arsenal de Elite.")
