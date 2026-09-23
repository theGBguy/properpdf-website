# ProperPDF website

Standalone static site for `tryproperpdf.app`. The site is generated with Python's standard library and deployed as static assets to Cloudflare Pages. There is no application server, database, tracking script, or required runtime in production.

## Preview locally

Run `npm run build` after changing content in `generate.py`. For a simple preview, run `python3 -m http.server 8000 --directory public` and open `http://localhost:8000`. To preview the Cloudflare Pages asset behavior, run `npm run dev`.

## Publish

In Cloudflare Pages, use `npm run build` as the build command and `public` as the output directory. Install dependencies with `npm install`, then authenticate Wrangler with `npx wrangler login`. Set `CLOUDFLARE_PAGES_PROJECT` when the Pages project is not named `tryproperpdf`, and run `npm run deploy`. Attach `tryproperpdf.app` as a custom domain in the Pages project.

The Privacy Policy and Terms of Service are shared by the iOS and Android apps. Their document bodies are stored under `legal-source/` and included in the generated site. Support is available at `hello@tryproperpdf.app`. Pricing shows Free and Pro features without a fixed amount because app offers are localized and configured outside this repository.

## Content structure

Edit the `features` and `guides` lists in `generate.py` to add or update content. The generator emits the tool pages, `/features/`, `/guides/`, `/blog/`, `/support/`, legal route aliases, `sitemap.xml`, `robots.txt`, `_headers`, and `_redirects` into `public/`.

The Android store URL and iOS App Store URL are centralized near the top of `generate.py`. Replace the Android placeholder when the official listing changes.
