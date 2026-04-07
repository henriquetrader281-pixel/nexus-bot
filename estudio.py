# --- DENTRO DO BOTAO GERAR LEGENDA ---
with st.spinner("Limpando ruído e gerando copy de impacto..."):
    # Isolamos apenas o nome essencial
    produto_limpo = st.session_state.sel_nome.split('|')[0].replace("NOME:", "").strip()

    prompt_blindado = f"""
    CONTEXTO: Você é um Diretor de Conversão.
    PRODUTO ATUAL: {produto_limpo}

    TAREFA: Gere APENAS a legenda AIDA e o Roteiro de Retenção para ESTE produto.
    
    REGRAS CRÍTICAS:
    1. PROIBIDO listar outros produtos da sessão.
    2. PROIBIDO repetir dados como 'CALOR' ou 'TICKET'.
    3. FOCO TOTAL no método AIDA (Atenção, Interesse, Desejo, Ação).
    4. O tom deve ser de 'Achadinho Viral'.

    FORMATO DE SAÍDA:
    🚨 [ATENÇÃO]: (Gancho que para o scroll)
    💡 [INTERESSE]: (Por que ele precisa disso?)
    ✨ [DESEJO]: (A transformação na rotina)
    🛒 [AÇÃO]: (Chamada para o link)
    """

    # Chama a IA com o prompt restrito
    resposta_ia = miny.minerar_produtos(prompt_blindado, "Shopee", motor_ia)
    
    # Blindagem do Link (Consertando o erro do https? que apareceu no seu print)
    link_raw = st.session_state.get('sel_link', 'https://shopee.com.br')
    link_final = link_raw.split('?')[0].split('|')[0].strip()
    link_afiliado = f"{link_final}?smtt=18316451024"

    st.session_state.copy_final_pronta = f"{resposta_ia}\n\n🔗 **LINK EXCLUSIVO:** {link_afiliado}"
