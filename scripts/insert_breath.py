"""Insert silence into a VO at a sentence boundary (e.g. one bar before the logo).
  python scripts/insert_breath.py in.mp3 out.mp3 --at 42.3 --seconds 2.24
Shift every later word timing / cue by --seconds afterwards."""
import argparse
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("out")
ap.add_argument("--at", type=float, required=True, help="VO time where the silence goes (between two sentences)")
ap.add_argument("--seconds", type=float, required=True)
a = ap.parse_args()
f = (f"[0:a]atrim=0:{a.at},asetpts=N/SR/TB[a];[0:a]atrim=start={a.at},asetpts=N/SR/TB[b];"
     f"anullsrc=r=48000:cl=mono,atrim=0:{a.seconds}[s];[a][s][b]concat=n=3:v=0:a=1")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.src, "-filter_complex", f, "-ar", "48000", "-b:a", "192k", a.out], check=True)
print(f"wrote {a.out}: +{a.seconds}s at {a.at}s")
