import streamlit as st
import nexus_copy as nxcopy 

def aplicar_id_afiliado(link, mkt):
    """Garante o rastreio com seu ID Shopee 18316451024"""
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
        mkt = st.session_state.get('mkt_global', 'Shopee')
        nome_bruto = st.session_state.sel_nome
        
        # Limpeza para a IA focar apenas no nome do produto
        nome_limpo = nome_bruto.split('|')[0].replace("NOME:", "").replace("*", "").strip()
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"📦 **Produto Selecionado:** {nome_limpo}")
            st.caption(f"🔗 Link com ID: {link_final}")
        
        if st.button("🔥 GERAR ESTRATÉGIAS VIRAIS (AIDA)", use_container_width=True):
            with st.spinner("IA Groq gerando Copys..."):
                nicho = st.session_state.get('foco_nicho', 'Ofertas')
                prompt = nxcopy.gerar_prompt_aida(nome_limpo, estilo="agressivo")
                prompt += f" Considere o nicho {nicho}."
                
                resultado_bruto = miny.minerar_produtos(prompt, mkt, "groq")
                resultado = nxcopy.limpar_copy(resultado_bruto)
                
                if "###" in resultado:
                    st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 15]
                else:
                    st.session_state.res_arsenal = [resultado.strip()]
                st.rerun()

        if "res_arsenal" in st.session_state:
            for i, texto_copy in enumerate(st.session_state.res_arsenal[:5]):
                with st.container(border=True):
                    st.write(texto_copy)
                    if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_{i}"):
                        micao_final = f"{texto_copy}\n\n🛒 LINK NO DIRECT: {link_final}"
                        st.session_state.copy_ativa = micao_final
                        st.session_state.link_final_afiliado = link_final
                        st.toast(f"Munição V{i+1} enviada!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")
