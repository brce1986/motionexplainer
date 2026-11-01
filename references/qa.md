# G7: The glitch hunt (before every delivery)

`hyperframes check` passing proves nothing about motion. Look at the **rendered MP4**:

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
