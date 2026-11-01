"""Gemini TTS (fallback voice). Writes a 24 kHz mono WAV.
  python scripts/tts_gemini.py script.txt out.wav --voice Puck --style "warm, confident explainer narrator"
Uses gemini-2.5-pro-preview-tts with "Say in <style>: <text>" (3.x TTS models read style prompts aloud).
Env: GEMINI_API_KEY."""
import argparse
import base64
import json
import re
import urllib.request
import wave

from _env import need


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("out")
    ap.add_argument("--voice", default="Puck")
    ap.add_argument("--style", default="a warm, clear, confident explainer narrator")
    ap.add_argument("--model", default="gemini-2.5-pro-preview-tts")
    a = ap.parse_args()
    key = need("GEMINI_API_KEY")
    text = " ".join(l.strip() for l in open(a.script, encoding="utf-8") if l.strip() and not re.fullmatch(r"\[pause \d+\]", l.strip()))
    body = {"contents": [{"parts": [{"text": f"Say in {a.style}: {text}"}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": a.voice}}}}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{a.model}:generateContent",
                                 data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key})
    try:
        r = json.load(urllib.request.urlopen(req, timeout=300))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Gemini TTS failed: HTTP {e.code} {e.read()[:300]!r}  (402 = prepaid credits depleted)")
    part = r["candidates"][0]["content"]["parts"][0]["inlineData"]
    pcm = base64.b64decode(part["data"])
    if pcm[:4] == b"RIFF":                       # some models return a full WAV
        open(a.out, "wb").write(pcm)
    else:                                        # raw 16-bit PCM, 24 kHz mono
        with wave.open(a.out, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
    print(f"wrote {a.out} with {a.voice}")


if __name__ == "__main__":
    main()
