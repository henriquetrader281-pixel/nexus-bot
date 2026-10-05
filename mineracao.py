"""Scanner de oportunidades baseado em anúncios reais dos marketplaces."""
from __future__ import annotations

import re

from multi_marketplace_engine import buscar_produtos_marketplace


def minerar_produtos(prompt: str, marketplace: str, _motor_ia=None) -> str:
    """Busca anúncios reais e retorna o formato textual legado do Scanner.

    O parâmetro ``_motor_ia`` permanece por compatibilidade com chamadas antigas,
    mas não é usado para fabricar produto, preço, link ou imagem.
    """
    match = re.search(
        r"produtos\s+promissores\s+de\s+(.+?)\s+no\s+(Mercado Livre|Shopee|Amazon)",
        prompt or "",
        flags=re.IGNORECASE,
    )
    query = (match.group(1) if match else prompt or "produtos úteis para casa").strip()
    try:
        results = buscar_produtos_marketplace(marketplace, query, limit=5)
    except Exception as exc:
        return f"Erro: {marketplace} indisponível para mineração real: {exc}"
    if not results:
        return f"Erro: {marketplace} não devolveu anúncios reais com imagem pública para '{query}'."
    lines = []
    for item in results:
        price = f"R$ {item['price']}" if item.get("price") is not None else "não informado"
        lines.append(
            f"NOME: {item.get('title', 'Produto')} | VALOR: {price} | "
            f"URL: {item.get('permalink', '')} | IMAGEM: {item.get('image_url', '')}"
        )
    return "\n".join(lines)
