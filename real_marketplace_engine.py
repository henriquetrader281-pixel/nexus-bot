"""Mineração real de produtos no Mercado Livre para o ciclo autónomo.

A API pública de pesquisa é usada apenas para descoberta. O ``permalink`` é a
origem do produto e a ``thumbnail`` é a imagem de referência do mesmo resultado.
Nenhum link de afiliado é fabricado: para publicar, a campanha ainda precisa do
URL emitido pelo Portal do Afiliado.
"""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import requests
from bs4 import BeautifulSoup

try:
    import streamlit as st
except Exception:  # pragma: no cover - permite executar o motor fora do Streamlit
    st = None


SEARCH_URL = "https://api.mercadolibre.com/sites/MLB/search"
LIST_URL = "https://lista.mercadolivre.com.br/{query}"
TIMEOUT = 15


class MarketplaceAccessError(RuntimeError):
    """Indica que a busca do marketplace exige autenticação ou foi bloqueada."""

    def __init__(self, status_code: int, message: str = "A API do Mercado Livre bloqueou a pesquisa") -> None:
        self.status_code = status_code
        super().__init__(f"{message} (HTTP {status_code}).")


def _session_get(key: str, default: Any = None) -> Any:
    if st is not None:
        try:
            value = st.session_state.get(key)
            if value not in (None, "", []):
                return value
            secrets = st.secrets
            value = secrets.get(key)
            if value not in (None, "", []):
                return value
        except Exception:
            pass
    return os.environ.get(key, default)


def _candidate_queries(query: str | None = None) -> list[str]:
    candidates: list[str] = []
    for value in (
        query,
        _session_get("NEXUS_ML_SEARCH_QUERY"),
        _session_get("nexus_mining_query"),
        _session_get("trend_term"),
    ):
        if isinstance(value, str) and value.strip():
            candidates.append(value.strip())
    trends = _session_get("real_trends", [])
    if isinstance(trends, (list, tuple)):
        candidates.extend(str(item).strip() for item in trends[:5] if str(item).strip())
    # Categoria de contingência, não produto pré-selecionado: o resultado final
    # continua vindo da API e precisa conter permalink e imagem do mesmo anúncio.
    candidates.append("produtos úteis para casa")
    return list(dict.fromkeys(candidates))


def buscar_produtos_mercado_livre(query: str, limit: int = 8) -> list[dict[str, Any]]:
    headers = {"User-Agent": "NexusBot-AutonomousMiner/2.0", "Accept": "application/json"}
    access_token = _session_get("ML_ACCESS_TOKEN") or _session_get("ML_API_ACCESS_TOKEN")
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    response = requests.get(
        SEARCH_URL,
        params={"q": query, "limit": limit},
        headers=headers,
        timeout=TIMEOUT,
    )
    if response.status_code in {401, 403}:
        raise MarketplaceAccessError(response.status_code)
    response.raise_for_status()
    payload = response.json()
    results: list[dict[str, Any]] = []
    for item in payload.get("results", []):
        title = str(item.get("title") or "").strip()
        permalink = str(item.get("permalink") or "").strip()
        image_url = str(item.get("secure_thumbnail") or item.get("thumbnail") or "").strip()
        if not title or not permalink or not image_url:
            continue
        results.append({
            "id": item.get("id"),
            "title": title,
            "permalink": permalink,
            "image_url": image_url,
            "price": item.get("price"),
            "condition": item.get("condition"),
            "sold_quantity": item.get("sold_quantity"),
            "available_quantity": item.get("available_quantity"),
        })
    return results


def buscar_produtos_mercado_livre_web(query: str, limit: int = 8) -> list[dict[str, Any]]:
    """Fallback para a listagem web quando a rota API estiver bloqueada."""
    response = requests.get(
        LIST_URL.format(query=quote_plus(query)),
        headers={"User-Agent": "Mozilla/5.0 (compatible; NexusBot/2.0)", "Accept-Language": "pt-BR,pt;q=0.9"},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        href = str(anchor.get("href") or "")
        parsed = urlparse(href)
        destination = unquote(parse_qs(parsed.query).get("urldest", [href])[0])
        if "mercadolivre.com.br" not in destination or any(token in destination for token in ("lista.mercadolivre", "registration", "login", "privacidade")):
            continue
        container = anchor
        for _ in range(4):
            if container.parent is None:
                break
            container = container.parent
            if container.find("img"):
                break
        image = container.find("img") if container else None
        title = anchor.get_text(" ", strip=True) or (image.get("alt", "").strip() if image else "")
        if len(title) < 12:
            continue
        image_url = ""
        if image:
            image_url = str(image.get("src") or image.get("data-src") or image.get("data-lazy-src") or "").strip()
            if not image_url:
                srcset = str(image.get("srcset") or "").strip()
                image_url = srcset.split(",")[0].strip().split(" ")[0] if srcset else ""
        key = destination or title
        if image_url and key not in seen:
            seen.add(key)
            results.append({"id": None, "title": title[:180], "permalink": destination, "image_url": image_url, "price": None})
        if len(results) >= limit:
            break
    return results


def _normalise_result(item: dict[str, Any], query: str) -> dict[str, Any]:
    title = item["title"]
    permalink = item["permalink"]
    image_url = item["image_url"]
    return {
        "produto": title,
        "product_name": title,
        "dificuldade": f"Encontrar uma solução melhor para {title.lower()}",
        "dor": f"Encontrar uma solução melhor para {title.lower()}",
        # link_ml é origem de consulta/imagem; não é apresentado como link afiliado.
        "link_ml": permalink,
        "product_source_url": permalink,
        "official_affiliate_url": None,
        "affiliate_url": None,
        "imagem": image_url,
        "image_url": image_url,
        "image_verified": True,
        "image_source": "Mercado Livre API · secure_thumbnail do mesmo resultado",
        "marketplace": "Mercado Livre",
        "nicho": "Mercado Livre · descoberta por pesquisa",
        "price": item.get("price"),
        "product_external_id": item.get("id"),
        "query": query,
        "source": "mercado_livre_public_api",
        "copy": None,
        "video_demo": None,
    }


def obter_produto_real_validado(provedor: str = "openai", query: str | None = None) -> dict[str, Any]:
    """Pesquisa anúncios atuais e escolhe o primeiro com URL e imagem públicas."""
    errors: list[str] = []
    api_blocked = False
    for candidate in _candidate_queries(query):
        if not api_blocked:
            try:
                results = buscar_produtos_mercado_livre(candidate, limit=8)
                if results:
                    return _normalise_result(results[0], candidate)
                errors.append(f"{candidate}: API sem resultado com imagem pública")
            except MarketplaceAccessError as exc:
                api_blocked = True
                errors.append(f"{candidate}: API bloqueada — {exc}")
            except Exception as exc:
                errors.append(f"{candidate}: API {exc}")
        try:
            web_results = buscar_produtos_mercado_livre_web(candidate, limit=8)
            if web_results:
                return _normalise_result(web_results[0], candidate)
            errors.append(f"{candidate}: listagem web sem anúncios com imagem")
        except Exception as web_exc:
            errors.append(f"{candidate}: web {web_exc}")
    details = " | ".join(errors[-5:])
    if api_blocked:
        details += " | API desativada após HTTP 401/403: configure ML_ACCESS_TOKEN ou ML_API_ACCESS_TOKEN; enquanto isso, use busca manual, link oficial ou upload da imagem."
    raise RuntimeError("Mercado Livre não devolveu um produto com imagem pública. " + details)


__all__ = ["MarketplaceAccessError", "buscar_produtos_mercado_livre", "buscar_produtos_mercado_livre_web", "obter_produto_real_validado"]
