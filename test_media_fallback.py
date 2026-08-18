import sys
import types


class SessionState(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__


fake_streamlit = types.ModuleType("streamlit")
fake_streamlit.session_state = SessionState()
sys.modules["streamlit"] = fake_streamlit

import media_pipeline
from generate_creatives import ProductData

media_pipeline.fetch_product_data = lambda url: ProductData(
    official_affiliate_url=url,
    resolved_url=url,
    title="Produto sem OG image",
    image_url=None,
)
product = media_pipeline._build_product({
    "product_name": "Produto sem OG image",
    "official_affiliate_url": "https://meli.la/teste",
    "image_url": "https://cdn.example.test/produto.jpg",
})
assert product.image_url == "https://cdn.example.test/produto.jpg"
print("MEDIA_FALLBACK_TEST_OK")
