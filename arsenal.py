# No arsenal.py, dentro de exibir_arsenal:
        mkt = st.session_state.mkt_global
        
        # LIMPEZA ABSOLUTA: Pega apenas o que interessa para a Copy
        bruto = st.session_state.sel_nome
        # Se vier no formato "NOME: Produto | CALOR...", limpamos tudo após o primeiro "|"
        nome_para_ia = bruto.split('|')[0].replace("NOME:", "").strip()
        
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"📦 **Foco da Operação:** {nome_para_ia}")
            st.markdown("#### 🔗 Link de Afiliado Blindado")
            st.code(link_final, language="text") # Verifique se termina em 18316451024 aqui!

        st.divider()

        if st.button(f"🔥 GERAR MUNIÇÃO DE ALTA PERSUASÃO", width='stretch'):
            with st.spinner("Gemini Pro triturando objeções..."):
                # PROMPT REFORÇADO PARA EVITAR REPETIÇÃO
                prompt = f"""
                Ignore dados técnicos. Crie 5 COPIES VIRAIS de venda para: {nome_para_ia}.
                Use o método AIDA. Estilo agressivo para TikTok/Reels.
                Cada copy deve ser única e focar em um desejo diferente (praticidade, status, economia, etc).
                Separe cada uma APENAS por ###.
                """
                # ... resto do código de chamada da IA
