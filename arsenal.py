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
        
        # LIMPEZA ABSOLUTA DO NOME (Identação corrigida aqui)
        bruto = st.session_state.sel_nome
        nome_para_ia = bruto.split('|')[0].replace("NOME:", "").strip()
        
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"📦 **Foco da Operação:** {nome_para_ia}")
            st.markdown("#### 🔗 Link de Afiliado Blindado")
            st.code(link_final, language="text")

        st.divider()

        if st.button(f"🔥 GERAR MUNIÇÃO DE ALTA PERSUASÃO", width='stretch'):
            with st.spinner("Gemini Pro triturando objeções..."):
                prompt = f"""
                Ignore dados técnicos. Crie 5 COPIES VIRAIS de venda para: {nome_para_ia}.
                Use o método AIDA (Atenção, Interesse, Desejo, Ação). Estilo agressivo.
                Cada copy deve ser única e focar em um desejo diferente.
                Separe cada uma APENAS por ###.
                """
                
                try:
                    resultado = miny.minerar_produtos(prompt, mkt, motor_ia)
                    
                    if "###" in resultado:
                        st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 20]
                    else:
                        st.session_state.res_arsenal = [resultado.strip()]
                except Exception as e:
                    st.error(f"Erro na IA: {e}")

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
