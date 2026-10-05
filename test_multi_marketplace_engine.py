from __future__ import annotations

import multi_marketplace_engine as miner


class Response:
    status_code = 200

    def __init__(self, text: str):
        self.text = text

    def raise_for_status(self):
        return None


def test_shopee_json_ld_product_is_validated(monkeypatch):
    html = '''<script type="application/ld+json">
    {"@type":"Product","name":"Organizador Shopee","url":"https://shopee.com.br/organizador-i.1.2","image":"https://cf.shopee.com.br/file/organizador.jpg"}
    </script>'''
    monkeypatch.setattr(miner.requests, "get", lambda *args, **kwargs: Response(html))
    result = miner.buscar_produtos_marketplace_web("Shopee", "organizador")
    assert result[0]["title"] == "Organizador Shopee"
    assert result[0]["permalink"].startswith("https://shopee.com.br/")


def test_amazon_product_card_is_validated(monkeypatch):
    html = '''<div class="card"><a href="/dp/B0TESTE123"><img src="https://m.media-amazon.com/images/I/teste.jpg" alt="Fone Amazon Bluetooth"></a></div>'''
    monkeypatch.setattr(miner.requests, "get", lambda *args, **kwargs: Response(html))
    result = miner.buscar_produtos_marketplace_web("Amazon", "fone bluetooth")
    assert result[0]["title"] == "Fone Amazon Bluetooth"
    assert "/dp/B0TESTE123" in result[0]["permalink"]


def test_normalised_product_keeps_marketplace_and_real_assets():
    result = miner._normalise(
        {"id": "x", "title": "Produto Shopee", "permalink": "https://shopee.com.br/p-i.1.2", "image_url": "https://cf.shopee.com.br/file/x.jpg"},
        "Shopee",
        "produto",
    )
    assert result["marketplace"] == "Shopee"
    assert result["image_verified"] is True
    assert result["product_source_url"].startswith("https://shopee.com.br/")
