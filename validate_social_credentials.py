#!/usr/bin/env python3
"""Valida credenciais e conectividade do Pinterest e do ManyChat.

Uso seguro:
  python validate_social_credentials.py
  python validate_social_credentials.py --send-manychat-test

Por padrão, o script NÃO envia nada ao ManyChat. Para um teste real, use
--send-manychat-test; o payload contém apenas um evento técnico de teste.

Variáveis aceitas:
  PINTEREST_ACCESS_TOKEN
  PINTEREST_BOARD_ID              (opcional; valida a pasta se informado)
  MANYCHAT_WEBHOOK_URL            (opcional; valida formato e, com a flag,
                                   envia uma requisição de teste)
  NEXUS_VALIDATION_TIMEOUT        (opcional; padrão: 15 segundos)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import requests


@dataclass
class CheckResult:
    service: str
    ok: bool
    message: str
    details: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "service": self.service,
            "ok": self.ok,
            "message": self.message,
            "details": self.details or {},
        }


def timeout_seconds() -> float:
    raw = os.getenv("NEXUS_VALIDATION_TIMEOUT", "15")
    try:
        value = float(raw)
        return max(3.0, min(value, 60.0))
    except ValueError:
        return 15.0


def mask_secret(value: str | None, visible: int = 4) -> str:
    if not value:
        return "ausente"
    if len(value) <= visible * 2:
        return "configurado"
    return f"{value[:visible]}…{value[-visible:]}"


def parse_json(response: requests.Response) -> dict[str, Any] | list[Any] | None:
    try:
        parsed = response.json()
        if isinstance(parsed, (dict, list)):
            return parsed
    except ValueError:
        pass
    return None


def pinterest_error(response: requests.Response) -> str:
    body = parse_json(response)
    if isinstance(body, dict):
        message = body.get("message") or body.get("error")
        if message:
            return f"HTTP {response.status_code}: {message}"
    return f"HTTP {response.status_code}: resposta sem detalhe legível"


def validate_pinterest(token: str | None, board_id: str | None) -> list[CheckResult]:
    results: list[CheckResult] = []
    if not token:
        return [CheckResult("Pinterest", False, "PINTEREST_ACCESS_TOKEN não configurado")]

    headers = {"Authorization": f"Bearer {token}"}
    timeout = timeout_seconds()
    results.append(
        CheckResult(
            "Pinterest token",
            True,
            "Token presente; valor não exibido",
            {"token": mask_secret(token)},
        )
    )

    try:
        response = requests.get(
            "https://api.pinterest.com/v5/user_account",
            headers=headers,
            timeout=timeout,
        )
        if response.ok:
            body = parse_json(response)
            username = body.get("username") if isinstance(body, dict) else None
            results.append(
                CheckResult(
                    "Pinterest API",
                    True,
                    "Token autenticado com sucesso",
                    {"username": username or "não informado"},
                )
            )
        else:
            results.append(CheckResult("Pinterest API", False, pinterest_error(response)))
            return results
    except requests.RequestException as exc:
        results.append(CheckResult("Pinterest API", False, f"Falha de rede: {exc}"))
        return results

    if not board_id:
        results.append(
            CheckResult(
                "Pinterest board",
                False,
                "PINTEREST_BOARD_ID não configurado; token válido, mas não há pasta definida",
            )
        )
        return results

    try:
        response = requests.get(
            f"https://api.pinterest.com/v5/boards/{board_id}",
            headers=headers,
            timeout=timeout,
        )
        if response.ok:
            body = parse_json(response)
            name = body.get("name") if isinstance(body, dict) else None
            results.append(
                CheckResult(
                    "Pinterest board",
                    True,
                    "Board ID válido e acessível",
                    {"board_id": board_id, "name": name or "não informado"},
                )
            )
        else:
            results.append(CheckResult("Pinterest board", False, pinterest_error(response)))
    except requests.RequestException as exc:
        results.append(CheckResult("Pinterest board", False, f"Falha de rede: {exc}"))

    return results


def validate_manychat(webhook_url: str | None, send_test: bool) -> list[CheckResult]:
    if not webhook_url:
        return [CheckResult("ManyChat", False, "MANYCHAT_WEBHOOK_URL não configurado")]

    parsed = urlparse(webhook_url)
    if parsed.scheme != "https" or not parsed.netloc:
        return [
            CheckResult(
                "ManyChat",
                False,
                "Webhook inválido: use uma URL HTTPS completa",
                {"host": parsed.netloc or "ausente"},
            )
        ]

    results = [
        CheckResult(
            "ManyChat webhook",
            True,
            "URL HTTPS válida; nenhum envio realizado",
            {"host": parsed.netloc},
        )
    ]
    if not send_test:
        results.append(
            CheckResult(
                "ManyChat delivery",
                False,
                "Teste de envio desativado por segurança; use --send-manychat-test para enviar um evento técnico",
            )
        )
        return results

    payload = {
        "event": "nexus_credentials_test",
        "test_mode": True,
        "produto": "NEXUS_TESTE_CREDENCIAIS",
        "link_afiliado": "https://example.com/nexus-test",
        "copy": "Teste técnico Nexus — não é uma oferta para cliente.",
        "trigger": "NEXUS_TEST",
    }
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json", "User-Agent": "NexusBot-CredentialValidator/1.0"},
            timeout=timeout_seconds(),
        )
        if 200 <= response.status_code < 300:
            results.append(
                CheckResult(
                    "ManyChat delivery",
                    True,
                    "Webhook aceitou o evento técnico",
                    {"status_code": response.status_code},
                )
            )
        else:
            results.append(
                CheckResult(
                    "ManyChat delivery",
                    False,
                    f"Webhook rejeitou o evento: HTTP {response.status_code}",
                )
            )
    except requests.RequestException as exc:
        results.append(CheckResult("ManyChat delivery", False, f"Falha de rede: {exc}"))
    return results


def print_report(results: list[CheckResult], json_output: bool) -> int:
    payload = [item.as_dict() for item in results]
    if json_output:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("Nexus Bot — validação Pinterest/ManyChat")
        print("=" * 46)
        for item in results:
            status = "OK" if item.ok else "ATENÇÃO"
            print(f"[{status}] {item.service}: {item.message}")
            if item.details:
                print(f"       {json.dumps(item.details, ensure_ascii=False)}")
        print("=" * 46)
        print("Nenhum segredo foi impresso.")

    # Falha se uma credencial presente foi rejeitada. Ausências também falham,
    # pois o objetivo do script é indicar se o ambiente está pronto para operar.
    return 0 if all(item.ok for item in results) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--send-manychat-test",
        action="store_true",
        help="envia um evento técnico test_mode=true ao webhook do ManyChat",
    )
    parser.add_argument("--json", action="store_true", help="imprime o relatório em JSON")
    args = parser.parse_args()

    results = []
    results.extend(
        validate_pinterest(
            os.getenv("PINTEREST_ACCESS_TOKEN"),
            os.getenv("PINTEREST_BOARD_ID"),
        )
    )
    results.extend(
        validate_manychat(
            os.getenv("MANYCHAT_WEBHOOK_URL"),
            args.send_manychat_test,
        )
    )
    return print_report(results, args.json)


if __name__ == "__main__":
    sys.exit(main())

__all__ = [
    "CheckResult",
    "validate_pinterest",
    "validate_manychat",
    "main",
]
