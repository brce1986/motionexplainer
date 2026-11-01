# The house style

A premium SaaS explainer: dark or light **liquid glass** over a **living background**, filmed by a **camera that never stops**, with screens that **fly, morph and dock** instead of cutting. Calm, centred, one subject at a time.

The reference videos (G1) tune the **pace, camera energy and transition vocabulary**. They never override the non-negotiables below.

## Composition
- **Centred and balanced.** One subject per frame, plus the title and the background. Too many elements is a defect.
- **Title band.** A fixed band at the top holds the verb of the beat ("Compare.", "Book it.", "Your rate."). It sits in the same place and size in every scene and rolls up through a mask, word by word with the VO. The highlight word uses the brand gradient.
- **Device mockups (phones):** at most **twice** per film, centred. A current model (Dynamic Island), never one with a notch; devices.css (MIT, in `assets/vendor`) restyled is fine. Some cuts are better with no phone at all: the client's photos plus floating UI cards.
- **Every UI card** is real UI rebuilt in HTML with the client's tokens, aligned by flex/grid, never by hand-set coordinates.

## The 3D world and the camera
- `#space` (perspective ~2400–2600) > `#world` (`preserve-3d`, centred under the title band). Every subject lives in the world, so all of them share one angle and scale.
- **The camera** is the world rotating and dollying:
  - `cam(t, dur, rotY, rotX, z, y)`, a slow drift on every segment;
  - a quicker "whip" (`power3.inOut`, ~0.9s) at scene changes;
  - the background moves the opposite way (parallax).
- **Focus:** whatever is not the subject gets `blur(4–8px) brightness(.85–.94)` and steps back in z.

## Motion
- **Flights:** `fly(sel, from, to, t, dur, ease, mb)`, one element on one path.
  - **Motion blur** is a blur that peaks mid-flight and clears on landing (`mb` 3–6px).
  - **Never** use lagged clone copies ("shutter streak"): they read as double images on big moves.
  - Native/registry motion blur ignores `preserve-3d`.
- **Entrances** come from depth (`z: -800…-900`, small offset, fade) or jump out of the element that triggered them (a button, a search bar, a card). **Exits** go back into depth. Two subjects swapping go out and in **in sequence**, never crossing near the lens.
- **Morph (card A becomes card B):**
  1. fade A's content out;
  2. set B, empty, at exactly A's box (non-uniform `scaleX/scaleY` from measured sizes);
  3. hide A in the same frame;
  4. grow B to its own size;
  5. fade B's content in while the box is still settling.

  On the return trip, reverse it and let A arrive already showing its new state.
- **Grid reveals** (e.g. a photo → 6 tiles):
  - the big image blurs up and fades out;
  - the tiles grow out of the centre (start at their offset to the centre, scale ~0.35, blur ~14px), sharpen and fade in with a small stagger.
- **Text that changes over time** (typing, counters) is computed from the time itself: `texts(t)` on `onUpdate` + the `hf-seek` event. That way any seek or render frame is right.
- **Eases:** `expo.out` for arrivals, `power3.in` for departures, `power3.inOut` for camera moves and morphs, `sine.inOut` for drifts.

## The living background
- A base gradient in the brand's background colours.
- 2–3 big blurred radial **glows** in the brand colours, drifting on long yoyo loops.
- **The drift moves the glow; scene-driven changes move a wrapper.** Scene changes are colour switches, convergence behind the logo, opacity. If both write the same property, the glow jumps.
- The client's photos, small, blurred (~9px), low opacity, drifting at the edges.
- Optional: a thin gradient "beam" crossing the frame. Its loop must restart **off-frame**.
- Loops must cover the whole duration (`repeat` × duration ≥ film length) or they stop mid-film.

## Glass
`background: linear-gradient(180deg, rgba(ink,.62), rgba(ink,.52)); backdrop-filter: blur(26px) saturate(160%); border: 1px solid rgba(255,255,255,.11); inset top highlight + deep soft shadow`. On light themes, use white at 0.6 with a white border instead.

## Brand
- **Text:** white on dark (or the brand ink on light).
- **Highlights:** the brand gradient through `background-clip: text`.
- **One colour, one meaning** (e.g. teal = customer side, yellow = provider side; switch the glows when the side switches).
- **Fonts:** the client's own webfont (self-hosted woff2 from the site) via `@font-face`. Check that the client's licence covers video use; mention it to the user.
- **The logo:**
  - from the client's SVG, inlined and split with `scripts/logo_split.py` so its parts animate (e.g. a mark that spins in, letters that rise in groups);
  - its distinctive mark (a ring, a symbol) can become a recurring device: a "verified" seal, a transition iris, a closing element.
- **Lockup:**
  1. logo + tagline arrive centred;
  2. when the CTA buttons and the URL arrive, logo + tagline lift and shrink slightly (~0.9) so the whole group stays centred;
  3. write the URL with `www.`.

## Audio-picture lock
- The VO starts ~1s in.
- The brand line lands on a musical downbeat.
- Every visible action has its SFX on the word that names it: pops for messages, whoosh on flights, ticks on list items, coin on money, success arpeggio on confirmations, riser + impact into the logo.
- Leave a **breath** (one bar, music thins, then rises) before the closing logo. Never run a riser under a word.
