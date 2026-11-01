"""Inline a client's SVG logo split into animatable parts.
  python scripts/logo_split.py logo.svg [--groups 5,2,2,2] [--id logoSvg] > logo_snippet.html
- Every <path>/<polygon>/<rect>/<circle> keeps its original attributes (fills, gradients) and gets class "lg".
- Paths filled with a gradient (url(#...)) are "marks": the first one gets id="lg-mark" (spin it in, reuse it as a seal).
- The other parts are grouped in document order: --groups 5,2,2,2 -> classes lg-a (5 parts), lg-b (2), lg-c, lg-d.
- <defs> (gradients) are kept; <metadata> and comments are dropped; CSS classes from <style> are resolved to fills."""
import argparse
import re
import sys

ap = argparse.ArgumentParser()
ap.add_argument("svg")
ap.add_argument("--groups", default="")
ap.add_argument("--id", default="logoSvg")
a = ap.parse_args()
src = open(a.svg, encoding="utf-8").read()
src = re.sub(r"<metadata>.*?</metadata>|<!--.*?-->|<\?xml.*?\?>", "", src, flags=re.S)
vb = re.search(r'viewBox="([^"]+)"', src).group(1)
styles = dict(re.findall(r"\.([\w-]+)\s*\{\s*fill:\s*([^;}]+)", src))      # .cls-1 { fill: url(#g) }
defs = "".join(re.findall(r"<linearGradient.*?</linearGradient>|<radialGradient.*?</radialGradient>", src, flags=re.S))
parts = re.findall(r"<(path|polygon|rect|circle|ellipse)\b([^>]*?)/?>", src)

def fill_of(attrs):
    m = re.search(r'fill="([^"]+)"', attrs)
    if m:
        return m.group(1)
    c = re.search(r'class="([^"]+)"', attrs)
    return styles.get(c.group(1).split()[0], "#fff") if c else "#fff"

sizes = [int(x) for x in a.groups.split(",") if x.strip()]
names = "abcdefghij"
out, mark_done, k, g = [], False, 0, 0
for tag, attrs in parts:
    fill = fill_of(attrs)
    attrs = re.sub(r'\s(class|fill)="[^"]*"', "", attrs).strip()
    if fill.startswith("url(") and not mark_done:
        out.append(f'<{tag} id="lg-mark" class="lg" fill="{fill}" {attrs}/>'); mark_done = True; continue
    cls = "lg"
    if sizes:
        while g < len(sizes) and k >= sizes[g]:
            k -= sizes[g]; g += 1
        cls += f" lg-{names[min(g, len(names) - 1)]}"
        k += 1
    out.append(f'<{tag} class="{cls}" fill="{fill}" {attrs}/>')
svg = f'<svg id="{a.id}" viewBox="{vb}" xmlns="http://www.w3.org/2000/svg" style="overflow:visible"><defs>{defs}</defs>' + "".join(out) + "</svg>"
sys.stdout.write(svg + "\n")
sys.stderr.write(f"{len(parts)} parts, mark: {'yes' if mark_done else 'no'}, viewBox {vb}\n"
                 "Spin the mark around its own centre: compute it from the path bbox (svgOrigin in viewBox units).\n")
