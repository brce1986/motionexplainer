# G4–G5: Voice, check, soundtrack

All scripts read keys from the environment or a local `.env` (see `.env.example`). They never print keys.

## Voice (primary: Azure Speech HD)
```bash
python scripts/tts_azure.py script.txt audio/vo_andrew.mp3 --voice "en-US-Andrew:DragonHDLatestNeural" --temperature 0.8
python scripts/tts_azure.py script.txt audio/vo_ava.mp3    --voice "en-US-Ava:DragonHDLatestNeural"
```
- `script.txt` holds one sentence per line. A blank line adds a 500ms break; `[pause 700]` adds a custom break.
- The script wraps every line in `<p><s>`, which stops HD voices from merging sentences.
- `temperature` 0.7–0.9: higher is livelier but riskier.
- **Voices worth trying:**
  - en-US: `Ava`, `Andrew`, `Emma`, `Brian` (`:DragonHDLatestNeural`);
  - pt-BR: `pt-BR-Thalita:DragonHDLatestNeural` (very good), `pt-BR-Macerio:DragonHDLatestNeural`;
  - with style control: `pt-BR-Luana:MAI-Voice-2.1` and similar, via `--style happy`.
- List what the user's region offers: `python scripts/tts_azure.py --list pt-BR`.
- Make 2 takes (2 voices), send both, and let the user pick.

## Voice (fallback: Gemini TTS)
```bash
python scripts/tts_gemini.py script.txt audio/vo_gemini.wav --voice Puck --style "warm, confident explainer narrator"
```
- Uses `gemini-2.5-pro-preview-tts`.
- 3.x TTS models read the style prompt out loud, so the script uses the "Say in <style>: <text>" form on 2.5.
- Voices: Puck, Charon, Kore, Aoede, Fenrir, Orus…

## Check every take (and the final mix)
```bash
python scripts/stt_check.py audio/vo_andrew.mp3 --script script.txt --lang en-US --words audio/vo_words.json
```
- Transcribes with Azure fast transcription, prints each phrase with its times, flags sentences that are missing or merged, and writes word timestamps (`--words`) for the timeline.
- Run it again on the **final mix**: a riser or SFX can mask a word. A real case: "Wynwood" was transcribed as "Windrill" until the riser was moved off it.
- **TTS failures:** a generation that "fails" with no reason is often quota. Read the HTTP status and body; never retry blindly on paid APIs.

## A breath before the logo
To insert silence into the VO at a sentence boundary:
```bash
python scripts/insert_breath.py audio/vo.mp3 audio/vo_breath.mp3 --at 42.3 --seconds 2.24
```
Use exactly one bar (60/BPM×4) so the music grid is kept.

## Soundtrack (code-made, zero cost)
```bash
python scripts/soundtrack.py --vo audio/vo.mp3 --cues cues.json --out audio/
```
- Writes `music.wav`, `sfx.wav` and `mix.mp3`. The mix is at -14 LUFS, true peak -1, with the music ducked ~7dB under speech and a slow release.
- `cues.json` (see `templates/cues.example.json`) holds:
  - `vo_offset`;
  - `bpm`;
  - `anchor`: the VO time of the brand line, which lands on a downbeat;
  - `final_bar`: the bar index of the logo;
  - `breakdowns`: quiet bars;
  - `sfx`: a list of `{type, t}` in **VO time**. Types: pop, whoosh, whoosh_down, tick, tap, coin, success, bell, riser_to_final, impact_final.
- **Fit the BPM** so `final_bar` lands on the logo word: `bpm = 60 * 4 * bars / (logo_time - anchor_time)`. Keep it between 95 and 120.
- The music is synthesised (pads, pluck arpeggio, bass, light kick/hat, final chord, a soft arpeggio under the lockup, a fade-out), so there are no licensing questions. If the user wants AI music, Gemini Lyria is an option (`lyria-3-clip-preview` gives ~30s); keep the SFX from this script.
