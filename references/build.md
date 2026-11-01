# G6 / G8: Building and rendering

## Project layout
```
<client>-explainer/
  TREATMENT.md          # references, tokens, story, script, beat sheet, decisions per round
  script.txt            # VO text, one sentence per line
  cues.json             # soundtrack cues
  audio/                # takes, vo_words.json, music/sfx/mix
  src/                  # composition sources (template + script), never inside video/
  video/                # the HyperFrames project: index.html, assets/, hyperframes.json, package.json, meta.json
```
- Keep the sources **outside** `video/`: HyperFrames rejects a second root composition in the same folder.
- For several cuts, use `src_v2/` → `video_v2/` and so on, each with its own `meta.json` id.

## Starting
1. `npx --yes hyperframes@<version> init video --example blank --resolution landscape --non-interactive` (or `portrait` for 9:16).
2. Copy `templates/composition.html` to `video/index.html` and set the size, duration and brand tokens.
3. Put the client's fonts in `video/assets/fonts`, photos in `video/assets/img`, the mix in `video/assets/audio/mix.mp3`.
4. **The logo:** `python scripts/logo_split.py client-logo.svg --groups 5,2,2,2 > logo_snippet.html`. Paste the result where the template says `<!--LOGO-->`. Each group gets a class (`lg-a`, `lg-b`…) and the first gradient-filled path gets `id="lg-mark"`. Open the SVG first to decide the groups (words, the mark, ™).

## Rules the runtime enforces (read hyperframes-core if available)
- One paused timeline at `window.__timelines["main"]`, registered after fonts and images load.
- No `Math.random`, `Date.now()` or CSS transitions. Seeded or fixed values only.
- Every `<audio>` has an `id`. `@font-face` for every named font.
- Never tween `visibility`/`autoAlpha` on a `.clip`.
- `data-layout-ignore` on decorative layers that overlap by design (background photos, modal sheets, grids under focus blur), so the layout audit stays meaningful.

## Rendering
```bash
cd video
npx --yes hyperframes@<version> check
npx --yes hyperframes@<version> snapshot --at 3,8,15,...      # read the contact sheet
npx --yes hyperframes@<version> render -o ../<Client>_explainer.mp4 -f 60 -q delivery
```
- A 55s render at 60fps takes ~5–10 min. Run it in the background.
- After rendering, run the QA in `qa.md` on the **MP4**.

## Delivering
Send the MP4 and a short note:
- scene by scene, what happens;
- what was verified and how (frames, transcription);
- what wasn't (e.g. you can't listen to the audio);
- open risks (UI designed without real screenshots, font licence).

Record every round's feedback and fixes in TREATMENT.md.
