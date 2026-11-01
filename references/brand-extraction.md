# G2: Extracting the brand and the story

## From a website
Use either way:
- **With a browser tool** (Claude Code): open the site, read the full page text, and run `scripts/extract_brand.js` in the page.
- **From the shell** (Codex, or any agent): `python scripts/extract_brand.py <url> brand/`. It writes `brand.json`, `page.txt` and screenshots (`hero.png`, `full.png`).
  - With Playwright it runs the same JS on the rendered page (`pip install playwright && python -m playwright install chromium`).
  - Without it, it falls back to parsing the HTML/CSS: approximate, and with no screenshots.

Both return JSON with:
- the CSS custom properties on `:root`, which often hold the brand tokens and gradients (e.g. `--brand-gradient`);
- every gradient in use, the background colours, the most-used text colours;
- the font families, `@font-face` sources (self-hosted woff2 URLs) and Google Fonts links;
- `<img>` sources: logo, hero and section photos;
- the H1 style (font, size, weight, tracking) and any gradient-clipped headline span.

Then take one screenshot of the hero to see the composition.

**Ask before downloading** the logo, webfonts and photos into `<project>/assets/`. They are the client's material, used for the client's own video. Note anything whose licence needs confirming (commercial webfonts, stock photos) in TREATMENT.md.

## From an assets folder
Read everything:
- brand guide PDF: colours, fonts, logo rules;
- logo files: prefer SVG;
- screenshots of the product: real UI to rebuild;
- photos.

If colours aren't documented, sample them from the screenshots.

## The token table (write it in TREATMENT.md)
| Role | Value |
|---|---|
| Background(s) | … |
| Text / secondary text | … |
| Brand colour A (meaning) | … |
| Brand colour B (meaning) | … |
| Signature gradient | … |
| Glow colours | … |
| Glass | … |
| Fonts | display / UI / numbers |

## The story
From the client's own words, write down:
- the problem;
- the audience (one side or two?);
- the 3–5 things the product does;
- the proof points (verification, numbers, guarantees);
- the places or segments;
- the CTA.

**Every claim in the script must trace back to this list.** Never invent prices, numbers, testimonials or guarantees. Example values inside UI mockups (a price on a card) must be plausible and consistent across scenes.

If the site shows no product UI, say so: the screens will be designed in the brand's language and may not match the real app. Ask for screenshots if they exist.
