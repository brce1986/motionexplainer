---
name: motionexplainer
description: Produce a 30–90s narrated explainer / product video for a client from their website (or an assets folder) in a premium "liquid glass" motion style. The output is HTML + GSAP rendered to MP4 with HyperFrames, with the client's own logo animated, a TTS voiceover (Azure Speech HD, Gemini fallback), and a code-made soundtrack locked to the words. Use whenever the user asks for an explainer, promo, launch or product video "for this company/site", hands over a client URL or a brand folder, or says things like "faz um vídeo explicativo para esse cliente", "explainer video for this site", "video like these YouTube references for our client".
---

# Site explainer video

You turn a client's website into a finished explainer video:
- **design:** the client's own colours, gradients, fonts, photos and **logo (animated)**;
- **content:** what the client actually says about themselves;
- **motion language:** set by this skill and tuned to the user's reference videos.

The style and every rule here come from shipped client work. Read `references/style.md` before building anything.

**Works with Claude Code and with Codex (or any agent that can run shell commands and read files).** Everything runs through the scripts in this folder; nothing depends on one agent's built-in tools.
- `<skill-dir>` is the folder holding this file (e.g. `~/.claude/skills/motionexplainer` or `~/.codex/skills/motionexplainer`).
- **Looking at images** (contact sheets, snapshots, reference frames): use your image viewer (Claude: Read on the PNG; Codex: `view_image` / attach the file).
- **Reading the client's site:**
  - with a browser tool, open the page and run `scripts/extract_brand.js`;
  - without one, run `python <skill-dir>/scripts/extract_brand.py <url> brand/`, which uses Playwright when installed and falls back to plain HTTP + CSS parsing.
- **Long renders:** run them in the background (or with a long timeout) and wait for them to finish.

## HARD STOPS (read this before anything else)

These are not style advice. Each one exists because an agent skipped it and shipped a film that looked like a slideshow. **When a step below fails, stop and tell the user what failed and what you need. Never substitute something weaker and carry on.**

| If… | Then | Never |
|---|---|---|
| a required key fails (401/403/quota) | stop, show the HTTP status, ask for a working key or region. Try the other TTS provider if its key is set. | use an OS voice (SAPI, `say`, espeak), speed up a weak take, or render with a "temporary" voice |
| you can't get contact sheets of a reference (download blocked, no yt-dlp) | stop and ask for a local file or timestamps + what they like | describe a reference you only saw one frame of |
| the client's webfont can't be self-hosted | stop and ask for the font files, or for approval of a named substitute shown on the style board | silently fall back to Arial/Helvetica/system fonts |
| `logo_split.py` errors or the logo looks wrong | fix the SVG (bake transforms) or ask for a better SVG | use the logo as an `<img>` in the lockup |
| `lint_composition.py` fails | fix the composition | render |
| `motion_check.py` fails on a render | rebuild the failing scenes | deliver, or explain the failure away in the notes |

**You build from the scene kit, `templates/kit/index.html`** (`references/scene-kit.md`): six scenes taken from shipped films (hook, reveal, ask, compare, detail, lockup) with the house helpers (`cam`, `fly`, `morph`, `focus`, `rise`, `texts`). You choose scenes, time them to the voice and fill them with the client's material. Do not write your own animation engine, do not use WAAPI (`element.animate`) or CSS animations, do not start from an empty HTML file, do not invent new layouts without an approved style frame. A fresh engine and fresh layouts are how every failed film so far became slides.

**The user sees the film twice before the final render, always.** Even when they said "go straight through" or "don't ask me anything", these two stops are not optional; they're how every good film here got made:
1. **G2c style frames:** 3 stills of the kit filled with the client's real material (a hook frame, a product frame, the lockup).
2. **G6b animatic:** the 1-fps contact sheet of a draft render + the motion report.
If the user is away, prepare both, say what you're waiting for, and stop. Delivering a final render without these approvals is a failed delivery.

**The checks are a floor, not the goal.** Never read the checkers' source to find what passes them, never shape the code to satisfy a pattern (an aliased font, a path renamed to match a regex, drift added only to raise a motion score). If a check fails, the film has the problem it describes: fix the film.

**Never reuse a direction the user rejected.** If an earlier cut of this client was rejected, start G2b again from the site and the references; don't copy its `tokens.css`, `design-system.md` or layouts.

**The two gates are scripts, not opinions:**
```bash
python <skill-dir>/scripts/lint_composition.py video/index.html      # before ANY render (draft or final)
python <skill-dir>/scripts/motion_check.py <render>.mp4              # after EVERY render; must PASS before delivery
```
Paste both outputs in the delivery note. A note that says "the checks don't establish quality" is not a delivery; fix the film.

## STEP 0: check the machine, then the first reply (mandatory, before any work)

**Before replying**, run the dependency check:
```bash
python <skill-dir>/scripts/doctor.py
```
It checks:
- Python ≥ 3.10;
- FFmpeg + FFprobe, with the loudnorm/ebur128/tile filters and libx264;
- Node.js ≥ 20 + npx;
- numpy + scipy;
- that HyperFrames (pinned) runs through npx, together with its headless Chromium;
- network access to the GSAP CDN;
- optional: yt-dlp, Playwright and git;
- which keys are set (values hidden).

It prints the install command for this OS for anything missing. Put the result **at the top of your first message**: what is ready, and what to install with the exact commands. Offer to install what can be installed from the shell (pip packages, `npx` caches) once the user agrees. Never install system packages without asking.

Then your **first message** lists what you need. Do not research, write or render anything until the user has answered. Send this checklist in the user's language:

1. **The client:** the website URL **or** a folder with brand assets (screenshots, photos, brand guide).
2. **The product logo:** an SVG file or a URL. SVG is strongly preferred because the logo gets animated part by part. PNG works, but it can only be animated as a whole.
3. **At least 3 reference videos** (YouTube links or files): the look, pace and transitions they like. Ask what they like in each one.
4. **API keys, kept as environment variables, never pasted into files that get shared:**
   - `AZURE_SPEECH_KEY` + `AZURE_SPEECH_REGION`: the primary voice (HD neural voices) and the transcription check;
   - `GEMINI_API_KEY`: the fallback voice.
   Explain how to set them: copy `.env.example` to `.env` in the working folder, or `export`/`setx` them. At least one TTS key is required. Without Azure, the transcription check is skipped and you must say so.
5. **Optional, stock imagery:** a free `PEXELS_API_KEY` and/or `PIXABAY_API_KEY` if they want extra photos beyond the client's own. Offer it, don't require it.
6. **Specs:**
   - format: 16:9 / 9:16 / 1:1;
   - duration: default 60s;
   - VO language and gender/tone;
   - CTA and URL;
   - anything that must or must not appear.

If something is missing, ask for it once, clearly, and continue only with what you have when it's optional (specs have defaults). Site/assets, logo, 3 references and one TTS key are **required**.

Never print, log, commit or write a key into a project file. Scripts read keys from the environment (or a local `.env` that `.gitignore` excludes). If the user pastes a key in chat:
- use it only through an environment variable for the session;
- remind them to rotate it.

## The pipeline (gates: show the result of each, then go on)

| Gate | What | Guide |
|---|---|---|
| G1 | **Read the references.** Contact sheets of **every** reference with `scripts/ref_frames.py` (the whole video, not an opening frame). Write what to borrow: pace, transitions, camera, type, density. **No sheets, no G1:** stop and ask. | `references/reference-videos.md` |
| G2 | **Extract the brand** from the site: colours, gradients, fonts (self-hosted webfonts), photos, logo. Understand the business: problem, audience, sides, proof points. | `references/brand-extraction.md` |
| G2b | **Design system for this video:** merge the client's brand (G2) with the references' treatment (G1) into `design-system.md` + `tokens.css`. Render the style board (`templates/design-system.html`) to a PNG: palette, gradient, type scale, glass, buttons, background, logo. **Show it for approval.** Fill photo gaps with stock only if keys were given. **Light brand** (white/near-white site)? Use its darkest colour as the stage, or the kit's `solid` cards: never glass on white (`references/scene-kit.md`). | `references/design-system.md`, `references/stock-images.md` |
| G2c | **Style frames (mandatory approval):** fill the kit with the client's real copy, photos, UI and split logo, then `npx hyperframes snapshot` 3 frames: the hook, the main product scene, the lockup. **Show them and wait for approval.** No approval, no G6. | `references/scene-kit.md` |
| G3 | **Script + beat sheet** in `TREATMENT.md`. ~2.2 words/s for the VO; every claim from the client's own material, nothing invented. One verb or short title per beat, **and the kit scene that carries it** (`references/scene-kit.md`). **Stop here for approval** unless the user said to go straight through. | `references/script.md` |
| G4 | **Voice:** 2 takes (2 voices) with `scripts/tts_azure.py` (fallback `scripts/tts_gemini.py`). Verify each with `scripts/stt_check.py`: every sentence present, the brand pronounced right. Pick one take and export word timings. **Only Azure HD or Gemini voices.** If neither works, stop: there is no fallback below them. | `references/audio.md` |
| G5 | **Soundtrack:** `scripts/soundtrack.py` with a cues JSON. BPM fitted so the brand line lands on a downbeat; SFX on the word timings; music ducked under the VO; -14 LUFS. Re-run `stt_check.py` on the **mix** (SFX can mask words). | `references/audio.md` |
| G6 | **Build** from the scene kit (`templates/kit/index.html`): pick the scenes for the beat sheet, set `S`/`WT` from the word timings, replace every `[REPLACE]` with the client's material, import `tokens.css`, paste the split logo. `scripts/lint_composition.py` must pass. | `references/scene-kit.md`, `references/style.md`, `references/build.md` |
| G6b | **Animatic (mandatory approval):** a draft render (`-q draft`, 30fps is fine here), `motion_check.py --min-fps 30` on it, and a 1-frame-per-second contact sheet of the whole film. **Show the sheet and the motion report and wait for approval before the final render**, whatever the user said about going straight through. Look at it yourself first and fix anything that reads as slides. | `references/qa.md` |
| G7 | **QA:** `npx hyperframes check`, snapshots, then `scripts/sheets.py` on the rendered MP4 around **every** transition. Fix every glitch before delivering. | `references/qa.md` |
| G8 | **Render** at 60fps (`-f 60 -q delivery`). `motion_check.py` must PASS on this file. `stt_check.py` on the mix. Deliver the MP4 with a short note: what each scene does, both check outputs, what was not verified (e.g. you can't listen to audio), open risks. | `references/build.md` |

If the user asks for several cuts (e.g. "with phone / without phone / free style"), they share G2b–G5. Build each cut as its own folder with its own sources.

## Non-negotiables (learned the hard way)

- **Never a slideshow.** The camera moves all the time and the background is always alive. Elements fly between scenes; no hard cuts, no "fade in a static card". What a slideshow looks like, so you recognise it in your own contact sheet:
  - every scene has the same layout (title left, card right) and only the words change;
  - scenes fade out to the empty background, then the next one fades in;
  - nothing moves for more than a second while the voice talks;
  - the subject is small, with half the frame empty;
  - the camera is a 2D drift of a few pixels.
  `motion_check.py` measures the second, third and (through low motion) the fifth; the first and fourth you check on the G6b sheet.
- **The subject fills the frame.** At 1920×1080 the hero element (card, phone, photo, headline) takes at least a third of the frame; headlines are at least ~110px. Small cards floating in a big empty canvas read as a web page, not a film.
- **Vary the staging.** At most two scenes in a row may share a layout. Change the camera angle, the subject's size and its position between beats.
- **The client's logo is used and animated**, from their own SVG, never redrawn. Never draw illustrations or shapes by hand in SVG; use the client's photos, real UI rebuilt in HTML, or licensed libraries.
- **Brand colours and gradients drive everything:**
  - text is white (or the brand's ink);
  - highlights use the brand gradient (background-clip text);
  - one colour = one meaning.
- **Glitch-free transitions.** Check every one in the rendered MP4, not just in the editor.
- **Keys stay out of the files.**

## Tooling

- **Video:** HyperFrames (`npx --yes hyperframes@<pinned> check|snapshot|render`) + GSAP 3 from the jsDelivr CDN. If the hyperframes skills are installed, read `hyperframes-core` before the first composition.
- **Tools:**
  - FFmpeg/FFprobe on PATH;
  - Python 3.10+ with numpy and scipy (soundtrack);
  - yt-dlp (optional, for reference frames).
- **Full list** (what `doctor.py` checks): Python 3.10+ (numpy, scipy), FFmpeg/FFprobe (full build), Node.js 20+ / npx, HyperFrames (via npx, with its bundled headless Chromium), GSAP 3.14.2 (CDN, needs network), yt-dlp (optional), Playwright + Chromium (optional, for `extract_brand.py`), git (optional), Azure Speech (TTS + fast transcription REST APIs), Gemini API (TTS fallback), Pexels / Pixabay APIs (optional stock photos).
