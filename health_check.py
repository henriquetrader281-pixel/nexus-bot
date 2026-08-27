from __future__ import annotations

import importlib.util
import shutil
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str
    required: bool = False


REQUIRED_PACKAGES = {
    "streamlit": "Interface principal",
    "PIL": "Processamento de imagens",
    "requests": "Integrações HTTP",
    "bs4": "Extração de metadados",
    "moviepy": "Renderização de vídeo",
}
OPTIONAL_PACKAGES = {
    "gtts": "Narração de fallback",
    "pytrends": "Fallback de tendências",
    "plotly": "Painéis de métricas",
}
SECRET_LABELS = {
    "NEXUS_PASSWORD": "Autenticação do painel",
    "GROQ_API_KEY": "Copy com IA",
    "ELEVENLABS_API_KEY": "Voz profissional",
    "ML_ACCESS_TOKEN": "Busca autenticada no Mercado Livre",
}


def _has_secret(name: str) -> bool:
    try:
        import streamlit as st

        value = st.secrets.get(name)
    except Exception:
        value = None
    if value in (None, ""):
        import os

        value = os.environ.get(name)
    return bool(value)


def run_checks() -> list[Check]:
    checks: list[Check] = []
    for package, purpose in REQUIRED_PACKAGES.items():
        installed = importlib.util.find_spec(package) is not None
        checks.append(Check(package, installed, purpose, required=True))
    for package, purpose in OPTIONAL_PACKAGES.items():
        installed = importlib.util.find_spec(package) is not None
        checks.append(Check(package, installed, purpose, required=False))
    ffmpeg = shutil.which("ffmpeg")
    checks.append(Check("ffmpeg", bool(ffmpeg), ffmpeg or "Instale o binário FFmpeg para exportar MP4.", required=True))
    for secret, purpose in SECRET_LABELS.items():
        configured = _has_secret(secret)
        checks.append(Check(secret, configured, purpose, required=secret == "NEXUS_PASSWORD"))
    return checks


def summary() -> dict[str, Any]:
    checks = run_checks()
    required_failed = [check.name for check in checks if check.required and not check.ok]
    return {
        "ok": not required_failed,
        "checks": checks,
        "required_failed": required_failed,
        "ready_for_media": not any(check.name in {"moviepy", "PIL", "ffmpeg"} and not check.ok for check in checks),
    }


def render_panel(st) -> None:
    result = summary()
    if result["ok"]:
        st.success("Nexus operacional: dependências críticas e autenticação disponíveis.")
    else:
        st.error("Nexus não está pronto para operação completa. Corrija os itens obrigatórios abaixo.")
    rows = []
    for check in result["checks"]:
        state = "OK" if check.ok else ("OBRIGATÓRIO" if check.required else "opcional")
        rows.append({"Item": check.name, "Estado": state, "Uso": check.detail})
    st.dataframe(rows, use_container_width=True, hide_index=True)
