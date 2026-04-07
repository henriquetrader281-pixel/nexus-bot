import streamlit as st

def processar_link_afiliado(link_original, mkt_alvo):
    """Retorna o link com o ID de afiliado aplicado conforme o marketplace"""
    # Buscamos os IDs nos secrets
    ids = {
        "Shopee": st.secrets.get("SHOPEE_ID", "default_shopee"),
        "Mercado Livre": st.secrets.get("MELI_ID", "default_meli"),
        "Amazon": st.secrets.get("AMAZON_ID", "default_amazon")
    }
    
    meu_id = ids.get(mkt_alvo)

    # Lógica de montagem de link por plataforma
    if mkt_alvo == "Shopee":
        return f"{link_original}?smtt={meu_id}"
    elif mkt_alvo == "Mercado Livre":
        # Exemplo: links de ML costumam usar parâmetros de tracking
        return f"{link_original}&utm_source=afiliado&utm_id={meu_id}"
    elif mkt_alvo == "Amazon":
        # Amazon usa o tag=ID-20
        return f"{link_original}&tag={meu_id}"
    
    return link_original

def exibir_aba_arsenal(miny, motor_ia):
    st.header("🚀 Arsenal de Vendas")
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        st.success(f"Produto: {st.session_state.sel_nome} ({mkt})")
        
        # 1. Configurações
        col1, col2 = st.columns(2)
        estilo = col1.selectbox("Estilo:", ["Viral", "Venda Direta", "Storytelling"])
        
        if st.button(f"⚡ Gerar Munição para {mkt}"):
            with st.spinner("IA preparando copies..."):
                prompt = f"Gere 5 copies para {st.session_state.sel_nome} no estilo {estilo}. Separe com ###"
                res = miny.minerar_produtos(prompt, mkt, motor_ia)
                st.session_state.res_arsenal = res.split("###")

        # 2. Exibição
        if "res_arsenal" in st.session_state:
            link_final = processar_link_afiliado(st.session_state.sel_link, mkt)
            
            for i, copy in enumerate(st.session_state.res_arsenal):
                if len(copy.strip()) > 5:
                    with st.container(border=True):
                        st.markdown(copy)
                        st.caption(f"🔗 Link: {link_final}")
                        
                        if st.button(f"🎬 Usar V{i+1}", key=f"ars_{i}"):
                            st.session_state.copy_ativa = f"{copy}\n\n🛒 Compre aqui: {link_final}"
                            st.toast("Pronto para o Estúdio!")
    else:
        st.warning("Selecione um produto no Scanner.")
