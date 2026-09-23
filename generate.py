"""Generate the standalone content pages and sitemap with the Python standard library."""

from html import escape
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

PUBLIC = Path(__file__).parent / "public"
BASE = "https://tryproperpdf.app"
SITE_NAME = "ProperPDF"
SITE_IMAGE = f"{BASE}/assets/home.jpg"
IOS = "https://apps.apple.com/app/id6760956540"
ANDROID = "https://play.google.com/store/apps/details?id=io.github.thegbguy.pdfmate"


def page(title: str, description: str, path: str, content: str) -> str:
    e_title, e_description = escape(title), escape(description)
    og_type = "website" if path in {"/", "/features", "/blog"} else "article"
    return f'''<!doctype html>
<html lang="en"><head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#f8f7f3"><meta name="description" content="{e_description}"><meta name="robots" content="index, follow">
    <meta property="og:type" content="{og_type}"><meta property="og:site_name" content="{SITE_NAME}"><meta property="og:title" content="{e_title}">
    <meta property="og:description" content="{e_description}"><meta property="og:url" content="{BASE}{path}"><meta property="og:image" content="{SITE_IMAGE}">
    <meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e_title}"><meta name="twitter:description" content="{e_description}"><meta name="twitter:image" content="{SITE_IMAGE}">
  <link rel="canonical" href="{BASE}{path}"><link rel="icon" href="/assets/icon.png" type="image/png">
  <link rel="stylesheet" href="/styles.css"><title>{e_title} — ProperPDF</title>
</head><body><a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="container nav-inner">
  <a class="brand" href="/"><img src="/assets/icon.png" alt="" width="38" height="38"><span>ProperPDF</span></a>
  <nav aria-label="Main navigation"><a href="/#features">Features</a><a href="/#pricing">Pricing</a><a href="/guides">Guides</a></nav>
  <a class="nav-cta" href="/#download">Get the app <span aria-hidden="true">↗</span></a>
</div></header>
<main id="main">{content}</main>
<footer class="site-footer"><div class="container footer-main"><div><a class="brand" href="/"><img src="/assets/icon.png" alt="" width="34" height="34"><span>ProperPDF</span></a><p>Every PDF tool, offline.</p></div><div class="footer-links"><a href="/guides">Guides</a><a href="/support">Support</a><a href="{IOS}">App Store</a><a href="{ANDROID}">Google Play</a><a href="/privacy-policy">Privacy policy</a><a href="/terms-of-service">Terms</a></div></div><div class="container footer-bottom"><span>© 2026 ProperPDF</span><span>Made for documents that matter.</span></div></footer>
</body></html>'''


def write_static_files() -> None:
    (PUBLIC / "_headers").write_text(
        "/*\n  X-Content-Type-Options: nosniff\n  X-Frame-Options: DENY\n  Referrer-Policy: strict-origin-when-cross-origin\n",
        encoding="utf-8",
    )
    (PUBLIC / "_redirects").write_text(
        """/index.html / 301
/guides.html /guides 301
/support.html /support 301
/privacy-policy.html /privacy-policy 301
/terms-of-service.html /terms-of-service 301
/merge-pdf.html /merge-pdf 301
/split-pdf.html /split-pdf 301
/compress-pdf.html /compress-pdf 301
/pdf-to-image.html /pdf-to-image 301
/offline-pdf-editor-iphone.html /offline-pdf-editor-iphone 301
/private-pdf-workflow.html /private-pdf-workflow 301
/offline-pdf-editor-android.html /offline-pdf-editor-android 301
/private-pdf-compressor.html /private-pdf-compressor 301
/offline-pdf-merger-android.html /offline-pdf-merger-android 301
""",
        encoding="utf-8",
    )


def paragraph(text: str) -> str:
    return f"<p>{escape(text)}</p>"


def section(title: str, paragraphs: list[str]) -> str:
    return f"<section><h2>{escape(title)}</h2>{''.join(map(paragraph, paragraphs))}</section>"


def cta() -> str:
    return f'''<aside class="content-cta"><p class="kicker">GET THE APP</p><h2>Work with PDFs on your device.</h2><p>ProperPDF processes documents in the app, not on this website.</p><div class="content-actions"><a class="button button-dark" href="{IOS}">Download for iPhone & iPad <span aria-hidden="true">↗</span></a><a class="button button-light" href="{ANDROID}">Get it on Android <span aria-hidden="true">↗</span></a></div></aside>'''


features = [
    dict(slug="merge-pdf", title="Merge PDF files offline", description="Combine PDFs on your phone without uploading your documents. Learn how ProperPDF helps you put multiple files into one.", lead="Turn separate documents into one tidy PDF, right on your device.", image="mockups/ios/merge-portrait.png", image_alt="ProperPDF Merge PDF screen on iPhone", sections=[
        ("Why merge PDFs on your device?", ["You may need to send a contract with its attachments, bundle class notes, or combine scans into a single file. ProperPDF joins selected PDFs locally, so the source documents do not have to be sent to a website for processing.", "A single PDF is easier to share and archive than a group of separate files. You can preview the result in the app before sending it on."]),
        ("How to merge PDFs with ProperPDF", ["Open Merge PDF in the app and select the documents you want to combine. Arrange them in the order you prefer, then save the merged file. It appears in your document library, where you can open, rename, or share it.", "If the combined document has pages you no longer need, use Organize Pages to reorder or remove them. For a smaller output, use Compress PDF afterward."]),
        ("Useful for", ["Combining application forms and supporting documents, collecting receipts, assembling a report, or keeping multi-part notes together. The same offline workflow is helpful whenever a document contains private details."]),
    ], related=["split-pdf", "compress-pdf"]),
    dict(slug="split-pdf", title="Split a PDF without uploading it", description="Extract pages and page ranges from PDFs offline with ProperPDF for iPhone, iPad, and Android.", lead="Keep the pages you need. Leave the rest in the original file.", image="mockups/ios/split-portrait.png", image_alt="ProperPDF Split PDF screen on iPhone", sections=[
        ("Share only the relevant pages", ["A large PDF often contains more information than the person receiving it needs. ProperPDF lets you select pages or page ranges and save them as a separate PDF on your device.", "This is useful for a single chapter of a report, a few signed pages, or a section of a long set of notes. It can also help avoid sharing unrelated pages by accident."]),
        ("How to split a PDF", ["Choose Split PDF, select your source document, and enter the pages or ranges to extract. Review the selection, then save the new document. Your original PDF stays available.", "You can open the extracted file in the built-in viewer, rename it in the library, or share it using your device's share sheet."]),
        ("Need to rearrange instead?", ["Use Organize Pages when you want to drag pages into a different order, rotate them, or delete pages from a document. Use Merge PDF when you need to bring pages from separate files together."]),
    ], related=["merge-pdf", "pdf-to-image"]),
    dict(slug="compress-pdf", title="Compress PDFs privately", description="Reduce PDF file size on your device with ProperPDF. Keep documents offline while preparing them for sharing.", lead="Make a large PDF easier to send, while keeping the processing local.", image="mockups/ios/compress-portrait.png", image_alt="ProperPDF Compress PDF screen on iPhone", sections=[
        ("When a PDF is too large", ["Scanned documents and image-heavy PDFs can be awkward to email or save. ProperPDF offers compression in the app so you can create a smaller copy without uploading your file to an online converter.", "The best result depends on the document. Text-focused files may already be compact, while scan-heavy files often have more room to shrink. Always review the output if image clarity matters."]),
        ("How to compress with ProperPDF", ["Open Compress PDF, select your document, choose a compression level, and save the result. The app creates a new file so you can compare its size and appearance with the original.", "If the document includes pages you do not need, split or remove them first. That can reduce size while preserving the quality of the pages you keep."]),
        ("A private workflow", ["Compression happens on your device. You can prepare contracts, records, and assignments for sharing without first transferring their contents to a PDF website."]),
    ], related=["split-pdf", "merge-pdf"]),
    dict(slug="pdf-to-image", title="Convert PDF pages to images", description="Export selected PDF pages as PNG or JPEG images with ProperPDF on your device.", lead="Turn the pages you choose into images you can use elsewhere.", image="mockups/ios/home-portrait.png", image_alt="ProperPDF conversion tools on iPhone", sections=[
        ("Choose the pages and format", ["ProperPDF can export selected PDF pages as PNG or JPEG images. This is handy when you need a page for a presentation, a message, or an image-based workflow.", "PNG works well for graphics and crisp text. JPEG may be a better fit when file size matters for a photo-heavy page. Check the exported image before sharing it."]),
        ("How to convert a PDF to images", ["Open PDF to Image, select the document, choose the pages you want, then pick PNG or JPEG. Save or share the resulting images using your device's normal controls.", "If you need the reverse conversion, use Image to PDF. You can select photos or scans, arrange their order, and create a PDF from them."]),
        ("No online converter required", ["Your source document is processed locally. This is especially useful when a PDF page contains private information that you do not want to upload to a third-party service."]),
    ], related=["split-pdf", "merge-pdf"]),
]

feature_lookup = {item["slug"]: item for item in features}


def feature_html(item: dict) -> str:
    related = "".join(f'<a href="/{slug}">{escape(feature_lookup[slug]["title"])} <span aria-hidden="true">↗</span></a>' for slug in item["related"])
    faq = section("Common questions", [f"Does {item['title'].lower()} require an upload? ProperPDF is designed to process the document in the app, so the source file does not need to be sent to this website.", "Can I use this offline? Core PDF tools work without an internet connection. Some on-device AI features may need a one-time model download first."])
    return f'''<div class="content-hero"><div class="container content-hero-grid"><div><p class="kicker">PROPERPDF TOOL GUIDE</p><h1>{escape(item["title"])}</h1><p>{escape(item["lead"])}</p><a class="text-link" href="/features">Explore every feature <span aria-hidden="true">↗</span></a></div><div class="content-image"><img src="/assets/{item["image"]}" alt="{escape(item["image_alt"])}" width="414" height="900"></div></div></div><div class="container content-layout"><article class="article-body">{''.join(section(title, paragraphs) for title, paragraphs in item["sections"])}{faq}<p class="content-disclaimer">Feature availability can vary by platform. Some tools require Pro on iOS.</p>{cta()}</article><aside class="related-links"><p class="kicker">MORE PDF TOOLS</p>{related}<a href="/features">All PDF tools <span aria-hidden="true">↗</span></a><a href="/guides">Read all guides <span aria-hidden="true">↗</span></a></aside></div>'''


guides = [
    dict(slug="offline-pdf-editor-iphone", title="How to work with PDFs offline on iPhone", description="A practical guide to scanning, combining, signing, and organizing PDFs on iPhone without uploading your documents.", lead="A reliable PDF workflow does not need to start with an upload.", sections=[
        ("Start with the document you have", ["If the document is on paper, scan it with your phone and save it as a PDF. If you already have a PDF, import it into ProperPDF's library so you can open it and choose the tool you need.", "The library gives you a place to find, rename, share, or delete saved files. For a quick read, use the built-in viewer and move between pages without switching apps."]),
        ("Prepare the file", ["Use Merge PDF to bring related files together, or Split PDF to extract just the pages you need. Organize Pages can reorder, rotate, or remove pages after that. If you have photos instead of a document, Image to PDF turns them into a multi-page PDF.", "For a file that is hard to send, compress a copy and compare it with the original. You can also export individual pages as PNG or JPEG images when an image format is more useful."]),
        ("Finish and share", ["ProperPDF can add a signature, fill PDF form fields, and password-protect a document. These tools are marked Pro on iOS. Once the PDF looks right, share it through the device's normal share sheet.", "The PDF processing runs locally. On-device AI can help answer questions about a document or summarize it; depending on the device, its model may need a one-time download first."]),
    ]),
    dict(slug="private-pdf-workflow", title="A more private way to handle everyday PDFs", description="Learn how to scan, edit, convert, and share PDFs while keeping document processing on your device.", lead="Sensitive documents deserve a workflow that keeps them close.", sections=[
        ("Know where the work happens", ["A PDF may contain addresses, signatures, financial details, or medical information. Before using a tool, it helps to know whether the file must leave your device. ProperPDF is designed to process documents locally rather than upload them for editing.", "The website explains the app and sends you to its official store listings. It does not accept PDF uploads or process your documents in the browser."]),
        ("Share less, on purpose", ["If someone only needs one section of a PDF, split out the relevant pages. If a document has blank or outdated pages, remove them before sharing. Review metadata such as the title, author, and keywords when those details matter.", "A password can help control access to a document, but it is still important to send the password through a separate trusted channel when you share a protected file."]),
        ("Keep an original copy", ["Make a copy before compressing, rearranging, or signing an important PDF. That way you can compare the result and keep the source intact. Review the final pages and file size before sending it onward.", "Offline processing is especially useful when you are traveling or working with a poor connection. Some AI models may require a one-time download before offline use."]),
    ]),
    dict(slug="offline-pdf-editor-android", title="Offline PDF editor for Android", description="Edit, merge, split, sign, and organize PDFs offline on Android with ProperPDF. Keep your documents on your device.", lead="A private PDF workflow for Android, even when the connection is unreliable.", sections=[
        ("What you can do offline", ["ProperPDF brings everyday PDF tools to your Android phone or tablet. Scan paper documents, merge files, split out pages, organize a document, convert images, and read PDFs without sending the source file to a website.", "Offline access is useful on flights, during travel, or anywhere you do not want a sensitive document leaving your device. Some AI features may need a one-time model download before they work offline."]),
        ("A simple Android PDF workflow", ["Import a PDF into the document library, then choose the tool that matches the job. Use Organize Pages to reorder or remove pages, Merge PDF to combine files, and Split PDF to create a smaller document for sharing.", "When the document is ready, review it in the built-in viewer and use Android's share sheet. Keep the original file until you have checked the final copy."]),
        ("Designed around privacy", ["Contracts, forms, receipts, and personal records can contain information you would not want in a third-party upload. ProperPDF keeps core PDF processing on your device so you can work locally first."]),
    ]),
    dict(slug="private-pdf-compressor", title="Private PDF compressor without uploading", description="Compress a PDF privately on your phone. ProperPDF reduces file size locally for iPhone, iPad, and Android.", lead="Shrink a PDF for sharing without handing the document to an online converter.", sections=[
        ("Why compress locally?", ["Online PDF compressors ask you to upload a document before they can process it. That may be convenient, but it is not a good fit for every contract, form, receipt, or personal record.", "ProperPDF compresses a copy on your device. The original stays available, and you can compare the smaller file before sharing it."]),
        ("Keep the right quality", ["Scan-heavy PDFs often have the most room to shrink because their pages contain large images. Choose a compression level, then check small text, signatures, and diagrams in the output.", "If the PDF contains pages you do not need, split or remove them first. Removing unnecessary pages can reduce the file size without changing the quality of the pages you keep."]),
        ("A safer sharing checklist", ["Review the page order, file size, and metadata before sending. If the document needs extra protection, use password protection where available and send the password separately through a trusted channel."]),
    ]),
    dict(slug="offline-pdf-merger-android", title="Offline PDF merger for Android", description="Merge PDF files offline on Android without uploading them. Combine scans, receipts, forms, and reports with ProperPDF.", lead="Combine PDFs on Android without uploading them.", sections=[
        ("Merge without an upload", ["A PDF merger is useful for combining a form with its attachments, collecting receipts, or turning several scans into one document. ProperPDF lets you select and combine files locally on your Android device.", "The result is created in the app, so you do not need to transfer the source documents to an online PDF service first."]),
        ("Put pages in the right order", ["Select the PDFs, arrange them in the order you want, and save the merged document. Open the result in the built-in viewer before sharing it.", "If you need to fix the order or remove a page afterward, use Organize Pages. If the finished file is too large, create a compressed copy for sharing."]),
        ("Good for private documents", ["Keeping the workflow offline can reduce unnecessary exposure for applications, invoices, medical paperwork, and other documents that contain personal details."]),
    ]),
    dict(slug="lock-pdf", title="Password protect a PDF on your phone", description="Add password protection to PDFs on iPhone, iPad, and Android with ProperPDF.", lead="Add a password before you share a PDF containing information that should stay private.", image="mockups/ios/lock-portrait.png", image_alt="ProperPDF password protection screen on iPhone", sections=[
        ("Protect a PDF before sharing", ["Password protection can add a useful layer of control to a contract, form, report, or personal record. ProperPDF lets you protect a PDF in the app without first uploading it to an online service.", "Choose a password you can share safely and remember. ProperPDF cannot recover a password you lose."]),
        ("How to lock a PDF", ["Open Lock PDF, select the document, enter and confirm a password, then save the protected copy. Review the result and test the password before sending it.", "Send the password through a separate trusted channel rather than placing it in the same message as the file."]),
        ("Keep the original", ["Save a separate original if you may need to edit the document later. Use Unlock PDF when you know the password and need to make changes."]),
    ], related=["sign-pdf", "compress-pdf"]),
    dict(slug="sign-pdf", title="Sign PDFs offline on your phone", description="Add a signature to a PDF on iPhone, iPad, or Android with ProperPDF.", lead="Finish a form or agreement from your phone without sending the PDF to a website.", image="mockups/ios/sign-portrait.png", image_alt="ProperPDF sign PDF screen on iPhone", sections=[
        ("Sign where the document is", ["When a PDF needs your signature, switching to an online editor can mean uploading the whole document. ProperPDF lets you work from the app and keep the source file on your device.", "Review the document carefully before signing, especially when it includes dates, amounts, or terms."]),
        ("How to sign a PDF", ["Open Sign PDF, choose your document, add or select your signature, and place it where it belongs. Save a new copy, then review every page before sharing it.", "Some signing features require Pro on iOS."]),
        ("A simple final check", ["Confirm that the signature is visible, the page order is correct, and the saved file is the copy you intend to send."]),
    ], related=["fill-pdf", "lock-pdf"]),
    dict(slug="fill-pdf", title="Fill PDF forms on your device", description="Fill PDF forms on iPhone, iPad, and Android with ProperPDF while keeping the document on your device.", lead="Complete forms from your phone and keep the finished document close.", image="mockups/ios/fill-portrait.png", image_alt="ProperPDF fill PDF form screen on iPhone", sections=[
        ("Complete forms privately", ["Forms often contain addresses, account details, or other personal information. ProperPDF helps you enter information in a PDF without requiring an upload to a browser-based editor.", "Use the built-in viewer to check that each field is complete before sharing the finished copy."]),
        ("How to fill a PDF", ["Open Fill PDF, choose the form, enter text in the available fields, and mark checkboxes where needed. Save the completed document as a new copy so the blank original remains available.", "If the form also needs a signature, finish the fields first and then use Sign PDF."]),
        ("Before sending", ["Review names, dates, numbers, and attachments carefully. Remove any pages or information the recipient does not need."]),
    ], related=["sign-pdf", "split-pdf"]),
    dict(slug="image-to-pdf", title="Turn images into a PDF offline", description="Combine photos and scans into a PDF on your phone with ProperPDF.", lead="Turn a handful of photos or scans into one document without uploading them.", image="mockups/ios/home-portrait.png", image_alt="ProperPDF image to PDF tools on iPhone", sections=[
        ("From photos to one document", ["Receipts, whiteboards, notes, and scanned pages often start as images. ProperPDF can combine selected images into a PDF and keep the workflow on your device.", "Arrange the pages before saving so the result reads in the right order."]),
        ("How to create a PDF from images", ["Open Image to PDF, select the photos or scans you want, arrange their order, and save the new document. Open it in the viewer to check the pages before sharing.", "Merge the new PDF with another file later or compress a copy if the images make it large."]),
        ("Useful for everyday paperwork", ["Create a single PDF from receipts, application pages, travel records, or handwritten notes while keeping the original images available."]),
    ], related=["pdf-to-image", "merge-pdf"]),
    dict(slug="scan-to-pdf", title="Scan documents to PDF on your phone", description="Scan paper documents into PDFs on iPhone, iPad, and Android with ProperPDF.", lead="Turn paper pages into a useful PDF without starting with a cloud upload.", image="mockups/ios/home-portrait.png", image_alt="ProperPDF document scanning tools on iPhone", sections=[
        ("Scan where the paperwork happens", ["A phone camera is often the quickest way to capture a receipt, form, or handwritten page. ProperPDF can turn captured pages into a PDF that stays in your app library.", "Good lighting and a flat page help produce a clearer scan."]),
        ("How to scan to PDF", ["Open the scan tool, capture each page, review the page order, and save the scan as a PDF. Use Organize Pages to rotate, reorder, or remove pages afterward.", "Combine the scan with an existing PDF using Merge PDF when the paperwork has attachments."]),
        ("Keep a clean copy", ["Name the finished file clearly and keep the source pages until you have checked the saved PDF. Compress a copy when a scan is too large to send."]),
    ], related=["image-to-pdf", "merge-pdf"]),
]


def guide_html(item: dict) -> str:
    return f'''<div class="content-hero guide-hero"><div class="container"><p class="kicker">PROPERPDF GUIDE</p><h1>{escape(item["title"])}</h1><p>{escape(item["lead"])}</p></div></div><div class="container content-layout"><article class="article-body">{''.join(section(title, paragraphs) for title, paragraphs in item["sections"])}{cta()}</article><aside class="related-links"><p class="kicker">KEEP EXPLORING</p><a href="/merge-pdf">Merge PDFs offline <span aria-hidden="true">↗</span></a><a href="/split-pdf">Split PDFs offline <span aria-hidden="true">↗</span></a><a href="/compress-pdf">Compress privately <span aria-hidden="true">↗</span></a><a href="/guides">All guides <span aria-hidden="true">↗</span></a></aside></div>'''


def write(slug: str, title: str, description: str, content: str) -> None:
    path = f"/{slug}"
    (PUBLIC / f"{slug}.html").write_text(page(title, description, path, content), encoding="utf-8")


write_static_files()

for item in features:
    write(item["slug"], item["title"], item["description"], feature_html(item))

for item in guides:
    write(item["slug"], item["title"], item["description"], guide_html(item))

guide_cards = "".join(f'''<a class="guide-card" href="/{item["slug"]}"><span>GUIDE</span><h2>{escape(item["title"])}</h2><p>{escape(item["description"])}</p><strong>Read guide <span aria-hidden="true">↗</span></strong></a>''' for item in guides)
tool_cards = "".join(f'''<a class="guide-card" href="/{item["slug"]}"><span>TOOL</span><h2>{escape(item["title"])}</h2><p>{escape(item["description"])}</p><strong>Explore tool <span aria-hidden="true">↗</span></strong></a>''' for item in features)
write("features", "PDF tools for iPhone, iPad, and Android", "Explore ProperPDF's private, offline-first PDF tools for mobile devices.", f'''<div class="content-hero guide-hero"><div class="container"><p class="kicker">THE PROPERPDF TOOLKIT</p><h1>PDF tools for mobile.</h1><p>Merge, split, compress, sign, scan, convert, and organize documents on your phone.</p></div></div><section class="container guide-index"><h2>Explore PDF tools</h2><div class="guide-list">{tool_cards}</div>{cta()}</section>''')
write("guides", "PDF guides and offline tips", "Practical guides to private, offline PDF workflows with ProperPDF.", f'''<div class="content-hero guide-hero"><div class="container"><p class="kicker">LEARN WITH PROPERPDF</p><h1>Better PDF habits.<br>More privacy.</h1><p>Practical guides for getting document work done on your device.</p></div></div><section class="container guide-index"><h2>Latest articles</h2><div class="guide-list">{guide_cards}</div><h2>Explore PDF tools</h2><div class="guide-list">{tool_cards}</div></section>''')
write("blog", "The ProperPDF blog", "Practical advice for private, offline PDF workflows on mobile.", f'''<div class="content-hero guide-hero"><div class="container"><p class="kicker">THE PROPERPDF BLOG</p><h1>Useful PDF advice.<br>Without the upload.</h1><p>Short, practical articles about working with documents on your phone.</p></div></div><section class="container guide-index"><h2>Articles</h2><div class="guide-list">{guide_cards}</div></section>''')

write("support", "Support and contact", "Get help with ProperPDF, including app downloads, purchases, and PDF tools.", f'''<div class="content-hero guide-hero"><div class="container"><p class="kicker">HERE TO HELP</p><h1>ProperPDF support</h1><p>Find the right place to get help with the app.</p></div></div><div class="container support-grid"><div><h2>Contact us</h2><p>For a bug, purchase question, or feature request, email the ProperPDF team. Please include your device model, app version, and a short description of what happened.</p><p>Do not send sensitive PDFs unless you choose to share them for troubleshooting.</p><a class="button button-dark" href="mailto:hello@tryproperpdf.app?subject=ProperPDF%20support">hello@tryproperpdf.app <span aria-hidden="true">↗</span></a></div><div><h2>Quick links</h2><div class="support-links"><a href="{IOS}">ProperPDF on the App Store <span aria-hidden="true">↗</span></a><a href="{ANDROID}">ProperPDF on Google Play <span aria-hidden="true">↗</span></a><a href="/#faq">Frequently asked questions <span aria-hidden="true">↗</span></a><a href="/guides">PDF guides <span aria-hidden="true">↗</span></a></div></div></div>''')

for slug, title, description, source in [
    ("privacy-policy", "Privacy Policy", "Read the ProperPDF Privacy Policy.", "https://nepali-indie-dev.github.io/properpdf/privacy-policy.html"),
    ("terms-of-service", "Terms of Service", "Read the ProperPDF Terms of Service.", "https://nepali-indie-dev.github.io/properpdf/terms-of-service.html"),
]:
    legal_text = (Path(__file__).parent / "legal-source" / f"{slug}.html").read_text(encoding="utf-8")
    content = f'''<div class="content-hero guide-hero legal-hero"><div class="container"><p class="kicker">LEGAL INFORMATION</p><h1>{title}</h1><p>This policy applies to ProperPDF on both iOS and Android.</p></div></div><div class="container legal-layout"><div class="legal-copy">{legal_text}</div><p class="legal-source">Questions about this policy? <a href="mailto:hello@tryproperpdf.app">hello@tryproperpdf.app</a></p></div>'''
    write(slug, title, description, content)
    write("privacy" if slug == "privacy-policy" else "terms", title, description, content)

paths = ["/", "/features", "/guides", "/blog", "/support", "/privacy", "/terms", "/privacy-policy", "/terms-of-service"] + [f"/{item['slug']}" for item in features + guides]
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{xml_escape(BASE + path)}</loc></url>\n" for path in paths) + "</urlset>\n"
(PUBLIC / "sitemap.xml").write_text(sitemap, encoding="utf-8")
print(f"Generated {len(paths)} pages and sitemap.xml")
