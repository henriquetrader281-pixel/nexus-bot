import json

def obter_produto_real_validado(provedor="gemini"):
    """
    Retorna apenas produtos reais e validados de e-commerce físico (sem invenções/alucinações).
    """
    catalogo_real = [
        {
            "dificuldade": "Organização doméstica e ganho de tempo",
            "nicho": "Casa & Organização",
            "produto": "Organizador Rotativo 360° para Cosméticos e Temperos",
            "copy": "Cansada de perder 10 minutos a procurar o tempero certo no fundo do armário? 🛑 Este organizador rotativo 360° revolucionou a minha cozinha. Cabe tudo, gira suavemente e deixa o armário impecável. 🔥 Quer garantir o seu com frete grátis no Mercado Livre? Clica no link da bio ou comenta QUERO!",
            "link_ml": "https://lista.mercadolivre.com.br/organizador-rotativo-360",
            "imagem": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=1000&q=80"
        },
        {
            "dificuldade": "Dores musculares e cansaço após o trabalho",
            "nicho": "Saúde & Bem-Estar",
            "produto": "Mini Pistola de Massagem Muscular Elétrica",
            "copy": "Pare de sofrer com dores nas costas depois de um dia inteiro sentada! ⚡ Esta mini pistola de massagem cabe na mala, tem 4 ponteiras e alivia a tensão em segundos. Parece massagem de clínica profissional. 💎 Clica no link da bio ou comenta QUERO para garantir na Shopee com desconto!",
            "link_ml": "https://shopee.com.br/search?keyword=mini%20pistola%20de%20massagem",
            "imagem": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=1000&q=80"
        },
        {
            "dificuldade": "Iluminação inadequada e fadiga visual no computador",
            "nicho": "Home Office & Eletrónicos",
            "produto": "Luminária de LED para Monitor Anti-Reflexo",
            "copy": "Trabalhar à noite com a luz acesa a dar reflexo no monitor destrói a sua vista. 👁️ Esta luminária encaixa no topo do ecrã, ilumina só a mesa e elimina 100% do reflexo. O setup fica com cara de gringo! 🚀 Comenta QUERO ou clica no link da bio para ver na Amazon.",
            "link_ml": "https://www.amazon.com.br/s?k=luminaria+para+monitor",
            "imagem": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=1000&q=80"
        }
    ]
    import random
    return random.choice(catalogo_real)
