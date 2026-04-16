import streamlit as st

def exibir_trends():
    st.markdown("### 🔱 Monitor Nexus Trends: Nível Elite")
    st.caption("Cruzamento de dados: TikTok Creative Center + Instagram Trends")

    if st.button("📊 SINCRONIZAR TENDÊNCIAS GLOBAIS", use_container_width=True):
        with st.spinner("IA Nexus fundindo dados das redes sociais..."):
            from app import get_nexus_intelligence
            res = get_nexus_intelligence()
            if res:
                st.session_state.cache_trends = res["trends"]
                st.success("Dados Elite atualizados!")

    trends = st.session_state.get('cache_trends', [])

    if trends:
        for item in trends:
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 3, 1])
                c1.image("https://cdn-icons-png.flaticon.com/512/174/174855.png", width=50)
                with c2:
                    st.markdown(f"**🎵 {item['musica']}**")
                    st.caption(f"💡 {item['razao']}")
                    st.info(f"🪝 Gancho IA: {item['aida_hook']}")
                with c3:
                    st.metric("Poder", f"{item['score']}%")
                    if st.button("USAR", key=f"use_{item['musica']}"):
                        st.session_state.musica_selecionada = item['musica']
                        st.session_state.hook_sugerido = item['aida_hook']
                        st.toast("Munição enviada ao Estúdio!")
    else:
        st.warning("Clique no botão acima para carregar as 5 tendências elite.")
