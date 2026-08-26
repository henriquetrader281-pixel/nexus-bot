from __future__ import annotations

import hmac
import os
from typing import Any


def _streamlit_secret(name: str) -> Any:
    """Lê um segredo do Streamlit sem tornar a dependência obrigatória fora da UI."""
    try:
        import streamlit as st

        return st.secrets.get(name)
    except Exception:
        return None


def get_secret(name: str, default: Any = None) -> Any:
    """Retorna o segredo do Streamlit, com fallback para variável de ambiente."""
    value = _streamlit_secret(name)
    if value not in (None, ""):
        return value
    return os.environ.get(name, default)


def configured_password() -> str | None:
    """Obtém a senha configurada; não existe credencial padrão em produção."""
    value = get_secret("NEXUS_PASSWORD")
    if value in (None, ""):
        return None
    return str(value)


def check_password(candidate: str, expected: str | None = None) -> bool:
    """Compara a senha sem revelar qual configuração está ausente."""
    configured = expected if expected is not None else configured_password()
    if not configured or not candidate:
        return False
    return hmac.compare_digest(str(candidate), configured)
