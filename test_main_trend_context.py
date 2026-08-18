import nexus_pipeline_ui as main_ui
import trends

assert "bateria" in main_ui.inferir_dor_produto("Power Bank 10000mah", "power bank").lower()
assert "desorganização" in main_ui.inferir_dor_produto("Organizador de Cozinha", "cozinha").lower()
assert "tensão muscular" in main_ui.inferir_dor_produto("Pistola de Massagem", "massagem muscular").lower()
assert "necessidade recorrente" in main_ui.inferir_dor_produto("Produto sem contexto", "").lower()
assert main_ui._keywords_for_product("Power Bank 10000mah", "carregador portátil")[0] == "carregador portátil"

original = trends._obter_trends
try:
    trends._obter_trends = lambda: (["power bank", "organizador de cozinha"], "Teste de tendências")
    values, source = trends.obter_tendencias_reais(limit=2)
finally:
    trends._obter_trends = original

assert values == ["power bank", "organizador de cozinha"]
assert source == "Teste de tendências"
print("MAIN_TREND_CONTEXT_TEST_OK")
