"""The slideshow detector: measures motion in a rendered MP4 and fails the film if it reads as slides.
  python scripts/motion_check.py film.mp4 [--json qa/motion.json] [--allow 0.6-2.5 ...]
Checks (sampled at 10 fps, 160 px wide, grayscale):
- STILL: no window where the picture barely changes may last longer than --max-still (default 3.0s),
         and at most --max-holds (default 4) may last longer than 1.5s;
- DIP:   no transition may fade to an empty background (content below --dip of the film's median) for --max-dip (0.8s) or more;
- FPS:    the file must be at the delivery frame rate (--min-fps, default 60);
- MOTION: the share of frames with visible motion must reach --min-moving (default 0.65).
Calibrated on shipped films (moving 75-80%, longest hold 2.8s, dips <= 0.6s through an iris)
and on a rejected slideshow (moving 29%, thirteen holds up to 4.3s, six 2s fades to empty).
The last --tail seconds (default 2.5, the lockup) may hold still.
--allow START-END exempts a window that is sparse on purpose (e.g. one word on black). Every allowed window
must be justified in TREATMENT.md; a fade between two scenes is never a valid exemption.
Exit code 1 if any check fails. Run it on the delivery MP4 before G8 ends; paste its output in the delivery note."""
import argparse
import json
import subprocess
import sys

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("--fps", type=float, default=10)
ap.add_argument("--still", type=float, default=0.35, help="mean abs frame diff (0-255) under which a frame counts as still")
ap.add_argument("--max-still", type=float, default=3.0)
ap.add_argument("--max-holds", type=int, default=4)
ap.add_argument("--dip", type=float, default=0.45)
ap.add_argument("--max-dip", type=float, default=0.8)
ap.add_argument("--min-moving", type=float, default=0.65)
ap.add_argument("--tail", type=float, default=2.5)
ap.add_argument("--min-fps", type=float, default=60, help="delivery frame rate")
ap.add_argument("--json")
ap.add_argument("--allow", nargs="*", default=[], help="START-END windows exempted on purpose")
a = ap.parse_args()

W, H = 160, 90
probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                        "-of", "csv=p=0", a.video], capture_output=True, text=True, check=True).stdout.strip().split(",")
vw, vh = int(probe[0]), int(probe[1])
num, den = probe[2].split("/")
src_fps = float(num) / float(den)
H = max(2, round(W * vh / vw / 2) * 2)
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", a.video, "-vf", f"fps={a.fps},scale={W}:{H},format=gray",
                      "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
f = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
n = len(f)
dur = n / a.fps
diff = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))           # motion between consecutive samples
# "content": edge energy, i.e. how much is drawn on the frame (an empty gradient background is close to 0)
gx = np.abs(np.diff(f, axis=2)).mean(axis=(1, 2))
gy = np.abs(np.diff(f, axis=1)).mean(axis=(1, 2))
content = gx + gy
limit = dur - a.tail

stills, run = [], None
for i, d in enumerate(diff):
    t = (i + 1) / a.fps
    if d < a.still and t < limit:
        run = run if run is not None else t
    else:
        if run is not None and t - run > 1.0:
            stills.append((round(run, 1), round(t, 1)))
        run = None
if run is not None and limit - run > 1.0:
    stills.append((round(run, 1), round(limit, 1)))

med = float(np.median(content))
dips = []
k = 0
while k < n:
    if content[k] < a.dip * med and 0.5 < k / a.fps < limit:
        j = k
        while j < n and content[j] < a.dip * med:
            j += 1
        dips.append((round(k / a.fps, 1), round(j / a.fps, 1)))
        k = j
    else:
        k += 1

body = diff[: max(1, int(limit * a.fps) - 1)]
moving = float((body >= a.still).mean())
allowed = [tuple(float(x) for x in w.split("-")) for w in a.allow]
def exempt(w):
    return any(s0 <= w[0] and w[1] <= e0 for s0, e0 in allowed)
stills = [w for w in stills if not exempt(w)]
dips = [d for d in dips if not exempt(d)]
too_long = [w for w in stills if w[1] - w[0] > a.max_still]
holds = [w for w in stills if w[1] - w[0] > 1.5]
bad_dips = [d for d in dips if d[1] - d[0] >= a.max_dip]
fps_ok = src_fps >= a.min_fps - 0.5
fail = bool(not fps_ok or too_long or len(holds) > a.max_holds or bad_dips or moving < a.min_moving)
report = {
    "video": a.video, "duration": round(dur, 2),
    "fps": round(src_fps, 2), "moving_share": round(moving, 3), "moving_required": a.min_moving,
    "median_motion": round(float(np.median(body)), 3),
    "still_windows": stills, "too_long": too_long, "holds_over_1_5s": len(holds), "empty_dips": dips, "bad_dips": bad_dips, "pass": not fail,
}
print(f"{a.video}: {dur:.1f}s sampled at {a.fps:g} fps")
print(f"  frame rate     : {src_fps:g} fps (need {a.min_fps:g})" + ("" if fps_ok else "  <- render again with -f 60"))
print(f"  moving frames : {moving:.0%} (need >= {a.min_moving:.0%}), median motion {report['median_motion']}")
print(f"  still > 1s     : {len(stills)}  " + " ".join(f"{s}-{e}s" for s, e in stills))
print(f"  holds > 1.5s   : {len(holds)} (max {a.max_holds}); longer than {a.max_still:g}s: {len(too_long)}")
print(f"  empty dips     : {len(dips)}, of {a.max_dip:g}s or more: {len(bad_dips)}  " + " ".join(f"{s}-{e}s" for s, e in bad_dips))
print("  RESULT: " + ("PASS" if not fail else "FAIL: this reads as a slideshow. See references/style.md, then rebuild the failing scenes."))
if a.json:
    with open(a.json, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
sys.exit(1 if fail else 0)
