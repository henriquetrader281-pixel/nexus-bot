# --- DENTRO DO BOTAO GERAR LEGENDA ---
with st.spinner("Limpando ruído e gerando copy de impacto..."):
    # Isolamos apenas o nome essencial para não confundir a IA com números
    produto_limpo = st.session_state.sel_nome.split('|')[0].replace("NOME:", "").strip()

    # PROMPT DE CHOQUE: Força a IA a sair do modo "lista"
    prompt_blindado = f"""
    [RESET DE CONTEXTO]: Ignore qualquer lista de 30 produtos citada anteriormente.
    
    VOCÊ É: Um Diretor de Edição de Vídeos Virais.
    PRODUTO ÚNICO: {produto_limpo}

    TAREFA: Escreva uma copy curta seguindo o método AIDA.
    
    REGRAS DE OURO:
    - NÃO mencione outros produtos. 
    - NÃO repita 'Calor', 'Ticket' ou 'Valor'.
    - Saída direta, sem introduções como "Aqui está sua legenda".
    - Estilo: Rápido, visual e persuasivo.

    FORMATO:
    🚨 [ATENÇÃO]: (Hook que para o scroll)
    💡 [INTERESSE]: (O problema que resolve)
    ✨ [DESEJO]: (O benefício satisfatório)
    🛒 [AÇÃO]: (Chamada para o link abaixo)
    """

    # Chama a IA
    resposta_ia = miny.minerar_produtos(prompt_blindado, "Shopee", motor_ia)
    
    # --- LIMPEZA DE SEGURANÇA (Caso a IA teime em mandar lixo) ---
    # Se a resposta contiver o número '1.' ou '30', nós filtramos para pegar só o AIDA
    if "1." in resposta_ia and "🚨" in resposta_ia:
        resposta_ia = resposta_ia.split("🚨")[1]
        resposta_ia = "🚨 " + resposta_ia

    # Blindagem do Link (ID: 18316451024)
    link_raw = st.session_state.get('sel_link', 'https://shopee.com.br')
    # Remove qualquer parâmetro antigo ou erro de duplicidade
    link_base = link_raw.split('?')[0].split('|')[0].replace("https://shopee.com.br/https", "https://shopee.com.br").strip()
    
    # Link final cravado com seu rastreio
    link_afiliado = f"{link_base}?smtt=18316451024"

    st.session_state.copy_final_pronta = f"{resposta_ia.strip()}\n\n🔗 **LINK EXCLUSIVO:** {link_afiliado}"
