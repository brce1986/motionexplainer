# G1: Reading the reference videos

The user sends **at least 3** references (YouTube links or files). They tune pace, camera energy, transitions and density. They never override the house style's non-negotiables (`style.md`).

## Getting frames
```bash
python scripts/ref_frames.py "<youtube-url-or-file>" refs/ref1     # needs yt-dlp + ffmpeg
```
The script downloads a low-res copy into its own folder, then writes `refs/ref1/sheet_*.jpg`: contact sheets at 2 fps, 6×4 tiles per sheet. Look at the sheets; don't guess from titles.

- **No yt-dlp, or the download is blocked:** ask the user for a local file, or for timestamps plus a sentence on what they like.
- **Never redistribute the downloaded videos.** They are for analysis only; delete them after G1 (`--keep` keeps them).

## What to write down (in TREATMENT.md, one block per reference)
| Aspect | Notes |
|---|---|
| Pace | average shot length, how long a title stays, how much breathing room |
| Camera | static / drifting / aggressive pushes; 2D or 3D |
| Transitions | match cuts, morphs, wipes, iris, push-throughs; what carries the eye |
| Type | size and weight of titles, kinetic or static, how many words on screen |
| Density | elements per frame |
| Colour/light | dark vs light, glow, grain |
| Sound | music style, SFX density |
| **Borrow** | 2–3 concrete techniques to reuse |
| **Avoid** | what doesn't fit the client or the style |

End G1 with a 3-line synthesis: what the film borrows from the references, and how it keeps the house style.
