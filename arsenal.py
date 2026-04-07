import streamlit as st

def aplicar_id_afiliado(link, mkt):
    """Garante que o link da Shopee permaneça e anexa o ID 18316451024"""
    if not link or link == "#":
        return link
    
    ID_FIXO_SHOPEE = "18316451024" 
    link = str(link).strip()
    
    if mkt == "Shopee":
        # Se for link de busca
        if "search?keyword=" in link:
            base_search = link.split("&")[0] 
            return f"{base_search}&smtt={ID_FIXO_SHOPEE}"
        
        # Se for link de produto, limpa o lixo e põe o ID
        base_link = link.split("?")[0]
        return f"{base_link}?smtt={ID_FIXO_SHOPEE}"
    
    return link

def exibir_arsenal(miny, motor_ia):
    """Esta é a função que o app.py está procurando"""
    st.markdown(f"### 🔱 Nexus 3.1 Pro | Estratégia AIDA")
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"📦 **Produto:** {st.session_state.sel_nome}")
            st.code(link_final, language="text")
            st.caption("Rastreio ativo: 18316451024")

        if st.button(f"🔥 GERAR MUNIÇÃO CEO", use_container_width=True):
            with st.spinner("Gemini Pro processando..."):
                prompt = f"Atue como Copywriter Sênior. Produto: {st.session_state.sel_nome}. Use AIDA. Separe com ###."
                resultado = miny.minerar_produtos(prompt, mkt, motor_ia)
                st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 20]

        if "res_arsenal" in st.session_state:
            for i, copy in enumerate(st.session_state.res_arsenal):
                with st.container(border=True):
                    st.markdown(copy)
                    if st.button(f"🎬 Enviar V{i+1}", key=f"btn_{i}"):
                        st.session_state.copy_ativa = f"{copy}\n\n🛒 **COMPRE AGORA:** {link_final}"
                        st.toast("Enviado ao Estúdio!")
    else:
        st.warning("Selecione um produto no Scanner.")
