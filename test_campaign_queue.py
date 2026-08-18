from __future__ import annotations

import os
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as temp_dir:
    os.environ["NEXUS_METRICS_DB"] = str(Path(temp_dir) / "queue.sqlite3")
    import campaign_queue

    campaign = {
        "product_name": "Power Bank 10000mah",
        "marketplace": "Mercado Livre",
        "product_external_id": "MLB-QUEUE-1",
        "product_source_url": "https://www.mercadolivre.com.br/power-bank/p/MLB-QUEUE-1",
        "official_affiliate_url": None,
        "image_url": "https://http2.mlstatic.com/product.jpg",
        "source_image_path": "/tmp/source_product_image.jpg",
        "image_path": "/tmp/creative_image_a.jpg",
        "video_path": "/tmp/creative_video_b.mp4",
        "audio_path": "/tmp/narration.mp3",
        "copy_final": "Copy AIDA pronta",
        "caption": "Legenda pronta para revisão",
        "hooks": ["Não fique sem bateria"],
        "keywords": ["power bank", "carregador portátil"],
        "media_manifest": {"publication": "not_executed"},
    }
    queue_id = campaign_queue.save_prepared_campaign(campaign)
    rows = campaign_queue.list_prepared_campaigns(status="ready")
    assert len(rows) == 1
    assert rows[0]["id"] == queue_id
    assert rows[0]["official_affiliate_url"] is None
    assert rows[0]["hooks"] == campaign["hooks"]
    assert rows[0]["keywords"] == campaign["keywords"]
    assert rows[0]["manifest"] == campaign["media_manifest"]

    loaded = campaign_queue.campaign_from_queue_row(rows[0])
    assert loaded["queue_id"] == queue_id
    assert loaded["copy"] == campaign["copy_final"]
    assert loaded["video_path"] == campaign["video_path"]
    assert campaign_queue.mark_prepared_campaign(queue_id, "needs_review") is True
    assert campaign_queue.list_prepared_campaigns(status="ready") == []

print("CAMPAIGN_QUEUE_TEST_OK")
