import streamlit as st

def aplicar_id_afiliado(link, mkt):
    """Gera o link final com o ID de afiliado correto"""
    if not link or link == "#": return link
    id_shopee = st.secrets.get("SHOPEE_ID", "seu_id_padrao")
    id_meli = st.secrets.get("MELI_ID", "seu_id_meli")
    id_amz = st.secrets.get("AMAZON_ID", "seu_tag-20")
    conector = "&" if "?" in link else "?"
    
    if mkt == "Shopee": return f"{link}{conector}smtt={id_shopee}"
    elif mkt == "Mercado Livre": return f"{link}{conector}utm_source=afiliado&utm_id={id_meli}"
    elif mkt == "Amazon": return f"{link}{conector}tag={id_amz}"
    return link

def exibir_arsenal(miny, motor_ia):
    st.header("🚀 Arsenal de Alta Conversão")
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"🎯 Foco: {st.session_state.sel_nome}")
            st.code(link_final, language="text")

        # --- NOVA CONFIGURAÇÃO DE COPY PODEROSA ---
        col1, col2 = st.columns(2)
        tom = col1.selectbox("Tom da Voz:", ["Agressivo (Venda Rápida)", "Curiosidade (Viral)", "Problema/Solução", "Engraçado"])
        rede = col2.selectbox("Rede Alvo:", ["TikTok/Reels", "WhatsApp/Direct", "Facebook Ads"])

        if st.button(f"🔥 Gerar Copies Magnéticas", use_container_width=True):
            with st.spinner("IA agindo como Copywriter Sênior..."):
                # PROMPT AVANÇADO: Aqui é onde a mágica acontece
                prompt = f"""
                Atue como um Copywriter especialista em vendas virais. 
                Gere 5 variações de copy para o produto: {st.session_state.sel_nome}.
                Contexto: O tom deve ser {tom} focado para {rede}.
                
                Regras:
                1. Use um Gancho (Hook) fortíssimo nos primeiros 3 segundos.
                2. Foque no BENEFÍCIO e na TRANSFORMAÇÃO, não apenas na característica.
                3. Use gatilhos de escassez e urgência.
                4. Use emojis estrategicamente.
                5. Separe cada variação estritamente com o símbolo ###.
                
                Não escreva introduções, entregue apenas as copies prontas para postar.
                """
                resultado = miny.minerar_produtos(prompt, mkt, motor_ia)
                st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 20]

        if "res_arsenal" in st.session_state:
            st.divider()
            for i, texto in enumerate(st.session_state.res_arsenal):
                with st.container(border=True):
                    v_limpa = texto.lstrip('0123456789. "').rstrip('"')
                    st.markdown(v_limpa) # Markdown permite negritos e listas
                    
                    if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_ars_{i}"):
                        st.session_state.copy_ativa = f"{v_limpa}\n\n🛒 Compre aqui: {link_final}"
                        st.toast("Munição carregada no Estúdio!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")
