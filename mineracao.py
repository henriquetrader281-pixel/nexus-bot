def minerar_produtos(nicho, mkt_alvo, motor_ia):
    """
    Função atualizada para aceitar os 3 parâmetros vindos do app.py
    """
    # Aqui vai o seu código de mineração...
    # Exemplo de retorno para não travar o app:
    return [f"Produto Viral 1 para {nicho}", f"Produto Viral 2 em {mkt_alvo}"]
    def formatar_saida_limpa(texto_bruto):
    """
    Remove ruídos da IA (como asteriscos, frases de introdução) 
    para que o Scanner consiga ler os dados corretamente.
    """
    if not texto_bruto:
        return ""
    
    # Remove negritos e textos comuns que a IA coloca e que quebram o código
    limpo = texto_bruto.replace("**", "").replace("Aqui está a lista:", "").strip()
    
    # Se a IA colocar introduções antes da lista, tentamos limpar
    if "NOME:" in limpo:
        pos = limpo.find("NOME:")
        limpo = limpo[pos:]
        
    return limpo
