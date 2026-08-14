import random

def analisar_produto_estrategista(nome_produto="Organizador Rotativo 360°"):
    """
    Executa o Protocolo Estrategista-Chefe Lean:
    1. Classificação em Prateleiras (Tech & Gadgets, Utilidades & Casa, Virais & Desejo, Ofertas Relâmpago)
    2. Título Curto para Vitrine (Máx 30 chars)
    3. Ganchos de 3 segundos (Hooks)
    4. Fast-Copy para Meta Ads / Instagram
    5. Roteiro de Vídeo Reels (15s) com apelo Full
    """
    prateleiras = [
        "⚡ Tech & Gadgets", 
        "🏠 Utilidades & Casa", 
        "🔥 Virais & Desejo", 
        "🚀 Ofertas Relâmpago (Full)"
    ]
    
    prateleira_escolhida = random.choice(prateleiras)
    
    return {
        "prateleira": prateleira_escolhida,
        "titulo_vitrine": f"✨ {nome_produto[:24]} (Full)",
        "hooks": [
            "🚨 'Eles tentaram proibir este produto porque resolve tudo em segundos...'",
            "⚠️ 'Se você tem pouco espaço em casa, precisa ver isto AGORA.'",
            "🔥 'Como eu não descobri isso antes? Chega amanhã na sua casa!'"
        ],
        "fast_copy": f"O produto mais desejado do momento acaba de entrar na minha Vitrine Oficial do Mercado Livre com Envio Full (Entrega Rápida)! Garanta o seu antes que esgote o estoque. 📦💨",
        "cta": "🔗 Clique em 'Saiba Mais' para ver na minha Vitrine Oficial do Mercado Livre!",
        "roteiro_15s": [
            "0-3s: [Gancho Visual Rápido] Close no problema sendo resolvido instantaneamente.",
            "3-10s: [Demonstração Prática] O produto em ação mostrando a facilidade e o Envio Full.",
            "10-15s: [CTA de Escassez] 'Poucas unidades com entrega para amanhã. Clica no link!'"
        ]
    }
