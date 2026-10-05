from __future__ import annotations

import mineracao


def test_scanner_formats_real_products_without_inventing_links(monkeypatch):
    monkeypatch.setattr(
        mineracao,
        "buscar_produtos_marketplace",
        lambda marketplace, query, limit=5: [{
            "title": "Organizador Amazon",
            "permalink": "https://www.amazon.com.br/dp/B0TESTE",
            "image_url": "https://m.media-amazon.com/images/I/teste.jpg",
            "price": 49.9,
        }],
    )
    result = mineracao.minerar_produtos("Liste produtos promissores de organização no Amazon.", "Amazon", None)
    assert "NOME: Organizador Amazon" in result
    assert "https://www.amazon.com.br/dp/B0TESTE" in result
    assert "https://m.media-amazon.com/images/I/teste.jpg" in result
