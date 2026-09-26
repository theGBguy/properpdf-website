-- Daily page views and app-store link clicks. Counts are events, not unique people.
SELECT day, event, path, platform, count
FROM analytics_daily
WHERE day >= date('now', '-30 days')
ORDER BY day DESC, event, count DESC;

-- Total signup requests. Addresses are intentionally omitted from this report.
SELECT COUNT(*) AS development_update_requests FROM development_subscribers;

-- Acquisition and downstream store clicks, attributed within a browser tab for 30 minutes.
-- These are event counts, not sessions, unique visitors, or installs.
SELECT source, landing,
  SUM(CASE WHEN event = 'page_view' THEN count ELSE 0 END) AS page_views,
  SUM(CASE WHEN event = 'download_click' AND platform = 'ios' THEN count ELSE 0 END) AS ios_clicks,
  SUM(CASE WHEN event = 'download_click' AND platform = 'android' THEN count ELSE 0 END) AS android_clicks
FROM analytics_sources_daily
WHERE day >= date('now', '-29 days')
GROUP BY source, landing
ORDER BY page_views DESC;

-- Pages that generate store clicks. Ratio is clicks per 100 views, not an install conversion rate.
SELECT path,
  SUM(CASE WHEN event = 'page_view' THEN count ELSE 0 END) AS page_views,
  SUM(CASE WHEN event = 'download_click' THEN count ELSE 0 END) AS store_clicks,
  ROUND(100.0 * SUM(CASE WHEN event = 'download_click' THEN count ELSE 0 END)
    / NULLIF(SUM(CASE WHEN event = 'page_view' THEN count ELSE 0 END), 0), 1) AS clicks_per_100_views
FROM analytics_daily
WHERE day >= date('now', '-29 days')
GROUP BY path
ORDER BY store_clicks DESC, page_views DESC;
