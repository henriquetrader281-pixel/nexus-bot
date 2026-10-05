"""Descoberta de anúncios reais do Mercado Livre para as campanhas do Nexus.

A API é a fonte preferencial. Quando ela está indisponível, a listagem pública é
lida por múltiplos formatos que o Mercado Livre já utilizou (cards HTML, JSON
embutido e JSON-LD). Em todos os casos o produto só passa se tiver título, URL
do anúncio e imagem pública associados ao mesmo resultado.
"""
from __future__ import annotations

import json
import os
from typing import Any, Iterator
from urllib.parse import parse_qs, quote_plus, unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

try:
    import streamlit as st
except Exception:  # pragma: no cover
    st = None

SEARCH_URL = "https://api.mercadolibre.com/sites/MLB/search"
LIST_URL = "https://lista.mercadolivre.com.br/{query}"
TIMEOUT = 15
PUBLIC_HOSTS = ("mercadolivre.com.br", "mercadolivre.com", "mercadolibre.com")
IMAGE_HOST_HINTS = ("mlstatic.com", "mercadolibre.com", "mercadolivre.com")


def _host_matches(hostname: str, allowed: tuple[str, ...]) -> bool:
    host = hostname.lower().split(":", 1)[0].rstrip(".")
    return any(host == value or host.endswith("." + value) for value in allowed)


class MarketplaceAccessError(RuntimeError):
    def __init__(self, status_code: int, message: str = "A API do Mercado Livre bloqueou a pesquisa") -> None:
        self.status_code = status_code
        super().__init__(f"{message} (HTTP {status_code}).")


def _session_get(key: str, default: Any = None) -> Any:
    if st is not None:
        try:
            value = st.session_state.get(key)
            if value not in (None, "", []):
                return value
            value = st.secrets.get(key)
            if value not in (None, "", []):
                return value
        except Exception:
            pass
    return os.environ.get(key, default)


def _candidate_queries(query: str | None = None) -> list[str]:
    candidates: list[str] = []
    for value in (query, _session_get("NEXUS_ML_SEARCH_QUERY"), _session_get("nexus_mining_query"), _session_get("trend_term")):
        if isinstance(value, str) and value.strip():
            candidates.append(value.strip())
    trends = _session_get("real_trends", [])
    if isinstance(trends, (list, tuple)):
        candidates.extend(str(item).strip() for item in trends[:5] if str(item).strip())
    candidates.append("produtos úteis para casa")
    return list(dict.fromkeys(candidates))


def _public_url(value: Any, base: str = "https://www.mercadolivre.com.br/") -> str:
    raw = unquote(str(value or "").strip())
    if not raw or raw.startswith(("javascript:", "#", "data:")):
        return ""
    parsed = urlparse(raw)
    if not parsed.scheme:
        raw = urljoin(base, raw)
        parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not _host_matches(parsed.hostname or "", PUBLIC_HOSTS):
        return ""
    return raw


def _image_url(item: dict[str, Any]) -> str:
    """Aceita o campo de imagem de várias versões do payload do ML."""
    pictures = item.get("pictures") or item.get("images") or []
    values: list[Any] = [item.get("secure_thumbnail"), item.get("thumbnail"), item.get("image_url"), item.get("image")]
    if isinstance(pictures, list):
        for picture in pictures:
            if isinstance(picture, dict):
                values.extend((picture.get("secure_url"), picture.get("url"), picture.get("source"), picture.get("src")))
            else:
                values.append(picture)
    for value in values:
        url = str(value or "").strip()
        if url.startswith("//"):
            url = "https:" + url
        parsed = urlparse(url)
        if parsed.scheme in {"http", "https"} and _host_matches(parsed.hostname or "", IMAGE_HOST_HINTS):
            return url
    return ""


def _api_item(item: dict[str, Any]) -> dict[str, Any] | None:
    title = str(item.get("title") or "").strip()
    permalink = _public_url(item.get("permalink"))
    image_url = _image_url(item)
    if not title or not permalink or not image_url:
        return None
    return {
        "id": item.get("id"), "title": title, "permalink": permalink,
        "image_url": image_url, "price": item.get("price"),
        "condition": item.get("condition"), "sold_quantity": item.get("sold_quantity"),
        "available_quantity": item.get("available_quantity"),
    }


def buscar_produtos_mercado_livre(query: str, limit: int = 8) -> list[dict[str, Any]]:
    base_headers = {"User-Agent": "NexusBot-AutonomousMiner/3.0", "Accept": "application/json"}
    token = _session_get("ML_ACCESS_TOKEN") or _session_get("ML_API_ACCESS_TOKEN")
    headers = {**base_headers, **({"Authorization": f"Bearer {token}"} if token else {})}
    response = requests.get(SEARCH_URL, params={"q": query, "limit": limit}, headers=headers, timeout=TIMEOUT)
    # Um token antigo/inválido não deve impedir a tentativa pública. Só falha
    # definitivamente depois de uma segunda chamada sem Authorization.
    if response.status_code in {401, 403} and token:
        response = requests.get(SEARCH_URL, params={"q": query, "limit": limit}, headers=base_headers, timeout=TIMEOUT)
    if response.status_code in {401, 403}:
        raise MarketplaceAccessError(response.status_code)
    response.raise_for_status()
    payload = response.json()
    return [normalised for item in payload.get("results", []) if isinstance(item, dict) and (normalised := _api_item(item))]


def _walk_json(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_json(child)


def _structured_web_results(soup: BeautifulSoup, limit: int) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    seen: set[str] = set()
    scripts = soup.find_all("script")
    for script in scripts:
        raw = script.string or script.get_text()
        if not raw or len(raw) > 5_000_000:
            continue
        raw = raw.strip()
        if script.get("type") == "application/ld+json" or raw.startswith(("{", "[")):
            try:
                data = json.loads(raw)
            except (ValueError, TypeError):
                continue
            for item in _walk_json(data):
                title = str(item.get("title") or item.get("name") or "").strip()
                url = _public_url(item.get("permalink") or item.get("url"))
                image = item.get("image")
                if isinstance(image, list):
                    image = image[0] if image else ""
                image_url = str(image or item.get("secure_thumbnail") or item.get("thumbnail") or "").strip()
                if image_url.startswith("//"):
                    image_url = "https:" + image_url
                if len(title) >= 8 and url and _host_matches(urlparse(image_url).hostname or "", IMAGE_HOST_HINTS) and url not in seen:
                    seen.add(url)
                    found.append({"id": item.get("id"), "title": title[:180], "permalink": url, "image_url": image_url, "price": item.get("price")})
                    if len(found) >= limit:
                        return found
    return found


def buscar_produtos_mercado_livre_web(query: str, limit: int = 8) -> list[dict[str, Any]]:
    response = requests.get(
        LIST_URL.format(query=quote_plus(query)),
        headers={"User-Agent": "Mozilla/5.0 (compatible; NexusBot/3.0)", "Accept-Language": "pt-BR,pt;q=0.9"},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    structured = _structured_web_results(soup, limit)
    results: list[dict[str, Any]] = list(structured)
    seen = {item["permalink"] for item in results}
    # Compatibilidade com cards antigos e atuais (poly-card/item__info).
    for anchor in soup.find_all("a", href=True):
        destination_raw = str(anchor.get("href") or "")
        parsed = urlparse(destination_raw)
        destination = _public_url(parse_qs(parsed.query).get("urldest", [destination_raw])[0])
        if not destination or any(token in destination for token in ("lista.mercadolivre", "registration", "login", "privacidade", "account-verification")):
            continue
        container = anchor
        for _ in range(6):
            if container.parent is None:
                break
            container = container.parent
            if container.find("img"):
                break
        image = container.find("img") if container else None
        title = anchor.get_text(" ", strip=True) or (image.get("alt", "").strip() if image else "")
        if len(title) < 8:
            title = str(anchor.get("aria-label") or "").strip()
        image_url = ""
        if image:
            for attr in ("src", "data-src", "data-lazy-src", "data-zoom", "data-image"):
                image_url = str(image.get(attr) or "").strip()
                if image_url:
                    break
            if not image_url:
                srcset = str(image.get("srcset") or "").strip()
                image_url = srcset.split(",")[0].strip().split(" ")[0] if srcset else ""
        if image_url.startswith("//"):
            image_url = "https:" + image_url
        if len(title) >= 8 and _host_matches(urlparse(image_url).hostname or "", IMAGE_HOST_HINTS) and destination not in seen:
            seen.add(destination)
            results.append({"id": None, "title": title[:180], "permalink": destination, "image_url": image_url, "price": None})
        if len(results) >= limit:
            break
    return results[:limit]


def _normalise_result(item: dict[str, Any], query: str) -> dict[str, Any]:
    title, permalink, image_url = item["title"], item["permalink"], item["image_url"]
    return {
        "produto": title, "product_name": title,
        "dificuldade": f"Encontrar uma solução melhor para {title.lower()}",
        "dor": f"Encontrar uma solução melhor para {title.lower()}",
        "link_ml": permalink, "product_source_url": permalink,
        "official_affiliate_url": None, "affiliate_url": None,
        "imagem": image_url, "image_url": image_url, "image_verified": True,
        "image_source": "Mercado Livre · imagem associada ao mesmo anúncio",
        "marketplace": "Mercado Livre", "nicho": "Mercado Livre · descoberta por pesquisa",
        "price": item.get("price"), "product_external_id": item.get("id"), "query": query,
        "source": "mercado_livre_public_api" if item.get("id") else "mercado_livre_public_web",
        "copy": None, "video_demo": None,
    }


def obter_produto_real_validado(provedor: str = "openai", query: str | None = None) -> dict[str, Any]:
    errors: list[str] = []
    api_blocked = False
    for candidate in _candidate_queries(query):
        if not api_blocked:
            try:
                results = buscar_produtos_mercado_livre(candidate, limit=8)
                if results:
                    return _normalise_result(results[0], candidate)
                errors.append(f"{candidate}: API sem resultado utilizável")
            except MarketplaceAccessError as exc:
                api_blocked = True
                errors.append(f"{candidate}: API bloqueada — {exc}")
            except Exception as exc:
                errors.append(f"{candidate}: API {exc}")
        try:
            web_results = buscar_produtos_mercado_livre_web(candidate, limit=8)
            if web_results:
                return _normalise_result(web_results[0], candidate)
            errors.append(f"{candidate}: web sem anúncios com imagem")
        except Exception as exc:
            errors.append(f"{candidate}: web {exc}")
    details = " | ".join(errors[-5:])
    if api_blocked:
        details += " | API bloqueada: configure ML_ACCESS_TOKEN/ML_API_ACCESS_TOKEN ou use busca manual/link oficial/upload."
    raise RuntimeError("Mercado Livre não devolveu um produto com imagem pública. " + details)


__all__ = ["MarketplaceAccessError", "buscar_produtos_mercado_livre", "buscar_produtos_mercado_livre_web", "obter_produto_real_validado"]
