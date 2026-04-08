import streamlit as st

def gerar_prompt_aida(produto, estilo="agressivo"):
    """
    Função mestra para gerar o prompt de vendas.
    """
    contexto = {
        "agressivo": "Foque na dor do cliente e na solução imediata. Use frases curtas e impacto visual.",
        "curioso": "Crie um mistério sobre o produto. Force o clique.",
        "prático": "Foque na facilidade de uso e economia de tempo.",
        "autoridade": "Aja como um especialista recomendando o melhor custo-benefício."
    }

    diretriz = contexto.get(estilo, contexto["agressivo"])

    prompt = f"""
    Aja como um Copywriter de Elite especialista em Reels e TikTok.
    Produto: {produto}
    
    REGRAS DE OURO:
    1. Estrutura AIDA (Atenção, Interesse, Desejo, Ação).
    2. {diretriz}
    3. Use emojis estratégicos.
    4. Proibido ficha técnica chata. Fale de BENEFÍCIOS.
    5. CTA OBRIGATÓRIA: Estimule o comentário "EU QUERO".
    
    Crie 5 variações únicas e separe cada uma APENAS pelo marcador: ###
    """
    return prompt

def limpar_copy(texto):
    """
    Remove saudações inúteis da IA.
    """
    if not texto:
        return ""
    
    proibidas = ["Aqui está", "Com certeza", "Claro", "Segue a copy", "Entendido", "Variação"]
    linhas = texto.split('\n')
    linhas_limpas = [l for l in linhas if not any(l.strip().lower().startswith(p.lower()) for p in proibidas)]
    
    resultado = "\n".join(linhas_limpas).strip()
    return resultado if len(resultado) > 10 else texto.strip()
