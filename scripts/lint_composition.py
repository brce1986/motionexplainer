"""The build gate: checks that a composition uses the house engine before anything is rendered.
  python scripts/lint_composition.py video/index.html [--duration 60]
Fails (exit 1) when the composition:
- doesn't load GSAP or register window.__timelines["main"];
- animates with anything else: WAAPI (el.animate), CSS @keyframes/animation, CSS transitions;
- has no 3D world (#space + #world, preserve-3d) or too few camera moves / flights / morphs for its length;
- shows the logo as an <img> or a flat block instead of the inline split SVG (.lg parts) animated in parts;
- has no @font-face, or aliases a system font with local() (a system font changes the brand), or no tokens.css;
- still contains [REPLACE] placeholders from the scene kit;
- uses Math.random or Date.now (renders must be deterministic).
Writing an engine from scratch is how a film turns into slides: start from templates/kit/index.html.
Make the film good, not this script quiet: these checks only catch the worst failures, and the user reviews the film."""
import argparse
import re
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("html")
ap.add_argument("--duration", type=float, help="film length in seconds (default: data-duration of #root)")
a = ap.parse_args()
src = Path(a.html).read_text(encoding="utf-8")
code = re.sub(r"<!--.*?-->", "", src, flags=re.S)
js = "\n".join(re.findall(r"<script[^>]*>(.*?)</script>", code, flags=re.S))
css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", code, flags=re.S))
js_nc = re.sub(r"//[^\n]*|/\*.*?\*/", "", js, flags=re.S)
dur = a.duration
if dur is None:
    m = re.search(r'data-composition-id="main"[^>]*data-duration="([\d.]+)"|data-duration="([\d.]+)"[^>]*data-composition-id="main"', code)
    dur = float(next(g for g in m.groups() if g)) if m else 60.0

def calls(name):
    return len(re.findall(rf"(?<![\w.]){name}\(\s*tl\b", js_nc))

errors, notes = [], []
def need(ok, msg):
    (notes if ok else errors).append(("ok   " if ok else "FAIL ") + msg)

need(re.search(r"gsap(@[\d.]+)?/dist/gsap(\.min)?\.js", code), "GSAP is loaded")
need('__timelines["main"]' in js_nc or "__timelines['main']" in js_nc, 'one timeline registered at window.__timelines["main"]')
need(not re.search(r"\.animate\(\s*\[|\.animate\(\s*keyframes|\bel\.animate\(", js_nc), "no WAAPI (element.animate)")
need(not re.search(r"@keyframes|\banimation\s*:", css), "no CSS @keyframes / animation")
need(not re.search(r"\btransition\s*:", css), "no CSS transitions")
need(not re.search(r"Math\.random|Date\.now", js_nc), "no Math.random / Date.now")
need('id="space"' in code and 'id="world"' in code and "preserve-3d" in css, "a 3D world (#space > #world, preserve-3d)")

n_cam, n_fly, n_morph = calls("cam"), calls("fly"), calls("morph")
need(n_cam >= dur / 6, f"camera moves: {n_cam} cam() calls (need >= {dur / 6:.0f}, one per ~6s)")
need(n_fly >= dur / 8, f"flights: {n_fly} fly() calls (need >= {dur / 8:.0f}, one per ~8s)")
box_morphs = len(re.findall(r"scaleX\s*:", js_nc))
if n_morph or box_morphs:
    notes.append(f"ok   morphs: {n_morph} morph() calls, {box_morphs} scaleX box tweens")
else:
    notes.append("WARN no morph: at least one element should become the next one (morph() helper)")

lg_parts = len(re.findall(r'<(?:path|polygon|rect|circle|ellipse)[^>]*class="lg\b', code))
logo_img = re.search(r'<img[^>]*(logo|brand)[^>]*>', code, flags=re.I)
need(lg_parts >= 2, f"the lockup logo is the inline split SVG from logo_split.py ({lg_parts} .lg parts)")
if logo_img:
    notes.append("WARN an <img> logo is also used: fine inside a UI mockup, never as the lockup")
need(re.search(r"#lg-mark|\.lg-[a-j]\b|\.lg\b", js_nc) is not None, "the logo parts are animated (#lg-mark / .lg-a ...)")
faces = re.findall(r"@font-face\s*\{[^}]*\}", css)
need(bool(faces) and all(re.search(r"url\(", f) for f in faces) and not any("local(" in f for f in faces),
     "the brand font is self-hosted (@font-face with url(), no local() aliases)")
body = re.sub(r"<script.*?</script>|<style.*?</style>", "", code, flags=re.S)
left = len(re.findall(r"\[REPLACE\]", body + js_nc))
need(left == 0, f"no [REPLACE] placeholders left ({left} found)")
empty_photos = len(re.findall(r'class="[^"]*\bphoto\b[^"]*"[^>]*>(?!\s*<img)', body))
if empty_photos:
    notes.append(f"WARN {empty_photos} .photo slots have no <img>: use the client's photos, not the gradient stand-ins")
need("tokens.css" in code, "tokens.css is imported")

for line in sorted(notes, key=lambda l: l.startswith("WARN")) + errors:
    print(line)
print(f"\n{a.html}: {dur:g}s, {len(errors)} problem(s)")
if errors:
    print("Build from templates/kit/index.html and its helpers (cam, fly, morph, focus, rise, texts). See references/scene-kit.md.")
sys.exit(1 if errors else 0)
