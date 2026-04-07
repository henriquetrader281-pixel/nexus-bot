import streamlit as st

def aplicar_id_afiliado(link, mkt):
    """Injeta o ID de afiliado corrigindo o conector da URL"""
    if not link or link == "#":
        return link
        
    # Busca os IDs configurados nos Secrets do Streamlit
    id_shopee = st.secrets.get("SHOPEE_ID", "seu_id_padrao")
    id_meli = st.secrets.get("MELI_ID", "seu_id_meli")
    id_amz = st.secrets.get("AMAZON_ID", "seu_tag-20")

    # Identifica se o link já tem '?' (como o link de search que você mandou)
    # Se já tiver '?', usamos '&'. Se não tiver, usamos '?'
    conector = "&" if "?" in link else "?"

    if mkt == "Shopee":
        return f"{link}{conector}smtt={id_shopee}"
    elif mkt == "Mercado Livre":
        return f"{link}{conector}utm_source=afiliado&utm_id={id_meli}"
    elif mkt == "Amazon":
        return f"{link}{conector}tag={id_amz}"
    
    return link

def exibir_arsenal(miny, motor_ia):
    st.header("🚀 Arsenal de Vendas Profissional")
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        
        # Gera o link completo com ID imediatamente ao carregar a página
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"📦 Produto Selecionado: {st.session_state.sel_nome} ({mkt})")
            st.write("**Link com seu ID:**")
            st.code(link_final, language="text") # Mostra o link completo para conferência

        st.divider()

        # Configurações para evitar copies rasas
        col1, col2 = st.columns(2)
        estilo = col1.selectbox("Estilo da Copy:", ["Viral (TikTok/Reels)", "Venda Direta", "Curiosidade/Mistério"])
        publico = col2.text_input("Público Alvo:", placeholder="Ex: Mulheres 20+, Donos de Pet...")

        if st.button(f"🔥 Gerar Munição Pesada para {mkt}", use_container_width=True):
            with st.spinner("IA agindo como Copywriter Sênior..."):
                # Prompt profissional para copies de alta conversão
                prompt = f"""
                Atue como um Copywriter especialista em vendas virais. 
                Gere 5 variações de copy para o produto: {st.session_state.sel_nome}.
                Estilo: {estilo}. Público: {publico}.
                Use Ganchos Fortes (Hooks), Emojis e Gatilhos de Escassez.
                Separe cada variação estritamente com o símbolo ###.
                Não inclua listas de produtos, apenas as copies.
                """
                resultado = miny.minerar_produtos(prompt, mkt, motor_ia)
                st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 10]

        # Exibição das Versões (V1, V2...)
        if "res_arsenal" in st.session_state:
            for i, texto in enumerate(st.session_state.res_arsenal):
                with st.container(border=True):
                    # Limpa restos de números ou aspas da IA
                    v_limpa = texto.lstrip('0123456789. "').rstrip('"')
                    st.markdown(f"**Versão V{i+1}**")
                    st.write(v_limpa)
                    
                    if st.button(f"🎬 Usar V{i+1} no Estúdio", key=f"btn_ars_{i}"):
                        st.session_state.copy_ativa = f"{v_limpa}\n\n🛒 Compre aqui: {link_final}"
                        st.toast("Copy e Link enviados ao Estúdio!")
    else:
        st.warning("Selecione um produto no Scanner primeiro.")
