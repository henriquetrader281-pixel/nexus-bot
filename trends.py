import streamlit as st
from datetime import datetime
import json

def exibir_trends():
    # TUDO PRECISA ESTAR COM UM TAB DE RECUO AQUI PARA DENTRO
    st.markdown("### 🔱 Monitor Nexus Trends: Nível Elite")
    st.caption("Cruzamento de dados: TikTok Creative Center + Instagram Trends")

    # Pega o motor que já foi criado no app.py
    motor_ia = st.session_state.get("motor_ia_obj")

    if st.button("📊 SINCRONIZAR TENDÊNCIAS GLOBAIS", use_container_width=True):
        if not motor_ia:
            st.error("❌ Motor IA não detetado no Painel Nexus.")
        else:
            with st.spinner("IA Nexus fundindo dados das redes sociais..."):
                try:
                    hoje = datetime.now().strftime("%d/%m/%Y")
                    prompt = f"Analise tendências virais de HOJE ({hoje}) no TikTok Brasil. Retorne JSON: {{'trends': [{{'musica': '...', 'razao': '...', 'aida_hook': '...', 'score': 95}}]}}"
                    
                    # Lógica Híbrida Groq/Gemini
                    if hasattr(motor_ia, 'chat'): 
                        chat_completion = motor_ia.chat.completions.create(
                            messages=[{"role": "user", "content": prompt}],
                            model="llama-3.3-70b-versatile",
                            response_format={"type": "json_object"}
                        )
                        res_text = chat_completion.choices[0].message.content
                    else: 
                        response = motor_ia.generate_content(prompt)
                        res_text = response.text.replace('```json', '').replace('```', '').strip()
                    
                    res = json.loads(res_text)
                    st.session_state.cache_trends = res["trends"]
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

    # Exibição dos cards
    trends = st.session_state.get('cache_trends', [])
    if trends:
        for idx, item in enumerate(trends):
            with st.container(border=True):
                st.write(f"🎵 **{item['musica']}**")
                st.caption(item['razao'])
                if st.button("USAR", key=f"trend_{idx}"):
                    st.session_state.hook_sugerido = item['aida_hook']
                    st.toast("Munição enviada!")
    else:
        st.warning("Clique no botão acima para carregar.")
