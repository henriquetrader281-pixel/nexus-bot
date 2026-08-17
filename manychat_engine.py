"""Integração Nexus -> Make webhook -> ManyChat."""

from __future__ import annotations

import os
from typing import Any

import requests
import streamlit as st


def _secret(name: str) -> str | None:
    try:
        value = st.secrets.get(name)
    except Exception:
        value = None
    return value or os.environ.get(name)


def _post(webhook_url: str, payload: dict[str, Any], *, user_agent: str) -> dict[str, Any]:
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json", "User-Agent": user_agent},
            timeout=10,
        )
        if 200 <= response.status_code < 300:
            return {"success": True, "status_code": response.status_code, "response": response.text}
        return {
            "success": False,
            "status_code": response.status_code,
            "error": f"Erro HTTP {response.status_code}: {response.text[:500]}",
        }
    except requests.RequestException as exc:
        return {"success": False, "error": f"Falha de rede: {exc}"}


def disparar_webhook_manychat(
    produto: str,
    link_afiliado: str,
    copy_texto: str,
    *,
    test_mode: bool = False,
    event: str = "nexus_offer_ready",
) -> dict[str, Any]:
    """Envia uma oferta ou um evento técnico ao webhook configurado."""
    webhook_url = _secret("MANYCHAT_WEBHOOK_URL")
    if not webhook_url:
        return {"success": False, "error": "MANYCHAT_WEBHOOK_URL não configurado nos Secrets."}
    if not webhook_url.startswith("https://"):
        return {"success": False, "error": "O webhook ManyChat/Make precisa usar HTTPS."}

    payload = {
        "event": "nexus_credentials_test" if test_mode else event,
        "test_mode": bool(test_mode),
        "produto": produto,
        "link_afiliado": link_afiliado,
        "copy": copy_texto,
        "trigger": "NEXUS_TEST" if test_mode else "QUERO",
    }
    return _post(webhook_url, payload, user_agent="NexusBot-ManyChat/1.0")


def testar_webhook_manychat(webhook_url: str | None = None) -> dict[str, Any]:
    """Envia apenas o evento técnico recomendado para validar o Make."""
    target = webhook_url or _secret("MANYCHAT_WEBHOOK_URL")
    if not target:
        return {"success": False, "error": "MANYCHAT_WEBHOOK_URL não configurado nos Secrets."}
    if not target.startswith("https://"):
        return {"success": False, "error": "O webhook precisa ser uma URL HTTPS."}
    payload = {
        "event": "nexus_credentials_test",
        "test_mode": True,
        "produto": "NEXUS_TESTE_CREDENCIAIS",
        "link_afiliado": "https://example.com/nexus-test",
        "copy": "Teste técnico Nexus — não é uma oferta para cliente.",
        "trigger": "NEXUS_TEST",
    }
    return _post(target, payload, user_agent="NexusBot-CredentialValidator/1.0")


__all__ = ["disparar_webhook_manychat", "testar_webhook_manychat"]
