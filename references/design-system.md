# G2b: The video's design system

Before writing the script, turn what you learned into **one design system for this video**. It comes from two sources:
- **G2, the client's brand:** colours, gradients, fonts, photos, logo;
- **G1, the references:** type sizes and weights, background treatment, density, glass vs solid, energy.

The brand wins on identity (colours, fonts, logo). The references win on treatment (how big, how dark, how much glow, how fast). Every later scene uses only these tokens, which is what keeps a 60s film coherent.

## Deliverables (in the project root)
1. **`design-system.md`:** the decisions, each with its source ("teal #2DC8C4: client CTA colour; glow strength: ref 2").
2. **`tokens.css`:** the same decisions as CSS custom properties (start from `templates/tokens.example.css`). The composition imports it, so no colour or size is hard-coded in a scene.
3. **The style board:** render `templates/design-system.html` (it reads `tokens.css`) to a PNG and show it to the user for approval:
   - copy it next to the composition;
   - run `npx hyperframes snapshot --at 0.5`.

   It shows the palette, the gradient, the type scale, a glass card, buttons and pills, the background and the logo on it.

## What to decide
| Group | Tokens | How to choose |
|---|---|---|
| **Colour** | backgrounds (2–3 steps), text, secondary text, brand A, brand B, signature gradient, success/warning if the UI needs them | from the site; give each colour **one meaning** (e.g. A = customer side, B = provider side) |
| **Theme** | dark or light | the client's own theme first; the references can push it (e.g. dark glass for a premium feel) |
| **Type** | display font, UI font, numbers font; sizes for the title band (88/112px), headline, card title, body, label; weights; tracking | the client's webfonts; sizes and weights from the references; min 28px for reading text in 1080p |
| **Highlights** | how the gradient appears (text clip on the key word, button fill, thin beam) | from the site's hero |
| **Glass** | fill, blur, border, inner highlight, shadow | dark: navy at 0.55–0.66 + 26px blur; light: white at 0.6 |
| **Radius & spacing** | card radius, pill radius, gaps | from the site's components |
| **Background** | base gradient, glow colours and strength, photo layer (blur, opacity), grain or beam | references for the strength, brand for the colours |
| **Motion** | eases (arrive / leave / camera / drift), durations (flight 0.6–0.9, morph 0.6, title roll 0.6), camera range (rotY ±12°, z 0–450), blur peak | references for the energy; keep the house style's rules |
| **Imagery** | the client's photos first; stock only to fill gaps (see `stock-images.md`); one grade for all of it (e.g. a slight cool shadow, shared corner radius) | consistency over quantity |

Show the board and the table. Adjust after feedback, then freeze the tokens: a change after G6 means re-checking every scene.
