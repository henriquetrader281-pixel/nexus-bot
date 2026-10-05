from __future__ import annotations

import real_marketplace_engine as miner


class Response:
    def __init__(self, payload=None, text="", status_code=200):
        self._payload = payload or {}
        self.text = text
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def test_api_accepts_picture_secure_url_when_thumbnail_is_missing(monkeypatch):
    monkeypatch.setattr(
        miner.requests,
        "get",
        lambda *args, **kwargs: Response({"results": [{
            "id": "MLB-1",
            "title": "Luminária LED de Monitor",
            "permalink": "https://www.mercadolivre.com.br/luminaria/p/MLB-1",
            "pictures": [{"secure_url": "https://http2.mlstatic.com/luminaria.jpg"}],
        }]}),
    )
    result = miner.buscar_produtos_mercado_livre("luminária")
    assert result[0]["image_url"].endswith("luminaria.jpg")


def test_web_accepts_embedded_product_json(monkeypatch):
    html = '''<html><script type="application/ld+json">
    {"@type":"Product","name":"Organizador de Cozinha","url":"https://www.mercadolivre.com.br/organizador/p/MLB-2","image":"https://http2.mlstatic.com/organizador.jpg"}
    </script></html>'''
    monkeypatch.setattr(miner.requests, "get", lambda *args, **kwargs: Response(text=html))
    result = miner.buscar_produtos_mercado_livre_web("organizador")
    assert result[0]["title"] == "Organizador de Cozinha"
    assert result[0]["permalink"].endswith("MLB-2")
    assert result[0]["image_url"].endswith("organizador.jpg")
