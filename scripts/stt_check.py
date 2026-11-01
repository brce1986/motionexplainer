"""Transcribe a take (or the final mix) with Azure fast transcription and check it against the script.
  python scripts/stt_check.py audio/vo.mp3 --script script.txt --lang en-US [--words audio/vo_words.json] [--from 38]
Prints every phrase with its times, flags script sentences that weren't heard, and can save word timestamps.
Env: AZURE_SPEECH_KEY, AZURE_SPEECH_REGION."""
import argparse
import difflib
import json
import re
import urllib.request
import uuid
from pathlib import Path

from _env import need


def norm(s):
    return re.sub(r"[^\w ]+", "", s.lower()).split()


def transcribe(path, lang, key, region):
    b = uuid.uuid4().hex
    data = (f'--{b}\r\nContent-Disposition: form-data; name="definition"\r\n\r\n{json.dumps({"locales": [lang]})}\r\n'
            f'--{b}\r\nContent-Disposition: form-data; name="audio"; filename="{Path(path).name}"\r\nContent-Type: application/octet-stream\r\n\r\n').encode()
    data += Path(path).read_bytes() + f"\r\n--{b}--\r\n".encode()
    req = urllib.request.Request(f"https://{region}.api.cognitive.microsoft.com/speechtotext/transcriptions:transcribe?api-version=2024-11-15",
                                 data=data, method="POST",
                                 headers={"Ocp-Apim-Subscription-Key": key, "Content-Type": f"multipart/form-data; boundary={b}"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=300))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Azure STT failed: HTTP {e.code} {e.read()[:300]!r}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--script")
    ap.add_argument("--lang", default="en-US")
    ap.add_argument("--words")
    ap.add_argument("--from", dest="t0", type=float, default=0, help="only print phrases after this time")
    a = ap.parse_args()
    d = transcribe(a.audio, a.lang, need("AZURE_SPEECH_KEY"), need("AZURE_SPEECH_REGION"))
    phrases = d.get("phrases", [])
    for p in phrases:
        s = p["offsetMilliseconds"] / 1000
        if s >= a.t0:
            print(f"{s:7.2f}-{(p['offsetMilliseconds'] + p['durationMilliseconds']) / 1000:7.2f}  {p['text']}")
    if a.words:
        ws = [{"w": w["text"], "s": w["offsetMilliseconds"] / 1000, "e": (w["offsetMilliseconds"] + w["durationMilliseconds"]) / 1000}
              for p in phrases for w in p.get("words", [])]
        Path(a.words).write_text(json.dumps(ws, ensure_ascii=False, indent=0), encoding="utf-8")
        print(f"\nwrote {len(ws)} word timings to {a.words}")
    if a.script:
        heard = norm(" ".join(p["text"] for p in phrases))
        print("\nScript check (word overlap per sentence):")
        bad = 0
        for line in Path(a.script).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("[pause"):
                continue
            want = norm(line)
            m = difflib.SequenceMatcher(None, heard, want).find_longest_match(0, len(heard), 0, len(want))
            score = sum(1 for w in want if w in heard) / max(1, len(want))
            flag = "OK " if score > 0.85 and m.size >= min(3, len(want)) else "?? "
            bad += flag != "OK "
            print(f"  {flag}{score:4.0%}  {line}")
        print("\nAll sentences heard." if not bad else f"\n{bad} sentence(s) to listen to: check the names and the words under SFX.")


if __name__ == "__main__":
    main()
