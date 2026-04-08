import streamlit as st

def aplicar_id_afiliado(link, mkt):
    if not link or link == "#":
        return link
    ID_FIXO_SHOPEE = "18316451024"
    link = str(link).strip()
    if mkt == "Shopee":
        base_link = link.split("?")[0]
        return f"{base_link}?smtt={ID_FIXO_SHOPEE}"
    return link

def exibir_arsenal(miny, motor_ia):
    st.markdown("### 🔱 Arsenal Nexus | Munição de Alta Persuasão")
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        bruto = st.session_state.sel_nome
        # Limpa o nome removendo Calor/Valor para a IA não repetir isso
        nome_limpo = bruto.split('|')[0].replace("NOME:", "").strip()
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"📦 **Produto:** {nome_limpo}")
            st.code(link_final, language="text")

        if st.button("🔥 GERAR ESTRATÉGIAS VIRAIS", width='stretch'):
            with st.spinner("Gemini Plus criando 5 variações agressivas..."):
                # PROMPT REESTRUTURADO (O PULO DO GATO)
                prompt = f"""
                Aja como um Copywriter de elite focado em Reels e TikTok. 
                Crie 5 variações de copy extremamente curtas e persuasivas para o produto: {nome_limpo}.
                
                REGRAS RÍGIDAS:
                1. Use o método AIDA, mas seja direto. 
                2. Use emojis que chamam atenção.
                3. Foque no benefício/desejo, NÃO na ficha técnica.
                4. Termine sempre instigando a pessoa a comentar para receber o link.
                5. NÃO diga "Aqui estão as cópias", apenas entregue o texto.
                
                SEPARE CADA UMA DAS 5 VARIAÇÕES APENAS COM O MARCADOR: ###
                """
                
                try:
                    # Chama o motor (Gemini Pro Estável via v1)
                    resultado = miny.minerar_produtos(prompt, mkt, "gemini-1.5-pro")
                    
                    if "###" in resultado:
                        st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 15]
                    else:
                        st.session_state.res_arsenal = [resultado.strip()]
                except Exception as e:
                    st.error(f"Erro na geração: {e}")

        if "res_arsenal" in st.session_state:
            for i, copy in enumerate(st.session_state.res_arsenal[:5]):
                with st.container(border=True):
                    st.markdown(f"#### 💎 Estratégia V{i+1}")
                    st.write(copy)
                    if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_{i}", width='stretch'):
                        st.session_state.copy_ativa = f"{copy}\n\n🛒 LINK NO DIRECT: {link_final}"
                        st.toast("Munição enviada!")
    else:
        st.warning("Selecione um produto no Scanner.")
