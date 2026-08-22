from __future__ import annotations


def test_video_metrics_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr("metrics_store.DB_PATH", tmp_path / "metrics.sqlite3")
    import metrics_store

    project = {
        "project_id": "video-test-1",
        "title": "Projeto teste",
        "product_name": "Produto teste",
        "niche": "casa",
        "platform": "YouTube Shorts",
        "version": 2,
    }
    metrics_store.register_video_project(project)
    publication_id = metrics_store.record_video_publication("video-test-1", "youtube", status="published")
    metrics_store.record_video_metrics(publication_id, views=1000, impressions=1200, avg_watch_time_seconds=8.0, completed_views=400, likes=100, comments=20, shares=30, clicks=24, follower_delta=18)

    rows = metrics_store.video_performance_rows("video-test-1")
    assert len(rows) == 1
    assert rows[0]["platform"] == "youtube"
    assert rows[0]["views"] == 1000
    assert round(rows[0]["completion_rate"], 2) == 0.4
    assert round(rows[0]["engagement_rate"], 2) == 0.15
    assert rows[0]["follower_delta"] == 18
