import streamlit as st
from datetime import datetime
import json

def exibir_trends():
    st.markdown("### 🔱 Monitor Nexus Trends: Nível Elite")
    st.caption("Cruzamento de dados: TikTok Creative Center + Instagram Trends")

    # 1. PEGAMOS O MOTOR IA QUE JÁ ESTÁ NO APP.PY SEM IMPORTAR O ARQUIVO
    motor_ia = st.session_state.get("motor_ia_obj")

    if st.button("📊 SINCRONIZAR TENDÊNCIAS GLOBAIS", use_container_width=True):
        if not motor_ia:
            st.error("❌ Motor IA não detetado. Reinicia o sistema no Painel Nexus.")
        else:
            with st.spinner("IA Nexus fundindo dados das redes sociais..."):
                try:
                    hoje = datetime.now().strftime("%d/%m/%Y")
                    prompt = f"""
                    Analise tendências virais de HOJE ({hoje}) no TikTok e Reels Brasil.
                    Retorne APENAS um JSON com esta estrutura:
                    {{"trends": [
                        {{"musica": "nome", "razao": "por que é trend", "aida_hook": "gancho viral", "score": 95}},
                        ... (total 5)
                    ]}}
                    """
                    # Chama o motor diretamente aqui para evitar o erro de import circular
                    response = motor_ia.generate_content(prompt)
                    clean_json = response.text.replace('```json', '').replace('```', '').strip()
                    res = json.loads(clean_json)
                    
                    if res:
                        st.session_state.cache_trends = res["trends"]
                        st.success("Dados Elite atualizados!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro ao fundir tendências: {e}")

    trends = st.session_state.get('cache_trends', [])

    if trends:
        for idx, item in enumerate(trends): # Adicionado idx para chaves únicas
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 3, 1])
                c1.image("https://cdn-icons-png.flaticon.com/512/174/174855.png", width=50)
                with c2:
                    st.markdown(f"**🎵 {item['musica']}**")
                    st.caption(f"💡 {item['razao']}")
                    st.info(f"🪝 Gancho IA: {item['aida_hook']}")
                with c3:
                    st.metric("Poder", f"{item['score']}%")
                    # Chave única usando idx para evitar o erro de Duplicate Key
                    if st.button("USAR", key=f"use_trend_{idx}_{item['musica'][:5]}"):
                        st.session_state.musica_selecionada = item['musica']
                        st.session_state.hook_sugerido = item['aida_hook']
                        st.toast("Munição enviada ao Estúdio!")
    else:
        st.warning("Clique no botão acima para carregar as 5 tendências elite.")
