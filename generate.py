"""Generate the standalone content pages and sitemap with the Python standard library."""

from html import escape
import json
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

PUBLIC = Path(__file__).parent / "public"
BASE = "https://tryproperpdf.app"
SITE_NAME = "ProperPDF"
SITE_IMAGE = f"{BASE}/assets/home.jpg"
IOS = "https://apps.apple.com/app/id6760956540"
ANDROID = "https://play.google.com/store/apps/details?id=io.github.thegbguy.pdfmate"
IOS_UTM = f"{IOS}?utm_source=site&utm_medium=hero&utm_campaign=homepage"
ANDROID_UTM = f"{ANDROID}&referrer=utm_source%3Dsite%26utm_medium%3Dhero%26utm_campaign%3Dhomepage"
APPLE_BADGE = "https://developer.apple.com/assets/elements/badges/download-on-the-app-store.svg"
GOOGLE_BADGE = "https://play.google.com/intl/en_us/badges/static/images/badges/en_badge_web_generic.png"
QR_URL = f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&margin=8&data={ANDROID_UTM}"

# Content dates. Bump UPDATED whenever page copy changes; it feeds the visible
# "Updated" line, Article schema and sitemap <lastmod>.
PUBLISHED = "2026-09-23"
UPDATED = "2026-10-22"
UPDATED_LABEL = "22 October 2026"

# IndexNow keys are public by design: search engines fetch /<key>.txt to confirm
# that whoever submits URLs controls the site. See scripts/indexnow.mjs.
INDEXNOW_KEY = "8ad089f0da123f2a9ee15d44dcb7e3cc"

# Facts that pages, the pricing table and llms.txt all repeat. Keep them in step
# with the shipped apps (iOS Route.isPremium, Android HomeScreen isPremium and the
# addWatermark view models) and the live store listings.
REQUIREMENTS = "iOS 17 or later on iPhone and iPad; Android 8.0 or later"
PRICES = [("Weekly", "$1.99 a week"), ("Monthly", "$3.99 a month"), ("Yearly", "$19.99 a year"), ("Lifetime", "$29.99 once")]
# US reference prices. Both stores use regional pricing, so most countries pay less.
REGIONAL_NOTE = "These are US prices. ProperPDF uses regional pricing, so Pro costs less in many countries, and the App Store or Google Play shows the price in your currency before you buy."
FREE = "Free"
FREE_WM = "Free, with watermark"
WATERMARK_NOTE = "\"With watermark\" means files saved with that tool carry a ProperPDF watermark. Pro removes it."
PRO = "Pro"
TOOLS = [
    # name, page slug, iPhone and iPad, Android
    ("Scan to PDF", "scan-to-pdf", FREE, FREE_WM),
    ("Merge PDF", "merge-pdf", FREE_WM, FREE_WM),
    ("Split PDF", "split-pdf", FREE_WM, FREE_WM),
    ("Organize pages (reorder, rotate, delete)", None, FREE, FREE_WM),
    ("Image to PDF", "image-to-pdf", FREE, FREE_WM),
    ("PDF to image (PNG or JPEG)", "pdf-to-image", FREE, FREE_WM),
    ("Edit metadata", None, FREE, FREE),
    ("PDF viewer and document library", None, FREE, FREE),
    ("Compress PDF", "compress-pdf", PRO, PRO),
    ("Sign PDF", "sign-pdf", PRO, PRO),
    ("Fill PDF forms", "fill-pdf", PRO, PRO),
    ("Lock and unlock PDF (password)", "lock-pdf", PRO, PRO),
    ("AI chat and summary (on-device)", None, FREE, PRO),
]
TOOL_BY_SLUG = {slug: (name, ios, android) for name, slug, ios, android in TOOLS if slug}


def download_buttons(context: str = "hero") -> str:
    return f'''<div class="download-buttons" data-download-context="{escape(context)}">
  <a class="store-badge ios-badge" href="{IOS_UTM}" target="_blank" rel="noopener noreferrer"><img src="{APPLE_BADGE}" alt="Download on the App Store" width="180" height="60"></a>
  <a class="store-badge android-badge" href="{ANDROID_UTM}" target="_blank" rel="noopener noreferrer"><img src="{GOOGLE_BADGE}" alt="Get it on Google Play" width="203" height="60"></a>
</div>'''


def software_schema() -> dict:
    return {"@context": "https://schema.org", "@graph": [{
        "@type": "MobileApplication",
        "@id": f"{BASE}/#app",
        "name": SITE_NAME,
        "operatingSystem": "Android 8.0+, iOS 17+, iPadOS 17+",
        "applicationCategory": "ProductivityApplication",
        "description": "Offline PDF app for iPhone, iPad and Android. Scan, merge, split, compress, sign, fill, lock and convert PDFs on the device, with no uploads and no account.",
        "url": f"{BASE}/",
        "downloadUrl": [IOS, ANDROID],
        "sameAs": [IOS, ANDROID],
        "offers": [{"@type": "Offer", "price": "0", "priceCurrency": "USD", "description": "Free download. Pro unlocks compress, sign, fill, lock and removes watermarks."}],
    }, {"@type": "Organization", "@id": f"{BASE}/#org", "name": SITE_NAME, "url": f"{BASE}/", "logo": f"{BASE}/assets/icon.png", "email": "hello@tryproperpdf.app"}]}


OG_PAGES: dict[str, dict] = {}


def share_image(path: str) -> str:
    """Per-page social card from scripts/og_images.py when it exists, else the site image."""
    slug = path.strip("/") or "home"
    return f"{BASE}/og/{slug}.png" if (PUBLIC / "og" / f"{slug}.png").exists() else SITE_IMAGE


def schema_script(data: dict) -> str:
    return f'<script type="application/ld+json">{json.dumps(data, separators=(",", ":"))}</script>'


def article_schema(title: str, description: str, path: str, section: str, faq: list | None) -> list[dict]:
    """Article + breadcrumb (+ FAQ) structured data for a content page."""
    url = f"{BASE}{path}"
    graph = [
        {"@type": "Article", "headline": title, "description": description, "url": url, "mainEntityOfPage": url,
         "datePublished": PUBLISHED, "dateModified": UPDATED, "image": share_image(path),
         "author": {"@id": f"{BASE}/#org"}, "publisher": {"@id": f"{BASE}/#org"}, "about": {"@id": f"{BASE}/#app"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE}/"},
            {"@type": "ListItem", "position": 2, "name": section, "item": f"{BASE}/{'features' if section == 'PDF tools' else 'guides'}"},
            {"@type": "ListItem", "position": 3, "name": title, "item": url}]},
    ]
    if faq:
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
    return [{"@context": "https://schema.org", "@graph": graph}]


def page(title: str, description: str, path: str, content: str, extra_schema: list[dict] | None = None) -> str:
    e_title, e_description = escape(title), escape(description)
    path = {"/privacy": "/privacy-policy", "/terms": "/terms-of-service", "/blog": "/guides"}.get(path, path)
    og_type = "article" if extra_schema else "website"
    image = share_image(path)
    if path not in {"/privacy-policy", "/terms-of-service"}:
        OG_PAGES[path.strip("/")] = {"title": title}
    schemas = "".join(schema_script(data) for data in [software_schema()] + (extra_schema or []))
    return f'''<!doctype html>
<html lang="en"><head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#f8f7f3"><meta name="description" content="{e_description}"><meta name="robots" content="index, follow"><meta name="apple-itunes-app" content="app-id=6760956540, app-argument={BASE}{path}">
    <meta property="og:type" content="{og_type}"><meta property="og:site_name" content="{SITE_NAME}"><meta property="og:title" content="{e_title}">
    <meta property="og:description" content="{e_description}"><meta property="og:url" content="{BASE}{path}"><meta property="og:image" content="{image}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
        <meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e_title}"><meta name="twitter:description" content="{e_description}"><meta name="twitter:image" content="{image}">
    {schemas}
  <link rel="canonical" href="{BASE}{path}"><link rel="icon" href="/assets/icon.png" type="image/png">
  <link rel="stylesheet" href="/styles.css"><title>{e_title} — ProperPDF</title>
</head><body><a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="container nav-inner">
  <a class="brand" href="/"><img src="/assets/icon.png" alt="" width="38" height="38"><span>ProperPDF</span></a>
  <nav aria-label="Main navigation"><a href="/features">Features</a><a href="/pricing">Pricing</a><a href="/guides">Guides</a></nav>
    <a class="nav-cta smart-download" href="{IOS_UTM}" data-ios-href="{IOS_UTM}" data-android-href="{ANDROID_UTM}">Download on iPhone <span aria-hidden="true">↗</span></a>
</div></header>
<main id="main">{content}</main>
<footer class="site-footer"><div class="container footer-main"><div><a class="brand" href="/"><img src="/assets/icon.png" alt="" width="34" height="34"><span>ProperPDF</span></a><p>Offline PDF tools for iPhone and Android.</p></div><div class="footer-links"><a href="/guides">Guides</a><a href="/pricing">Pricing</a><a href="/support">Support</a><a href="/how-offline-works">How offline works</a><a href="/changelog">Changelog</a><a href="/about">About</a><a href="/press">Press</a><a href="/privacy-policy">Privacy policy</a><a href="/terms-of-service">Terms</a></div></div><div class="container footer-bottom"><span>© 2026 ProperPDF</span><span>PDF processing on your device.</span></div></footer>
<script>(function () {{ var ua = navigator.userAgent; var platform = /Android/i.test(ua) ? 'android' : /iPhone|iPad|iPod/i.test(ua) ? 'ios' : 'desktop'; document.body.dataset.platform = platform; document.querySelectorAll('.smart-download').forEach(function (link) {{ if (platform === 'android') {{ link.href = link.dataset.androidHref; link.innerHTML = 'Get it on Google Play <span aria-hidden="true">↗</span>'; }} }}); }}());</script>
<script src="/site-data.js?v=1" defer></script>
</body></html>'''


def write_static_files(slugs: list[str]) -> None:
    (PUBLIC / "_headers").write_text(
        "/*\n  X-Content-Type-Options: nosniff\n  X-Frame-Options: DENY\n  Referrer-Policy: strict-origin-when-cross-origin\n",
        encoding="utf-8",
    )
    aliases = {"privacy": "privacy-policy", "terms": "terms-of-service", "blog": "guides"}
    redirects = ["/index.html / 301"]
    redirects += [f"/{slug}.html /{slug} 301" for slug in slugs]
    for alias, target in aliases.items():
        redirects += [f"/{alias} /{target} 301", f"/{alias}/ /{target} 301", f"/{alias}.html /{target} 301"]
    (PUBLIC / "_redirects").write_text("\n".join(redirects) + "\n", encoding="utf-8")
    (PUBLIC / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY, encoding="utf-8")


def paragraph(text: str) -> str:
    return f"<p>{escape(text)}</p>"


def cta() -> str:
    return f'''<aside class="content-cta"><p class="kicker">GET THE APP</p><h2>Download ProperPDF</h2><p>Free on the App Store and Google Play. No account needed.</p>{download_buttons("landing-page")}</aside>'''


def facts_table(slug: str) -> str:
    """Plain at-a-glance table for one tool, so the price and limits are stated, not implied."""
    name, ios, android = TOOL_BY_SLUG[slug]
    long = lambda v: "Free, with a ProperPDF watermark on the saved file (Pro removes it)" if v == FREE_WM else v
    rows = [("iPhone and iPad", long(ios)), ("Android", long(android)), ("Works offline", "Yes"),
            ("Files uploaded", "No, processing happens on the device"), ("Account needed", "No"), ("Requires", REQUIREMENTS)]
    body = "".join(f'<tr><th scope="row">{escape(k)}</th><td>{escape(v)}</td></tr>' for k, v in rows)
    return f'<table class="facts-table"><caption>{escape(name)} in ProperPDF at a glance</caption><tbody>{body}</tbody></table>'


def tools_table() -> str:
    """Every tool with its Free/Pro status on each platform."""
    rows = []
    for name, slug, ios, android in TOOLS:
        label = f'<a href="/{slug}">{escape(name)}</a>' if slug else escape(name)
        rows.append(f'<tr><th scope="row">{label}</th><td>{escape(ios)}</td><td>{escape(android)}</td></tr>')
    rows = "".join(rows)
    return f'<table class="facts-table tools-table"><thead><tr><th scope="col">Tool</th><th scope="col">iPhone and iPad</th><th scope="col">Android</th></tr></thead><tbody>{rows}</tbody></table><p class="table-note">{escape(WATERMARK_NOTE)}</p>'


def faq_html(faq: list) -> str:
    items = "".join(f"<h3>{escape(q)}</h3><p>{escape(a)}</p>" for q, a in faq)
    return f'<section class="article-faq"><h2>Questions</h2>{items}</section>'


features = [
    dict(slug="merge-pdf", title="Merge PDFs on iPhone and Android without uploading",
         description="Combine PDF files into one on iPhone, iPad or Android. ProperPDF merges them on your phone, offline, with no account. Free to use.",
         lead="Pick the files, set the order, save one PDF. Nothing leaves your phone.",
         answer="To merge PDFs on your phone without uploading them, open Merge PDF in ProperPDF, pick two or more files, drag them into the order you want and save. The app joins them on the device, so it works offline and you don't need an account. Merging is free on iPhone, iPad and Android. Free exports carry a ProperPDF watermark, which Pro removes.",
         steps_title="How to merge PDFs in ProperPDF",
         steps=["Open ProperPDF and tap Merge PDF.", "Select two or more PDFs.", "Long-press a file and drag it to change the merge order.", "Save. The merged PDF appears in your library and the original files stay as they were.", "Open the result to check it, then share it from the share sheet."],
         sections=[
             ("When merging helps", ["A contract with its attachments, a visa application with its supporting documents, a month of receipts: one PDF is easier to send and easier to find later than five separate files.", "Merging copies the pages as they are. It doesn't re-compress them, so text and scans look the same as in the originals."]),
             ("After you merge", ["Use Organize Pages to reorder, rotate or delete pages in the merged file. If it's too big for email, Compress PDF (Pro) saves a smaller copy."]),
         ],
         faq=[
             ("Is merging PDFs free in ProperPDF?", "Yes, on both iPhone and Android. The saved file gets a ProperPDF watermark unless you have Pro."),
             ("Are my PDFs uploaded when I merge them?", "No. ProperPDF merges the files on your phone and doesn't send them to a server, so it also works in airplane mode."),
             ("Does merging lower the quality of my PDF?", "No. The pages are copied into the new file without being re-compressed."),
             ("Can I merge PDFs on iPhone without an app?", "On iOS 26 and later, yes: Apple's Preview app can insert pages from another PDF. See our guide to merging PDFs on iPhone without an app."),
         ], related=["split-pdf", "compress-pdf"]),
    dict(slug="split-pdf", title="Split a PDF on iPhone and Android without uploading",
         description="Extract pages from a PDF on iPhone, iPad or Android. Split by page range or every few pages, offline, with no account. Free to use.",
         lead="Keep the pages you need as a new PDF. The original stays untouched.",
         answer="To split a PDF on your phone, open Split PDF in ProperPDF, choose the document, then enter a page range or split it every few pages. The app saves the extracted pages as a new PDF and leaves the original as it was. It runs offline on iPhone, iPad and Android, and it's free. Free exports carry a ProperPDF watermark, which Pro removes.",
         steps_title="How to split a PDF in ProperPDF",
         steps=["Open ProperPDF and tap Split PDF.", "Select the PDF you want to split.", "Choose how to split it: a range (for example pages 3 to 7) or an interval (a new file every N pages). On Android you can also tick individual pages.", "Save. The new PDF appears in your library and the original stays available."],
         sections=[
             ("Share only the pages that matter", ["A long PDF often holds more than the person receiving it needs: one chapter of a report, the signed pages of a contract, a single bank statement out of a year. Sending only those pages keeps the file small and keeps the rest private."]),
             ("Need to rearrange instead?", ["Use Organize Pages to drag pages into a different order, rotate them or delete them. Use Merge PDF to bring pages from separate files together."]),
         ],
         faq=[
             ("Can I extract a single page from a PDF?", "Yes. Enter the same page as the start and end of the range, and ProperPDF saves that page as its own PDF."),
             ("Does splitting change the original PDF?", "No. ProperPDF writes the extracted pages to a new file."),
             ("Is splitting free?", "Yes, on iPhone and Android. Without Pro the saved file has a ProperPDF watermark."),
         ], related=["merge-pdf", "pdf-to-image"]),
    dict(slug="compress-pdf", title="Compress a PDF on iPhone and Android without uploading",
         description="Reduce PDF file size on iPhone, iPad or Android. ProperPDF compresses on the device, offline, so the document is never uploaded.",
         lead="Make a large PDF small enough to email, without sending it to an online compressor.",
         answer="ProperPDF compresses PDFs on the phone itself: pick the file, lower the image resolution, check the estimated size and save a smaller copy. Nothing is uploaded, so it works offline. Compression is a Pro feature on iPhone, iPad and Android. It shrinks scanned and photo-heavy PDFs the most. A PDF that is mostly text may barely change, because text is already compact.",
         steps_title="How to compress a PDF in ProperPDF",
         steps=["Open ProperPDF and tap Compress PDF.", "Select the PDF.", "Move the image resolution slider. Lower means a smaller file and softer images. The app shows the current size and an estimate of the new one.", "Save. ProperPDF writes a new, smaller copy and keeps the original.", "Open the copy and zoom in on small text and signatures before you send it."],
         sections=[
             ("Why compress on the device", ["Online compressors have to receive your file before they can shrink it. That is fine for a flyer, less fine for a payslip, a medical letter or a signed contract. ProperPDF does the same job without the upload."]),
             ("Getting a smaller file", ["Scans and photo-heavy PDFs shrink the most; a 20-page text export from Word has very little to give. If the file is still too big, split off or delete the pages the recipient doesn't need, which cuts size without touching quality.", "On iPhone, compression currently turns each page into an image. Text in the copy can no longer be selected or searched, and form fields, links and annotations are removed, so keep the original if you need those. On Android, only the images inside the PDF are shrunk."]),
         ],
         faq=[
             ("Is PDF compression free in ProperPDF?", "No. Compress PDF is part of Pro on both iPhone and Android."),
             ("How much smaller will my PDF get?", "It depends on the file. Scans and photo-heavy PDFs often shrink a lot; text-only PDFs may hardly change. The app shows an estimated size before you save."),
             ("Will compression make my PDF blurry?", "Lower resolutions soften images and scanned text. Save, zoom in on the smallest text, and pick a higher setting if it's hard to read."),
             ("Will I still be able to select text after compressing?", "On Android, yes. On iPhone, compression currently turns pages into images, so text can't be selected and form fields and links are removed. ProperPDF keeps your original file."),
         ], related=["split-pdf", "merge-pdf"]),
    dict(slug="pdf-to-image", title="Convert PDF pages to images offline",
         description="Export PDF pages as PNG or JPEG images on iPhone, iPad or Android, offline and without uploading the document.",
         lead="Turn the pages you choose into PNG or JPEG images.",
         answer="To turn PDF pages into images, open PDF to Image in ProperPDF, pick the pages, choose PNG or JPEG and save. The conversion happens on the device, offline. It's free on iPhone and iPad. On Android it's free with a ProperPDF watermark on the images, which Pro removes.",
         steps_title="How to convert a PDF to images in ProperPDF",
         steps=["Open ProperPDF and tap PDF to Image.", "Select the PDF and choose the pages to export.", "Pick PNG or JPEG.", "Save the images, or share them straight from the app."],
         sections=[
             ("PNG or JPEG?", ["PNG keeps text and line drawings sharp and is the better choice for slides, diagrams and documents. JPEG files are smaller and are fine for photo-heavy pages."]),
             ("Going the other way", ["To make a PDF from photos or screenshots, use Image to PDF. To capture paper pages with the camera, use Scan to PDF."]),
         ],
         faq=[
             ("Can I convert only some pages?", "Yes. Choose the pages you want before exporting."),
             ("Is PDF to image free?", "Yes. On Android the images carry a ProperPDF watermark unless you have Pro; on iPhone and iPad they don't."),
         ], related=["image-to-pdf", "split-pdf"]),
]

feature_lookup = {item["slug"]: item for item in features}


# Place each existing app mockup beside the section it illustrates (index 0 is the
# steps section). Home-screen images are labelled as tool menus, not as
# screenshots of a conversion result.
article_mockups = {
    "merge-pdf": (0, "android/1merge-portrait.png", "Merge PDF on Android", "The Merge PDF screen in ProperPDF for Android."),
    "split-pdf": (0, "android/2split-portrait.png", "Split PDF on Android", "The Split PDF screen in ProperPDF for Android."),
    "compress-pdf": (0, "android/3compress-portrait.png", "PDF compression settings on Android", "Adjust image resolution in the Android compression screen. Results depend on the source PDF."),
    "pdf-to-image": (0, "ios/pdf-to-image-portrait.png", "PDF to Image screen in ProperPDF on iPhone, with PNG selected and four pages chosen", "Pick PNG or JPEG, tick the pages you want, then convert. Here 4 pages of a 1,153-page PDF are selected."),
    "offline-pdf-editor-iphone": (1, "ios/merge-portrait.png", "Selected PDFs and merge order on iPhone", "The iPhone Merge PDF screen shows the selected files and their order before merging."),
    "private-pdf-workflow": (1, "ios/lock-portrait.png", "PDF password protection screen on iPhone", "The Lock PDF screen in ProperPDF for iPhone."),
    "offline-pdf-editor-android": (1, "android/1merge-portrait.png", "Merge PDF screen in ProperPDF for Android", "Combine documents using Merge PDF in the Android app."),
    "private-pdf-compressor": (0, "android/3compress-portrait.png", "Image resolution setting for PDF compression on Android", "The Android compression screen lets you adjust image resolution. Check text and signatures in the saved copy."),
    "offline-pdf-merger-android": (0, "android/1merge-portrait.png", "Merge PDF screen on Android", "The Android Merge PDF screen used to combine your documents."),
    "lock-pdf": (0, "ios/lock-portrait.png", "Lock PDF screen on iPhone", "Password protection in the iPhone app. The Android screen looks different."),
    "sign-pdf": (0, "ios/sign-portrait.png", "Sign PDF screen on iPhone", "The Sign PDF screen in ProperPDF for iPhone. The Android screen looks different."),
    "fill-pdf": (0, "ios/fill-portrait.png", "Fill PDF screen on iPhone", "The Fill PDF screen in ProperPDF for iPhone. The Android screen looks different."),
    "image-to-pdf": (0, "ios/image-to-pdf-portrait.png", "Image to PDF screen in ProperPDF on iPhone with two images in page order", "Drag the handle to reorder images. Each image becomes one page of the PDF."),
    "scan-to-pdf": (0, "ios/home-portrait.png", "iPhone tools menu showing Scan Document", "Choose Scan Document from the iPhone tools menu shown here."),
}


def mockup_figure(image: str, alt: str, caption: str) -> str:
    asset = PUBLIC / "assets" / "mockups" / image
    # PNG's IHDR stores the intrinsic dimensions; reserve the correct ratio.
    header = asset.read_bytes()[:24]
    width = int.from_bytes(header[16:20], "big")
    height = int.from_bytes(header[20:24], "big")
    full = f"/assets/mockups/{image}"
    # Show the 480px WebP (about 25 KB) and link the full-size PNG.
    small = image.removesuffix(".png") + "-480.webp"
    src = f"/assets/mockups/{small}" if (PUBLIC / "assets" / "mockups" / small).exists() else full
    return f'''<figure class="article-mockup"><a href="{escape(full)}" target="_blank" rel="noopener" aria-label="{escape('View full-size screenshot: ' + alt)}"><img src="{escape(src)}" alt="{escape(alt)}" width="480" height="{round(height * 480 / width)}" loading="lazy" decoding="async"></a><figcaption>{escape(caption)} <a href="{escape(full)}" target="_blank" rel="noopener">View full-size screenshot</a></figcaption></figure>'''

def article_body(item: dict) -> str:
    """Answer first, then the facts, numbered steps, supporting sections and FAQ."""
    blocks = [f'<p class="answer">{escape(item["answer"])}</p>']
    if item.get("tool_table"):
        blocks.append(tools_table())
    elif item["slug"] in TOOL_BY_SLUG:
        blocks.append(facts_table(item["slug"]))
    sections = list(item["sections"])
    if item.get("steps"):
        sections.insert(0, (item["steps_title"], {"steps": item["steps"]}))
    illustration = article_mockups.get(item["slug"])
    for index, (title, body) in enumerate(sections):
        if isinstance(body, dict):
            html = "<ol class=\"steps\">" + "".join(f"<li>{escape(step)}</li>" for step in body["steps"]) + "</ol>"
        else:
            html = "".join(map(paragraph, body))
        if illustration and illustration[0] == index:
            html += mockup_figure(*illustration[1:])
        blocks.append(f"<section><h2>{escape(title)}</h2>{html}</section>")
    if item.get("faq"):
        blocks.append(faq_html(item["faq"]))
    return "".join(blocks)


def hero(kicker: str, item: dict) -> str:
    return f'''<div class="content-hero guide-hero"><div class="container"><p class="kicker">{kicker}</p><h1>{escape(item["title"])}</h1><p>{escape(item["lead"])}</p><p class="landing-proof">Offline processing · No account required</p>{download_buttons("tool-header")}<p class="updated">Updated {UPDATED_LABEL}</p></div></div>'''


def feature_html(item: dict) -> str:
    related = "".join(f'<a href="/{slug}">{escape(page_lookup[slug]["title"])} <span aria-hidden="true">↗</span></a>' for slug in item["related"])
    return f'''{hero("PROPERPDF TOOL GUIDE", item)}<div class="container content-layout"><article class="article-body">{article_body(item)}{cta()}</article><aside class="related-links"><p class="kicker">MORE PDF TOOLS</p>{related}<a href="/features">All PDF tools <span aria-hidden="true">↗</span></a><a href="/pricing">Free vs Pro <span aria-hidden="true">↗</span></a><a href="/guides">Read all guides <span aria-hidden="true">↗</span></a></aside></div>'''


guides = [
    dict(slug="offline-pdf-editor-iphone", title="Offline PDF editor for iPhone and iPad",
         description="ProperPDF scans, merges, splits, compresses, signs, fills and locks PDFs offline on iPhone and iPad, with no uploads and no account.",
         lead="What ProperPDF can and can't do on iPhone, what's free, and what needs Pro.",
         answer="ProperPDF is an offline PDF app for iPhone and iPad (iOS 17 or later). It scans, merges, splits, organizes, converts, compresses, signs, fills and password-protects PDFs on the device, without uploading them and without an account. Scanning, merging, splitting, organizing, converting and the on-device AI chat are free; compress, sign, fill and lock need Pro. It doesn't edit the existing text in a PDF and doesn't have highlighting or annotation yet.",
         tool_table=True,
         sections=[
             ("A typical workflow", ["Scan the paper pages, or import a PDF into the library. Merge it with any attachments, drop the pages nobody needs with Split or Organize Pages, sign it, then share it from the share sheet. Each step saves a new copy, so the original stays available."]),
             ("What it doesn't do", ["ProperPDF can't change the existing text in a PDF, convert PDF to Word, or add highlights, comments and drawings. If you need those, PDF Expert or Adobe Acrobat Reader are better fits. Both annotate for free, and both charge for text editing. On iOS 26 and later, Apple's built-in Preview app can also highlight and draw on PDFs."]),
             ("Offline, with one exception", ["The PDF tools need no internet connection at all. The on-device AI chat and summary may need a one-time model download on some devices before it can work offline."]),
         ],
         faq=[
             ("Does ProperPDF work without internet on iPhone?", "Yes. All PDF tools run on the device. The AI feature may need a one-time model download first on some devices."),
             ("Is ProperPDF free on iPhone?", "The app is free to download. Scan, merge, split, organize, convert and AI chat are free; merge and split add a watermark unless you have Pro. Compress, sign, fill forms and lock need Pro."),
             ("Can ProperPDF edit the text inside a PDF?", "No. It works with whole pages, signatures, form fields and passwords, not with the existing text."),
         ]),
    dict(slug="private-pdf-workflow", title="Is it safe to upload PDFs to online PDF tools?",
         description="What happens to a PDF when you upload it to an online converter, and how to merge, compress and sign documents on your phone instead.",
         lead="Online PDF tools need a copy of your file. Here's when that matters and what to do instead.",
         answer="Online PDF tools have to upload your file to their servers before they can merge, compress or convert it. Reputable services encrypt the transfer and delete files after a few hours, but you are still trusting a third party with the document. For contracts, IDs, medical or financial records, an app that processes the file on your phone, such as ProperPDF, avoids the upload entirely.",
         sections=[
             ("What an upload means", ["When you drop a PDF into a website, a copy travels to a server, gets processed there and is sent back. The service's privacy policy decides how long that copy is kept, who can access it and where it is stored. Most large services say they delete files within hours. That is a promise, not something you can check."]),
             ("When it's worth avoiding", ["A flyer or a public brochure doesn't need protecting. A passport scan, a payslip, a tax return, a lease or a medical letter does. If a leak of the file would worry you, do the work on your own device."]),
             ("How to keep the work on your phone", ["Use an app that states it processes files locally, and check it still works in airplane mode. ProperPDF merges, splits, compresses, signs and locks PDFs that way on iPhone, iPad and Android. Share only the pages the recipient needs, keep the original, and if you password-protect a file, send the password through a different channel than the PDF."]),
         ],
         faq=[
             ("How can I tell if a PDF app uploads my files?", "Turn on airplane mode and try the tool. If it still works, the processing happens on your device."),
             ("Does ProperPDF upload my documents?", "No. ProperPDF processes PDFs on the phone. The website doesn't accept uploads either."),
         ]),
    dict(slug="offline-pdf-editor-android", title="Offline PDF editor for Android",
         description="ProperPDF scans, merges, splits, compresses, signs, fills and locks PDFs offline on Android 8.0 and later, with no uploads and no account.",
         lead="What ProperPDF can and can't do on Android, what's free, and what needs Pro.",
         answer="ProperPDF is an offline PDF app for Android 8.0 and later. It scans, merges, splits, organizes, converts, compresses, signs, fills and password-protects PDFs on the phone, without uploading them and without an account. The scanning, merging, splitting, organizing and conversion tools are free, with a ProperPDF watermark on saved files; Pro removes the watermark and unlocks compress, sign, fill, lock and the on-device AI chat. It doesn't edit the existing text in a PDF.",
         tool_table=True,
         sections=[
             ("A typical workflow", ["Scan the pages with the camera or open a PDF from another app. Merge it with attachments, remove pages with Split or Organize Pages, add a signature and share it from Android's share sheet. Each step saves a new copy, so the original stays available."]),
             ("What it doesn't do", ["ProperPDF can't change the existing text in a PDF, convert PDF to Word, or add highlights and comments. Adobe Acrobat Reader and Xodo both annotate for free; text editing in Acrobat is a paid feature. PDFgear is a free option that edits text."]),
             ("Offline, with one exception", ["The PDF tools need no connection. The AI chat needs a one-time model download before it works offline."]),
         ],
         faq=[
             ("Does ProperPDF work offline on Android?", "Yes. All PDF tools run on the phone. The AI chat needs a one-time model download first."),
             ("Which Android versions does ProperPDF support?", "Android 8.0 and later."),
             ("Does ProperPDF have ads?", "No. The free version adds a watermark to files saved with some tools instead."),
         ]),
    dict(slug="private-pdf-compressor", title="Compress a PDF without uploading it",
         description="Shrink a PDF privately on iPhone, iPad or Android. ProperPDF compresses on the device instead of sending the file to an online compressor.",
         lead="Shrink a PDF for email without handing it to a website.",
         answer="To compress a PDF without uploading it, use an app that does the work on your phone. In ProperPDF, open Compress PDF, pick the file, lower the image resolution and save a smaller copy. The file never leaves the device and the tool works offline. Compression is part of ProperPDF Pro on iPhone, iPad and Android.",
         steps_title="Compress privately in four steps",
         steps=["Open ProperPDF and tap Compress PDF.", "Select the PDF.", "Lower the image resolution until the estimated size is small enough.", "Save the copy, then zoom in on small text and signatures to check them."],
         sections=[
             ("Why not an online compressor?", ["Sites like Smallpdf and iLovePDF process your file on their servers. Smallpdf says it deletes uploads after one hour, and for most documents that's fine. For a payslip, a medical letter or a signed contract, skipping the upload removes the question."]),
             ("If the file is still too big", ["Text-heavy PDFs have little to compress. Remove the pages the recipient doesn't need with Split PDF or Organize Pages, which cuts size without touching quality.", "On iPhone, compression currently turns pages into images, so the copy loses selectable text, form fields and links. Keep the original if you need them."]),
         ],
         faq=[
             ("Can I compress a PDF offline?", "Yes. ProperPDF compresses PDFs on iPhone, iPad and Android without an internet connection."),
             ("Is it free?", "No. Compress PDF is a Pro tool in ProperPDF."),
         ]),
    dict(slug="offline-pdf-merger-android", title="Merge PDFs offline on Android",
         description="Combine PDF files on Android without uploading them. ProperPDF merges scans, receipts, forms and reports on the phone. Free to use.",
         lead="Combine PDFs on Android in airplane mode if you like.",
         answer="To merge PDFs offline on Android, install ProperPDF, open Merge PDF, select the files, drag them into order and save. The merge runs on the phone, so it works without a connection and nothing is uploaded. It's free on Android 8.0 and later; free exports carry a ProperPDF watermark, which Pro removes.",
         steps_title="How to merge PDFs on Android",
         steps=["Open ProperPDF and tap Merge PDF.", "Select two or more PDFs.", "Drag the files into the order you want.", "Save, then open the merged file to check it before sharing."],
         sections=[
             ("Good for private paperwork", ["Applications with their attachments, invoices, medical paperwork and scans of IDs are the kind of files you'd rather not send to a website just to staple them together."]),
             ("After merging", ["Use Organize Pages to fix the order or remove a page. If the file is too large, Compress PDF (Pro) saves a smaller copy."]),
         ],
         faq=[
             ("Can Android merge PDFs without an app?", "Google's own apps (Files by Google and Google Drive) don't have a merge tool, so you need an app or a website. Some phone makers ship their own PDF tools. ProperPDF merges offline on any phone with Android 8.0 or later."),
             ("Is merging free on Android?", "Yes. Without Pro the merged file carries a ProperPDF watermark."),
         ]),
    dict(slug="lock-pdf", title="Password protect a PDF on your phone",
         description="Add a password to a PDF on iPhone, iPad or Android with ProperPDF, offline. Also restrict printing and editing, or remove a password you know.",
         lead="Add a password before you share a PDF with private details in it.",
         answer="To password-protect a PDF on your phone, open Lock PDF in ProperPDF, pick the file, enter and confirm a password and save the protected copy. It runs offline on iPhone, iPad and Android. Lock and Unlock are Pro tools. ProperPDF can't recover a forgotten password, so keep the original or store the password safely.",
         steps_title="How to lock a PDF in ProperPDF",
         steps=["Open ProperPDF and tap Lock/Unlock PDF.", "Select the PDF.", "Type a password and confirm it, or tap Generate Strong Password.", "Save. ProperPDF writes a protected copy.", "Open the copy and test the password before you send it."],
         sections=[
             ("Open passwords and restrictions", ["A full lock means nobody can open the PDF without the password. You can also set restrictions instead, which let people open the file but limit printing or editing in standard PDF viewers. Restrictions are easier to bypass with specialist tools than an open password."]),
             ("Share the password separately", ["Send the PDF by email and the password by text message or a call. If both travel in the same thread, the lock does little."]),
             ("Removing a password", ["If you know a PDF's password and want an unlocked copy, use Unlock in the same tool."]),
         ],
         faq=[
             ("Can ProperPDF remove a password I don't know?", "No. Unlock needs the current password."),
             ("Is locking a PDF free?", "No. Lock and Unlock are part of ProperPDF Pro."),
         ], related=["sign-pdf", "compress-pdf"]),
    dict(slug="sign-pdf", title="Sign a PDF on your phone without uploading it",
         description="Draw your signature and place it on a PDF on iPhone, iPad or Android. ProperPDF signs documents offline, with no account.",
         lead="Sign a form or agreement on your phone without sending it to an e-signature website.",
         answer="To sign a PDF on your phone, open Sign PDF in ProperPDF, choose the document, draw your signature with your finger (or pick one you saved before), place it on the page, resize it and save. Signing happens on the device, offline and without an account. It's a Pro tool on iPhone, iPad and Android. This adds a drawn signature to the page; it isn't a certificate-based digital signature.",
         steps_title="How to sign a PDF in ProperPDF",
         steps=["Open ProperPDF and tap Sign PDF.", "Select the document.", "Draw your signature, or choose a saved one.", "Tap the page where it belongs, then move and resize it.", "Save a signed copy and check every page before sending."],
         sections=[
             ("Drawn signature vs digital signature", ["ProperPDF places an image of your handwritten signature on the page, which is what most forms, leases and permission slips ask for. Some legal and government processes need a certificate-based digital signature instead, which tools like Foxit PDF Editor's paid plan create. ProperPDF doesn't."]),
             ("Fill first, then sign", ["If the document is a form, complete the fields with Fill PDF first, then add your signature."]),
         ],
         faq=[
             ("Is signing a PDF free in ProperPDF?", "No. Sign PDF is a Pro tool on both iPhone and Android."),
             ("Can I reuse my signature?", "Yes. On iPhone you can pick a signature you created earlier instead of drawing it again."),
             ("Is my signature uploaded?", "No. The signature and the document stay on your phone."),
         ], related=["fill-pdf", "lock-pdf"]),
    dict(slug="fill-pdf", title="Fill PDF forms on your phone",
         description="Fill PDF forms on iPhone, iPad or Android with ProperPDF, offline: type into form fields, or add text to a scanned or flat form, and save a copy.",
         lead="Type into form fields, tick checkboxes and save the finished PDF.",
         answer="To fill a PDF form on your phone, open Fill PDF in ProperPDF, pick the form, type into its fields, tick the checkboxes and save a completed copy. It works offline on iPhone, iPad and Android and is a Pro tool. If the PDF has no form fields, such as a scanned form, ProperPDF switches to placing text where you tap instead.",
         steps_title="How to fill a PDF form in ProperPDF",
         steps=["Open ProperPDF and tap Fill Forms.", "Select the PDF form.", "Tap each field to type, and tap checkboxes to tick them. On a form without fields, tap where the text should go and type it.", "Save. The completed form is a new copy, so the blank original stays available.", "If it needs a signature, open the completed copy in Sign PDF."],
         sections=[
             ("Forms with and without fields", ["Many government, school and HR forms have built-in fields; ProperPDF finds them and you type straight into them. A scanned or flat form has no fields, so ProperPDF lets you place text on the page instead. That works, but the text isn't a form field, so check it lines up with the boxes before you send it."]),
             ("Before sending", ["Check names, dates and numbers, then remove any pages the recipient doesn't need."]),
         ],
         faq=[
             ("Is filling PDF forms free?", "No. Fill Forms is a Pro tool in ProperPDF."),
             ("Can I fill a scanned form?", "Yes. When a PDF has no form fields, ProperPDF lets you tap anywhere on the page and type, so you can fill in scanned or flat forms."),
         ], related=["sign-pdf", "split-pdf"]),
    dict(slug="image-to-pdf", title="Turn photos into a PDF on your phone",
         description="Combine photos, screenshots and scans into one PDF on iPhone, iPad or Android with ProperPDF, offline. Free to use.",
         lead="Turn a handful of photos or screenshots into one PDF.",
         answer="To turn photos into a PDF, open Image to PDF in ProperPDF, select the images, put them in order and save. Each image becomes a page and the PDF is created on the device, offline. It's free on iPhone and iPad, and free on Android with a ProperPDF watermark that Pro removes.",
         steps_title="How to make a PDF from images",
         steps=["Open ProperPDF and tap Image to PDF.", "Select the photos or screenshots.", "Arrange the pages in the order you want.", "Save, then open the PDF to check it."],
         sections=[
             ("Useful for everyday paperwork", ["Receipts for an expense claim, photos of a whiteboard, screenshots of a booking, pages of handwritten notes. One PDF is easier to send than twelve photos."]),
             ("If the PDF is large", ["Phone photos are big, so a PDF made from them can be too. Compress PDF (Pro) makes a smaller copy."]),
         ],
         faq=[
             ("Is Image to PDF free?", "Yes. On Android the PDF carries a ProperPDF watermark unless you have Pro."),
             ("Are my photos uploaded?", "No. ProperPDF builds the PDF on your phone."),
         ], related=["scan-to-pdf", "merge-pdf"]),
    dict(slug="scan-to-pdf", title="Scan documents to PDF on your phone",
         description="Scan paper documents into PDFs with your phone camera on iPhone, iPad or Android. ProperPDF finds the page edges and saves offline.",
         lead="Point your camera at a page, review the scans and save one PDF.",
         answer="To scan a document to PDF, open Scan Document in ProperPDF and point the camera at the page. The scanner finds the edges and straightens the page; add more pages, review them and save one PDF. Scanning is free on iPhone and iPad and free on Android with a ProperPDF watermark that Pro removes. The scan stays on the device.",
         steps_title="How to scan a document in ProperPDF",
         steps=["Open ProperPDF and tap Scan Document.", "Hold the phone over the page. The scanner detects the edges and captures it.", "Scan the remaining pages.", "Review the scanned pages, then save them as one PDF."],
         sections=[
             ("Getting a clean scan", ["Lay the page flat on a dark surface, use daylight or an even light, and avoid your phone's shadow. Scan each page straight on."]),
             ("After scanning", ["Use Organize Pages to rotate or reorder pages, Merge PDF to attach the scan to another file, and Compress PDF (Pro) if it's too big to email."]),
         ],
         faq=[
             ("Is scanning free in ProperPDF?", "Yes. On Android the saved PDF carries a ProperPDF watermark unless you have Pro."),
             ("Does the scanner need internet?", "No. Scanning and saving happen on the phone."),
         ], related=["image-to-pdf", "merge-pdf"]),
]

# Comparison, alternatives and best-of pages. Every competitor claim must come
# from a source in the page's `sources` list (checked on CHECKED_LABEL). Leave a
# fact out rather than guess; re-check the sources before bumping the date.
CHECKED_LABEL = "22 October 2026"
SRC = {
    "acrobat_ios": ("Adobe Acrobat Reader on the App Store", "https://apps.apple.com/us/app/adobe-acrobat-reader-for-pdf/id469337564"),
    "acrobat_play": ("Adobe Acrobat Reader on Google Play", "https://play.google.com/store/apps/details?id=com.adobe.reader&hl=en_US"),
    "acrobat_faq": ("Adobe Acrobat mobile app FAQ", "https://helpx.adobe.com/acrobat/mobile-app-faq.html"),
    "acrobat_scan": ("Adobe Reader FAQ (scanning)", "https://helpx.adobe.com/sa_en/reader/faq.html"),
    "pdfexpert_ios": ("PDF Expert on the App Store", "https://apps.apple.com/us/app/pdf-expert-pdf-editor-reader/id743974925"),
    "pdfexpert_pricing": ("PDF Expert pricing", "https://pdfexpert.com/pricing"),
    "pdfexpert_privacy": ("PDF Expert app privacy notice", "https://pdfexpert.com/legal/privacy-app"),
    "pdfgear": ("PDFgear website", "https://www.pdfgear.com/"),
    "pdfgear_android": ("PDFgear for Android", "https://www.pdfgear.com/pdfgear-for-android/"),
    "pdfgear_play": ("PDFgear on Google Play", "https://play.google.com/store/apps/details?hl=en&id=com.pdfeditor.pdfeditorandriod"),
    "smallpdf_play": ("Smallpdf on Google Play", "https://play.google.com/store/apps/details?id=com.smallpdf.app.android&hl=en_US"),
    "smallpdf_pricing": ("Smallpdf pricing", "https://smallpdf.com/pricing"),
    "ilovepdf_pricing": ("iLovePDF pricing", "https://www.ilovepdf.com/pricing"),
    "ilovepdf_faq": ("iLovePDF help and FAQ", "https://www.ilovepdf.com/help/faq"),
    "ilovepdf_privacy": ("iLovePDF privacy policy", "https://www.ilovepdf.com/help/privacy"),
    "foxit_play": ("Foxit PDF Editor on Google Play", "https://play.google.com/store/apps/details?id=com.foxit.mobile.pdf.lite&hl=en_US"),
    "foxit_sub": ("Foxit mobile help: subscribe and activate", "https://help.foxit.com/manuals/pdf-editor/mobile/en_us/2026.4.0/Subscribe_and_Activate_Foxit_PDF_Editor.html"),
    "xodo_plans": ("Xodo plans explained", "https://xodo.com/blog/xodo-plans-explained"),
    "xodo_ios": ("Xodo on the App Store", "https://apps.apple.com/us/app/all-pdf-reader-editor-xodo/id805075929"),
    "preview_start": ("Apple: get started with Preview on iPhone", "https://support.apple.com/guide/iphone/get-started-with-preview-on-iphone-iph7239ea3b5/ios"),
    "preview_pages": ("Apple: add, delete, rotate or move PDF pages on iPhone", "https://support.apple.com/guide/iphone/add-delete-rotate-move-or-crop-pdf-pages-iphbf4977cff/26/ios/26"),
    "preview_export": ("Apple: export or compress PDFs on iPhone", "https://support.apple.com/guide/iphone/export-or-compress-pdfs-and-images-iph61c20afe1/26/ios/26"),
    "preview_lock": ("Apple: lock PDFs on iPhone", "https://support.apple.com/guide/iphone/lock-pdfs-iphe85f2ea31/26/ios/26"),
    "preview_fill": ("Apple: fill out and sign PDF forms on iPhone", "https://support.apple.com/guide/iphone/fill-out-and-sign-pdf-forms-iphd7e3c0c74/26/ios/26"),
    "files_scan": ("Google: scan documents with Files by Google", "https://support.google.com/files/answer/15598575?hl=en"),
    "files_edit": ("Google: annotate PDFs in Files by Google", "https://support.google.com/files/answer/15949407?hl=en"),
    "files_topics": ("Files by Google help topics", "https://support.google.com/files/topic/7513702?hl=en"),
    "drive_scan": ("Google: scan documents with Google Drive", "https://support.google.com/drive/answer/3145835?co=GENIE.Platform%3DAndroid&hl=en"),
}

comparisons = [
    dict(slug="best-offline-pdf-apps", shot=('ios/home-portrait.png', 'ProperPDF tools on iPhone', 'ProperPDF on iPhone. Every tool here works in airplane mode.'), kicker="COMPARISON",
         title="The best PDF apps that work offline on iPhone and Android",
         description="Six PDF apps compared for working offline, without uploads: ProperPDF, PDFgear, Apple Preview, Files by Google, Foxit and Xodo. Prices and limits included.",
         lead="Which PDF apps keep working in airplane mode, what they cost, and what each one can't do.",
         answer="For PDF work without an internet connection, ProperPDF and PDFgear are the strongest picks on both iPhone and Android. ProperPDF does everyday jobs (scan, merge, split, compress, sign, lock) with no account. PDFgear is free and also edits text, but its AI needs a connection. On iPhone with iOS 26 or later, Apple's built-in Preview app covers scanning, signing, locking and inserting pages for free. On Android, Files by Google scans and annotates but can't merge or sign.",
         table=(["App", "Platforms", "Price", "Offline", "Edits existing text"], [
             ["ProperPDF", "iPhone, iPad, Android", "Free; Pro from $3.99 a month or $29.99 once (US)", "All tools; AI needs a one-time download", "No"],
             ["PDFgear", "iPhone, iPad, Android, desktop", "Free", "Editing and page tools; AI needs internet", "Yes"],
             ["Apple Preview", "iPhone and iPad (iOS 26+)", "Free, built in", "Built-in app", "No"],
             ["Files by Google", "Android", "Free", "Scans save on the device", "No"],
             ["Foxit PDF Editor", "iPhone, iPad, Android", "Free; subscription for advanced tools", "Not stated", "Paid"],
             ["Xodo", "iPhone, iPad, Android", "Free with watermark; subscription", "Not stated", "Not stated"],
         ]),
         disclosure=True,
         sections=[
             ("1. ProperPDF: everyday PDF jobs, no account", ["ProperPDF processes every file on the device and has no accounts and no ads. Scan, merge, split, organize and convert are free; merge and split add a watermark unless you have Pro, and on Android most free tools do. Compress, sign, fill forms and password protection need Pro ($3.99 a month, $19.99 a year or $29.99 once in the US, less in many countries).", "Limits: it can't edit the existing text in a PDF, convert to Word, or add highlights and comments."]),
             ("2. PDFgear: free, and it edits text", ["PDFgear says it is completely free, with no sign-up, ads or watermark, and it edits text and images and converts PDF to Word, Excel and PowerPoint. Its Android FAQ says editing and page management work offline, but the Copilot AI needs an internet connection because it uses OpenAI's ChatGPT API. Scanning is in a separate app, PDFgear Scan.", "Limits: PDFgear's mobile listings don't mention password protection, and its Android page notes that some advanced options could cost money in the future."]),
             ("3. Apple Preview: built into iPhone", ["iOS 26 added Preview to iPhone. It scans documents, fills and signs forms, inserts pages from another PDF (which is how you merge), rotates and reorders pages, locks a PDF with a password, and exports a smaller copy with a file-size slider. It's free and needs no account.", "Limits: iPhone and iPad only, iOS 26 or later. Merging means inserting one file at a time into another, and Apple doesn't say how much the size slider shrinks a PDF."]),
             ("4. Files by Google: scanning on Android", ["Files by Google scans pages into searchable PDFs saved on the phone, and lets you draw and highlight on a PDF. It's free.", "Limits: Google's help pages list no merge, split, compress, password or signature tool. Saving an annotated copy uploads it to Google Drive."]),
             ("5. Foxit PDF Editor", ["Foxit's free app opens, annotates, scans and fills PDFs, and adds handwritten signatures. Merging, compressing, password protection, OCR and editing need a subscription and a Foxit account. Foxit doesn't say which tools work offline."]),
             ("6. Xodo", ["Xodo's free version covers reading, annotating, scanning and signing, but Xodo says the free version adds a watermark to documents. Its iOS listing puts merging, high compression and PDF to Office behind a subscription. Xodo doesn't say which mobile tools work offline."]),
             ("How we compared them", ["We read each app's store listing, pricing page and help pages on " + CHECKED_LABEL + " and only list what the developer states. \"Not stated\" means we couldn't find it in their own documentation. Prices are US prices and change, so check the store before buying."]),
         ],
         faq=[
             ("Which PDF app works best offline?", "ProperPDF and PDFgear both work offline for their PDF tools on iPhone and Android. PDFgear is free and edits text; ProperPDF has no account and covers scan, merge, split, compress, sign and lock."),
             ("Is there a free PDF editor that works without internet?", "PDFgear is free and its Android FAQ says editing works offline. On iPhone with iOS 26 or later, Apple's built-in Preview app is free and on-device."),
             ("How can I check whether a PDF app uploads my files?", "Turn on airplane mode and run the tool. If it still works, the processing happens on your phone."),
         ],
         sources=["pdfgear", "pdfgear_android", "pdfgear_play", "preview_start", "preview_pages", "preview_export", "preview_lock", "preview_fill", "files_scan", "files_edit", "files_topics", "foxit_play", "foxit_sub", "xodo_plans", "xodo_ios"],
         related=["acrobat-alternatives", "ilovepdf-smallpdf-alternatives", "merge-pdf-iphone-without-app"]),
    dict(slug="acrobat-alternatives", shot=('ios/merge-portrait.png', 'Merge PDF screen in ProperPDF on iPhone', 'Merging is free in ProperPDF, with a watermark unless you have Pro.'), kicker="ALTERNATIVES",
         title="Adobe Acrobat Reader alternatives for iPhone and Android",
         description="Alternatives to Adobe Acrobat Reader on mobile for merging, compressing and signing PDFs: ProperPDF, PDFgear, PDF Expert, Apple Preview, Foxit and Xodo.",
         lead="Acrobat Reader is free for reading and signing. Merging, compressing and organizing pages are paid. Here are the alternatives.",
         answer="Adobe Acrobat Reader's free tier covers viewing, annotating and Fill & Sign, but merging, organizing pages, compressing, converting and password protection need a paid plan, and the Android app shows ads. If that's why you're looking: PDFgear is free and edits text; ProperPDF merges, splits and scans for free and sells Pro as a one-time purchase ($29.99 in the US); PDF Expert is the polished choice on iPhone and Mac; and iPhones on iOS 26 or later have Apple's Preview built in.",
         table=(["App", "Merge", "Compress", "Sign", "Price"], [
             ["Adobe Acrobat Reader", "Paid", "Paid", "Free (Fill & Sign)", "Free; subscription"],
             ["ProperPDF", "Free, with watermark", "Pro", "Pro", "Free; Pro $3.99 a month or $29.99 once (US)"],
             ["PDFgear", "Free", "Free", "Free", "Free"],
             ["PDF Expert (iPhone, iPad, Mac)", "Premium", "Premium", "Free", "Free; Premium $79.99 a year"],
             ["Apple Preview (iOS 26+)", "Insert pages from another PDF", "Export with a size slider", "Free", "Free, built in"],
             ["Foxit PDF Editor", "Subscription", "Subscription", "Free (handwritten)", "Free; subscription"],
         ]),
         disclosure=True,
         sections=[
             ("What Acrobat Reader does well", ["It's the most installed PDF reader (500M+ downloads on Google Play), Fill & Sign is free, and its paid plans edit text, export to Word, Excel and PowerPoint, and sync through Adobe's cloud. If you need those, the alternatives below won't replace it fully. Scanning lives in a separate app, Adobe Scan."]),
             ("ProperPDF", ["Merge, split, scan, organize and convert for free (with a watermark on some free exports), all offline, with no account and no ads. Compress, sign, fill and lock are Pro, and there's a lifetime option ($29.99 in the US, less in many countries) instead of a subscription. It doesn't edit text or annotate."]),
             ("PDFgear", ["Free with no sign-up, ads or watermarks according to PDFgear, and it edits text and converts to Office formats. Its AI assistant needs an internet connection."]),
             ("PDF Expert", ["iPhone, iPad and Mac only. Reading, annotating, and filling and signing forms are free; editing, merging, compressing, converting and the AI Copilot are Premium at $79.99 a year on Readdle's pricing page. Readdle's privacy notice says some AI features use OpenAI or Azure OpenAI."]),
             ("Apple Preview", ["On iOS 26 and later, Preview scans, fills and signs forms, inserts pages from another PDF, locks files and exports smaller copies, for free."]),
             ("Foxit PDF Editor", ["Free for viewing, annotating, scanning, filling forms and handwritten signatures. Merging, compressing, password protection and OCR need a subscription, which you activate by signing in to a Foxit account."]),
         ],
         faq=[
             ("Is there a free alternative to Adobe Acrobat on mobile?", "PDFgear is free with no stated limits. ProperPDF's merge, split, scan and convert tools are free with a watermark. On iPhone with iOS 26 or later, Apple's Preview app is free."),
             ("Can I merge PDFs for free without Acrobat?", "Yes. PDFgear merges for free, ProperPDF merges for free with a watermark, and Apple's Preview can insert pages from one PDF into another on iOS 26 or later."),
             ("Does Adobe Acrobat Reader have ads?", "Its Google Play listing says it contains ads. ProperPDF and PDFgear don't show ads."),
         ],
         sources=["acrobat_ios", "acrobat_play", "acrobat_faq", "acrobat_scan", "pdfgear", "pdfexpert_ios", "pdfexpert_pricing", "pdfexpert_privacy", "preview_start", "preview_pages", "foxit_play", "foxit_sub"],
         related=["properpdf-vs-adobe-acrobat", "best-offline-pdf-apps", "merge-pdf"]),
    dict(slug="ilovepdf-smallpdf-alternatives", shot=('ios/compress-portrait.png', 'Compress PDF screen in ProperPDF on iPhone', 'ProperPDF compresses on the phone and shows the estimated size before you save.'), kicker="ALTERNATIVES",
         title="iLovePDF and Smallpdf alternatives that don't upload your files",
         description="iLovePDF and Smallpdf process PDFs on their servers. These alternatives merge, compress and sign PDFs on your phone instead, offline.",
         lead="Both services process files on their servers. These apps do the work on your phone.",
         answer="iLovePDF and Smallpdf both process your PDFs on their own servers: Smallpdf says it deletes uploads after one hour, and iLovePDF describes securing files while they are on its servers. If you'd rather not upload a document, use an app that works on the device. ProperPDF (iPhone and Android) merges, splits, compresses and signs offline, PDFgear is free and edits text, and Apple's Preview does the basics on iPhones with iOS 26 or later.",
         table=(["", "Where files are processed", "Free tier", "Paid"], [
             ["Smallpdf", "Smallpdf's servers; deleted after one hour", "1 task a day in the Android app", "$7.99 a month on Google Play"],
             ["iLovePDF", "iLovePDF's servers", "Limited files per task", "$9 a month, or $60 a year"],
             ["ProperPDF", "On your phone", "Merge, split, scan, convert (some with watermark)", "$3.99 a month, $19.99 a year or $29.99 once (US; regional prices lower)"],
             ["PDFgear", "Android app works offline except the AI assistant", "Everything", "None"],
             ["Apple Preview (iOS 26+)", "On your iPhone", "Everything it does", "None"],
         ]),
         disclosure=True,
         sections=[
             ("Is uploading to iLovePDF or Smallpdf safe?", ["For most files, probably yes: both are established services, Smallpdf says it deletes uploads after an hour, and iLovePDF's privacy policy says it doesn't use file contents to train AI models. The question is whether you want a passport scan, payslip or medical letter on someone else's server at all, even briefly. If not, the tools below avoid the upload."]),
             ("What the online tools do better", ["Both have larger tool sets than any phone app here: PDF to Word with OCR, editing, translation, desktop apps and cloud storage integrations. iLovePDF also sells a desktop app that it markets for offline use."]),
             ("ProperPDF", ["Merge, split, scan, organize and convert for free, with a watermark on some free exports. Compress, sign, fill and lock are Pro. Everything runs on the phone, with no account."]),
             ("PDFgear", ["Free, with no sign-up. The apps edit, convert, compress, merge and split; its Android FAQ says these work offline, while the AI assistant needs a connection."]),
             ("Apple Preview", ["Built into iPhone from iOS 26: scan, fill, sign, insert pages from another PDF, lock with a password, and export a smaller copy."]),
         ],
         faq=[
             ("Does Smallpdf store my files?", "Smallpdf's Google Play listing says uploaded files are deleted one hour after processing unless you save them."),
             ("Is there an offline version of iLovePDF?", "iLovePDF markets its desktop app for offline use. On a phone, ProperPDF and PDFgear work offline."),
             ("What's the cheapest way to compress PDFs without uploading?", "PDFgear is free. ProperPDF includes compression in Pro, from $3.99 a month or $29.99 once in the US, with lower regional prices."),
         ],
         sources=["smallpdf_play", "smallpdf_pricing", "ilovepdf_pricing", "ilovepdf_faq", "ilovepdf_privacy", "pdfgear", "pdfgear_android", "preview_start", "preview_export"],
         related=["private-pdf-workflow", "private-pdf-compressor", "best-offline-pdf-apps"]),
    dict(slug="properpdf-vs-adobe-acrobat", shot=('android/1merge-portrait.png', 'Merge PDF screen in ProperPDF on Android', 'Merge on Android: free in ProperPDF, paid in Acrobat Reader.'), kicker="COMPARISON",
         title="ProperPDF vs Adobe Acrobat Reader on mobile",
         description="ProperPDF vs Adobe Acrobat Reader for iPhone and Android: which tools are free, offline use, accounts, ads and what each one can't do.",
         lead="Acrobat Reader gives away signing; ProperPDF gives away merging and splitting. The rest depends on what you need.",
         answer="Pick Adobe Acrobat Reader if you mainly read, annotate, and fill and sign forms: those are free in Acrobat. Pick ProperPDF if you mainly merge, split, scan and compress, want no account and no ads, and prefer a one-time purchase ($29.99 in the US) to a subscription. Acrobat's paid plans do much more, including editing text and exporting to Word; ProperPDF does neither.",
         table=(["", "ProperPDF", "Adobe Acrobat Reader"], [
             ["Merge and split", "Free, with watermark", "Paid"],
             ["Organize pages", "Free (watermark on Android)", "Paid"],
             ["Compress", "Pro", "Paid"],
             ["Fill and sign forms", "Pro", "Free"],
             ["Password protect", "Pro", "Paid"],
             ["Scan to PDF", "Free, in the app", "Separate Adobe Scan app"],
             ["Annotate and highlight", "No", "Free"],
             ["Edit existing text", "No", "Paid"],
             ["Export to Word", "No", "Paid"],
             ["AI chat", "On-device; free on iPhone, Pro on Android", "Paid AI Assistant"],
             ["Ads", "None", "Android listing says it contains ads"],
             ["Account", "None", "Sign-in needed to buy and to sync"],
             ["One-time purchase", "$29.99 lifetime (US)", "Not listed"],
         ]),
         disclosure=True,
         sections=[
             ("Where Acrobat wins", ["Annotating, filling forms and signing are free in Acrobat Reader and Pro-only in ProperPDF. Acrobat's paid plans also edit text and images, export to Word, Excel and PowerPoint, and sync files through Adobe's cloud. It is by far the more complete PDF editor."]),
             ("Where ProperPDF wins", ["Merging, splitting, organizing pages and scanning are free in ProperPDF and paid (or in a separate app) with Acrobat. ProperPDF has no account, no ads, works offline, and offers a one-time purchase."]),
         ],
         faq=[
             ("Is ProperPDF cheaper than Adobe Acrobat?", "ProperPDF Pro is $3.99 a month or $29.99 once in the US, and less in many other countries. We couldn't find Adobe's mobile prices on its website, so compare them in the store listing before buying."),
             ("Can ProperPDF edit text like Acrobat?", "No. ProperPDF works with pages, signatures, form fields and passwords, not the existing text."),
         ],
         sources=["acrobat_ios", "acrobat_play", "acrobat_faq", "acrobat_scan"],
         related=["acrobat-alternatives", "properpdf-vs-pdf-expert", "pricing"]),
    dict(slug="properpdf-vs-pdf-expert", shot=('android/8home1-portrait.png', 'ProperPDF tools on Android', 'ProperPDF also runs on Android, which PDF Expert does not.'), kicker="COMPARISON",
         title="ProperPDF vs PDF Expert on iPhone and iPad",
         description="ProperPDF vs PDF Expert by Readdle: free tools, Premium prices, offline use, Android support and what each app can't do.",
         lead="PDF Expert is the fuller editor. ProperPDF is the cheaper, offline, cross-platform toolkit.",
         answer="PDF Expert is the better editor: it edits text, converts to Office formats and annotates well, and reading, annotating, filling and signing are free. Its merge, compress and convert tools are Premium at $79.99 a year. ProperPDF merges, splits and scans for free, sells Pro for $19.99 a year or $29.99 once for lifetime access (US prices), has no account, and also runs on Android. PDF Expert has no Android app.",
         table=(["", "ProperPDF", "PDF Expert"], [
             ["Platforms", "iPhone, iPad, Android", "iPhone, iPad, Mac"],
             ["Merge, split, organize", "Free (merge and split with watermark)", "Premium"],
             ["Compress", "Pro", "Premium"],
             ["Fill and sign forms", "Pro", "Free"],
             ["Annotate", "No", "Free"],
             ["Edit text, convert to Word", "No", "Premium"],
             ["Scan with the camera", "Free", "Not listed"],
             ["AI", "On-device chat, free on iPhone", "AI Copilot, Premium; can use OpenAI or Azure OpenAI"],
             ["Yearly price (US)", "$19.99", "$79.99"],
             ["One-time purchase", "$29.99 lifetime (US)", "Not listed for iPhone"],
         ]),
         disclosure=True,
         sections=[
             ("Choose PDF Expert if", ["You annotate a lot, need to change text in PDFs, convert to Word, or work across iPhone, iPad and Mac. It's an Editors' Choice app with a 4.7 rating from over 200,000 App Store ratings."]),
             ("Choose ProperPDF if", ["Your work is mostly merging, splitting, scanning, compressing and signing, you also use Android, or you'd rather pay once than every year."]),
         ],
         faq=[
             ("Is PDF Expert free?", "Reading, annotating, and filling and signing forms are free. Editing, merging, compressing, converting and AI are part of Premium."),
             ("Does PDF Expert work on Android?", "No. It's available for iPhone, iPad and Mac. ProperPDF is on iPhone, iPad and Android."),
         ],
         sources=["pdfexpert_ios", "pdfexpert_pricing", "pdfexpert_privacy"],
         related=["acrobat-alternatives", "properpdf-vs-adobe-acrobat", "offline-pdf-editor-iphone"]),
    dict(slug="merge-pdf-iphone-without-app", shot=('ios/merge-portrait.png', 'Merge PDF screen in ProperPDF on iPhone', 'ProperPDF merges several files at once: pick them, drag them into order, save.'), kicker="GUIDE",
         title="How to merge PDFs on iPhone without an app",
         description="Combine PDFs on iPhone with Apple's built-in Preview app (iOS 26 and later), step by step, and what to use on older iOS versions.",
         lead="On iOS 26 and later, the Preview app can do it. On older versions, you'll need an app.",
         answer="On iOS 26 and later, open the first PDF in Apple's Preview app, tap the page count to show thumbnails, touch and hold a thumbnail, choose Insert from File and pick the second PDF. Its pages are added at that point, and you can drag thumbnails to reorder them. Apple only documents this in Preview, so on older iOS versions use an app such as ProperPDF, which merges several files at once for free.",
         steps_title="Merge PDFs with Preview (iOS 26 and later)",
         steps=["Open the first PDF in the Preview app.", "Tap the page count to show page thumbnails.", "Touch and hold the thumbnail where the other PDF should go.", "Choose Insert from File, then pick the second PDF.", "Drag thumbnails to fix the order, then share or save the file."],
         sections=[
             ("When Preview isn't enough", ["Preview inserts one file at a time, which gets slow with five or ten PDFs, and it isn't available before iOS 26. ProperPDF (iOS 17 and later) lets you pick several PDFs, drag them into order and merge them in one go, offline. Merging is free, with a watermark on the result unless you have Pro."]),
             ("Merging in ProperPDF", ["Open Merge PDF, select the files, long-press and drag to set the order, and save. The merged file appears in your library and the originals are left as they were."]),
             ("On Android", ["Google's own apps (Files by Google and Google Drive) don't merge PDFs. Use an app such as ProperPDF, which merges offline on Android 8.0 and later."]),
         ],
         faq=[
             ("Can the Files app merge PDFs on iPhone?", "Apple doesn't document a merge option in the iPhone Files app. Its documented route is the Preview app on iOS 26 and later."),
             ("Does merging in Preview upload my files?", "Preview is a built-in app that edits files on your iPhone."),
         ],
         sources=["preview_start", "preview_pages", "files_topics", "drive_scan"],
         related=["merge-pdf", "offline-pdf-merger-android", "best-offline-pdf-apps"]),
]


def comparison_html(item: dict) -> str:
    blocks = [f'<p class="answer">{escape(item["answer"])}</p>']
    if item.get("disclosure"):
        blocks.append('<p class="disclosure">We make ProperPDF. The other apps are described from their own store listings, pricing and help pages, linked under Sources.</p>')
    if item.get("table"):
        headers, rows = item["table"]
        head = "".join(f'<th scope="col">{escape(h)}</th>' for h in headers)
        body = "".join("<tr>" + f'<th scope="row">{escape(row[0])}</th>' + "".join(f"<td>{escape(cell)}</td>" for cell in row[1:]) + "</tr>" for row in rows)
        blocks.append(f'<div class="table-wrap"><table class="facts-table compare-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')
    sections = list(item["sections"])
    if item.get("steps"):
        sections.insert(0, (item["steps_title"], {"steps": item["steps"]}))
    shot_index = 0 if item.get("steps") else min(1, len(sections) - 1)
    for index, (title, paragraphs) in enumerate(sections):
        if isinstance(paragraphs, dict):
            html = '<ol class="steps">' + "".join(f"<li>{escape(step)}</li>" for step in paragraphs["steps"]) + "</ol>"
        else:
            html = "".join(map(paragraph, paragraphs))
        if item.get("shot") and index == shot_index:
            html += mockup_figure(*item["shot"])
        blocks.append(f"<section><h2>{escape(title)}</h2>{html}</section>")
    blocks.append(faq_html(item["faq"]))
    sources = "".join(f'<li><a href="{escape(SRC[key][1])}" rel="nofollow noopener" target="_blank">{escape(SRC[key][0])}</a></li>' for key in item["sources"])
    blocks.append(f'<section class="sources"><h2>Sources</h2><p>Checked {CHECKED_LABEL}. Prices are US prices and change. ProperPDF uses regional pricing, so check the store for your local price.</p><ol>{sources}</ol></section>')
    return "".join(blocks)


page_lookup = {item["slug"]: item for item in features + guides + comparisons}
page_lookup["pricing"] = {"title": "ProperPDF pricing: what's free and what's Pro"}


def guide_html(item: dict) -> str:
    related = item.get("related", ["merge-pdf", "split-pdf", "compress-pdf"])
    links = "".join(f'<a href="/{slug}">{escape(page_lookup[slug]["title"])} <span aria-hidden="true">↗</span></a>' for slug in related)
    return f'''{hero("PROPERPDF GUIDE", item)}<div class="container content-layout"><article class="article-body">{article_body(item)}{cta()}</article><aside class="related-links"><p class="kicker">KEEP EXPLORING</p>{links}<a href="/pricing">Free vs Pro <span aria-hidden="true">↗</span></a><a href="/guides">All guides <span aria-hidden="true">↗</span></a></aside></div>'''


def write(slug: str, title: str, description: str, content: str, extra_schema: list[dict] | None = None) -> None:
    path = f"/{slug}"
    (PUBLIC / f"{slug}.html").write_text(page(title, description, path, content, extra_schema), encoding="utf-8")


pricing_faq = [
    ("Is ProperPDF free?", "Yes, the app is free to download on the App Store and Google Play. Scan, merge, split, organize and convert are free. Some free exports carry a ProperPDF watermark. Compress, sign, fill forms and lock need Pro."),
    ("How much does ProperPDF Pro cost?", "In the US: $1.99 a week, $3.99 a month, $19.99 a year, or $29.99 once for lifetime access. ProperPDF uses regional pricing, so it costs less in many countries; the store shows your local price before you buy."),
    ("Is there a one-time purchase?", "Yes. Lifetime Pro is a single payment of $29.99 in the US, about a year and a half of the yearly plan, and less in many countries. There is no subscription to cancel."),
    ("Does ProperPDF have ads?", "No. The free version adds a watermark to files saved with some tools instead of showing ads."),
    ("Do I need an account?", "No. ProperPDF doesn't have accounts. Purchases go through your Apple or Google account."),
]

slugs = ["features", "guides", "support", "pricing", "privacy-policy", "terms-of-service", "how-offline-works", "changelog", "about", "press"] + [item["slug"] for item in features + guides + comparisons]
write_static_files(slugs)


# Trust pages: how offline processing works, the release history, and who makes the app.
# Network facts come from the shipped apps' dependencies (Firebase Analytics, Crashlytics
# and Messaging, RevenueCat, and the AI model download). Keep them in step with the code.
NETWORK_USES = [
    ("Buying Pro", "Your purchase and its status go through the App Store or Google Play, with RevenueCat checking whether Pro is active. No document data is involved."),
    ("Usage statistics", "Firebase Analytics records which tools are used and when something fails, so we know what to improve. It never receives the contents of your documents."),
    ("Crash reports", "Firebase Crashlytics sends a technical report when the app crashes. It contains no document content."),
    ("Notifications", "Firebase Cloud Messaging delivers the occasional tip or update notice. You can turn notifications off in your phone's settings."),
    ("The AI chat model", "AI chat runs on the device. On iPhones with Apple Intelligence it uses Apple's built-in model. On other iPhones and on Android, the app downloads a small open model once, then works offline."),
]

CHANGELOG = [
    # (version, month label, platform, [changes]). Newest first; user-facing changes only.
    ("1.4.2", "September 2026", "iPhone, iPad and Android", ["Open the ProperPDF website from Settings.", "Updated the support email and the Privacy Policy and Terms links."]),
    ("1.4.1", "September 2026", "Android", ["A new design that matches the iPhone app.", "A shorter first-run setup.", "The scanner no longer fails to open on phones without certified Google Play services."]),
    ("1.4.1", "September 2026", "iPhone and iPad", ["Performance and stability improvements."]),
    ("1.4.0", "June 2026", "iPhone and iPad", ["A redesigned app, from the home screen to every tool.", "A shorter first-run setup.", "Text you add in Fill Forms now looks and edits correctly."]),
    ("1.4.0", "May 2026", "Android", ["Merge, split and compress handle large PDFs without running out of memory.", "Split shows a full page preview.", "Pages render correctly in dark theme."]),
    ("1.3.0", "June 2026", "iPhone and iPad", ["AI chat rebuilt on Apple's on-device models, and you can start a chat from the library.", "Compression no longer makes already-optimized PDFs bigger."]),
    ("1.3.0", "April 2026", "Android", ["Place signatures on each page separately.", "A new first-run setup.", "Large PDFs no longer run out of memory."]),
    ("1.2.0", "May 2026", "iPhone and iPad", ["Redeem App Store offer codes from Settings."]),
    ("1.2.0", "March 2026", "Android", ["Organize Pages: reorder, rotate and delete pages.", "When locking a PDF, you can restrict printing and editing instead of requiring a password to open it.", "Stability fixes for large files and Image to PDF (1.2.1 and 1.2.2)."]),
    ("1.1.0", "May 2026", "iPhone and iPad", ["Sign several pages in one go.", "Five more languages.", "Runs on iOS 17 and later (previously a newer version was required).", "Better answers from AI chat."]),
    ("1.1.0", "February 2026", "Android", ["Fill forms that have no form fields by placing text on the page.", "Improved signing."]),
    ("1.0", "April 2026", "iPhone and iPad", ["First release: scan, merge, split, compress, organize, sign, fill, lock, convert, edit metadata and on-device AI chat, in six languages."]),
]


def info_page(slug: str, kicker: str, title: str, description: str, lead: str, body: str, faq: list | None = None) -> None:
    item = {"title": title, "lead": lead}
    faq_block = faq_html(faq) if faq else ""
    content = f'''{hero(kicker, item)}<div class="container content-layout"><article class="article-body">{body}{faq_block}{cta()}</article><aside class="related-links"><p class="kicker">KEEP EXPLORING</p><a href="/how-offline-works">How offline works <span aria-hidden="true">↗</span></a><a href="/changelog">Changelog <span aria-hidden="true">↗</span></a><a href="/about">About ProperPDF <span aria-hidden="true">↗</span></a><a href="/pricing">Free vs Pro <span aria-hidden="true">↗</span></a></aside></div>'''
    write(slug, title, description, content, article_schema(title, description, f"/{slug}", "Guides", faq))


network_rows = "".join(f'<tr><th scope="row">{escape(name)}</th><td>{escape(text)}</td></tr>' for name, text in NETWORK_USES)
offline_faq = [
    ("Does ProperPDF upload my PDFs?", "No. Every PDF tool runs on your phone or tablet. ProperPDF has no server that receives documents."),
    ("Does ProperPDF collect any data?", "Anonymous usage statistics and crash reports through Firebase, and purchase status through the App Store or Google Play. None of it includes the contents of your documents."),
    ("Can I check this myself?", "Yes. Turn on airplane mode and use any PDF tool. On iPhone you can also turn on App Privacy Report in Settings, Privacy & Security, to see every domain an app contacts."),
]
info_page("how-offline-works", "PRIVACY", "How ProperPDF works offline",
          "Every ProperPDF tool runs on your phone, so PDFs are never uploaded. Here is what does use the internet, what is collected, and how to check it yourself.",
          "What happens on your phone, what uses the internet, and how to check both.",
          f'''<p class="answer">ProperPDF does all PDF work on your phone or tablet: merging, splitting, compressing, signing, filling, locking, scanning and converting. Your documents never go to a ProperPDF server, because there isn't one that receives files. The app does use the internet for a few things that don't involve your documents: purchases, anonymous usage statistics, crash reports, notifications and a one-time AI model download.</p>
<section><h2>What happens on your phone</h2><p>On iPhone and iPad, ProperPDF uses Apple's own PDF and camera frameworks. On Android, it uses the open-source PDFBox library and Google's on-device document scanner. Files you create are saved in ProperPDF's library on the device and leave it only when you share them.</p><p>Because nothing is uploaded, every PDF tool works in airplane mode, and a large file takes the same time on a slow connection as on a fast one.</p></section>
<section><h2>What does use the internet</h2><table class="facts-table"><tbody>{network_rows}</tbody></table></section>
<section><h2>Check it yourself</h2><ol class="steps"><li>Turn on airplane mode.</li><li>Open ProperPDF and merge, compress or sign a PDF.</li><li>It works the same as online. Nothing could have been uploaded.</li></ol><p>On iPhone, Settings, then Privacy & Security, then App Privacy Report lists every domain each app contacts, so you can see for yourself what ProperPDF connects to.</p></section>
<section><h2>What offline doesn't cover</h2><p>When you share a PDF by email, WhatsApp or a cloud drive, it goes wherever you send it. Device backups, such as iCloud Backup or Google's backup, may include ProperPDF's library, depending on your backup settings. If a file needs protecting in transit, lock it with a password and send the password separately.</p><p>The full details are in the <a href="/privacy-policy">privacy policy</a>.</p></section>''',
          offline_faq)

changelog_html = "".join(
    f'<section class="release"><h2>{escape(version)} <span>{escape(platform)} · {escape(month)}</span></h2><ul>' + "".join(f"<li>{escape(change)}</li>" for change in changes) + "</ul></section>"
    for version, month, platform, changes in CHANGELOG) + '<p class="table-note">Android versions before 1.1.0 and minor bug-fix releases are not listed.</p>'
info_page("changelog", "CHANGELOG", "What's new in ProperPDF",
          "Release history for ProperPDF on iPhone, iPad and Android: new tools, fixes and changes in each version.",
          "Every release on iPhone, iPad and Android, newest first.",
          f'''<p class="answer">ProperPDF is updated on both platforms. The iPhone and Android apps are built separately, so a version number can arrive on each at a different time, with different changes.</p>{changelog_html}''')

info_page("about", "ABOUT", "About ProperPDF",
          "ProperPDF is an offline PDF app for iPhone, iPad and Android, made by an independent developer. Why it exists, how it's built and how it makes money.",
          "An offline PDF app made by one independent developer.",
          '''<p class="answer">ProperPDF is made by one independent developer. It started from a simple annoyance: most phone PDF tools want you to upload a document, make an account, or watch an ad before they'll merge two files. ProperPDF does the everyday PDF jobs on the phone instead, with no account, no ads and no uploads.</p>
<section><h2>How it's built</h2><p>There are two native apps rather than one shared codebase. The iPhone and iPad app is written in Swift with Apple's PDFKit. The Android app is written in Kotlin with Jetpack Compose and the PDFBox library. They share a design and a feature list, so a tool works the same way on both.</p></section>
<section><h2>How it makes money</h2><p>Pro unlocks compress, sign, fill forms and password protection, and removes the watermark from free exports. That's the only income: no ads, and no selling of data. You can pay once for lifetime access instead of subscribing.</p></section>
<section><h2>Contact</h2><p>Bug reports, feature requests and questions go to <a href="mailto:hello@tryproperpdf.app">hello@tryproperpdf.app</a>, and a person reads every one.</p></section>''')

# Press kit: copy-ready descriptions, facts, and downloadable assets.
APP_LANGUAGES = "English, Arabic, Chinese (Simplified and Traditional), German, Hindi, Japanese, Korean, Portuguese, Russian, Spanish and Turkish"
PRESS_SHOTS = [
    # (file under assets/mockups, label)
    ("ios/home-portrait.png", "iPhone: tools"), ("ios/merge-portrait.png", "iPhone: merge"), ("ios/split-portrait.png", "iPhone: split"),
    ("ios/compress-portrait.png", "iPhone: compress"), ("ios/sign-portrait.png", "iPhone: sign"), ("ios/fill-portrait.png", "iPhone: fill forms"),
    ("ios/lock-portrait.png", "iPhone: lock"), ("ios/image-to-pdf-portrait.png", "iPhone: images to PDF"), ("ios/pdf-to-image-portrait.png", "iPhone: PDF to images"),
    ("android/8home1-portrait.png", "Android: tools"), ("android/1merge-portrait.png", "Android: merge"), ("android/3compress-portrait.png", "Android: compress"),
    ("android/4sign-portrait.png", "Android: sign"), ("android/5lock-portrait.png", "Android: lock"), ("android/7chatwithai-portrait.png", "Android: AI chat"),
]
press_short = "ProperPDF is an offline PDF app for iPhone, iPad and Android. It merges, splits, compresses, signs, fills, locks, scans and converts PDFs on the device, with no uploads, no account and no ads."
press_long = ("Most phone PDF tools upload your document to a server before they work on it. ProperPDF does the same everyday jobs on the phone itself: merging and splitting files, "
              "compressing large scans, signing and filling forms, adding passwords, scanning paper, and converting between PDF and images. Every tool works in airplane mode, "
              "and the app has no accounts and no ads. Scanning, merging, splitting and converting are free; Pro adds compression, signing, form filling and password protection "
              "for $3.99 a month, $19.99 a year or $29.99 once (US prices, with regional pricing elsewhere). ProperPDF is made by an independent developer, with native apps "
              "written in Swift for iPhone and iPad and in Kotlin for Android.")
press_facts = [
    ("Name", "ProperPDF"), ("Made by", "An independent developer"), ("Platforms", REQUIREMENTS),
    ("First released", "Android: December 2025. iPhone and iPad: April 2026"), ("Current version", "1.4.2 on both platforms"),
    ("Price", "Free download. Pro: " + ", ".join(f"{plan.lower()} {price}" for plan, price in PRICES) + " (US prices)"),
    ("App languages", APP_LANGUAGES), ("Website", "tryproperpdf.app"), ("Press contact", "hello@tryproperpdf.app"),
]
press_fact_rows = "".join(f'<tr><th scope="row">{escape(k)}</th><td>{escape(v)}</td></tr>' for k, v in press_facts)
def png_size(image: str) -> tuple[int, int]:
    header = (PUBLIC / "assets" / "mockups" / image).read_bytes()[:24]
    return int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big")


press_shots = "".join(
    f'<li><a href="/assets/mockups/{escape(image)}" download><img src="/assets/mockups/{escape(image.removesuffix(".png"))}-480.webp" alt="{escape(label)}" width="480" height="{round(png_size(image)[1] * 480 / png_size(image)[0])}" loading="lazy" decoding="async"><span>{escape(label)}</span></a></li>'
    for image, label in PRESS_SHOTS)
info_page("press", "PRESS", "ProperPDF press kit",
          "Descriptions, facts, the app icon, screenshots and a demo video for writing about ProperPDF, the offline PDF app for iPhone, iPad and Android.",
          "Descriptions, facts and images you're free to use when writing about ProperPDF.",
          f'''<p class="answer">{escape(press_short)}</p>
<section><h2>Descriptions</h2><h3 class="press-label">One paragraph</h3><p>{escape(press_long)}</p><h3 class="press-label">One sentence</h3><p>{escape(press_short)}</p></section>
<section><h2>Facts</h2><table class="facts-table"><tbody>{press_fact_rows}</tbody></table></section>
<section><h2>Worth getting right</h2><ul class="press-notes"><li>Files are processed on the device. ProperPDF is not a web service and has no server that receives documents.</li><li>It doesn't edit the existing text in a PDF or convert PDF to Word.</li><li>Signing places a drawn signature on the page; it is not a certificate-based digital signature.</li><li>Some free exports carry a ProperPDF watermark; Pro removes it.</li></ul><p>More detail: <a href="/how-offline-works">how offline works</a>, <a href="/pricing">pricing</a> and <a href="/changelog">changelog</a>.</p></section>
<section><h2>App icon</h2><p><a href="/press/properpdf-icon-1024.png" download>1024 × 1024 PNG</a> · <a href="/press/properpdf-icon-512.png" download>512 × 512 PNG</a>. Square artwork; the App Store and Google Play apply their own rounded mask, so please do the same or show it unmasked.</p></section>
<section><h2>Screenshots</h2><p>Real app screens in a device frame. Click one to download the full-size PNG.</p><ul class="press-shots">{press_shots}</ul></section>
<section><h2>Video</h2><p><a href="/assets/sign-pdf-demo.mp4" download>Signing a PDF on iPhone</a> (33 seconds, MP4).</p></section>
<section><h2>Contact</h2><p>For interviews, review access or questions, email <a href="mailto:hello@tryproperpdf.app?subject=Press">hello@tryproperpdf.app</a>. Pro access for reviewers is available on request.</p></section>''')

for item in features:
    write(item["slug"], item["title"], item["description"], feature_html(item), article_schema(item["title"], item["description"], f"/{item['slug']}", "PDF tools", item.get("faq")))

for item in guides:
    write(item["slug"], item["title"], item["description"], guide_html(item), article_schema(item["title"], item["description"], f"/{item['slug']}", "Guides", item.get("faq")))

for item in comparisons:
    links = "".join(f'<a href="/{slug}">{escape(page_lookup[slug]["title"])} <span aria-hidden="true">↗</span></a>' for slug in item["related"])
    content = f'''{hero(item["kicker"], item)}<div class="container content-layout"><article class="article-body">{comparison_html(item)}{cta()}</article><aside class="related-links"><p class="kicker">KEEP EXPLORING</p>{links}<a href="/pricing">Free vs Pro <span aria-hidden="true">↗</span></a><a href="/guides">All guides <span aria-hidden="true">↗</span></a></aside></div>'''
    write(item["slug"], item["title"], item["description"], content, article_schema(item["title"], item["description"], f"/{item['slug']}", "Guides", item["faq"]))

# Guides hub: grouped by task as plain lists, so a reader finds the job, not a card wall.
GUIDE_GROUPS = [
    ("Merge and split", ["merge-pdf", "split-pdf", "offline-pdf-merger-android", "merge-pdf-iphone-without-app"]),
    ("Compress", ["compress-pdf", "private-pdf-compressor"]),
    ("Sign, fill and protect", ["sign-pdf", "fill-pdf", "lock-pdf"]),
    ("Scan and convert", ["scan-to-pdf", "image-to-pdf", "pdf-to-image"]),
    ("Choosing a PDF app", ["best-offline-pdf-apps", "acrobat-alternatives", "ilovepdf-smallpdf-alternatives", "properpdf-vs-adobe-acrobat", "properpdf-vs-pdf-expert"]),
    ("Offline and privacy", ["how-offline-works", "private-pdf-workflow", "offline-pdf-editor-iphone", "offline-pdf-editor-android"]),
]
page_lookup["how-offline-works"] = {"title": "How ProperPDF works offline", "description": "What runs on your phone, what uses the internet, and how to check it yourself."}
listed = {slug for _, slugs_ in GUIDE_GROUPS for slug in slugs_}
missing = [item["slug"] for item in features + guides + comparisons if item["slug"] not in listed]
assert not missing, f"Add these pages to GUIDE_GROUPS: {missing}"


def link_list(slugs_: list[str]) -> str:
    return '<ul class="link-list">' + "".join(f'<li><a href="/{slug}">{escape(page_lookup[slug]["title"])}</a><p>{escape(page_lookup[slug]["description"])}</p></li>' for slug in slugs_) + "</ul>"


groups_html = "".join(f'<section><h2>{escape(name)}</h2>{link_list(slugs_)}</section>' for name, slugs_ in GUIDE_GROUPS)
hub = f'<div class="container guide-groups">{groups_html}</div>'
write("features", "PDF tools for iPhone, iPad, and Android", "Every ProperPDF tool, what it does and whether it's free or Pro on iPhone, iPad and Android. All tools work offline.", f'''<div class="content-hero guide-hero"><div class="container"><p class="kicker">THE PROPERPDF TOOLKIT</p><h1>Offline PDF tools for iPhone and Android</h1><p>Merge, split, compress, sign, scan, convert, and organize documents on your phone.</p></div></div><section class="container guide-index"><h2>Free and Pro tools</h2>{tools_table()}<h2>How each tool works</h2>{link_list([item["slug"] for item in features] + ["sign-pdf", "fill-pdf", "lock-pdf", "scan-to-pdf", "image-to-pdf"])}{cta()}</section>''')
write("guides", "PDF guides and offline tips", "Step-by-step guides to merging, compressing, signing, scanning and converting PDFs on iPhone and Android, plus comparisons of PDF apps.", f'''<div class="content-hero guide-hero"><div class="container"><p class="kicker">GUIDES</p><h1>PDF guides for iPhone and Android</h1><p>How to do each PDF job on your phone, and how ProperPDF compares with other apps.</p></div></div>{hub}''')
write("blog", "The ProperPDF blog", "Practical advice for private, offline PDF workflows on mobile.", f'''<div class="content-hero guide-hero"><div class="container"><p class="kicker">GUIDES</p><h1>PDF guides for iPhone and Android</h1><p>How to do each PDF job on your phone, and how ProperPDF compares with other apps.</p></div></div>{hub}''')

price_rows = "".join(f'<tr><th scope="row">{escape(plan)}</th><td>{escape(price)}</td></tr>' for plan, price in PRICES)
pricing_faq_items = "".join(f"<h3>{escape(q)}</h3><p>{escape(a)}</p>" for q, a in pricing_faq)
write("pricing", "ProperPDF pricing: what's free and what's Pro",
      "ProperPDF is free to download. See which tools are free on iPhone and Android, which need Pro, and Pro prices: weekly, monthly, yearly or lifetime.",
      f'''<div class="content-hero guide-hero"><div class="container"><p class="kicker">PRICING</p><h1>What's free and what's Pro</h1><p>ProperPDF is free to download. Pro unlocks compress, sign, fill and lock, and removes watermarks.</p>{download_buttons("pricing")}<p class="updated">Updated {UPDATED_LABEL}</p></div></div><div class="container content-layout"><article class="article-body"><p class="answer">ProperPDF is free on the App Store and Google Play, with no ads and no account. Scanning, merging, splitting, organizing pages and converting between PDF and images are free; some free exports carry a ProperPDF watermark. Pro costs $3.99 a month, $19.99 a year or $29.99 once for lifetime access (US prices; lower in many countries), and unlocks compress, sign, fill forms and password protection.</p><section><h2>Tools by platform</h2>{tools_table()}</section><section><h2>Pro plans</h2><table class="facts-table"><tbody>{price_rows}</tbody></table><p>{escape(REGIONAL_NOTE)} Subscriptions renew through your Apple or Google account until you cancel.</p></section><section class="article-faq"><h2>Questions</h2>{pricing_faq_items}</section>{cta()}</article><aside class="related-links"><p class="kicker">KEEP EXPLORING</p><a href="/features">All PDF tools <span aria-hidden="true">↗</span></a><a href="/guides">Guides <span aria-hidden="true">↗</span></a><a href="/support">Support <span aria-hidden="true">↗</span></a></aside></div>''',
      [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pricing_faq]}])

write("support", "Support and contact", "Get help with ProperPDF, including app downloads, purchases, and PDF tools.", f'''<div class="content-hero guide-hero"><div class="container"><p class="kicker">HERE TO HELP</p><h1>ProperPDF support</h1><p>Find the right place to get help with the app.</p>{download_buttons("support")}</div></div><div class="container support-grid"><div><h2>Contact us</h2><p>For a bug, purchase question, or feature request, email the ProperPDF team. Please include your device model, app version, and a short description of what happened.</p><p>Do not send sensitive PDFs unless you choose to share them for troubleshooting.</p><a class="button button-dark" href="mailto:hello@tryproperpdf.app?subject=ProperPDF%20support">hello@tryproperpdf.app <span aria-hidden="true">↗</span></a></div><div><h2>Quick links</h2><div class="support-links"><a href="{IOS_UTM}">ProperPDF on the App Store <span aria-hidden="true">↗</span></a><a href="{ANDROID_UTM}">ProperPDF on Google Play <span aria-hidden="true">↗</span></a><a href="/pricing">Free vs Pro <span aria-hidden="true">↗</span></a><a href="/#faq">Frequently asked questions <span aria-hidden="true">↗</span></a><a href="/guides">PDF guides <span aria-hidden="true">↗</span></a></div></div></div>''')

for slug, title, description, source in [
    ("privacy-policy", "Privacy Policy", "Read the ProperPDF Privacy Policy.", "https://nepali-indie-dev.github.io/properpdf/privacy-policy.html"),
    ("terms-of-service", "Terms of Service", "Read the ProperPDF Terms of Service.", "https://nepali-indie-dev.github.io/properpdf/terms-of-service.html"),
]:
    legal_text = (Path(__file__).parent / "legal-source" / f"{slug}.html").read_text(encoding="utf-8")
    website_notice = ""
    if slug == "privacy-policy":
        website_notice = '<section id="website-data"><h2>Website data: analytics and development updates</h2><p>The app policy below describes the mobile apps. Separately, this website stores daily counts of page views and app-store link clicks in Cloudflare D1. These counters contain a page path, event type, date, destination store, landing page, and a traffic-source category such as Google, Reddit, or email. We classify referring websites and campaign tags in your browser; we do not save their raw values. Temporary tab storage keeps the source and landing page for up to 30 minutes to attribute subsequent app-store clicks. We do not store visitor IP addresses, user identifiers, cookies, raw query strings, or raw referrer URLs in these analytics tables. The website does not send analytics when your browser signals Do Not Track or Global Privacy Control. Counts older than 730 days are removed when new events are recorded.</p><p>If you opt in to development updates, we store your email address, signup time, signup source, and consent version in Cloudflare D1. Addresses are not verified by an email confirmation at signup. These records are separate from analytics and are used for ProperPDF development updates. To stop updates or request deletion of your address, email <a href="mailto:hello@tryproperpdf.app">hello@tryproperpdf.app</a>. We retain your signup until you request removal. Cloudflare processes website requests to host this site; this notice describes the data our application saves in D1.</p></section>'
    content = f'''<div class="content-hero guide-hero legal-hero"><div class="container"><p class="kicker">LEGAL INFORMATION</p><h1>{title}</h1><p>This policy applies to ProperPDF on both iOS and Android.</p></div></div><div class="container legal-layout"><div class="legal-copy">{website_notice}{legal_text}</div><p class="legal-source">Questions about this policy? <a href="mailto:hello@tryproperpdf.app">hello@tryproperpdf.app</a></p></div>'''
    write(slug, title, description, content)
    write("privacy" if slug == "privacy-policy" else "terms", title, description, content)

# llms.txt: a plain-text fact sheet for AI assistants that read it.
tool_lines = "\n".join(f"- {name}: iPhone/iPad: {ios}. Android: {android}." + (f" Guide: {BASE}/{slug}" if slug else "") for name, slug, ios, android in TOOLS)
page_lines = "\n".join(f"- [{item['title']}]({BASE}/{item['slug']}): {item['description']}" for item in features + guides + comparisons)
(PUBLIC / "llms.txt").write_text(f"""# ProperPDF

> Offline PDF app for iPhone, iPad and Android. Scans, merges, splits, compresses, signs, fills, locks and converts PDFs on the device. Files are not uploaded and there is no account.

- Platforms: {REQUIREMENTS}.
- App Store: {IOS}
- Google Play: {ANDROID}
- Price: free download, no ads. Pro: {", ".join(f"{plan} {price}" for plan, price in PRICES)} (US prices; regional pricing makes Pro cheaper in many countries).
- Limits: does not edit existing PDF text, convert PDF to Word, or add highlights/annotations.
- Contact: hello@tryproperpdf.app

## Tools: free or Pro

{tool_lines}

{WATERMARK_NOTE}

## Pages

- [Pricing]({BASE}/pricing): what's free, what's Pro, prices.
- [How ProperPDF works offline]({BASE}/how-offline-works): what runs on the device and what uses the internet.
- [Changelog]({BASE}/changelog): release history for iPhone and Android.
- [About]({BASE}/about): who makes ProperPDF and how it makes money.
- [Press kit]({BASE}/press): descriptions, facts, icon and screenshots.
{page_lines}
""", encoding="utf-8")

paths = ["/", "/features", "/guides", "/pricing", "/how-offline-works", "/changelog", "/about", "/press", "/support", "/privacy-policy", "/terms-of-service"] + [f"/{item['slug']}" for item in features + guides + comparisons]
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{xml_escape(BASE + path)}</loc><lastmod>{UPDATED}</lastmod></url>\n" for path in paths) + "</urlset>\n"
(PUBLIC / "sitemap.xml").write_text(sitemap, encoding="utf-8")
# Titles for scripts/og_images.py, which renders /og/<slug>.png locally (it needs a browser,
# so it isn't part of the Cloudflare build). Re-run it after adding pages or changing titles.
(Path(__file__).parent / "scripts" / "og-pages.json").write_text(json.dumps(dict(sorted(OG_PAGES.items())), indent=1) + "\n", encoding="utf-8")
print(f"Generated {len(paths)} pages and sitemap.xml")

# A bounded path list keeps arbitrary URLs and personal query data out of D1.
server = Path(__file__).parent / "server"
server.mkdir(exist_ok=True)
(server / "analytics-paths.js").write_text("export const analyticsPaths = " + json.dumps(paths) + ";\n", encoding="utf-8")
