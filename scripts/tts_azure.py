"""Azure Speech TTS (HD neural voices) from a plain script.
  python scripts/tts_azure.py script.txt out.mp3 --voice "en-US-Andrew:DragonHDLatestNeural" [--temperature 0.8] [--lang en-US] [--style happy]
  python scripts/tts_azure.py --list pt-BR
script.txt: one sentence per line; a blank line = 500 ms break; "[pause 700]" = custom break.
Env: AZURE_SPEECH_KEY, AZURE_SPEECH_REGION."""
import argparse
import json
import re
import urllib.request
from xml.sax.saxutils import escape

from _env import need


def ssml(lines, voice, lang, temperature, style):
    out, para = [], []

    def flush():
        if para:
            body = " ".join(f"<s>{escape(s)}</s>" for s in para)
            out.append(f"<p>{body}</p>")
            para.clear()

    for raw in lines:
        line = raw.strip()
        m = re.fullmatch(r"\[pause (\d+)\]", line)
        if m:
            flush(); out.append(f'<break time="{m.group(1)}ms"/>')
        elif not line:
            flush(); out.append('<break time="500ms"/>')
        else:
            para.append(line); flush()   # one sentence per <p><s>: HD voices stop merging sentences
    flush()
    body = "\n".join(out)
    if style:
        body = f'<mstts:express-as style="{escape(style)}">{body}</mstts:express-as>'
    params = f' parameters="temperature={temperature}"' if temperature is not None and "Dragon" in voice else ""
    return (f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="{lang}">'
            f'<voice name="{escape(voice)}"{params}>\n{body}\n</voice></speak>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script", nargs="?")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--voice", default="en-US-Andrew:DragonHDLatestNeural")
    ap.add_argument("--lang", default=None, help="defaults to the voice's locale")
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--style", default=None)
    ap.add_argument("--list", metavar="LOCALE", help="list voices for a locale, e.g. pt-BR")
    a = ap.parse_args()
    key, region = need("AZURE_SPEECH_KEY"), need("AZURE_SPEECH_REGION")

    if a.list:
        req = urllib.request.Request(f"https://{region}.tts.speech.microsoft.com/cognitiveservices/voices/list",
                                     headers={"Ocp-Apim-Subscription-Key": key})
        for v in json.load(urllib.request.urlopen(req, timeout=60)):
            if v["Locale"] == a.list:                     # native voices of that locale (HD ones included)
                print(f'{v["ShortName"]:50} {v["Gender"]:7} {v.get("VoiceType", "")} {",".join(v.get("StyleList", []))}')
        return
    if not (a.script and a.out):
        ap.error("script and out are required")
    lang = a.lang or "-".join(a.voice.split("-")[:2])
    lines = open(a.script, encoding="utf-8").read().splitlines()
    body = ssml(lines, a.voice, lang, a.temperature, a.style).encode("utf-8")
    fmt = "audio-48khz-192kbitrate-mono-mp3" if a.out.endswith(".mp3") else "riff-48khz-16bit-mono-pcm"
    req = urllib.request.Request(f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1", data=body, method="POST",
                                 headers={"Ocp-Apim-Subscription-Key": key, "Content-Type": "application/ssml+xml",
                                          "X-Microsoft-OutputFormat": fmt, "User-Agent": "motionexplainer"})
    try:
        data = urllib.request.urlopen(req, timeout=180).read()
    except urllib.error.HTTPError as e:
        hint = ""
        if e.code in (401, 403):
            hint = (f"\nThe key was rejected in region '{region}'. A Speech key only works in its resource's region: "
                    "check AZURE_SPEECH_REGION in the Azure portal (Speech resource > Keys and Endpoint). "
                    "Try tts_gemini.py if GEMINI_API_KEY is set; otherwise STOP and ask the user for a working key. "
                    "Never fall back to an OS voice.")
        raise SystemExit(f"Azure TTS failed: HTTP {e.code} {e.read()[:300]!r}{hint}")
    open(a.out, "wb").write(data)
    print(f"wrote {a.out} ({len(data) // 1024} KB) with {a.voice}")


if __name__ == "__main__":
    main()
