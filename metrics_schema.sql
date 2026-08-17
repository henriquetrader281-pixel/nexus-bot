-- Nexus Bot: métricas de criativos e publicações.
-- Compatível com SQLite. As métricas devem ser atualizadas por consulta da API
-- ou por importação de dados; não são geradas como projeções.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    marketplace TEXT NOT NULL,
    official_affiliate_url TEXT NOT NULL,
    product_name TEXT NOT NULL,
    product_external_id TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS creatives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    variant TEXT NOT NULL CHECK (variant IN ('image_a', 'video_b')),
    asset_path TEXT,
    asset_url TEXT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    cta TEXT NOT NULL,
    width INTEGER,
    height INTEGER,
    duration_seconds REAL,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'ready', 'published', 'failed')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(campaign_id, variant)
);

CREATE TABLE IF NOT EXISTS publications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creative_id INTEGER NOT NULL REFERENCES creatives(id) ON DELETE CASCADE,
    channel TEXT NOT NULL CHECK (channel IN ('pinterest', 'instagram', 'tiktok')),
    external_post_id TEXT,
    external_url TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'published', 'failed', 'removed')),
    published_at TEXT,
    last_checked_at TEXT,
    UNIQUE(creative_id, channel)
);

CREATE TABLE IF NOT EXISTS creative_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    publication_id INTEGER NOT NULL REFERENCES publications(id) ON DELETE CASCADE,
    impressions INTEGER NOT NULL DEFAULT 0 CHECK (impressions >= 0),
    clicks INTEGER NOT NULL DEFAULT 0 CHECK (clicks >= 0),
    conversions INTEGER NOT NULL DEFAULT 0 CHECK (conversions >= 0),
    spend_cents INTEGER NOT NULL DEFAULT 0 CHECK (spend_cents >= 0),
    revenue_cents INTEGER NOT NULL DEFAULT 0 CHECK (revenue_cents >= 0),
    measured_at TEXT NOT NULL DEFAULT (datetime('now')),
    CHECK (clicks <= impressions OR impressions = 0),
    CHECK (conversions <= clicks OR clicks = 0)
);

CREATE INDEX IF NOT EXISTS idx_campaigns_created_at ON campaigns(created_at);
CREATE INDEX IF NOT EXISTS idx_creatives_variant ON creatives(variant);
CREATE INDEX IF NOT EXISTS idx_publications_channel_status ON publications(channel, status);
CREATE INDEX IF NOT EXISTS idx_metrics_publication_time ON creative_metrics(publication_id, measured_at);

CREATE VIEW IF NOT EXISTS creative_performance AS
SELECT
    c.id AS campaign_id,
    c.product_name,
    cr.variant,
    p.channel,
    COALESCE(SUM(m.impressions), 0) AS impressions,
    COALESCE(SUM(m.clicks), 0) AS clicks,
    COALESCE(SUM(m.conversions), 0) AS conversions,
    CASE WHEN COALESCE(SUM(m.impressions), 0) > 0
         THEN CAST(SUM(m.clicks) AS REAL) / SUM(m.impressions) ELSE 0 END AS ctr,
    CASE WHEN COALESCE(SUM(m.clicks), 0) > 0
         THEN CAST(SUM(m.conversions) AS REAL) / SUM(m.clicks) ELSE 0 END AS conversion_rate,
    CASE WHEN COALESCE(SUM(m.spend_cents), 0) > 0
         THEN CAST(SUM(m.revenue_cents) - SUM(m.spend_cents) AS REAL) / SUM(m.spend_cents) ELSE NULL END AS roas_net
FROM campaigns c
JOIN creatives cr ON cr.campaign_id = c.id
LEFT JOIN publications p ON p.creative_id = cr.id
LEFT JOIN creative_metrics m ON m.publication_id = p.id
GROUP BY c.id, c.product_name, cr.variant, p.channel;
