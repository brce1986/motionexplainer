# The scene kit (G6)

`templates/kit/index.html` is a complete, rendering film made of **six scenes taken from shipped client work**. You build a video by **choosing scenes, timing them to the voice and filling them with the client's material**, not by designing scenes from scratch. Inventing a new layout is the exception and needs the user's approval on a style frame first.

Why: the films that worked were never first drafts. They came out of many review rounds; the kit is what survived those rounds. An agent that starts from an empty canvas reproduces the rejected first drafts (a title on the left, a small card on the right, a fade, repeat).

## How to use it
1. Copy `templates/kit/index.html` to `video/index.html` and `tokens.css` (G2b) next to it.
2. Map the beat sheet (G3) to scenes. Delete the scenes you don't use: their HTML block **and** their line in `build()`.
3. Set `S` (scene starts) and `WT` (title-band words) from the VO word timings (`stt_check.py --words`).
4. Replace every `[REPLACE]`:
   - copy → the client's own words;
   - `.photo` slots → `<img src="assets/img/....jpg" alt="" />` with the client's photos (from the site, G2; stock only to fill gaps, with credits);
   - UI rows → the client's real UI, rebuilt in HTML.
5. Paste the split logo (`scripts/logo_split.py`) into the LOGO slot. The lockup finds `#lg-mark` and spins it around its own centre; `.lg-a`…`.lg-e` rise in groups.
6. `lint_composition.py` must pass. It fails while any `[REPLACE]` is left.

A scene can be used twice: duplicate its HTML with new ids and call its function again with a new start.

## The scenes

| # | Scene | Min. length | What it says | What you swap |
|---|---|---|---|---|
| 1 | **Hook** `sceneHook` | 4.5s | The everyday problem, one short line at a time; earlier lines step up and dim. Ends with an **iris** (or the logo's mark) that spins in and passes the lens. | 2–4 lines of the script's hook; the sting word in `.g`. Use the logo's mark as the iris when it has one. |
| 2 | **Reveal** `sceneReveal` | 4s | The product's world: one big photo arrives from depth (slow push-in), steps back and **opens into a 3×2 mosaic** of what the client offers. | the hero photo + 6 tiles (services, products, use cases) with the client's photos and names. |
| 3 | **Ask** `sceneAsk` | 2.4s | The user's intent: the mosaic goes out of focus and steps back; an input floats in front and **types** a real query. | the label, the query (`QUERY`), two filter chips. Works for search, a form, a prompt, a message. |
| 4 | **Compare** `sceneCompare` | 3s | Options: three cards **jump out of the input** in a fan; their attributes light up in turn with the VO. | three options (people, plans, products) with their real attributes. |
| 5 | **Detail** `sceneDetail` | 4s | The choice: a tap on the middle card, the others leave into depth, it **morphs** into a detail card; checks fill one by one; the action button confirms. | the detail title, 3 checks (proof points from the site), the action and its confirmed state. |
| 6 | **Lockup** `sceneLockup` | 5s | The brand: glows converge, the **logo builds part by part** (mark spins), the tagline arrives, then logo + tagline lift for the CTA and the URL (with `www.`). | the split logo, tagline, CTA, URL. |

Typical stories:
- **Marketplace / services:** 1 → 2 → 3 → 4 → 5 → 6 (the Built In One film).
- **SaaS / workflow:** 1 → 2 (modules instead of services) → 3 (a request) → 5 (approval checks) → 6.
- **20s cut:** 1 → 2 → 5 → 6.

Things that stay the same in every film: the background (glows, beam, blurred client photos at the edges), the camera calls in each scene, the title band, the helpers.

## Light brands
The style needs something dark or saturated behind the glass. For a brand whose site is white or near-white:
1. **Preferred:** keep the stage dark using the brand's own darkest colour as `--ink` (most light brands have a near-black ink) and its accent as `--a`/`--b`. The film stays on-brand and the glass reads.
2. Otherwise add `class="solid"` to `#root`: cards become solid (`--card`, `--card-text`) with a deep shadow, over a tinted background (`--ink` = a mid-tone of the brand, never near-white).

Never put translucent glass on a near-white background: it turns into faint grey boxes.

## What not to do
- Don't rebuild these scenes in your own code, and don't swap the helpers for your own.
- Don't keep the gradient stand-ins in `.photo` slots in a delivered film: use the client's images.
- Don't shrink cards or type to fit more: one subject per frame, reading text at least 28px on screen.
