"""Contact sheets of a reference video (YouTube URL or local file) for G1.
  python scripts/ref_frames.py "<url-or-file>" refs/ref1 [--fps 2] [--keep]
Downloads a low-res copy with yt-dlp (for analysis only), writes sheet_NN.jpg (6x4 tiles), then deletes the video
unless --keep. Never redistribute downloaded references."""
import argparse
import shutil
import subprocess
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("out")
ap.add_argument("--fps", type=float, default=2)
ap.add_argument("--keep", action="store_true")
a = ap.parse_args()
out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
src = Path(a.src)
if not src.is_file():
    if not shutil.which("yt-dlp"):
        raise SystemExit("yt-dlp not found (pip install yt-dlp), or pass a local file.")
    subprocess.run(["yt-dlp", "-f", "bv*[height<=480]+ba/b[height<=480]/b", "-o", str(out / "ref.%(ext)s"),
                    "--no-playlist", a.src], check=True)
    src = next(p for p in out.iterdir() if p.stem == "ref")
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)],
                           capture_output=True, text=True).stdout.strip() or 0)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", f"fps={a.fps},scale=320:-1,tile=6x4",
                str(out / "sheet_%02d.jpg")], check=True)
print(f"{src.name}: {dur:.1f}s -> {len(list(out.glob('sheet_*.jpg')))} sheets at {a.fps} fps in {out}")
if not a.keep and src.parent == out:
    src.unlink()
