# --- DENTRO DA FUNÇÃO exibir_estudio ---

if "sel_nome" in st.session_state and st.session_state.sel_nome:
    # Criamos uma variável limpa com APENAS o nome do produto selecionado
    produto_foco = st.session_state.sel_nome.split('|')[0].strip() 

    with st.container(border=True):
        if st.button(f"🔥 GERAR MUNIÇÃO AIDA: {produto_foco}", use_container_width=True):
            with st.spinner("Gemini Plus isolando produto e criando copy..."):
                
                # PROMPT BLINDADO: Proíbe a IA de listar outros produtos
                prompt_aida = f"""
                Ignore qualquer lista anterior. Foque EXCLUSIVAMENTE no produto: {produto_foco}.
                
                Tarefa: Crie uma legenda de Venda Direta usando o método AIDA.
                Regras Estritas:
                - NÃO liste outros produtos.
                - NÃO repita dados técnicos (Calor, Valor, ID).
                - Use emojis e foco total em RETENÇÃO.
                
                Estrutura:
                [ATENÇÃO] (Hook de 1 linha)
                [INTERESSE] (O problema resolvido)
                [DESEJO] (O benefício transformador)
                [AÇÃO] (Chamada para o link)
                """
                
                # Chama a IA passando apenas o nome isolado
                copy_aida = miny.minerar_produtos(prompt_aida, "Shopee", motor_ia)
                
                # Reconstrução do Link Blindado (ID: 18316451024)
                link_original = st.session_state.get('sel_link', 'https://shopee.com.br')
                # Limpa o lixo do link antes de injetar o seu ID
                link_base = link_original.split('?')[0] 
                link_final = f"{link_base}?smtt=18316451024"
                
                st.session_state.copy_final_pronta = f"{copy_aida.strip()}\n\n🛒 **LINK COM DESCONTO:** {link_final}"
