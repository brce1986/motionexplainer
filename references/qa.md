# G6b–G7: The animatic, the slideshow detector, the glitch hunt

`hyperframes check` passing proves nothing about motion: a film of static slides passes it with zero warnings.

## 1. Before any render: the build gate
```bash
python scripts/lint_composition.py video/index.html
```
It fails a composition that doesn't load GSAP, animates with WAAPI/CSS, has no 3D world, has too few `cam()`/`fly()` calls for its length (one camera move per ~6s, one flight per ~8s), shows the lockup logo as an `<img>`, or has no `@font-face`/`tokens.css`.

## 2. The animatic (G6b)
Render a draft, then measure and look:
```bash
npx --yes hyperframes@<version> render -o ../draft.mp4 -q draft
python scripts/motion_check.py ../draft.mp4 --min-fps 30
ffmpeg -v error -y -i ../draft.mp4 -vf "fps=1,scale=384:-1,tile=6x10" -frames:v 1 qa/animatic.jpg
```
`motion_check.py` fails the film when:
- less than 65% of the frames move;
- any hold (picture barely changing) is longer than 3s, or more than 4 holds are longer than 1.5s;
- a transition fades to the empty background for 0.8s or more;
- (final render) the file isn't 60fps.

It was calibrated on shipped films (75–80% moving, longest hold 2.8s) and on a rejected slideshow (29% moving, 13 holds up to 4.3s, six 2s fades to empty). A window that is sparse on purpose (one word on black) can be exempted with `--allow START-END`, justified in TREATMENT.md. A fade between two scenes is never a valid exemption.

On `animatic.jpg`, check what the script can't: does every scene have the same layout? Is the subject small, with half the frame empty? Does anything carry the eye from one scene into the next? If it looks like a deck of slides, rebuild the staging; adding more fades or drifts doesn't fix it.

## 3. The glitch hunt (G7)
Look at the **rendered MP4**:

```bash
python scripts/sheets.py Client_explainer.mp4 qa/ 6.2 8.6 11.8 14.4 20.1 ...    # 10fps contact sheets, 1.2s each
```
Pick the times just before every transition, entrance and exit. Read every sheet.

## What to look for (each one has really happened)
| Symptom | Usual cause | Fix |
|---|---|---|
| Elements flash for a frame before their entrance | no initial `opacity: 0` (a `fromTo` with `immediateRender: false` doesn't hide them earlier) | `tl.set(..., {opacity: 0}, 0)` on everything that enters later |
| Double or ghost images on a flight | lagged clone motion blur | a blur peak on the element itself |
| Two versions of a card on screen | a morph without the swap | set B at A's box, hide A in the same frame |
| A card reappears or blinks mid-flight | two tweens fighting over the same property (a flight's `opacity` vs a separate fade) | one tween owns each property |
| The background jumps or pops, mostly near the end | a drift loop and a scene tween on the same element and property; a loop that ends before the film; a loop restart visible on screen | wrappers; enough repeats; restart off-frame |
| Wrong font or size on dynamic text | a CSS rule meant for labels also matching the value (`.field span`) | a child combinator (`.field > span`) |
| Two big subjects cross near the lens | simultaneous lateral swap | out into depth, then in from depth |
| A word missing or garbled in the audio | a riser or SFX under it | `stt_check.py` on the mix; move the SFX |
| Text wraps badly in a small bubble | no fixed width | width + line-height, or `nowrap` |
| A blur "pulse" on a big device | motion blur on a large element | `mb: 0` for phones and full-frame photos |

After fixing, render again and **re-sheet the same times**. Deliver only when no sheet shows a glitch. Say what you checked and what you couldn't (audio by ear).
