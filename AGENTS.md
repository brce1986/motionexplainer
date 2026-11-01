# MotionExplainer: agent instructions

This repository is an agent skill. The full workflow is in **[SKILL.md](SKILL.md)**. Read it first, then the guides in `references/` as each gate needs them.

When the user asks for an explainer, promo or product video for a company or website:
1. Run `python scripts/doctor.py` and report what is ready and what is missing (with install commands).
2. In the same first reply, ask for everything SKILL.md's STEP 0 lists:
   - the client's site or an assets folder;
   - the logo (SVG preferred);
   - at least 3 reference videos;
   - the Azure Speech and Gemini keys, as environment variables;
   - optionally, Pexels / Pixabay keys for extra stock photos;
   - the specs.
3. Follow the gates G1–G8, including **G2b, a design system for the video** (`design-system.md` + `tokens.css` + a style board PNG for approval) and **G2c, style frames** from the scene kit. Stop for approval after the script (G3) unless the user said to go straight through; the G2c and G6b approvals are never skipped.

**Read the HARD STOPS table in SKILL.md before starting.** In short:
- When a required step fails (a key returns 401, a reference can't be downloaded, the font can't be self-hosted), **stop and ask**. Never substitute an OS voice, a guessed reference, a system font or an `<img>` logo.
- Build from the scene kit `templates/kit/index.html` (`references/scene-kit.md`): choose scenes, time them to the voice, fill them with the client's material. Never write your own animation engine, WAAPI or CSS animations, and never invent layouts without an approved style frame.
- **Two approvals are mandatory even if the user said to go straight through:** the G2c style frames and the G6b animatic. If the user is away, prepare them and stop.
- The checks are a floor: never read their source to find what passes, never alias a system font, never add drift just to raise a score.
- Never reuse a direction (tokens, layouts) from a cut the user rejected.
- `python scripts/lint_composition.py video/index.html` must pass before any render.
- `python scripts/motion_check.py <render>.mp4` must PASS before delivery (it also enforces 60fps). Show the user a draft contact sheet (G6b) before the final render.

Rules that apply to any agent:
- **Never write, print or commit an API key.** Keys come only from the environment or a git-ignored `.env`.
- Keep client material (logos, fonts, photos, renders) out of this repository.
- Before delivering, look at the QA contact sheets (`scripts/sheets.py`) of the rendered MP4. Open the PNGs with your image viewer.
- If you can't open the client's site in a browser tool, use `scripts/extract_brand.py`.
