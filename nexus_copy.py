def limpar_copy(texto):
    """Remove saudações, mas garante que o conteúdo principal fique."""
    if not texto:
        return ""
    
    # Lista de frases que a IA costuma usar e queremos apagar
    proibidas = ["Aqui está", "Com certeza", "Claro", "Segue a copy", "Variação", "Entendido"]
    
    linhas = texto.split('\n')
    # Só mantém a linha se ela NÃO começar com uma das frases proibidas
    linhas_limpas = []
    for l in linhas:
        if not any(l.strip().lower().startswith(p.lower()) for p in proibidas):
            linhas_limpas.append(l)
    
    resultado = "\n".join(linhas_limpas).strip()
    
    # Se a limpeza apagar TUDO por erro, devolve o texto original
    return resultado if len(resultado) > 10 else texto.strip()
