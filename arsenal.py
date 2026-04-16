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
    st.markdown("### 🔱 Arsenal Nexus | Munição Elite")
    nome = st.session_state.get("sel_nome", "")
    link = st.session_state.get("sel_link", "")
    nicho = st.session_state.get("foco_nicho", "Ofertas")

    if nome:
        nome_ia = nome.replace("*", "").split('|')[0].replace("NOME:", "").strip()
        link_final = aplicar_id_afiliado(link, st.session_state.get('mkt_global', 'Shopee'))
        st.success(f"📦 Produto Ativo: {nome_ia}")
        
        if st.button("🔥 GERAR ESTRATÉGIAS VIRAIS (AIDA)", use_container_width=True):
            with st.spinner("IA Groq gerando Copys..."):
                prompt = nxcopy.gerar_prompt_aida(nome_ia, estilo="agressivo")
                prompt += f" Considere o nicho {nicho}."
                resultado_bruto = miny.minerar_produtos(prompt, "Shopee", "groq")
                resultado = nxcopy.limpar_copy(resultado_bruto)
                st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 15]
                st.rerun()

        if "res_arsenal" in st.session_state:
            for i, texto_copy in enumerate(st.session_state.res_arsenal[:5]):
                with st.container(border=True):
                    st.write(texto_copy)
                    if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_{i}"):
                        st.session_state.copy_ativa = f"{texto_copy}\n\n🛒 LINK: {link_final}"
                        st.session_state.link_final_afiliado = link_final
                        st.toast("Enviado para o Estúdio!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")
