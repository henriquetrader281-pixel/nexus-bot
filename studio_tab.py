import streamlit as st

def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio Automatizado Nexus | Google Labs 🔱")
    
    if "sel_nome" not in st.session_state:
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")
        return

    # Isola o nome para evitar confusão na IA
    produto = st.session_state.sel_nome.split('|')[0].replace("NOME:", "").strip()

    # --- LINHA DE COMANDO: GERAÇÃO DE MUNIÇÃO ---
    c1, c2 = st.columns([1, 1])
    
    with c1:
        if st.button("📝 GERAR COPY & PROMPT", use_container_width=True):
            with st.spinner("Preparando comandos..."):
                # Pedimos o AIDA e o Prompt em Inglês de uma vez só
                prompt_master = f"""
                Ignore listas. Produto: {produto}.
                1. Gere legenda AIDA em Português (com ID 18316451024).
                2. Gere um Prompt VISUAL em INGLÊS para vídeo cinematográfico.
                Separe por '###'
                """
                res = miny.minerar_produtos(prompt_master, "Shopee", motor_ia)
                st.session_state.micao_nexus = res.split('###')
                st.rerun()

    # --- EXIBIÇÃO DA MUNIÇÃO ---
    if "micao_nexus" in st.session_state:
        copy_pt = st.session_state.micao_nexus[0].strip()
        prompt_en = st.session_state.micao_nexus[1].strip() if len(st.session_state.micao_nexus) > 1 else ""

        with st.expander("📄 LEGENDA PARA POSTAR", expanded=False):
            st.text_area("Copie aqui:", value=copy_pt, height=150)

        st.success("🎯 PROMPT PARA COLAR NO GOOGLE LABS:")
        st.code(prompt_en, language="text")
        st.caption("Clique no ícone de copiar no canto do bloco acima ☝️")

        st.divider()

        # --- INTEGRAÇÃO DO GOOGLE LABS DENTRO DO NEXUS ---
        st.markdown("#### 📺 Gerador de Vídeo (Execução Direta)")
        
        # Link do projeto específico que você mandou
        url_google = "https://labs.google/fx/pt/tools/flow/project/b7c52242-fa5a-4370-9975-61cc86da1483"
        
        # Criando a janela interna (IFrame)
        # Nota: Alguns sites bloqueiam exibição em IFrame por segurança. 
        # Se o Google bloquear, o botão de 'Abrir em Nova Aba' servirá como backup.
        st.components.v1.iframe(url_google, height=600, scrolling=True)
        
        if st.button("🌍 Não carregou? Abrir Google Labs em tela cheia"):
            st.markdown(f'<a href="{url_google}" target="_blank">Clique aqui para abrir</a>', unsafe_allow_value=True)

    else:
        st.info("Clique no botão acima para preparar a automação do produto.")
