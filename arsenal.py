import streamlit as st
import nexus_copy as nxcopy 

def aplicar_id_afiliado(link, mkt):
    if not link or link == "#": return link
    ID_FIXO_SHOPEE = "18316451024"
    if mkt == "Shopee":
        base_link = link.split("?")[0]
        return f"{base_link}?smtt={ID_FIXO_SHOPEE}"
    return link

def exibir_arsenal(miny, motor_ia):
    st.markdown("### 🔱 Arsenal Nexus | Munição de Alta Persuasão")
    
    # Recupera o nicho definido no Scanner
    nicho_atual = st.session_state.get('foco_nicho', 'Ofertas')
    
    if st.session_state.get("sel_nome"):
        nome_limpo = st.session_state.sel_nome.split('|')[0].replace("NOME:", "").strip()
        link_final = aplicar_id_afiliado(st.session_state.sel_link, st.session_state.mkt_global)
        
        if st.button("🔥 GERAR ESTRATÉGIAS VIRAIS (AIDA)", use_container_width=True):
            with st.spinner("IA Groq gerando Copys..."):
                prompt_mestre = nxcopy.gerar_prompt_aida(nome_limpo, estilo="agressivo")
                prompt_mestre += f" Considere o nicho {nicho_atual}."
                
                resultado_bruto = miny.minerar_produtos(prompt_mestre, st.session_state.mkt_global, "groq")
                resultado = nxcopy.limpar_copy(resultado_bruto)
                
                if "###" in resultado:
                    st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 15]
                else:
                    st.session_state.res_arsenal = [resultado.strip()]

        if "res_arsenal" in st.session_state:
            for i, texto_copy in enumerate(st.session_state.res_arsenal[:5]):
                with st.container(border=True):
                    st.write(texto_copy)
                    if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_{i}"):
                        micao_final = f"{texto_copy}\n\n🛒 LINK NO DIRECT: {link_final}"
                        st.session_state.copy_ativa = micao_final
                        st.session_state.link_final_afiliado = link_final
                        st.toast("Munição enviada!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")
