"""Glitch hunt: a 10 fps contact sheet (6x2 tiles = 1.2 s) starting at each given time of a rendered MP4.
  python scripts/sheets.py film.mp4 qa/ 6.2 8.6 11.8
Read every sheet; see references/qa.md for what to look for."""
import subprocess
import sys
from pathlib import Path

if len(sys.argv) < 4:
    raise SystemExit(__doc__)
video, out, times = sys.argv[1], Path(sys.argv[2]), sys.argv[3:]
out.mkdir(parents=True, exist_ok=True)
for t in times:
    dst = out / f"s_{t}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", t, "-t", "1.2", "-i", video,
                    "-vf", "fps=10,scale=240:-1,tile=6x2", "-frames:v", "1", str(dst)], check=True)
    print(dst)
