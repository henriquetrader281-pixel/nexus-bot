import os
from pathlib import Path

os.environ["NEXUS_METRICS_DB"] = "/tmp/nexus_metrics_test.sqlite3"
try:
    Path(os.environ["NEXUS_METRICS_DB"]).unlink()
except FileNotFoundError:
    pass

import metrics_store

campaign_id = metrics_store.create_campaign("Mercado Livre", "https://meli.la/11v5uxd", "Power Bank")
image_id = metrics_store.create_creative(campaign_id, "image_a", "Power Bank", "Descrição", "Ver oferta", width=1000, height=1500, status="ready")
video_id = metrics_store.create_creative(campaign_id, "video_b", "Power Bank", "Roteiro", "Ver oferta", width=1080, height=1920, duration_seconds=10, status="ready")
image_pub = metrics_store.record_publication(image_id, "pinterest", external_url="https://pinterest.com/pin/test-image", status="published")
video_pub = metrics_store.record_publication(video_id, "pinterest", external_url="https://pinterest.com/pin/test-video", status="published")
metrics_store.record_metrics(image_pub, 1000, 40, 2, revenue_cents=1000)
metrics_store.record_metrics(video_pub, 1000, 70, 4, revenue_cents=2000)
rows = metrics_store.performance_rows()
assert len(rows) == 2
assert any(row["variant"] == "image_a" and abs(row["ctr"] - 0.04) < 1e-9 for row in rows)
assert any(row["variant"] == "video_b" and abs(row["ctr"] - 0.07) < 1e-9 for row in rows)
print("METRICS_TEST_OK")
