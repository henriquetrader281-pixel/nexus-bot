import streamlit as st

def aplicar_id_afiliado(link, mkt):
    """Gera o link final com o ID de afiliado correto para cada plataforma"""
    if mkt == "Shopee":
        id_shopee = st.secrets.get("SHOPEE_ID", "seu_id_padrao")
        # Ajuste para garantir que o link não duplique interrogações
        conector = "&" if "?" in link else "?"
        return f"{link}{conector}smtt={id_shopee}"
    
    elif mkt == "Mercado Livre":
        id_meli = st.secrets.get("MELI_ID", "seu_id_meli")
        conector = "&" if "?" in link else "?"
        return f"{link}{conector}utm_source=afiliado&utm_id={id_meli}"
    
    elif mkt == "Amazon":
        id_amz = st.secrets.get("AMAZON_ID", "seu_tag-20")
        conector = "&" if "?" in link else "?"
        return f"{link}{conector}tag={id_amz}"
    
    return link

def exibir_arsenal(miny, motor_ia):
    st.header("🚀 Arsenal de Vendas")
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        
        # CARD DE PRODUTO ATIVO
        with st.container(border=True):
            c_prod1, c_prod2 = st.columns([3, 1])
            c_prod1.success(f"📦 Produto Selecionado: {st.session_state.sel_nome} ({mkt})")
            if c_prod2.button("Limpar", use_container_width=True):
                st.session_state.sel_nome = ""
                st.rerun()

        # --- MELHORIA: FILTROS DE REFINAMENTO (SEM MUDAR A ESTRUTURA) ---
        col_ars1, col_ars2 = st.columns(2)
        estilo = col_ars1.selectbox("Estilo da Copy:", ["Viral (TikTok/Reels)", "Venda Direta", "Storytelling", "Curiosidade"])
        publico = col_ars2.text_input("Público Alvo (Opcional):", placeholder="Ex: Donas de casa, Jovens...")

        if st.button(f"⚡ Gerar Munição Viral para {mkt}", use_container_width=True):
            with st.spinner("IA preparando munição de vendas..."):
                # Prompt melhorado usando as variáveis de estilo e público
                prompt = f"Gere 5 variações de copy para o produto {st.session_state.sel_nome}. Estilo: {estilo}. Público: {publico}. Use emojis e separe cada uma com ###"
                resultado = miny.minerar_produtos(prompt, mkt, motor_ia)
                st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 10]

        # EXIBIÇÃO EM CARDS
        if "res_arsenal" in st.session_state:
            link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
            st.divider()
            
            for i, texto in enumerate(st.session_state.res_arsenal):
                with st.container(border=True):
                    # Limpeza de números automáticos
                    v_limpa = texto.lstrip('0123456789. ')
                    st.write(v_limpa)
                    st.caption(f"🔗 Link de Afiliado {mkt} Gerado")
                    
                    col_btn1, col_btn2 = st.columns([1, 1])
                    
                    if col_btn1.button(f"🎬 Usar V{i+1} no Estúdio", key=f"btn_ars_{i}"):
                        st.session_state.copy_ativa = f"{v_limpa}\n\n🛒 Compre aqui: {link_final}"
                        st.toast("Copy e Link enviados ao Estúdio!")
                    
                    # MELHORIA: Botão de cópia rápida
                    col_btn2.code(link_final, language="text")

    else:
        st.warning("⚠️ Selecione um produto no Scanner antes de gerar o arsenal.")
