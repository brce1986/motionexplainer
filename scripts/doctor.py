"""Check every dependency the skill uses, and which keys are set (values are never shown).
  python scripts/doctor.py            # exit 0 = ready, 1 = something required is missing
Run it on the first call of the skill, before asking the user for anything else."""
import platform
import re
import shutil
import subprocess
import sys
import urllib.request

from _env import has

HYPERFRAMES = "0.8.198"              # the version the skill is tested with (pinned in every npx call)
OS = platform.system()               # Windows / Darwin / Linux
INSTALL = {
    "ffmpeg": {"Windows": "winget install Gyan.FFmpeg", "Darwin": "brew install ffmpeg", "Linux": "sudo apt install ffmpeg"},
    "node": {"Windows": "winget install OpenJS.NodeJS.LTS", "Darwin": "brew install node", "Linux": "https://nodejs.org (or nvm install --lts)"},
    "python": {"Windows": "winget install Python.Python.3.12", "Darwin": "brew install python", "Linux": "sudo apt install python3 python3-pip"},
}
missing_required, missing_optional = [], []


def run(cmd, timeout=60):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=(OS == "Windows" and cmd[0] in ("npx", "npm")))
        return r.returncode, (r.stdout + r.stderr).strip()
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return 1, str(e)


def row(name, good, fix="", required=True, detail=""):
    print(f"  {'OK ' if good else ('-- ' if required else 'opt')} {name}{('  ' + detail) if detail else ''}{'' if good else '  -> ' + fix}")
    if not good:
        (missing_required if required else missing_optional).append(name)


print(f"System: {OS} {platform.release()}  Python {platform.python_version()}\n")

print("Core tools")
row("Python >= 3.10", sys.version_info >= (3, 10), INSTALL["python"].get(OS, ""))
ff = shutil.which("ffmpeg")
row("ffmpeg", bool(ff), INSTALL["ffmpeg"].get(OS, ""))
row("ffprobe", bool(shutil.which("ffprobe")), "comes with FFmpeg")
if ff:
    _, filters = run(["ffmpeg", "-hide_banner", "-filters"])
    _, encoders = run(["ffmpeg", "-hide_banner", "-encoders"])
    row("ffmpeg filters loudnorm/ebur128/tile", all(f in filters for f in ("loudnorm", "ebur128", "tile")), "use a full FFmpeg build")
    row("ffmpeg encoder libx264", "libx264" in encoders, "use a full FFmpeg build (GPL)")
node = shutil.which("node")
nv = run(["node", "--version"])[1] if node else ""
major = int(re.findall(r"v(\d+)", nv)[0]) if re.findall(r"v(\d+)", nv) else 0
row("Node.js >= 20", major >= 20, INSTALL["node"].get(OS, ""), detail=nv)
row("npx", bool(shutil.which("npx")), "comes with Node.js")

print("\nPython packages")
for mod, fix, req in (("numpy", "pip install numpy", True), ("scipy", "pip install scipy", True)):
    try:
        __import__(mod); row(mod, True)
    except ImportError:
        row(mod, False, fix, required=req)

print("\nVideo engine")
if shutil.which("npx"):
    code, out = run(["npx", "--yes", f"hyperframes@{HYPERFRAMES}", "--version"], timeout=300)
    row(f"HyperFrames {HYPERFRAMES} (npx, downloads on first use + its headless Chromium)", code == 0,
        f"check the network / npm registry access ({out[-120:]})", detail=out.splitlines()[-1] if code == 0 and out else "")
try:
    urllib.request.urlopen("https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js", timeout=15)
    row("GSAP 3.14.2 on cdn.jsdelivr.net (loaded by the composition)", True)
except Exception as e:
    row("GSAP on cdn.jsdelivr.net", False, f"network access needed at render time ({e})")

print("\nOptional")
row("yt-dlp (reference-video frames)", bool(shutil.which("yt-dlp")), "pip install yt-dlp", required=False)
row("git (publishing/versioning)", bool(shutil.which("git")), "install git", required=False)

print("\nKeys (values hidden)")
row("AZURE_SPEECH_KEY", has("AZURE_SPEECH_KEY"), "primary voice + transcription check", required=False)
row("AZURE_SPEECH_REGION", has("AZURE_SPEECH_REGION"), "e.g. eastus", required=False)
row("GEMINI_API_KEY", has("GEMINI_API_KEY"), "fallback voice", required=False)
if not (has("AZURE_SPEECH_KEY") or has("GEMINI_API_KEY")):
    missing_required.append("a TTS key (Azure or Gemini)")
    print("  !! at least one TTS key is required (Azure preferred: it also enables the transcription check)")

print()
if missing_required:
    print("NOT READY. Missing: " + ", ".join(missing_required))
else:
    print("READY" + (f"  (optional missing: {', '.join(missing_optional)})" if missing_optional else ""))
sys.exit(1 if missing_required else 0)
