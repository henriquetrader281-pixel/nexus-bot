import real_marketplace_engine as miner


class Response:
    status_code = 403
    text = "forbidden"

    def raise_for_status(self):
        raise RuntimeError("403 Client Error")


def test_api_403_is_reported_as_marketplace_access_error(monkeypatch):
    monkeypatch.setattr(miner.requests, "get", lambda *args, **kwargs: Response())
    try:
        miner.buscar_produtos_mercado_livre("fone bluetooth")
    except miner.MarketplaceAccessError as exc:
        assert exc.status_code == 403
        assert "HTTP 403" in str(exc)
    else:
        raise AssertionError("A resposta 403 deveria gerar MarketplaceAccessError")


def test_validation_stops_repeating_api_after_403_and_uses_web_fallback(monkeypatch):
    api_calls = []
    web_calls = []

    def blocked_api(query, limit=8):
        api_calls.append(query)
        raise miner.MarketplaceAccessError(403)

    def web_result(query, limit=8):
        web_calls.append(query)
        if query == "fone bluetooth":
            return [{
                "id": None,
                "title": "Fone Bluetooth com Cancelamento de Ruído",
                "permalink": "https://www.mercadolivre.com.br/fone-teste",
                "image_url": "https://http2.mlstatic.com/fone.jpg",
                "price": 199.0,
            }]
        return []

    monkeypatch.setattr(miner, "buscar_produtos_mercado_livre", blocked_api)
    monkeypatch.setattr(miner, "buscar_produtos_mercado_livre_web", web_result)
    result = miner.obter_produto_real_validado(query="fone bluetooth")

    assert result["image_verified"] is True
    assert len(api_calls) == 1
    assert web_calls[0] == "fone bluetooth"
