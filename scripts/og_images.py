"""Render 1200x630 social share cards for every generated page into public/og/.

Run locally after `npm run build` whenever page titles change:
    python3 scripts/og_images.py            # only cards that are missing
    python3 scripts/og_images.py --all      # re-render every card
It drives a local Chromium-family browser in headless mode (Edge by default; set
OG_BROWSER to another binary). The PNGs are committed, because the Cloudflare
build has no browser. Run `npm run build` again afterwards so pages link the cards.
"""

from html import escape
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
OUT = PUBLIC / "og"
BROWSER = os.environ.get("OG_BROWSER", "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge")
ICON = (PUBLIC / "assets" / "icon.png").as_uri()
# Card language and tagline per translated folder, from i18n/<code>.json.
LANGS = {path.stem: ({"pt-br": "pt-BR"}.get(path.stem, path.stem), json.loads(path.read_text(encoding="utf-8"))["ui"]["footer_tagline"])
         for path in (ROOT / "i18n").glob("*.json") if path.stem != "en"}

TEMPLATE = """<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><style>
html,body{{margin:0;width:1200px;height:630px;overflow:hidden}}
body{{background:#f8f7f3;color:#17242d;font-family:'Avenir Next','Segoe UI',system-ui,sans-serif;
  display:flex;flex-direction:column;justify-content:space-between;padding:68px 80px 60px;box-sizing:border-box;
  border-bottom:10px solid #1671c4}}
.brand{{display:flex;align-items:center;gap:16px;font-size:30px;font-weight:700;letter-spacing:-.02em}}
.brand img{{width:60px;height:60px;border-radius:14px}}
h1{{word-break:auto-phrase;text-wrap:balance;margin:0;font-size:{size}px;line-height:1.08;letter-spacing:-.045em;font-weight:800;max-width:1000px}}
.foot{{display:flex;justify-content:space-between;font-size:24px;color:#5e6b73}}
.foot strong{{color:#17242d;font-weight:700}}
</style></head><body>
<div class="brand"><img src="{icon}" alt=""><span>ProperPDF</span></div>
<h1>{title}</h1>
<div class="foot"><span>{tagline}</span><strong>tryproperpdf.app</strong></div>
</body></html>"""


def font_size(title: str) -> int:
    return 76 if len(title) <= 38 else 66 if len(title) <= 56 else 56


def render(slug: str, title: str, workdir: Path) -> None:
    page = workdir / f"{slug.replace('/', '_')}.html"
    (OUT / slug).parent.mkdir(parents=True, exist_ok=True)
    code = slug.split("/")[0] if "/" in slug else "en"
    lang, tagline = LANGS.get(code, ("en", "Offline PDF tools for iPhone and Android"))
    page.write_text(TEMPLATE.format(title=escape(title), size=font_size(title), icon=ICON, lang=lang, tagline=escape(tagline)), encoding="utf-8")
    subprocess.run([BROWSER, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={workdir / 'profile'}",
                    "--window-size=1200,630", "--force-device-scale-factor=1", f"--screenshot={OUT / (slug + '.png')}", page.as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)


def main() -> None:
    pages = json.loads((ROOT / "scripts" / "og-pages.json").read_text(encoding="utf-8"))
    OUT.mkdir(exist_ok=True)
    redo = "--all" in sys.argv
    todo = {slug: page for slug, page in pages.items() if redo or not (OUT / f"{slug}.png").exists()}
    with tempfile.TemporaryDirectory() as tmp:
        for slug, page in todo.items():
            render(slug, page["title"], Path(tmp))
            print(f"og/{slug}.png")
    print(f"Rendered {len(todo)} of {len(pages)} cards. Run `npm run build` so pages link them.")


if __name__ == "__main__":
    main()
