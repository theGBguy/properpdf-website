CREATE TABLE IF NOT EXISTS development_subscribers (
  email TEXT PRIMARY KEY COLLATE NOCASE,
  subscribed_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  consent_version TEXT NOT NULL,
  source TEXT NOT NULL DEFAULT 'homepage',
  email_verified INTEGER NOT NULL DEFAULT 0 CHECK (email_verified IN (0, 1))
);

CREATE TABLE IF NOT EXISTS analytics_daily (
  day TEXT NOT NULL,
  event TEXT NOT NULL CHECK (event IN ('page_view', 'download_click')),
  path TEXT NOT NULL,
  platform TEXT NOT NULL CHECK (platform IN ('none', 'ios', 'android')),
  count INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (day, event, path, platform)
);

-- Global endpoint budgets: no visitor identifiers or IP addresses are stored.
CREATE TABLE IF NOT EXISTS api_limits (
  endpoint TEXT NOT NULL,
  minute INTEGER NOT NULL,
  count INTEGER NOT NULL,
  PRIMARY KEY (endpoint, minute)
);
