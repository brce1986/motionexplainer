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
5. **Specs:**
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
| G1 | **Read the references.** Pull frames from each video and write what to borrow: pace, transitions, camera, type, density. | `references/reference-videos.md` |
| G2 | **Extract the brand** from the site: colours, gradients, fonts (self-hosted webfonts), photos, logo. Understand the business: problem, audience, sides, proof points. | `references/brand-extraction.md` |
| G3 | **Script + beat sheet** in `TREATMENT.md`. ~2.2 words/s for the VO; every claim from the client's own material, nothing invented. One verb or short title per beat. **Stop here for approval** unless the user said to go straight through. | `references/script.md` |
| G4 | **Voice:** 2 takes (2 voices) with `scripts/tts_azure.py` (fallback `scripts/tts_gemini.py`). Verify each with `scripts/stt_check.py`: every sentence present, the brand pronounced right. Pick one take and export word timings. | `references/audio.md` |
| G5 | **Soundtrack:** `scripts/soundtrack.py` with a cues JSON. BPM fitted so the brand line lands on a downbeat; SFX on the word timings; music ducked under the VO; -14 LUFS. Re-run `stt_check.py` on the **mix** (SFX can mask words). | `references/audio.md` |
| G6 | **Build** the composition from `templates/composition.html`: one 3D world, moving camera, glass, flights and morphs, the logo split with `scripts/logo_split.py`. | `references/style.md`, `references/build.md` |
| G7 | **QA:** `npx hyperframes check`, snapshots, then `scripts/sheets.py` on the rendered MP4 around **every** transition. Fix every glitch before delivering. | `references/qa.md` |
| G8 | **Render** at 60fps, delivery quality. Deliver the MP4 with a short note: what each scene does, what was not verified (e.g. you can't listen to audio), open risks. | `references/build.md` |

If the user asks for several cuts (e.g. "with phone / without phone / free style"), they share G3–G5. Build each cut as its own folder with its own sources.

## Non-negotiables (learned the hard way)

- **Never a slideshow.** The camera moves all the time and the background is always alive. Elements fly between scenes; no hard cuts, no "fade in a static card".
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
- **Full list** (what `doctor.py` checks): Python 3.10+ (numpy, scipy), FFmpeg/FFprobe (full build), Node.js 20+ / npx, HyperFrames (via npx, with its bundled headless Chromium), GSAP 3.14.2 (CDN, needs network), yt-dlp (optional), Playwright + Chromium (optional, for `extract_brand.py`), git (optional), Azure Speech (TTS + fast transcription REST APIs), Gemini API (TTS fallback).
