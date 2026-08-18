from __future__ import annotations

import types

import real_marketplace_engine as miner


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"{self.status_code} Client Error")

    def json(self):
        return self._payload


product_url = "https://www.mercadolivre.com.br/power-bank-teste/p/MLB123"
image_url = "https://http2.mlstatic.com/D_NQ_NP_2X_TEST.jpg"
html = f'''<html><body><div class="card"><a href="{product_url}"><img src="{image_url}" alt="Power Bank 10000mah"></a></div></body></html>'''

original_get = miner.requests.get
calls = []

def fake_get(url, **kwargs):
    calls.append(url)
    if "api.mercadolibre.com" in url:
        return FakeResponse(status_code=403)
    return FakeResponse(text=html)

miner.requests.get = fake_get
try:
    result = miner.obter_produto_real_validado(query="power bank")
finally:
    miner.requests.get = original_get

assert result["produto"] == "Power Bank 10000mah"
assert result["product_source_url"] == product_url
assert result["image_url"] == image_url
assert result["image_verified"] is True
assert result["official_affiliate_url"] is None
assert any("api.mercadolibre.com" in url for url in calls)
assert any("lista.mercadolivre.com.br" in url for url in calls)
print("REAL_MARKETPLACE_FALLBACK_OK")
