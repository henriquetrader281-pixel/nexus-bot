from __future__ import annotations

import os
import shutil
import sys
import types
from pathlib import Path

from PIL import Image


class SessionState(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__


class Progress:
    def progress(self, *_args, **_kwargs):
        return None


fake_streamlit = types.ModuleType("streamlit")
fake_streamlit.session_state = SessionState()
fake_streamlit.secrets = {}
fake_streamlit.progress = lambda *_args, **_kwargs: Progress()
fake_streamlit.success = lambda *_args, **_kwargs: None
fake_streamlit.warning = lambda *_args, **_kwargs: None
fake_streamlit.info = lambda *_args, **_kwargs: None
fake_streamlit.error = lambda *_args, **_kwargs: None
fake_streamlit.button = lambda *_args, **_kwargs: False
fake_streamlit.balloons = lambda *_args, **_kwargs: None
sys.modules["streamlit"] = fake_streamlit

os.environ["NEXUS_ML_SEARCH_QUERY"] = "power bank carregador portátil"

import campaign_state
import hermes_engine
import metrics_store
import self_optimizer
import stock_validator
import tts_engine
import update
import real_marketplace_engine
import generate_creatives
from generate_creatives import ProductData

MINED_IMAGE_URL = "https://http2.mlstatic.com/nexus-test-power-bank.jpg"
MINED_PRODUCT = {
    "id": "MLB-TEST-POWERBANK",
    "title": "Power Bank 10000mah Carregador Portátil Turbo",
    "permalink": "https://www.mercadolivre.com.br/power-bank-teste/p/MLB-TEST-POWERBANK",
    "image_url": MINED_IMAGE_URL,
    "price": 89.90,
}
real_marketplace_engine.buscar_produtos_mercado_livre = lambda _query, limit=8: [MINED_PRODUCT]

def fake_fetch_product_data(url):
    assert url == MINED_PRODUCT["permalink"]
    return ProductData(
        official_affiliate_url="",
        resolved_url=url,
        title=MINED_PRODUCT["title"],
        image_url=MINED_IMAGE_URL,
        price=MINED_PRODUCT["price"],
        marketplace="Mercado Livre",
    )

def fake_download_image(product, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "source_product_image.jpg"
    Image.new("RGB", (800, 800), "#0f172a").save(path, format="JPEG", quality=94)
    assert product.image_url == MINED_IMAGE_URL
    return path

generate_creatives.fetch_product_data = fake_fetch_product_data
generate_creatives.download_image = fake_download_image

from autonomo_engine import executar_ciclo_mestre_um_clique

# O teste valida a pipeline real, mas isola integrações que publicariam ou dependem
# de credenciais externas. Não há ManyChat, Pinterest ou outro disparo no dry run.
stock_validator.validar_link_e_stock = lambda _url: {"valido": True, "status": "teste"}
update.registrar_mineracao = lambda *_args, **_kwargs: None
self_optimizer.obter_instrucao_estrategica = lambda: "manter clareza e benefício verificável"
self_optimizer.avaliar_e_otimizar = lambda *_args, **_kwargs: "sem mutação: teste de integração"
tts_engine.gerar_narração_ia = lambda _text: {"success": False, "error": "voz isolada no teste; legenda deve permanecer ativa"}
hermes_engine.hermes_elite_programmer = lambda *_args, **_kwargs: {"success": True, "status": "teste"}
hermes_engine.supervisionar_entrega = lambda *_args, **_kwargs: {"success": True, "status": "teste"}

# Evita dormir durante o teste e não usa reels_demo opcional.
import autonomo_engine
autonomo_engine.time.sleep = lambda _seconds: None

shutil.rmtree(".nexus_media", ignore_errors=True)
result = executar_ciclo_mestre_um_clique(provedor="test", publicar=False)
campaign = campaign_state.get_campaign()

assert result["produto"]
assert campaign.get("copy_final")
assert len(campaign.get("hooks", [])) >= 8
assert campaign.get("caption")
assert campaign.get("keywords")
assert campaign.get("intent_label")
assert campaign.get("image_url") == MINED_IMAGE_URL
assert campaign.get("source_image_url") == MINED_IMAGE_URL
assert campaign.get("product_source_url") == MINED_PRODUCT["permalink"]
assert campaign.get("affiliate_url") is None

source_path = Path(campaign["source_image_path"])
image_path = Path(campaign["image_path"])
video_path = Path(campaign["video_path"])
assert source_path.name == "source_product_image.jpg"
assert source_path.is_file() and source_path.stat().st_size > 0
assert image_path.is_file() and image_path.stat().st_size > 0
assert video_path.is_file() and video_path.stat().st_size > 0
with Image.open(source_path) as source_image:
    source_image.verify()
with Image.open(image_path) as creative_image:
    assert creative_image.size == (1000, 1500)
manifest = campaign["media_manifest"]
assert manifest["source_image_path"] == str(source_path)
assert manifest["product"]["image_url"] == MINED_IMAGE_URL
assert manifest["product"]["source_image_url"] == MINED_IMAGE_URL
assert manifest["product"]["product_source_url"] == MINED_PRODUCT["permalink"]
assert len(manifest["caption_lines"]) >= 8
assert manifest["publication"] == "not_executed"

print("AUTONOMOUS_DRY_RUN_OK")
print(f"PRODUCT={campaign['product_name']}")
print(f"SOURCE_IMAGE={source_path}")
print(f"IMAGE_A={image_path}")
print(f"VIDEO_B={video_path}")
print(f"HOOKS={len(campaign['hooks'])}")
print(f"KEYWORDS={len(campaign['keywords'])}")
print("PUBLICATION=SKIPPED")
