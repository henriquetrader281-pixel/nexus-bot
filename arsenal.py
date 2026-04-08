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
        if "shopee.com.br" not in base_link:
            path = base_link.split("/")[-1]
            base_link = f"https://shopee.com.br/{path}"
        return f"{base_link}?smtt={ID_FIXO_SHOPEE}"
    return link

def exibir_arsenal(miny, motor_ia):
    st.markdown(f"### 🔱 Nexus 3.1 Pro | Estratégia AIDA (Nível CEO)")
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        
        # Limpeza do nome para a IA focar na copy e não nos dados técnicos
        bruto = st.session_state.sel_nome
        nome_para_ia = bruto.split('|')[0].replace("NOME:", "").strip()
        
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"📦 **Foco da Operação:** {nome_para_ia}")
            st.markdown("#### 🔗 Link de Afiliado Blindado")
            st.code(link_final, language="text")

        st.divider()

        if st.button(f"🔥 GERAR MUNIÇÃO DE ALTA PERSUASÃO", width='stretch'):
            with st.spinner("Gemini Plus processando gatilhos..."):
                prompt = f"""
                Ignore dados técnicos. Crie 5 COPIES VIRAIS de venda para o produto: {nome_para_ia}.
                Use o método AIDA (Atenção, Interesse, Desejo, Ação). Estilo agressivo e direto.
                Separe cada uma das 5 variações APENAS com o símbolo ###.
                """
                
                try:
                    # 🚀 AQUI ESTÁ A CHAVE: Forçamos o uso do motor_ia (Gemini) 
                    # mesmo que o minerador esteja usando a Groq.
                    resultado = miny.minerar_produtos(prompt, mkt, "gemini-1.5-pro")
                    
                    if "###" in resultado:
                        st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 20]
                    else:
                        st.session_state.res_arsenal = [resultado.strip()]
                except Exception as e:
                    st.error(f"Erro no motor Gemini: {e}")

        if "res_arsenal" in st.session_state:
            for i, copy in enumerate(st.session_state.res_arsenal):
                with st.container(border=True):
                    v_limpa = copy.replace("[ATENÇÃO]", "🚨").replace("[INTERESSE]", "💡").replace("[DESEJO]", "✨").replace("[AÇÃO]", "🛒")
                    st.markdown(f"#### 💎 Estratégia de Elite V{i+1}")
                    st.markdown(v_limpa)
                    
                    if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_v_{i}", width='stretch'):
                        st.session_state.copy_ativa = f"{v_limpa}\n\n🛒 **COMPRE AGORA:** {link_final}"
                        st.toast("Munição enviada com sucesso!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")
