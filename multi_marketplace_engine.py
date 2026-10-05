"""Mineração unificada de produtos reais nos marketplaces suportados pelo Nexus.

Mercado Livre usa o motor autenticado/API já existente. Shopee e Amazon usam
suas páginas públicas de busca como fallback, sem fabricar links ou imagens.
Integrações oficiais de afiliados continuam sendo usadas apenas para o link de
publicação, nunca para inventar um produto.
"""
from __future__ import annotations

import json
from typing import Any, Iterator
from urllib.parse import parse_qs, quote_plus, unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from real_marketplace_engine import obter_produto_real_validado

TIMEOUT = 15
MARKETPLACES = ("Mercado Livre", "Shopee", "Amazon")
SEARCH_URLS = {
    "Shopee": "https://shopee.com.br/search?keyword={query}",
    "Amazon": "https://www.amazon.com.br/s?k={query}",
}
PRODUCT_HOSTS = {
    "Shopee": ("shopee.com.br", "shopee.co.th", "susercontent.com"),
    "Amazon": ("amazon.com.br", "amazon.com"),
}
IMAGE_HOSTS = {
    "Shopee": ("shopee.com.br", "susercontent.com", "shopeeimg.com"),
    "Amazon": ("amazon.com.br", "amazon.com", "ssl-images-amazon.com", "media-amazon.com"),
}


class MarketplaceMiningError(RuntimeError):
    """Busca bloqueada, indisponível ou sem anúncio/imagem verificáveis."""


def _host_matches(hostname: str, allowed: tuple[str, ...]) -> bool:
    host = hostname.lower().split(":", 1)[0].rstrip(".")
    return any(host == value or host.endswith("." + value) for value in allowed)


def _url(value: Any, marketplace: str, *, image: bool = False) -> str:
    raw = unquote(str(value or "").strip())
    if not raw or raw.startswith(("javascript:", "#", "data:")):
        return ""
    if raw.startswith("//"):
        raw = "https:" + raw
    parsed = urlparse(urljoin("https://www." + ("amazon.com.br" if marketplace == "Amazon" else "shopee.com.br"), raw))
    allowed = IMAGE_HOSTS[marketplace] if image else PRODUCT_HOSTS[marketplace]
    if parsed.scheme not in {"http", "https"} or not _host_matches(parsed.hostname or "", allowed):
        return ""
    return parsed.geturl()


def _walk_json(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_json(child)


def _json_results(soup: BeautifulSoup, marketplace: str, limit: int) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    for script in soup.find_all("script"):
        raw = script.string or script.get_text()
        if not raw or len(raw) > 5_000_000:
            continue
        raw = raw.strip()
        if script.get("type") != "application/ld+json" and not raw.startswith(("{", "[")):
            continue
        try:
            payload = json.loads(raw)
        except (TypeError, ValueError):
            continue
        for item in _walk_json(payload):
            title = str(item.get("name") or item.get("title") or "").strip()
            product_url = _url(item.get("url") or item.get("permalink"), marketplace)
            image = item.get("image")
            if isinstance(image, list):
                image = image[0] if image else ""
            image_url = _url(image, marketplace, image=True)
            if len(title) >= 8 and product_url and image_url and product_url not in seen:
                seen.add(product_url)
                results.append({"id": item.get("sku") or item.get("asin"), "title": title[:180], "permalink": product_url, "image_url": image_url, "price": None})
                if len(results) >= limit:
                    return results
    return results


def _card_results(soup: BeautifulSoup, marketplace: str, limit: int, existing: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = list(existing)
    seen = {item["permalink"] for item in results}
    for anchor in soup.find_all("a", href=True):
        href = str(anchor.get("href") or "")
        parsed = urlparse(href)
        destination = unquote(parse_qs(parsed.query).get("url", parse_qs(parsed.query).get("urldest", [href]))[0])
        product_url = _url(destination, marketplace)
        if not product_url:
            continue
        if marketplace == "Amazon" and not any(part in product_url for part in ("/dp/", "/gp/product/", "/gp/aw/d/")):
            continue
        container = anchor
        for _ in range(6):
            if container.parent is None:
                break
            container = container.parent
            if container.find("img"):
                break
        image = container.find("img") if container else None
        title = anchor.get_text(" ", strip=True) or str(anchor.get("aria-label") or "").strip()
        if image and len(title) < 8:
            title = str(image.get("alt") or "").strip()
        image_url = ""
        if image:
            for attr in ("src", "data-src", "data-lazy-src", "data-a-dynamic-image"):
                value = image.get(attr)
                if isinstance(value, str) and value.strip().startswith("{"):
                    try:
                        value = next(iter(json.loads(value)))
                    except (TypeError, ValueError, StopIteration):
                        value = ""
                image_url = str(value or "").strip()
                if image_url:
                    break
            if not image_url:
                srcset = str(image.get("srcset") or "").strip()
                image_url = srcset.split(",")[0].strip().split(" ")[0] if srcset else ""
        image_url = _url(image_url, marketplace, image=True)
        if len(title) >= 8 and image_url and product_url not in seen:
            seen.add(product_url)
            results.append({"id": None, "title": title[:180], "permalink": product_url, "image_url": image_url, "price": None})
        if len(results) >= limit:
            break
    return results[:limit]


def buscar_produtos_marketplace_web(marketplace: str, query: str, limit: int = 8) -> list[dict[str, Any]]:
    if marketplace not in SEARCH_URLS:
        raise ValueError(f"Marketplace não suportado: {marketplace}")
    response = requests.get(
        SEARCH_URLS[marketplace].format(query=quote_plus(query)),
        headers={"User-Agent": "Mozilla/5.0 (compatible; NexusBot/3.0)", "Accept-Language": "pt-BR,pt;q=0.9"},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return _card_results(soup, marketplace, limit, _json_results(soup, marketplace, limit))


def _normalise(item: dict[str, Any], marketplace: str, query: str) -> dict[str, Any]:
    title = str(item.get("title") or "").strip()
    permalink = str(item.get("permalink") or "").strip()
    image_url = str(item.get("image_url") or "").strip()
    if not title or not permalink or not image_url:
        raise MarketplaceMiningError(f"{marketplace} devolveu um resultado sem produto, link ou imagem pública.")
    return {
        "produto": title, "product_name": title,
        "dificuldade": f"Encontrar uma solução melhor para {title.lower()}",
        "dor": f"Encontrar uma solução melhor para {title.lower()}",
        "link_ml": permalink, "product_source_url": permalink,
        "official_affiliate_url": None, "affiliate_url": None,
        "imagem": image_url, "image_url": image_url, "image_verified": True,
        "image_source": f"{marketplace} · imagem associada ao mesmo anúncio",
        "marketplace": marketplace, "nicho": f"{marketplace} · descoberta por pesquisa",
        "price": item.get("price"), "product_external_id": item.get("id"), "query": query,
        "source": f"{marketplace.lower().replace(' ', '_')}_public_web",
        "copy": None, "video_demo": None,
    }


def obter_produto_marketplace(marketplace: str, query: str | None = None, provedor: str = "openai") -> dict[str, Any]:
    """Retorna um anúncio real validado para qualquer marketplace suportado."""
    if marketplace == "Mercado Livre":
        product = obter_produto_real_validado(provedor, query=query)
        product["marketplace"] = marketplace
        return product
    search = (query or "produtos úteis para casa").strip()
    try:
        results = buscar_produtos_marketplace_web(marketplace, search, limit=8)
    except Exception as exc:
        raise MarketplaceMiningError(f"{marketplace} indisponível para busca pública: {exc}") from exc
    if not results:
        raise MarketplaceMiningError(f"{marketplace} não devolveu anúncio com imagem pública para '{search}'. Configure o link oficial ou faça upload da imagem real.")
    return _normalise(results[0], marketplace, search)


def buscar_produtos_marketplace(marketplace: str, query: str, limit: int = 8) -> list[dict[str, Any]]:
    if marketplace == "Mercado Livre":
        from real_marketplace_engine import buscar_produtos_mercado_livre, buscar_produtos_mercado_livre_web
        try:
            results = buscar_produtos_mercado_livre(query, limit=limit)
        except Exception:
            results = []
        if not results:
            results = buscar_produtos_mercado_livre_web(query, limit=limit)
        return [{**item, "marketplace": marketplace} for item in results]
    return buscar_produtos_marketplace_web(marketplace, query, limit)


__all__ = ["MARKETPLACES", "MarketplaceMiningError", "buscar_produtos_marketplace", "buscar_produtos_marketplace_web", "obter_produto_marketplace"]
