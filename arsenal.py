import streamlit as st

def exibir_arsenal(miny, motor_ia):
    st.markdown("### 🔱 Arsenal Nexus | Estratégia AIDA")
    
    if st.session_state.get("sel_nome"):
        produto = st.session_state.sel_nome.split('|')[0].replace("NOME:", "").strip()
        link_id = f"{st.session_state.sel_link}&smtt=18316451024"

        if st.button("🔥 GERAR MUNIÇÃO DE ELTA PERSUASÃO", width='stretch'):
            with st.spinner("Gemini Plus triturando objeções..."):
                prompt = f"Ignore saudações. Crie 5 variações AIDA curtas e agressivas para: {produto}. Separe cada uma por [QUEBRA]."
                res = miny.minerar_produtos(prompt, "", "")
                st.session_state.res_arsenal = [c.strip() for c in res.split("[QUEBRA]") if len(c) > 10]

        if "res_arsenal" in st.session_state:
            for i, copy in enumerate(st.session_state.res_arsenal[:5]):
                with st.container(border=True):
                    st.markdown(f"#### 💎 Estratégia V{i+1}")
                    st.write(copy)
                    if st.button(f"🎬 Enviar V{i+1}", key=f"v{i}", width='stretch'):
                        st.session_state.copy_ativa = f"{copy}\n\n🛒 COMPRE: {link_id}"
                        st.toast("Enviado!")
    else:
        st.warning("Selecione um produto no Scanner.")
