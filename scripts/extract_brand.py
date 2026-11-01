"""Brand extraction from the command line, for agents without a browser tool (e.g. Codex CLI).
  python scripts/extract_brand.py https://client.com brand/            # -> brand/brand.json, hero.png, page.txt
Mode 1 (best): Playwright + Chromium renders the page and runs extract_brand.js (computed styles, gradients, fonts).
   pip install playwright && python -m playwright install chromium
Mode 2 (fallback, no install): fetches the HTML and its CSS and pulls :root variables, gradients, @font-face,
   Google Fonts links, images and the visible text with regexes. Less exact: no computed styles."""
import json
import re
import sys
import urllib.request
from html import unescape
from pathlib import Path
from urllib.parse import urljoin

UA = {"User-Agent": "Mozilla/5.0 (motionexplainer brand extraction)"}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode("utf-8", "replace")


def with_playwright(url, out):
    from playwright.sync_api import sync_playwright
    js = (Path(__file__).parent / "extract_brand.js").read_text(encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.goto(url, wait_until="networkidle", timeout=60000)
        pg.screenshot(path=str(out / "hero.png"))
        pg.screenshot(path=str(out / "full.png"), full_page=True)
        data = pg.evaluate(js)
        (out / "page.txt").write_text(pg.inner_text("body"), encoding="utf-8")
        b.close()
    return data


def with_regex(url, out):
    html = get(url)
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, flags=re.S))
    sheets = [urljoin(url, h) for h in re.findall(r'<link[^>]+rel=["\']?stylesheet["\']?[^>]*href=["\']([^"\']+)', html)]
    sheets += [urljoin(url, h) for h in re.findall(r'<link[^>]+href=["\']([^"\']+\.css[^"\']*)', html)]
    for s in dict.fromkeys(sheets):
        try:
            css += "\n" + get(s)
        except Exception:
            pass
    text = re.sub(r"\s+", " ", unescape(re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", html, flags=re.S))).strip()
    (out / "page.txt").write_text(text, encoding="utf-8")
    return {
        "url": url,
        "mode": "regex (approximate; install Playwright for computed styles)",
        "rootVars": dict(re.findall(r"(--[\w-]+)\s*:\s*([^;}{]+)", css)[:150]),
        "gradients": list(dict.fromkeys(re.findall(r"(?:linear|radial|conic)-gradient\([^;{}]+\)", css)))[:30],
        "colors": [c for c, _ in sorted(((c, css.count(c)) for c in set(re.findall(r"#[0-9a-fA-F]{6}\b", css))), key=lambda x: -x[1])][:20],
        "fontFaces": [urljoin(url, u) for u in re.findall(r"@font-face[^}]*?url\(['\"]?([^)'\"]+)", css)][:20],
        "fontFamilies": list(dict.fromkeys(f.strip().strip("'\"") for f in re.findall(r"font-family\s*:\s*([^;,}]+)", css)))[:15],
        "fontLinks": re.findall(r'href=["\'](https://fonts\.googleapis\.com[^"\']+)', html),
        "logo": [urljoin(url, s) for s in re.findall(r'<img[^>]+src=["\']([^"\']*logo[^"\']*)', html, flags=re.I)][:5],
        "images": list(dict.fromkeys(urljoin(url, s) for s in re.findall(r'<img[^>]+src=["\']([^"\']+)', html) if not s.startswith("data:")))[:40],
        "title": (re.findall(r"<title>(.*?)</title>", html, flags=re.S) or [""])[0].strip(),
    }


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    url, out = sys.argv[1], Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    try:
        data = with_playwright(url, out); data["mode"] = "playwright"
    except ImportError:
        print("Playwright not installed: using the regex fallback (pip install playwright && python -m playwright install chromium)")
        data = with_regex(url, out)
    (out / "brand.json").write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out / 'brand.json'} ({data['mode']}), page.txt" + (", hero.png, full.png" if data["mode"] == "playwright" else ""))


if __name__ == "__main__":
    main()
