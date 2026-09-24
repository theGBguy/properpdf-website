# ProperPDF website

Static pages generated with Python's standard library, hosted on Cloudflare Workers with static assets. Two API handlers use Cloudflare D1 for development-update signup requests and aggregate analytics. Documents are never uploaded through this website.

## Local preview

Run `npm install` and `npm run dev`. This builds the pages, applies local D1 migrations, and starts Wrangler Workers at `http://localhost:8788`. Local signups and analytics stay in `.wrangler/state`; they do not reach the production database. A plain Python static server can display pages but cannot serve the `/api/` endpoints.

After changing the Worker configuration, restart any older development process so it loads the new entry point and bindings. `npm test` runs the database/API and carousel regression tests (Node 22.13+ required). `npm run check:deploy` checks generated assets and performs a Worker deployment dry run. `npm run check:worker` (also available as `check:functions`) bundles the Worker without publishing.

## Cloudflare setup and publishing

`wrangler.jsonc` targets the existing Worker **properpdf-website**, with `server/worker.js` as its entry point, `public/` as static assets, and `DB` bound to `properpdf-site-data`. API paths invoke the Worker first; content and media are served directly from static assets. The existing handlers under `functions/api/` are explicitly imported by the Worker; they are not deployed as Pages Functions.

The D1 database and initial tables have already been provisioned. The database ID is not a secret. Authenticate with `npx wrangler login` if needed. Use `npm run deploy` to generate the site and deploy both the Worker and assets. Do not use `wrangler pages deploy`: this account's live site is a Worker, not a Pages project.

For the Git-connected Cloudflare **Workers Builds** project, set:

- Build command: `npm run build`
- Deploy command: `npx wrangler deploy`
- Root directory: this repository's root
- Worker name: `properpdf-website` (matches `wrangler.jsonc`)

`npm run deploy` is also a valid deploy command; it repeats the generation step. The Worker configuration supplies the asset directory, so no Pages output-directory setting is needed. Preserve the existing custom domain in Cloudflare.

For a fresh account, create a D1 database with `npx wrangler d1 create properpdf-site-data`, replace `database_id` in `wrangler.jsonc`, and run `npm run db:migrate:remote`.

Migrations are additive and tracked by D1. Run `npm run db:migrate:remote` before deploying code that requires new tables. Never use `--remote` for test signups or analytics fixtures.

## Stored data

- `analytics_daily`: UTC date, event (`page_view` or `download_click`), canonical page path, destination store, count. No visitor IDs, IP addresses, cookies, query strings, referrers, or raw user agents. Counts are browser-reported events, not unique visitors or verified installs. QR scans and blocked JavaScript are not counted. The client respects Do Not Track and Global Privacy Control; the server also respects those headers. Counters older than 730 days are deleted as new events arrive.
- `development_subscribers`: unique normalized email, signup timestamp, consent version, source, and an `email_verified` flag (initially 0). Duplicate submissions do not expose list membership or modify the original consent record. Explicit opt-in is required.
- `api_limits`: short-lived global per-minute request counts, with no visitor identifier. Limits are 30 signup submissions and 2,000 analytics submissions per minute across the site; excess requests receive HTTP 429. A hidden form field filters basic bots. This is a basic abuse guard, not a guarantee that submitted addresses belong to the visitor.

There are no public subscriber-list or analytics-read endpoints. Only your Cloudflare account can query the database. Frontend code receives no database credentials.

## View analytics and manage signups

Open Cloudflare **Workers & Pages → D1 → properpdf-site-data → Studio**. Run the queries in `scripts/analytics-report.sql`, or run:

```sh
npx wrangler d1 execute properpdf-site-data --remote --file scripts/analytics-report.sql
```

For local results, replace `--remote` with `--local`. Inspect or export `development_subscribers` privately in D1 Studio when connecting a mailing provider. Never place a subscriber export in `public/` or source control.

D1 saves requests; it does not send campaigns or verify email ownership. Before sending campaigns, connect an email provider and confirm addresses. The form and website privacy notice direct removal requests to `hello@tryproperpdf.app`. Process those requests by deleting the matching subscriber in D1 Studio and removing it from any future mailing provider. No emails are sent by this code.

## Content

The homepage is maintained in `public/index.html`. Edit the `features`, `guides`, and `article_mockups` lists in `generate.py` for content pages. The generator writes the articles, route aliases, sitemap, security headers, analytics path allowlist. `public/site-data.js` handles signups and site events on all canonical pages.

The app Privacy Policy and Terms of Service remain in `legal-source/`. A separate website-specific data notice is generated on the privacy page. Pricing lists reference USD amounts for weekly, monthly, yearly, and lifetime Pro plans; actual offers are shown in the app.
