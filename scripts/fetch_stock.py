"""Optional: free stock photos (Pexels / Pixabay) to fill gaps the client's own photos don't cover.
  python scripts/fetch_stock.py "dog walker city street" assets/img/stock --n 6 [--source pexels|pixabay|both] [--orientation landscape]
Writes the images plus credits.json (source, author, page URL, licence) for every file. Read the credits before using.
Env: PEXELS_API_KEY and/or PIXABAY_API_KEY (both free). Keys are never printed or saved."""
import argparse
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

from _env import has, need

UA = {"User-Agent": "motionexplainer/1.0"}


def get_json(url, headers=None):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    try:
        return json.load(urllib.request.urlopen(req, timeout=30))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"stock API error: HTTP {e.code} (check the key and the query)")


def pexels(q, n, orientation):
    params = {"query": q, "per_page": n, "orientation": orientation}
    d = get_json("https://api.pexels.com/v1/search?" + urllib.parse.urlencode(params), {"Authorization": need("PEXELS_API_KEY")})
    for p in d.get("photos", []):
        yield {"src": p["src"]["large2x"], "id": f"pexels-{p['id']}", "author": p["photographer"], "author_url": p["photographer_url"],
               "page": p["url"], "alt": p.get("alt", ""), "license": "Pexels License (free to use; credit appreciated): https://www.pexels.com/license/"}


def pixabay(q, n, orientation):
    params = {"key": need("PIXABAY_API_KEY"), "q": q, "image_type": "photo", "per_page": max(3, n), "safesearch": "true",
              "orientation": {"landscape": "horizontal", "portrait": "vertical"}.get(orientation, "all")}
    d = get_json("https://pixabay.com/api/?" + urllib.parse.urlencode(params))
    for h in d.get("hits", [])[:n]:
        yield {"src": h["largeImageURL"], "id": f"pixabay-{h['id']}", "author": h["user"], "author_url": f"https://pixabay.com/users/{h['user']}-{h['user_id']}/",
               "page": h["pageURL"], "alt": h.get("tags", ""), "license": "Pixabay Content License: https://pixabay.com/service/license-summary/"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("out")
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--source", default="auto", choices=["auto", "pexels", "pixabay", "both"])
    ap.add_argument("--orientation", default="landscape", choices=["landscape", "portrait", "square"])
    a = ap.parse_args()
    srcs = {"pexels": ["pexels"], "pixabay": ["pixabay"], "both": ["pexels", "pixabay"],
            "auto": [s for s, k in (("pexels", "PEXELS_API_KEY"), ("pixabay", "PIXABAY_API_KEY")) if has(k)]}[a.source]
    if not srcs:
        raise SystemExit("No stock key set (PEXELS_API_KEY or PIXABAY_API_KEY). This step is optional: use the client's photos.")
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    credits_path = out / "credits.json"
    credits = json.loads(credits_path.read_text(encoding="utf-8")) if credits_path.is_file() else []
    fn = {"pexels": pexels, "pixabay": pixabay}
    for s in srcs:
        for item in fn[s](a.query, a.n, a.orientation):
            name = re.sub(r"[^\w-]", "", item["id"]) + ".jpg"
            data = urllib.request.urlopen(urllib.request.Request(item["src"], headers=UA), timeout=60).read()
            (out / name).write_bytes(data)
            credits.append({"file": name, "query": a.query, **{k: v for k, v in item.items() if k != "src"}})
            print(f"{name}  by {item['author']}  ({s})")
    credits_path.write_text(json.dumps(credits, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\ncredits -> {credits_path}. Check each image: no visible brands/logos, no person implying endorsement, consistent grade.")


if __name__ == "__main__":
    main()
