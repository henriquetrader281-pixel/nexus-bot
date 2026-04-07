import streamlit as st

def aplicar_id_afiliado(link, mkt):
    """Gera o link final com o ID de afiliado correto para cada plataforma"""
    if mkt == "Shopee":
        id_shopee = st.secrets.get("SHOPEE_ID", "seu_id_padrao")
        return f"{link}&smtt={id_shopee}"
    
    elif mkt == "Mercado Livre":
        id_meli = st.secrets.get("MELI_ID", "seu_id_meli")
        # Estrutura padrão de trackid para ML
        return f"{link}&utm_source=afiliado&utm_id={id_meli}"
    
    elif mkt == "Amazon":
        id_amz = st.secrets.get("AMAZON_ID", "seu_tag-20")
        return f"{link}&tag={id_amz}"
    
    return link

def exibir_arsenal(miny, motor_ia):
    st.header("🚀 Arsenal de Vendas")
    
    # Verifica se há um produto selecionado no estado da sessão
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        st.success(f"📦 Produto Selecionado: {st.session_state.sel_nome} ({mkt})")
        
        if st.button(f"⚡ Gerar Munição Viral para {mkt}", use_container_width=True):
            with st.spinner("IA preparando munição de vendas..."):
                prompt = f"Gere 5 variações de copy viral curta para o produto {st.session_state.sel_nome}. Use emojis e separe cada uma com ###"
                resultado = miny.minerar_produtos(prompt, mkt, motor_ia)
                # Divide o texto da IA em uma lista usando o separador
                st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 10]

        # Exibição organizada em cards
        if "res_arsenal" in st.session_state:
            link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
            
            for i, texto in enumerate(st.session_state.res_arsenal):
                with st.container(border=True):
                    # Remove números automáticos que a IA costuma colocar (ex: "1. ")
                    v_limpa = texto.lstrip('0123456789. ')
                    st.write(v_limpa)
                    st.caption(f"🔗 Link de Afiliado {mkt} Gerado")
                    
                    if st.button(f"🎬 Usar V{i+1} no Estúdio", key=f"btn_ars_{i}"):
                        st.session_state.copy_ativa = f"{v_limpa}\n\n🛒 Compre aqui: {link_final}"
                        st.toast("Copy e Link enviados ao Estúdio!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner antes de gerar o arsenal.")
