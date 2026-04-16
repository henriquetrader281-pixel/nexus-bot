import streamlit as st
import re

def gerar_prompt_aida(produto, estilo="agressivo"):
    """
    Gera o prompt de vendas com Gatilhos Mentais de Elite para o Gemini Pro.
    """
    contextos = {
        "agressivo": "Foque no CONTRASTE: Problema terrível vs. Solução mágica. Use gatilhos de Escassez e Urgência. Frases curtas e ordens diretas.",
        "curioso": "Gatilho da Antecipação. Comece com 'Você não vai acreditar...' ou 'Isso deveria ser proibido'. Mantenha o mistério.",
        "prático": "Gatilho da Facilidade. Foque em 'Sem esforço', 'Em segundos' e 'Economia de tempo'.",
        "autoridade": "Gatilho da Exclusividade. Aja como um especialista que descobriu o segredo dos influencers."
    }

    diretriz = contextos.get(estilo, contextos["agressivo"])

    # PROMPT ENCOSTADO NA ESQUERDA PARA EVITAR BUG DE INDENTAÇÃO NA IA
    prompt = f"""Aja como um Copywriter de Elite especialista em Reels e TikTok Brasil.
Sua missão é criar 3 roteiros virais para o produto: {produto}

REGRAS DE OURO:
1. ESTRUTURA AIDA: Atenção (Hook), Interesse (Problema), Desejo (Solução), Ação (CTA).
2. ESTILO: {diretriz}
3. GANCHO EXPLOSIVO: Os primeiros 3 segundos devem impedir o scroll.
4. CTA OBRIGATÓRIA: Force o usuário a comentar "EU QUERO" para receber o link.
5. FORMATAÇÃO: Use emojis e linguagem de rede social (POV, Trend, Viral).

Separe as 3 variações APENAS pelo marcador: ###
Não escreva introduções. Comece direto no Hook."""
    
    return prompt

def limpar_copy(texto):
    """
    Remove rótulos técnicos (Hook, CTA, etc) para a copy ficar pronta para postar.
    """
    if not texto: return ""
    
    # Lista de palavras que a IA adora usar mas que não queremos na copy final
    lixo = ["aqui está", "com certeza", "claro", "segue a copy", "entendido", "variação", "copywriter", "olá", "claro!"]
    
    linhas = texto.split('\n')
    linhas_limpas = []
    
    for linha in linhas:
        l_low = linha.strip().lower()
        if l_low and not any(l_low.startswith(p) for p in lixo):
            # Remove rótulos como "Hook:", "CTA:", "Atenção:", "Variação 1:"
            limpa = re.sub(r'^(atenção|interesse|desejo|ação|hook|gancho|cta|copy \d+|variação \d+):', '', linha, flags=re.IGNORECASE).strip()
            if limpa:
                linhas_limpas.append(limpa)
    
    return "\n".join(linhas_limpas).strip()
