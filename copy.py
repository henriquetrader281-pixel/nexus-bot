import streamlit as st

def gerar_prompt_aida(produto, estilo="agressivo"):
    """
    Centraliza a inteligência de vendas do Nexus.
    Estilos: agressivo, curioso, prático, autoridade.
    """
    
    contexto = {
        "agressivo": "Foque na dor do cliente e na solução imediata. Use frases curtas e impacto visual.",
        "curioso": "Crie um mistério sobre o produto. Não revele tudo de cara, force o clique.",
        "prático": "Foque na facilidade de uso e como o produto economiza tempo no dia a dia.",
        "autoridade": "Aja como um especialista recomendando o melhor custo-benefício do mercado."
    }

    diretriz = contexto.get(estilo, contexto["agressivo"])

    prompt = f"""
    Aja como um Copywriter de Elite especialista em Reels e TikTok.
    Produto: {produto}
    
    REGRAS DE OURO:
    1. Estrutura AIDA (Atenção, Interesse, Desejo, Ação).
    2. {diretriz}
    3. Use emojis estratégicos (🚨, 💡, ✨, 🛒).
    4. Proibido ficha técnica chata. Fale de BENEFÍCIOS.
    5. CTA OBRIGATÓRIA: Estimule o comentário "EU QUERO" ou "LINK".
    
    Crie 5 variações únicas e separe cada uma APENAS pelo marcador: ###
    """
    return prompt

def limpar_copy(texto):
    """Remove lixo da IA como 'Aqui estão as cópias'."""
    lixo = ["Aqui está", "Com certeza", "Claro", "Segue a copy", "Variação"]
    linhas = texto.split('\n')
    linhas_limpas = [l for l in linhas if not any(palavra in l for palavra in lixo)]
    return "\n".join(linhas_limpas).strip()
