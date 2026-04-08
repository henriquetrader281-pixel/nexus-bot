import streamlit as st

def aplicar_id_afiliado(link, mkt):
    if not link or link == "#":
        return link
    ID_FIXO_SHOPEE = "18316451024"
    link = str(link).strip()
    if mkt == "Shopee":
        if "search?keyword=" in link:
            try:
                keyword = link.split("keyword=")[1].split("&")[0]
                return f"https://shopee.com.br/search?keyword={keyword}&smtt={ID_FIXO_SHOPEE}"
            except:
                return f"https://shopee.com.br/search?keyword=produto&smtt={ID_FIXO_SHOPEE}"
        base_link = link.split("?")[0]
        return f"{base_link}?smtt={ID_FIXO_SHOPEE}"
    return link

def exibir_arsenal(miny, motor_ia):
    st.markdown(f"### 🔱 Nexus 3.1 Pro | Estratégia AIDA")
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        
        # Limpeza para a IA não se confundir com o texto do Scanner
        bruto = st.session_state.sel_nome
        nome_para_ia = bruto.split('|')[0].replace("NOME:", "").strip()
        
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"📦 **Foco:** {nome_para_ia}")
            st.markdown("#### 🔗 Link Rastreado")
            st.code(link_final, language="text")

        st.divider()

        # Atualizado para width='stretch' (Padrão 2026)
        if st.button(f"🔥 GERAR MUNIÇÃO DE ALTA PERSUASÃO", width='stretch'):
            with st.spinner("Gemini Plus processando..."):
                # O comando 'Ignore saudações' agora serve de gatilho no seu mineracao.py
                prompt = f"""Ignore saudações. 
                Crie 5 variações AIDA curtas para o produto: {nome_para_ia}. 
                Separe cada uma das 5 variações APENAS com o símbolo ###."""
                
                try:
                    # Aqui ele chama o mineracao.py que já ajustamos para a rota v1
                    resultado = miny.minerar_produtos(prompt, mkt, "gemini-1.5-pro")
                    
                    if "###" in resultado:
                        st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 20]
                    else:
                        st.session_state.res_arsenal = [resultado.strip()]
                except Exception as e:
                    st.error(f"Erro no disparo: {e}")

        # EXIBIÇÃO EM CARDS
        if "res_arsenal" in st.session_state:
            for i, copy in enumerate(st.session_state.res_arsenal):
                with st.container(border=True):
                    st.markdown(f"#### 💎 Estratégia V{i+1}")
                    st.write(copy)
                    
                    if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_v_{i}", width='stretch'):
                        st.session_state.copy_ativa = f"{copy}\n\n🛒 **COMPRE:** {link_final}"
                        st.toast("Enviado ao Estúdio!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")
