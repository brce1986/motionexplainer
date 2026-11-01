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
3. Follow the gates G1–G8, including **G2b, a design system for the video** (`design-system.md` + `tokens.css` + a style board PNG for approval). Stop for approval after the script (G3) unless the user said to go straight through.

Rules that apply to any agent:
- **Never write, print or commit an API key.** Keys come only from the environment or a git-ignored `.env`.
- Keep client material (logos, fonts, photos, renders) out of this repository.
- Before delivering, look at the QA contact sheets (`scripts/sheets.py`) of the rendered MP4. Open the PNGs with your image viewer.
- If you can't open the client's site in a browser tool, use `scripts/extract_brand.py`.
