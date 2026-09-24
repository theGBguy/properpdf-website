-- Daily page views and app-store link clicks. Counts are events, not unique people.
SELECT day, event, path, platform, count
FROM analytics_daily
WHERE day >= date('now', '-30 days')
ORDER BY day DESC, event, count DESC;

-- Total signup requests. Addresses are intentionally omitted from this report.
SELECT COUNT(*) AS development_update_requests FROM development_subscribers;
