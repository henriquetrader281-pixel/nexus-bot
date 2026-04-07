import streamlit as st

def aplicar_id_afiliado(link, mkt):
    """Gera o link final com o ID de afiliado correto para cada plataforma"""
    if not link or link == "#":
        return link
        
    # Busca IDs nos secrets
    id_shopee = st.secrets.get("SHOPEE_ID", "seu_id_padrao")
    id_meli = st.secrets.get("MELI_ID", "seu_id_meli")
    id_amz = st.secrets.get("AMAZON_ID", "seu_tag-20")

    # Verifica se o link já tem '?' para usar '&' ou '?'
    conector = "&" if "?" in link else "?"

    if mkt == "Shopee":
        return f"{link}{conector}smtt={id_shopee}"
    
    elif mkt == "Mercado Livre":
        return f"{link}{conector}utm_source=afiliado&utm_id={id_meli}"
    
    elif mkt == "Amazon":
        return f"{link}{conector}tag={id_amz}"
    
    return link

def exibir_arsenal(miny, motor_ia):
    st.header("🚀 Arsenal de Vendas")
    
    # 1. PEGA O PRODUTO E JÁ APLICA O ID AUTOMATICAMENTE
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        
        # O Link já é processado aqui ao carregar a aba
        link_com_id = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        st.success(f"📦 Produto Selecionado: {st.session_state.sel_nome} ({mkt})")
        st.info(f"🔗 Link de Afiliado Pronto: {link_com_id}")

        # 2. GERADOR DE COPIES
        if st.button(f"⚡ Gerar 5 variações de Copy para {mkt}", use_container_width=True):
            with st.spinner("IA preparando munição de vendas..."):
                # Prompt reforçado para evitar textos explicativos da IA
                prompt = f"Gere APENAS 5 variações de copy viral curta para o produto {st.session_state.sel_nome}. Não escreva introduções. Separe cada uma estritamente com ###"
                resultado = miny.minerar_produtos(prompt, mkt, motor_ia)
                
                # Divide e limpa a lista
                st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 10]

        # 3. EXIBIÇÃO EM CARDS
        if "res_arsenal" in st.session_state:
            st.divider()
            for i, texto in enumerate(st.session_state.res_arsenal):
                with st.container(border=True):
                    # Limpeza profunda de números, pontos e aspas que a IA coloca
                    v_limpa = texto.lstrip('0123456789. "').rstrip('"')
                    
                    st.write(f"**V{i+1}:** {v_limpa}")
                    
                    if st.button(f"🎬 Usar V{i+1} no Estúdio", key=f"btn_ars_{i}"):
                        # Envia o texto + o link que já foi processado com ID lá em cima
                        st.session_state.copy_ativa = f"{v_limpa}\n\n🛒 Compre aqui: {link_com_id}"
                        st.toast(f"V{i+1} enviada com link de afiliado!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner antes de gerar o arsenal.")
