import nexus_pipeline_ui as main_ui
import trends

assert "bateria" in main_ui.inferir_dor_produto("Power Bank 10000mah", "power bank").lower()
assert "desorganização" in main_ui.inferir_dor_produto("Organizador de Cozinha", "cozinha").lower()
assert "tensão muscular" in main_ui.inferir_dor_produto("Pistola de Massagem", "massagem muscular").lower()
assert "necessidade recorrente" in main_ui.inferir_dor_produto("Produto sem contexto", "").lower()
assert main_ui._keywords_for_product("Power Bank 10000mah", "carregador portátil")[0] == "carregador portátil"
raw_values = ["apac", "presidente", "gloria maria", "previsão do tempo recife", "Power Bank", "organizador de cozinha", "zz top"]
commercial_values = trends.filtrar_tendencias_comerciais(raw_values, limit=10)
assert commercial_values == ["Power Bank", "organizador de cozinha"]

import real_marketplace_engine
original_api = real_marketplace_engine.buscar_produtos_mercado_livre
original_web = real_marketplace_engine.buscar_produtos_mercado_livre_web
try:
    real_marketplace_engine.buscar_produtos_mercado_livre = lambda _term, limit=3: []
    real_marketplace_engine.buscar_produtos_mercado_livre_web = lambda term, limit=3: [{
        "title": f"{term} Produto Teste",
        "permalink": f"https://www.mercadolivre.com.br/{term.replace(' ', '-')}",
        "image_url": "https://http2.mlstatic.com/test.jpg",
        "price": 99,
    }]
    hot_products = main_ui._buscar_produtos_para_tendencias(["power bank"], per_term=1)
finally:
    real_marketplace_engine.buscar_produtos_mercado_livre = original_api
    real_marketplace_engine.buscar_produtos_mercado_livre_web = original_web
assert hot_products[0]["trend_term"] == "power bank"
assert hot_products[0]["image_url"].endswith("test.jpg")

original = trends._obter_trends
try:
    trends._obter_trends = lambda: (["power bank", "organizador de cozinha"], "Teste de tendências")
    values, source = trends.obter_tendencias_reais(limit=2)
finally:
    trends._obter_trends = original

assert values == ["power bank", "organizador de cozinha"]
assert source == "Teste de tendências"
print("MAIN_TREND_CONTEXT_TEST_OK")
