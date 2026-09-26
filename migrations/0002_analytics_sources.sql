-- Separate table preserves historical totals; historical sources cannot be recovered.
CREATE TABLE IF NOT EXISTS analytics_sources_daily (
  day TEXT NOT NULL,
  event TEXT NOT NULL CHECK (event IN ('page_view', 'download_click')),
  path TEXT NOT NULL,
  platform TEXT NOT NULL CHECK (platform IN ('none', 'ios', 'android')),
  source TEXT NOT NULL,
  landing TEXT NOT NULL,
  count INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (day, event, path, platform, source, landing)
);
